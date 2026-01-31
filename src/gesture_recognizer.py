"""Gesture recognition based on finger patterns and hand position."""

from typing import List, Optional, Dict
import numpy as np

from hand_detector import HandInfo
from config import GESTURES


class GestureRecognizer:
    """
    Recognize hand gestures based on finger patterns.
    
    Supported gestures:
    - Fist (0 fingers)
    - Pointing (index only)
    - Peace/Victory (index + middle)
    - Three (index + middle + ring)
    - Four (all except thumb)
    - Five (all fingers)
    - Thumbs Up
    - Thumbs Down
    - OK sign
    - Rock on (index + pinky)
    """
    
    def __init__(self):
        """Initialize gesture recognizer."""
        self.gesture_history = []
        self.history_size = 5
    
    def recognize(self, hand_info: HandInfo) -> Dict[str, any]:
        """
        Recognize gesture from hand information.
        
        Args:
            hand_info: HandInfo object
            
        Returns:
            Dictionary with gesture name, description, and confidence
        """
        fingers = hand_info.fingers_up
        count = hand_info.finger_count
        landmarks = hand_info.landmarks
        
        # Check specific gestures
        gesture = self._identify_gesture(fingers, count, landmarks, hand_info.hand_label)
        
        # Add to history for smoothing
        self.gesture_history.append(gesture)
        if len(self.gesture_history) > self.history_size:
            self.gesture_history.pop(0)
        
        # Get most common gesture in history
        if self.gesture_history:
            most_common = max(set(self.gesture_history), key=self.gesture_history.count)
            confidence = self.gesture_history.count(most_common) / len(self.gesture_history)
        else:
            most_common = gesture
            confidence = 1.0
        
        return {
            "gesture": most_common,
            "description": GESTURES.get(most_common, "Unknown gesture"),
            "confidence": confidence,
            "finger_count": count,
            "fingers_up": fingers
        }
    
    def _identify_gesture(self,
                         fingers: List[bool],
                         count: int,
                         landmarks: List[tuple],
                         hand_label: str) -> str:
        """
        Identify specific gesture pattern.
        
        Args:
            fingers: List of boolean indicating which fingers are up
            count: Total number of fingers up
            landmarks: Hand landmarks
            hand_label: "Left" or "Right"
            
        Returns:
            Gesture name
        """
        thumb, index, middle, ring, pinky = fingers
        
        # Fist - no fingers up
        if count == 0:
            return "fist"
        
        # Pointing - only index finger
        if count == 1 and index:
            return "pointing"
        
        # Peace/Victory - index and middle
        if count == 2:
            if index and middle and not thumb:
                return "peace"
            # Thumbs up/down detection
            elif thumb and not index and not middle and not ring and not pinky:
                # Check if thumb is pointing up or down based on landmark positions
                if self._is_thumbs_up(landmarks, hand_label):
                    return "thumbs_up"
                else:
                    return "thumbs_down"
            else:
                return "two"
        
        # Three fingers
        if count == 3:
            if thumb and index and middle:
                return "three"
            elif index and middle and ring and not thumb:
                return "three"
            else:
                return "three"
        
        # Four fingers
        if count == 4:
            if not thumb and index and middle and ring and pinky:
                return "four"
            else:
                return "four"
        
        # Five - all fingers up (open hand)
        if count == 5:
            return "five"
        
        # Rock on - index and pinky
        if index and pinky and not middle and not ring:
            return "rock"
        
        # OK sign - check if thumb and index are forming a circle
        if thumb and not index and middle and ring and pinky:
            if self._is_ok_sign(landmarks):
                return "ok"
        
        # Default to simple count
        return {
            0: "fist",
            1: "one",
            2: "two",
            3: "three",
            4: "four",
            5: "five"
        }.get(count, "unknown")
    
    def _is_thumbs_up(self, landmarks: List[tuple], hand_label: str) -> bool:
        """
        Determine if thumb is pointing up or down.
        
        Args:
            landmarks: Hand landmarks
            hand_label: "Left" or "Right"
            
        Returns:
            True if thumbs up, False if thumbs down
        """
        # Thumb tip (4) vs wrist (0)
        thumb_tip_y = landmarks[4][1]
        wrist_y = landmarks[0][1]
        
        # Thumbs up if tip is above wrist
        return thumb_tip_y < wrist_y
    
    def _is_ok_sign(self, landmarks: List[tuple]) -> bool:
        """
        Check if thumb and index finger are forming a circle (OK sign).
        
        Args:
            landmarks: Hand landmarks
            
        Returns:
            True if forming OK sign
        """
        # Get thumb tip and index tip
        thumb_tip = np.array(landmarks[4])
        index_tip = np.array(landmarks[8])
        
        # Calculate distance
        distance = np.linalg.norm(thumb_tip - index_tip)
        
        # Get palm size for reference
        wrist = np.array(landmarks[0])
        middle_mcp = np.array(landmarks[9])
        palm_size = np.linalg.norm(wrist - middle_mcp)
        
        # OK sign if tips are close together (within 30% of palm size)
        return distance < (palm_size * 0.3)
    
    def reset_history(self):
        """Reset gesture history."""
        self.gesture_history = []
    
    def get_gesture_list(self) -> Dict[str, str]:
        """
        Get list of all supported gestures.
        
        Returns:
            Dictionary of gesture names and descriptions
        """
        return GESTURES


if __name__ == "__main__":
    # Test gesture recognizer
    import cv2
    from hand_detector import HandDetector
    
    detector = HandDetector()
    recognizer = GestureRecognizer()
    cap = cv2.VideoCapture(0)
    
    print("Gesture Recognition Test - Press 'q' to quit")
    print("Supported gestures:")
    for name, desc in recognizer.get_gesture_list().items():
        print(f"  - {name}: {desc}")
    
    while True:
        success, image = cap.read()
        if not success:
            break
        
        # Detect hands
        image, hands_info = detector.find_hands(image)
        
        # Recognize gestures
        for hand_info in hands_info:
            gesture_info = recognizer.recognize(hand_info)
            
            # Draw gesture information
            x, y, w, h = hand_info.bbox
            
            gesture_text = f"{gesture_info['gesture'].upper()}"
            confidence_text = f"Conf: {gesture_info['confidence']:.2f}"
            
            # Background for text
            cv2.rectangle(image, (10, 10), (300, 80), (0, 0, 0), -1)
            
            # Gesture name
            cv2.putText(
                image,
                gesture_text,
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 0),
                2
            )
            
            # Confidence
            cv2.putText(
                image,
                confidence_text,
                (20, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1
            )
        
        # Draw hand info
        image = detector.draw_info(image, hands_info)
        
        # Display
        cv2.imshow("Gesture Recognition", image)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    detector.close()
