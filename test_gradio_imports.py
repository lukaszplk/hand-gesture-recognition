"""Simple test to verify the Gradio app can load."""
import sys
sys.path.append('src')

print("Testing Gradio app imports...")

try:
    from hand_detector import HandDetector
    print("[OK] HandDetector imported")
except Exception as e:
    print(f"[ERROR] HandDetector import failed: {e}")
    sys.exit(1)

try:
    from gesture_recognizer import GestureRecognizer
    print("[OK] GestureRecognizer imported")
except Exception as e:
    print(f"[ERROR] GestureRecognizer import failed: {e}")
    sys.exit(1)

try:
    import gradio as gr
    print(f"[OK] Gradio {gr.__version__} imported")
except Exception as e:
    print(f"[ERROR] Gradio import failed: {e}")
    sys.exit(1)

try:
    # Initialize components
    detector = HandDetector(max_hands=2)
    recognizer = GestureRecognizer()
    print("[OK] Components initialized")
    detector.close()
except Exception as e:
    print(f"[ERROR] Component initialization failed: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("ALL IMPORTS SUCCESSFUL!")
print("="*60)
print("\nThe Gradio app should work. Run it with:")
print("  python api\\gradio_app.py")
print("\nOr use the batch file:")
print("  run_gradio.bat")
