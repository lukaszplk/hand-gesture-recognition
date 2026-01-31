"""Hand detection and finger counting using MediaPipe 0.10.x."""

import cv2
import numpy as np
import os
from typing import Tuple, List, Optional, Dict
from dataclasses import dataclass

# MediaPipe 0.10.x imports
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from config import (
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    MAX_NUM_HANDS,
    FINGER_TIP_IDS,
    FINGER_PIP_IDS,
    FINGER_NAMES
)


@dataclass
class HandInfo:
    """Information about a detected hand."""
    hand_label: str  # "Left" or "Right"
    landmarks: List[Tuple[int, int]]  # List of (x, y) coordinates
    fingers_up: List[bool]  # Which fingers are up
    finger_count: int  # Total fingers up
    bbox: Tuple[int, int, int, int]  # Bounding box (x, y, w, h)


class HandDetector:
    """
    Hand detector using MediaPipe 0.10.x HandLandmarker.
    
    Features:
    - Detect up to 2 hands simultaneously
    - Count fingers
    - Get hand landmarks
    - Calculate bounding boxes
    - Determine hand orientation (left/right)
    """
    
    def __init__(self,
                 max_hands: int = MAX_NUM_HANDS,
                 detection_confidence: float = MIN_DETECTION_CONFIDENCE,
                 tracking_confidence: float = MIN_TRACKING_CONFIDENCE,
                 model_path: Optional[str] = None):
        """
        Initialize hand detector.
        
        Args:
            max_hands: Maximum number of hands to detect
            detection_confidence: Minimum confidence for hand detection
            tracking_confidence: Minimum confidence for hand tracking
            model_path: Path to hand_landmarker.task model file
        """
        self.max_hands = max_hands
        self.detection_confidence = detection_confidence
        self.tracking_confidence = tracking_confidence
        
        # Find model path
        if model_path is None:
            # Try to find model in models/ directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            model_path = os.path.join(project_root, 'models', 'hand_landmarker.task')
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Hand landmarker model not found at {model_path}.\n"
                "Please download it from: https://storage.googleapis.com/mediapipe-models/"
                "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            )
        
        # Create HandLandmarker
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_confidence,
            min_hand_presence_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )
        
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        print(f"[OK] HandDetector initialized with MediaPipe {mp.__version__}")
    
    def find_hands(self, image: np.ndarray, draw: bool = True) -> Tuple[np.ndarray, List[HandInfo]]:
        """
        Detect hands in an image.
        
        Args:
            image: Input image (BGR format)
            draw: Whether to draw landmarks on the image
            
        Returns:
            Tuple of (processed image, list of HandInfo objects)
        """
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Create MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        
        # Detect hands
        detection_result = self.landmarker.detect(mp_image)
        
        # Convert back to BGR for display
        image_output = image.copy()
        
        hands_info = []
        
        if detection_result.hand_landmarks and detection_result.handedness:
            for hand_landmarks, handedness in zip(
                detection_result.hand_landmarks,
                detection_result.handedness
            ):
                # Draw landmarks if requested
                if draw:
                    self._draw_landmarks(image_output, hand_landmarks)
                
                # Get hand information
                hand_info = self._process_hand(
                    hand_landmarks,
                    handedness,
                    image.shape
                )
                hands_info.append(hand_info)
        
        return image_output, hands_info
    
    def _draw_landmarks(self, image: np.ndarray, hand_landmarks):
        """Draw hand landmarks on image."""
        h, w, _ = image.shape
        
        # Draw connections
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),  # Index
            (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
            (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
            (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
            (5, 9), (9, 13), (13, 17)  # Palm
        ]
        
        # Convert landmarks to pixel coordinates
        points = []
        for landmark in hand_landmarks:
            x, y = int(landmark.x * w), int(landmark.y * h)
            points.append((x, y))
            cv2.circle(image, (x, y), 5, (0, 255, 0), -1)
        
        # Draw connections
        for start, end in connections:
            cv2.line(image, points[start], points[end], (255, 0, 0), 2)
    
    def _process_hand(self,
                     hand_landmarks,
                     handedness,
                     image_shape: Tuple[int, int, int]) -> HandInfo:
        """
        Process a single hand and extract information.
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            handedness: Hand label (left/right)
            image_shape: Shape of the image (h, w, c)
            
        Returns:
            HandInfo object
        """
        h, w, c = image_shape
        
        # Get hand label
        hand_label = handedness[0].category_name
        
        # Extract landmark positions
        landmarks = []
        for lm in hand_landmarks:
            cx, cy = int(lm.x * w), int(lm.y * h)
            landmarks.append((cx, cy))
        
        # Count fingers
        fingers_up = self._count_fingers(landmarks, hand_label)
        finger_count = sum(fingers_up)
        
        # Calculate bounding box
        bbox = self._calculate_bbox(landmarks)
        
        return HandInfo(
            hand_label=hand_label,
            landmarks=landmarks,
            fingers_up=fingers_up,
            finger_count=finger_count,
            bbox=bbox
        )
    
    def _count_fingers(self, landmarks: List[Tuple[int, int]], hand_label: str) -> List[bool]:
        """
        Count which fingers are up.
        
        Args:
            landmarks: List of landmark coordinates
            hand_label: "Left" or "Right"
            
        Returns:
            List of booleans indicating which fingers are up
        """
        fingers = []
        
        # Thumb (special case - check horizontal position)
        if hand_label == "Right":
            # For right hand, thumb up means tip is to the right of joint
            if landmarks[FINGER_TIP_IDS[0]][0] > landmarks[FINGER_TIP_IDS[0] - 1][0]:
                fingers.append(True)
            else:
                fingers.append(False)
        else:
            # For left hand, thumb up means tip is to the left of joint
            if landmarks[FINGER_TIP_IDS[0]][0] < landmarks[FINGER_TIP_IDS[0] - 1][0]:
                fingers.append(True)
            else:
                fingers.append(False)
        
        # Other fingers (check vertical position)
        for i in range(1, 5):
            # Finger is up if tip is above the PIP joint
            if landmarks[FINGER_TIP_IDS[i]][1] < landmarks[FINGER_TIP_IDS[i] - 2][1]:
                fingers.append(True)
            else:
                fingers.append(False)
        
        return fingers
    
    def _calculate_bbox(self, landmarks: List[Tuple[int, int]]) -> Tuple[int, int, int, int]:
        """
        Calculate bounding box for the hand.
        
        Args:
            landmarks: List of landmark coordinates
            
        Returns:
            Tuple of (x, y, width, height)
        """
        x_coords = [lm[0] for lm in landmarks]
        y_coords = [lm[1] for lm in landmarks]
        
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        return (x_min, y_min, x_max - x_min, y_max - y_min)
    
    def draw_info(self,
                  image: np.ndarray,
                  hands_info: List[HandInfo],
                  show_count: bool = True,
                  show_label: bool = True,
                  show_bbox: bool = False) -> np.ndarray:
        """
        Draw information on the image.
        
        Args:
            image: Input image
            hands_info: List of HandInfo objects
            show_count: Show finger count
            show_label: Show hand label (Left/Right)
            show_bbox: Show bounding box
            
        Returns:
            Image with drawn information
        """
        for hand_info in hands_info:
            x, y, w, h = hand_info.bbox
            
            # Draw bounding box
            if show_bbox:
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Prepare text
            text_parts = []
            if show_label:
                text_parts.append(hand_info.hand_label)
            if show_count:
                text_parts.append(f"{hand_info.finger_count} fingers")
            
            text = " - ".join(text_parts)
            
            # Draw text with background
            if text:
                (text_w, text_h), _ = cv2.getTextSize(
                    text,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    2
                )
                cv2.rectangle(image, (x, y - 35), (x + text_w + 10, y - 5), (0, 0, 0), -1)
                cv2.putText(
                    image,
                    text,
                    (x + 5, y - 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )
            
            # Draw individual finger status
            finger_text = ""
            for i, (finger_name, is_up) in enumerate(zip(FINGER_NAMES, hand_info.fingers_up)):
                if is_up:
                    finger_text += f"{finger_name[0]} "
            
            if finger_text:
                cv2.putText(
                    image,
                    f"Up: {finger_text}",
                    (x, y + h + 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 255),
                    1
                )
        
        return image
    
    def close(self):
        """Release resources."""
        self.landmarker.close()


if __name__ == "__main__":
    # Test the hand detector
    detector = HandDetector()
    cap = cv2.VideoCapture(0)
    
    print("Hand Detector Test - Press 'q' to quit")
    
    while True:
        success, image = cap.read()
        if not success:
            break
        
        # Detect hands
        image, hands_info = detector.find_hands(image)
        
        # Draw information
        image = detector.draw_info(image, hands_info, show_bbox=True)
        
        # Display
        cv2.imshow("Hand Detector", image)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    detector.close()
