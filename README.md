# 🖐️ Hand Gesture Recognition

A production-ready real-time hand gesture recognition system using MediaPipe and deep learning. Features webcam support, REST API, interactive web interface, and Docker deployment.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![MediaPipe](https://img.shields.io/badge/MediaPipe-latest-green)
![License](https://img.shields.io/badge/license-MIT-green)

## 🎯 Features

- **Real-time Hand Detection**: Detect up to 2 hands simultaneously
- **Finger Counting**: Accurate finger counting with per-finger status
- **Gesture Recognition**: 10+ gestures including peace, thumbs up, OK sign, rock on
- **Hand Orientation**: Left/Right hand detection
- **Web Interface**: Interactive Gradio UI with webcam support
- **REST API**: FastAPI service with WebSocket streaming
- **Recording**: Save screenshots and record videos
- **Docker Support**: Containerized deployment
- **Production Ready**: Modular code, tests, comprehensive docs

## 📊 Supported Gestures

| Gesture | Description | Pattern |
|---------|-------------|---------|
| 🤜 Fist | Closed hand | 0 fingers |
| ☝️ Pointing | Index finger only | 1 finger |
| ✌️ Peace | Victory sign | Index + Middle |
| 🖖 Three | Three fingers up | 3 fingers |
| 🤚 Four | Four fingers up | 4 fingers |
| ✋ Five | Open hand | All fingers |
| 👍 Thumbs Up | Thumb pointing up | Thumb only (up) |
| 👎 Thumbs Down | Thumb pointing down | Thumb only (down) |
| 👌 OK | Thumb + Index circle | Circle shape |
| 🤘 Rock On | Metal horns | Index + Pinky |

## 📁 Project Structure

```
hand_detector/
├── src/                          # Source code
│   ├── config.py                 # Configuration
│   ├── hand_detector.py          # Hand detection module
│   ├── gesture_recognizer.py    # Gesture recognition
│   └── utils.py                  # Utilities (recording, FPS, etc.)
├── api/                          # Web services
│   ├── main.py                   # FastAPI service
│   └── gradio_app.py             # Gradio web interface
├── docker/                       # Docker configuration
│   ├── Dockerfile
│   └── docker-compose.yml
├── notebooks/                    # Jupyter notebooks
│   └── hand_and_fin_detector.ipynb
├── tests/                        # Unit tests
├── outputs/                      # Screenshots & recordings (generated)
├── static/                       # Static assets
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/lukaszplk/hand_gesture_recognition.git
cd hand_gesture_recognition
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Running the Application

#### Option 1: Gradio Web Interface (Recommended)

```bash
python api/gradio_app.py
```

Then open: http://localhost:7861

**Features:**
- Upload images for detection
- Real-time webcam feed
- Interactive gesture recognition
- Gesture guide and documentation

#### Option 2: FastAPI Service

```bash
python api/main.py
```

API docs: http://localhost:8001/docs

**Endpoints:**
- `POST /detect` - Detect hands in uploaded image
- `POST /detect/annotated` - Get annotated image
- `POST /detect/base64` - Detect from base64 image
- `WS /stream/webcam` - WebSocket streaming
- `GET /gestures` - List all gestures

#### Option 3: Python Script

```bash
cd src
python hand_detector.py
```

Press 'q' to quit.

### Docker Deployment

**Run with Docker Compose:**
```bash
docker-compose -f docker/docker-compose.yml up --build
```

Services:
- Gradio UI: http://localhost:7861
- FastAPI: http://localhost:8001

## 📚 Usage

### Python API

```python
from hand_detector import HandDetector
from gesture_recognizer import GestureRecognizer
import cv2

# Initialize
detector = HandDetector(max_hands=2)
recognizer = GestureRecognizer()

# Capture from webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    
    # Detect hands
    frame, hands_info = detector.find_hands(frame)
    
    # Recognize gestures
    for hand_info in hands_info:
        gesture_info = recognizer.recognize(hand_info)
        print(f"Gesture: {gesture_info['gesture']}")
        print(f"Fingers: {hand_info.finger_count}")
    
    # Draw information
    frame = detector.draw_info(frame, hands_info)
    
    cv2.imshow("Hand Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### REST API

**Detect hands in image:**
```bash
curl -X POST "http://localhost:8001/detect" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@hand_image.jpg"
```

**Response:**
```json
{
  "hands_detected": 1,
  "hands": [
    {
      "hand_label": "Right",
      "finger_count": 2,
      "fingers_up": {
        "thumb": false,
        "index": true,
        "middle": true,
        "ring": false,
        "pinky": false
      },
      "gesture": {
        "name": "peace",
        "description": "Peace sign (index and middle up)",
        "confidence": 1.0
      }
    }
  ],
  "processing_time_ms": 45.2
}
```

## 🎨 Features in Detail

### Hand Detection

- **Technology**: MediaPipe Hands
- **Landmarks**: 21 points per hand
- **Max Hands**: Up to 2 simultaneous
- **Detection Confidence**: 70% (configurable)
- **Tracking Confidence**: 50% (configurable)

### Gesture Recognition

- **Method**: Pattern-based matching
- **Smoothing**: 5-frame history for stability
- **Confidence**: Per-gesture confidence scoring
- **Custom Gestures**: Easy to add new patterns

### Recording & Screenshots

```python
from utils import VideoRecorder, save_screenshot

# Record video
recorder = VideoRecorder(fps=30)
recorder.start_recording()
# ... process frames ...
recorder.write_frame(frame)
recorder.stop_recording()

# Save screenshot
save_screenshot(frame, "my_gesture.jpg")
```

## ⚙️ Configuration

Edit `src/config.py` to customize:

```python
# Detection settings
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.5
MAX_NUM_HANDS = 2

# Video settings
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 30

# API settings
API_PORT = 8001
GRADIO_PORT = 7861
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_hand_detector.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

## 📈 Performance

| Metric | Value |
|--------|-------|
| **FPS** | 30+ (modern hardware) |
| **Latency** | < 50ms per frame |
| **Accuracy** | ~95% for common gestures |
| **Max Hands** | 2 simultaneous |
| **Processing Time** | 20-50ms per frame |

## 🛠️ Development

**Install development dependencies:**
```bash
pip install -r requirements.txt
pip install jupyter pytest black flake8
```

**Format code:**
```bash
black src/ api/ tests/
```

**Lint code:**
```bash
flake8 src/ api/ tests/
```

## 📖 API Documentation

### HandDetector Class

```python
HandDetector(
    max_hands: int = 2,
    detection_confidence: float = 0.7,
    tracking_confidence: float = 0.5
)
```

**Methods:**
- `find_hands(image, draw=True)` - Detect hands in image
- `draw_info(image, hands_info)` - Draw information on image
- `close()` - Release resources

### GestureRecognizer Class

```python
GestureRecognizer()
```

**Methods:**
- `recognize(hand_info)` - Recognize gesture from hand info
- `get_gesture_list()` - Get all supported gestures
- `reset_history()` - Reset gesture smoothing history

## 🎯 Use Cases

- **Sign Language Recognition**: Foundation for ASL detection
- **Gesture Control**: Control applications with hand gestures
- **Gaming**: Hand-based game controllers
- **Accessibility**: Hands-free computer interaction
- **Education**: Interactive learning tools
- **VR/AR**: Hand tracking for virtual environments
- **Security**: Gesture-based authentication

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- **MediaPipe**: Google's hand tracking solution
- **OpenCV**: Computer vision library
- **Gradio**: Easy-to-use web interfaces
- **FastAPI**: Modern web framework

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Made with ❤️ using MediaPipe, OpenCV, FastAPI, and Gradio**
