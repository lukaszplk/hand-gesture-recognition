# Hand Gesture Recognition - Complete Structure

```
hand_gesture_recognition/
│
├── 📁 src/                          # Core application code
│   ├── __init__.py                  # Package initialization
│   ├── config.py                    # Configuration & settings
│   ├── hand_detector.py             # Hand detection with MediaPipe
│   ├── gesture_recognizer.py       # Gesture recognition system
│   └── utils.py                     # Utilities (recording, FPS, etc.)
│
├── 📁 api/                          # Web services
│   ├── __init__.py                  # API package initialization
│   ├── main.py                      # FastAPI REST service (port 8001)
│   └── gradio_app.py                # Gradio web interface (port 7861)
│
├── 📁 tests/                        # Unit tests
│   ├── __init__.py                  # Tests initialization
│   ├── test_hand_detector.py       # Hand detector tests
│   └── test_gesture_recognizer.py  # Gesture recognizer tests
│
├── 📁 notebooks/                    # Jupyter notebooks
│   └── hand_and_fin_detector.ipynb # Original notebook
│
├── 📁 docker/                       # Docker configuration
│   ├── Dockerfile                   # Docker image definition
│   └── docker-compose.yml           # Multi-container orchestration
│
├── 📁 outputs/                      # Generated files
│   └── .gitkeep                     # Keep directory in git
│
├── 📁 static/                       # Static assets
│
├── 📄 README.md                     # Main documentation
├── 📄 QUICKSTART.md                 # Quick start guide
├── 📄 requirements.txt              # Python dependencies
├── 📄 .gitignore                    # Git ignore patterns
└── 📄 LICENSE                       # Project license
```

## Key Components

### Core Modules (src/)

| File | Lines | Purpose |
|------|-------|---------|
| config.py | ~100 | Settings & configuration |
| hand_detector.py | ~300 | MediaPipe hand detection |
| gesture_recognizer.py | ~250 | Pattern-based gestures |
| utils.py | ~250 | Recording & utilities |

### Web Services (api/)

| Service | Type | Port | Purpose |
|---------|------|------|---------|
| main.py | FastAPI | 8001 | REST API + WebSocket |
| gradio_app.py | Gradio | 7861 | Interactive web UI |

### Tests (tests/)

- **test_hand_detector.py**: 10+ test cases for detection
- **test_gesture_recognizer.py**: 8+ test cases for gestures

## Features

✅ **Hand Detection**
- Detect up to 2 hands
- 21 landmarks per hand
- Bounding boxes
- Left/Right orientation

✅ **Gesture Recognition**
- 10+ gestures
- Pattern matching
- Confidence scoring
- Smoothing with history

✅ **Web Interface**
- Image upload
- Real-time webcam
- Gesture guide
- Statistics

✅ **REST API**
- Upload detection
- Base64 support
- WebSocket streaming
- Annotated images

✅ **Recording**
- Video recording
- Screenshots
- FPS counter
- Output management

✅ **Production Ready**
- Docker support
- Unit tests
- Comprehensive docs
- Clean architecture

## Technology Stack

**Computer Vision:**
- MediaPipe (hand tracking)
- OpenCV (image processing)
- NumPy (numerical ops)

**Web Frameworks:**
- FastAPI (REST API)
- Gradio (web UI)
- Uvicorn (ASGI server)
- WebSockets (streaming)

**DevOps:**
- Docker & Docker Compose
- Pytest (testing)
- Git (version control)

## Quick Commands

```bash
# Setup
pip install -r requirements.txt

# Run Gradio
python api/gradio_app.py

# Run API
python api/main.py

# Run detector
python src/hand_detector.py

# Docker
docker-compose -f docker/docker-compose.yml up

# Test
pytest tests/ -v
```

---

**Status**: ✅ Production Ready

**Version**: 1.0.0

**Last Updated**: 2026-01-31
