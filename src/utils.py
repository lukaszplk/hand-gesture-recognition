"""Utility functions for video processing, recording, and visualization."""

import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
import base64

from config import (
    OUTPUTS_DIR,
    VIDEO_CODEC,
    VIDEO_EXTENSION,
    IMAGE_EXTENSION,
    FRAME_WIDTH,
    FRAME_HEIGHT
)


class VideoRecorder:
    """Record video with hand detection."""
    
    def __init__(self, fps: int = 30, frame_size: Tuple[int, int] = (640, 480)):
        """
        Initialize video recorder.
        
        Args:
            fps: Frames per second
            frame_size: (width, height)
        """
        self.fps = fps
        self.frame_size = frame_size
        self.video_writer = None
        self.is_recording = False
        self.output_path = None
    
    def start_recording(self, output_name: Optional[str] = None) -> str:
        """
        Start recording video.
        
        Args:
            output_name: Optional output filename
            
        Returns:
            Path to output file
        """
        if self.is_recording:
            return self.output_path
        
        if output_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"hand_detection_{timestamp}{VIDEO_EXTENSION}"
        
        self.output_path = str(OUTPUTS_DIR / output_name)
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*VIDEO_CODEC)
        self.video_writer = cv2.VideoWriter(
            self.output_path,
            fourcc,
            self.fps,
            self.frame_size
        )
        
        self.is_recording = True
        print(f"Recording started: {self.output_path}")
        return self.output_path
    
    def write_frame(self, frame: np.ndarray):
        """
        Write a frame to the video.
        
        Args:
            frame: Frame to write
        """
        if self.is_recording and self.video_writer is not None:
            # Resize frame if needed
            if frame.shape[:2][::-1] != self.frame_size:
                frame = cv2.resize(frame, self.frame_size)
            self.video_writer.write(frame)
    
    def stop_recording(self) -> Optional[str]:
        """
        Stop recording and save video.
        
        Returns:
            Path to saved video file
        """
        if not self.is_recording:
            return None
        
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
        
        self.is_recording = False
        print(f"Recording stopped: {self.output_path}")
        
        return self.output_path
    
    def __del__(self):
        """Cleanup."""
        if self.is_recording:
            self.stop_recording()


def save_screenshot(frame: np.ndarray, filename: Optional[str] = None) -> str:
    """
    Save a screenshot of the current frame.
    
    Args:
        frame: Frame to save
        filename: Optional filename
        
    Returns:
        Path to saved image
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}{IMAGE_EXTENSION}"
    
    output_path = OUTPUTS_DIR / filename
    cv2.imwrite(str(output_path), frame)
    print(f"Screenshot saved: {output_path}")
    
    return str(output_path)


def image_to_base64(image: np.ndarray) -> str:
    """
    Convert image to base64 string for web display.
    
    Args:
        image: Image array
        
    Returns:
        Base64 encoded string
    """
    _, buffer = cv2.imencode('.jpg', image)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{jpg_as_text}"


def base64_to_image(base64_string: str) -> np.ndarray:
    """
    Convert base64 string to image.
    
    Args:
        base64_string: Base64 encoded image
        
    Returns:
        Image array
    """
    # Remove data URL prefix if present
    if 'base64,' in base64_string:
        base64_string = base64_string.split('base64,')[1]
    
    img_data = base64.b64decode(base64_string)
    nparr = np.frombuffer(img_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    return image


def resize_image(image: np.ndarray, 
                width: Optional[int] = None, 
                height: Optional[int] = None) -> np.ndarray:
    """
    Resize image maintaining aspect ratio.
    
    Args:
        image: Input image
        width: Target width
        height: Target height
        
    Returns:
        Resized image
    """
    h, w = image.shape[:2]
    
    if width is None and height is None:
        return image
    
    if width is None:
        # Calculate width based on height
        aspect_ratio = w / h
        width = int(height * aspect_ratio)
    elif height is None:
        # Calculate height based on width
        aspect_ratio = h / w
        height = int(width * aspect_ratio)
    
    return cv2.resize(image, (width, height))


def add_text_with_background(image: np.ndarray,
                            text: str,
                            position: Tuple[int, int],
                            font_scale: float = 0.7,
                            font_thickness: int = 2,
                            text_color: Tuple[int, int, int] = (255, 255, 255),
                            bg_color: Tuple[int, int, int] = (0, 0, 0),
                            padding: int = 5) -> np.ndarray:
    """
    Add text with background rectangle to image.
    
    Args:
        image: Input image
        text: Text to display
        position: (x, y) position
        font_scale: Font scale
        font_thickness: Font thickness
        text_color: Text color (BGR)
        bg_color: Background color (BGR)
        padding: Padding around text
        
    Returns:
        Image with text
    """
    x, y = position
    
    # Get text size
    (text_w, text_h), baseline = cv2.getTextSize(
        text,
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        font_thickness
    )
    
    # Draw background rectangle
    cv2.rectangle(
        image,
        (x - padding, y - text_h - padding),
        (x + text_w + padding, y + baseline + padding),
        bg_color,
        -1
    )
    
    # Draw text
    cv2.putText(
        image,
        text,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        text_color,
        font_thickness
    )
    
    return image


def draw_fps(image: np.ndarray, fps: float) -> np.ndarray:
    """
    Draw FPS counter on image.
    
    Args:
        image: Input image
        fps: FPS value
        
    Returns:
        Image with FPS counter
    """
    text = f"FPS: {fps:.1f}"
    return add_text_with_background(
        image,
        text,
        (10, 30),
        font_scale=0.6,
        text_color=(0, 255, 0)
    )


class FPSCounter:
    """Calculate FPS for video processing."""
    
    def __init__(self, buffer_size: int = 30):
        """
        Initialize FPS counter.
        
        Args:
            buffer_size: Number of frames to average
        """
        self.buffer_size = buffer_size
        self.timestamps = []
    
    def update(self) -> float:
        """
        Update FPS calculation.
        
        Returns:
            Current FPS
        """
        import time
        self.timestamps.append(time.time())
        
        if len(self.timestamps) > self.buffer_size:
            self.timestamps.pop(0)
        
        if len(self.timestamps) < 2:
            return 0.0
        
        time_diff = self.timestamps[-1] - self.timestamps[0]
        fps = (len(self.timestamps) - 1) / time_diff if time_diff > 0 else 0.0
        
        return fps


def create_info_panel(width: int = 300, height: int = 200) -> np.ndarray:
    """
    Create an information panel image.
    
    Args:
        width: Panel width
        height: Panel height
        
    Returns:
        Panel image
    """
    panel = np.zeros((height, width, 3), dtype=np.uint8)
    return panel


if __name__ == "__main__":
    # Test utilities
    print("Testing video utilities...")
    
    # Test screenshot
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(test_image, "Test Screenshot", (50, 240), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    screenshot_path = save_screenshot(test_image, "test_screenshot.jpg")
    print(f"Screenshot saved to: {screenshot_path}")
    
    # Test FPS counter
    fps_counter = FPSCounter()
    for _ in range(10):
        import time
        time.sleep(0.03)
        fps = fps_counter.update()
    
    print(f"Calculated FPS: {fps:.2f}")
    print("Utilities test complete!")
