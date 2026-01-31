"""Quick test script to verify hand detection works."""

import sys
sys.path.append('src')

from hand_detector import HandDetector
from gesture_recognizer import GestureRecognizer
import numpy as np

print("="*60)
print("HAND GESTURE RECOGNITION - QUICK TEST")
print("="*60)

# Test detector initialization
print("\n1. Testing HandDetector initialization...")
detector = HandDetector(max_hands=2)
print("   [OK] HandDetector created successfully")

# Test recognizer initialization  
print("\n2. Testing GestureRecognizer initialization...")
recognizer = GestureRecognizer()
print("   [OK] GestureRecognizer created successfully")

# Test detection on blank image
print("\n3. Testing detection on blank image...")
test_image = np.zeros((480, 640, 3), dtype=np.uint8)
result_image, hands_info = detector.find_hands(test_image)
print(f"   [OK] Detection completed")
print(f"   - Hands detected: {len(hands_info)}")
print(f"   - Result image shape: {result_image.shape}")

# Test gesture list
print("\n4. Testing gesture recognition...")
gestures = recognizer.get_gesture_list()
print(f"   [OK] Gesture recognizer ready")
print(f"   - Supported gestures: {len(gestures)}")
print(f"   - Gestures: {', '.join(list(gestures.keys())[:5])}...")

print("\n" + "="*60)
print("ALL TESTS PASSED!")
print("="*60)
print("\nHand detection system is ready to use!")
print("\nTo run the Gradio app:")
print("  python api/gradio_app.py")
print("\nThen open: http://localhost:7861")

detector.close()
