"""FastAPI service for hand gesture recognition."""

from fastapi import FastAPI, File, UploadFile, WebSocket, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import cv2
import numpy as np
from PIL import Image
import io
import base64
import sys
from pathlib import Path
import asyncio

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from hand_detector import HandDetector
from gesture_recognizer import GestureRecognizer
from utils import image_to_base64, base64_to_image
from config import API_HOST, API_PORT, API_TITLE, API_VERSION, GESTURES

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="API for real-time hand gesture recognition"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize detector and recognizer
detector = HandDetector(max_hands=2)
recognizer = GestureRecognizer()


class HandDetectionResponse(BaseModel):
    """Response model for hand detection."""
    hands_detected: int
    hands: List[Dict]
    processing_time_ms: float


class GestureListResponse(BaseModel):
    """Response model for gesture list."""
    gestures: Dict[str, str]
    total_gestures: int


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Hand Detection & Gesture Recognition API",
        "version": API_VERSION,
        "endpoints": {
            "health": "/health",
            "gestures": "/gestures",
            "detect": "/detect (POST)",
            "detect_base64": "/detect/base64 (POST)",
            "webcam_stream": "/stream/webcam (WebSocket)"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "detector_ready": detector is not None,
        "recognizer_ready": recognizer is not None
    }


@app.get("/gestures", response_model=GestureListResponse)
async def get_gestures():
    """Get list of all supported gestures."""
    return {
        "gestures": GESTURES,
        "total_gestures": len(GESTURES)
    }


@app.post("/detect", response_model=HandDetectionResponse)
async def detect_hands(file: UploadFile = File(...)):
    """
    Detect hands and recognize gestures in an uploaded image.
    
    Args:
        file: Uploaded image file
        
    Returns:
        Detection results with hand information and gestures
    """
    import time
    start_time = time.time()
    
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        image = np.array(image)
        
        # Convert RGB to BGR if needed
        if image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Detect hands
        _, hands_info = detector.find_hands(image, draw=False)
        
        # Process each hand
        results = []
        for hand_info in hands_info:
            # Recognize gesture
            gesture_info = recognizer.recognize(hand_info)
            
            # Format response
            hand_data = {
                "hand_label": hand_info.hand_label,
                "finger_count": hand_info.finger_count,
                "fingers_up": {
                    "thumb": hand_info.fingers_up[0],
                    "index": hand_info.fingers_up[1],
                    "middle": hand_info.fingers_up[2],
                    "ring": hand_info.fingers_up[3],
                    "pinky": hand_info.fingers_up[4]
                },
                "gesture": {
                    "name": gesture_info["gesture"],
                    "description": gesture_info["description"],
                    "confidence": gesture_info["confidence"]
                },
                "bounding_box": {
                    "x": hand_info.bbox[0],
                    "y": hand_info.bbox[1],
                    "width": hand_info.bbox[2],
                    "height": hand_info.bbox[3]
                }
            }
            results.append(hand_data)
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "hands_detected": len(hands_info),
            "hands": results,
            "processing_time_ms": processing_time
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing image: {str(e)}"
        )


@app.post("/detect/base64")
async def detect_hands_base64(image_data: Dict[str, str]):
    """
    Detect hands from base64 encoded image.
    
    Args:
        image_data: Dict with "image" key containing base64 string
        
    Returns:
        Detection results
    """
    try:
        # Decode base64 image
        image = base64_to_image(image_data["image"])
        
        # Detect hands
        _, hands_info = detector.find_hands(image, draw=False)
        
        # Process hands
        results = []
        for hand_info in hands_info:
            gesture_info = recognizer.recognize(hand_info)
            
            results.append({
                "hand_label": hand_info.hand_label,
                "finger_count": hand_info.finger_count,
                "gesture": gesture_info["gesture"],
                "confidence": gesture_info["confidence"]
            })
        
        return {
            "hands_detected": len(hands_info),
            "hands": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing image: {str(e)}"
        )


@app.post("/detect/annotated")
async def detect_with_annotations(file: UploadFile = File(...)):
    """
    Detect hands and return annotated image.
    
    Args:
        file: Uploaded image file
        
    Returns:
        Annotated image with detections
    """
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        image = np.array(image)
        
        # Convert RGB to BGR
        if image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Detect and draw
        image, hands_info = detector.find_hands(image, draw=True)
        
        # Add gesture annotations
        for hand_info in hands_info:
            gesture_info = recognizer.recognize(hand_info)
            
            x, y, w, h = hand_info.bbox
            gesture_text = f"{gesture_info['gesture'].upper()}"
            
            cv2.rectangle(image, (x, y-40), (x+200, y), (0, 0, 0), -1)
            cv2.putText(
                image,
                gesture_text,
                (x+5, y-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )
        
        image = detector.draw_info(image, hands_info, show_bbox=True)
        
        # Convert to bytes
        _, buffer = cv2.imencode('.jpg', image)
        
        return StreamingResponse(
            io.BytesIO(buffer.tobytes()),
            media_type="image/jpeg"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing image: {str(e)}"
        )


@app.websocket("/stream/webcam")
async def websocket_webcam(websocket: WebSocket):
    """
    WebSocket endpoint for real-time webcam streaming with detection.
    
    Client should send base64 encoded frames and will receive
    annotated frames back.
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive frame from client
            data = await websocket.receive_json()
            
            if "image" not in data:
                continue
            
            # Decode image
            image = base64_to_image(data["image"])
            
            # Detect hands
            image, hands_info = detector.find_hands(image, draw=True)
            
            # Process gestures
            results = []
            for hand_info in hands_info:
                gesture_info = recognizer.recognize(hand_info)
                
                # Draw gesture
                x, y, w, h = hand_info.bbox
                gesture_text = f"{gesture_info['gesture'].upper()}"
                
                cv2.rectangle(image, (x, y-40), (x+200, y), (0, 0, 0), -1)
                cv2.putText(
                    image,
                    gesture_text,
                    (x+5, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )
                
                results.append({
                    "hand": hand_info.hand_label,
                    "fingers": hand_info.finger_count,
                    "gesture": gesture_info["gesture"]
                })
            
            image = detector.draw_info(image, hands_info)
            
            # Encode and send back
            image_base64 = image_to_base64(image)
            
            await websocket.send_json({
                "image": image_base64,
                "hands": results
            })
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    
    print(f"Starting Hand Detection API on {API_HOST}:{API_PORT}")
    print(f"API Documentation: http://{API_HOST}:{API_PORT}/docs")
    print(f"Interactive docs: http://{API_HOST}:{API_PORT}/redoc")
    
    uvicorn.run(app, host=API_HOST, port=API_PORT)
