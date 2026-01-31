"""Unit tests for hand detector module."""

import pytest
import numpy as np
import cv2
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from hand_detector import HandDetector, HandInfo


class TestHandDetector:
    """Test HandDetector class."""
    
    def test_initialization(self):
        """Test detector initialization."""
        detector = HandDetector()
        assert detector is not None
        assert detector.max_hands == 2
        assert detector.detection_confidence == 0.7
        assert detector.tracking_confidence == 0.5
    
    def test_custom_initialization(self):
        """Test detector with custom parameters."""
        detector = HandDetector(
            max_hands=1,
            detection_confidence=0.8,
            tracking_confidence=0.6
        )
        assert detector.max_hands == 1
        assert detector.detection_confidence == 0.8
        assert detector.tracking_confidence == 0.6
    
    def test_find_hands_empty_image(self):
        """Test detection on empty image."""
        detector = HandDetector()
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        result_image, hands_info = detector.find_hands(image)
        
        assert result_image is not None
        assert isinstance(hands_info, list)
        assert len(hands_info) == 0
    
    def test_find_hands_returns_correct_types(self):
        """Test that find_hands returns correct types."""
        detector = HandDetector()
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        result_image, hands_info = detector.find_hands(image)
        
        assert isinstance(result_image, np.ndarray)
        assert isinstance(hands_info, list)
    
    def test_draw_info_with_no_hands(self):
        """Test drawing info with no hands detected."""
        detector = HandDetector()
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        hands_info = []
        
        result = detector.draw_info(image, hands_info)
        
        assert result is not None
        assert result.shape == image.shape
    
    def test_bbox_calculation(self):
        """Test bounding box calculation."""
        detector = HandDetector()
        
        # Create mock landmarks
        landmarks = [(100, 100), (150, 150), (200, 200)]
        
        bbox = detector._calculate_bbox(landmarks)
        
        assert len(bbox) == 4
        assert bbox[0] == 100  # x_min
        assert bbox[1] == 100  # y_min
        assert bbox[2] == 100  # width
        assert bbox[3] == 100  # height
    
    def test_count_fingers_all_down(self):
        """Test finger counting with all fingers down."""
        detector = HandDetector()
        
        # Create mock landmarks with all fingers down
        landmarks = [(x * 10, 100) for x in range(21)]
        
        fingers = detector._count_fingers(landmarks, "Right")
        
        assert len(fingers) == 5
        assert isinstance(fingers[0], bool)


class TestHandInfo:
    """Test HandInfo dataclass."""
    
    def test_hand_info_creation(self):
        """Test creating HandInfo object."""
        hand_info = HandInfo(
            hand_label="Right",
            landmarks=[(0, 0)] * 21,
            fingers_up=[True, False, True, False, True],
            finger_count=3,
            bbox=(10, 10, 100, 100)
        )
        
        assert hand_info.hand_label == "Right"
        assert len(hand_info.landmarks) == 21
        assert hand_info.finger_count == 3
        assert len(hand_info.bbox) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
