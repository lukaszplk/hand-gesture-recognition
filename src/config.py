"""Configuration file for Hand Detector and Gesture Recognition."""

from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
STATIC_DIR = PROJECT_ROOT / "static"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Ensure directories exist
STATIC_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

# MediaPipe Hand Detection Configuration
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.5
MAX_NUM_HANDS = 2

# Finger tip landmark IDs (MediaPipe hand landmarks)
FINGER_TIP_IDS = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
FINGER_PIP_IDS = [2, 6, 10, 14, 18]  # PIP joints for comparison

# Finger names
FINGER_NAMES = ["Thumb", "Index", "Middle", "Ring", "Pinky"]

# Gesture definitions
GESTURES = {
    "fist": "Closed fist - all fingers down",
    "one": "One finger up",
    "two": "Two fingers up (peace/victory)",
    "three": "Three fingers up",
    "four": "Four fingers up",
    "five": "All fingers up (open hand)",
    "thumbs_up": "Thumbs up gesture",
    "thumbs_down": "Thumbs down gesture",
    "ok": "OK sign (thumb and index forming circle)",
    "peace": "Peace sign (index and middle up)",
    "rock": "Rock on! (index and pinky up)",
    "pointing": "Pointing (index finger only)",
}

# Video/Camera Configuration
DEFAULT_CAMERA_ID = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 30

# Visualization settings
LANDMARK_DRAWING_SPEC = {
    "color": (0, 255, 0),
    "thickness": 2,
    "circle_radius": 3
}

CONNECTION_DRAWING_SPEC = {
    "color": (255, 0, 0),
    "thickness": 2
}

# Text display settings
TEXT_COLOR = (255, 255, 255)
TEXT_FONT = 0  # cv2.FONT_HERSHEY_SIMPLEX
TEXT_SCALE = 1.0
TEXT_THICKNESS = 2
BACKGROUND_COLOR = (0, 0, 0)

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8001
API_TITLE = "Hand Detection and Gesture Recognition API"
API_VERSION = "1.0.0"

# Gradio Configuration
GRADIO_PORT = 7861
GRADIO_SHARE = False

# Recording settings
VIDEO_CODEC = "mp4v"
VIDEO_EXTENSION = ".mp4"
IMAGE_EXTENSION = ".jpg"
