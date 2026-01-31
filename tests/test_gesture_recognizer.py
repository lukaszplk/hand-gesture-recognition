"""Unit tests for gesture recognizer."""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from gesture_recognizer import GestureRecognizer
from hand_detector import HandInfo


class TestGestureRecognizer:
    """Test GestureRecognizer class."""
    
    def test_initialization(self):
        """Test recognizer initialization."""
        recognizer = GestureRecognizer()
        assert recognizer is not None
        assert recognizer.history_size == 5
        assert len(recognizer.gesture_history) == 0
    
    def test_recognize_fist(self):
        """Test recognizing fist gesture."""
        recognizer = GestureRecognizer()
        
        # Create mock hand info with all fingers down
        hand_info = HandInfo(
            hand_label="Right",
            landmarks=[(x * 10, 100) for x in range(21)],
            fingers_up=[False, False, False, False, False],
            finger_count=0,
            bbox=(10, 10, 100, 100)
        )
        
        result = recognizer.recognize(hand_info)
        
        assert result["gesture"] == "fist"
        assert result["finger_count"] == 0
        assert 0.0 <= result["confidence"] <= 1.0
    
    def test_recognize_pointing(self):
        """Test recognizing pointing gesture."""
        recognizer = GestureRecognizer()
        
        hand_info = HandInfo(
            hand_label="Right",
            landmarks=[(x * 10, 100) for x in range(21)],
            fingers_up=[False, True, False, False, False],
            finger_count=1,
            bbox=(10, 10, 100, 100)
        )
        
        result = recognizer.recognize(hand_info)
        
        assert result["gesture"] == "pointing"
        assert result["finger_count"] == 1
    
    def test_recognize_peace(self):
        """Test recognizing peace gesture."""
        recognizer = GestureRecognizer()
        
        hand_info = HandInfo(
            hand_label="Right",
            landmarks=[(x * 10, 100) for x in range(21)],
            fingers_up=[False, True, True, False, False],
            finger_count=2,
            bbox=(10, 10, 100, 100)
        )
        
        result = recognizer.recognize(hand_info)
        
        assert result["gesture"] == "peace"
        assert result["finger_count"] == 2
    
    def test_recognize_five(self):
        """Test recognizing five/open hand gesture."""
        recognizer = GestureRecognizer()
        
        hand_info = HandInfo(
            hand_label="Right",
            landmarks=[(x * 10, 100) for x in range(21)],
            fingers_up=[True, True, True, True, True],
            finger_count=5,
            bbox=(10, 10, 100, 100)
        )
        
        result = recognizer.recognize(hand_info)
        
        assert result["gesture"] == "five"
        assert result["finger_count"] == 5
    
    def test_gesture_history(self):
        """Test gesture history smoothing."""
        recognizer = GestureRecognizer()
        
        hand_info = HandInfo(
            hand_label="Right",
            landmarks=[(x * 10, 100) for x in range(21)],
            fingers_up=[False, False, False, False, False],
            finger_count=0,
            bbox=(10, 10, 100, 100)
        )
        
        # Recognize same gesture multiple times
        for _ in range(3):
            recognizer.recognize(hand_info)
        
        assert len(recognizer.gesture_history) == 3
    
    def test_reset_history(self):
        """Test resetting gesture history."""
        recognizer = GestureRecognizer()
        
        hand_info = HandInfo(
            hand_label="Right",
            landmarks=[(x * 10, 100) for x in range(21)],
            fingers_up=[False, False, False, False, False],
            finger_count=0,
            bbox=(10, 10, 100, 100)
        )
        
        recognizer.recognize(hand_info)
        assert len(recognizer.gesture_history) > 0
        
        recognizer.reset_history()
        assert len(recognizer.gesture_history) == 0
    
    def test_get_gesture_list(self):
        """Test getting gesture list."""
        recognizer = GestureRecognizer()
        
        gestures = recognizer.get_gesture_list()
        
        assert isinstance(gestures, dict)
        assert len(gestures) > 0
        assert "fist" in gestures
        assert "peace" in gestures
        assert "five" in gestures


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
