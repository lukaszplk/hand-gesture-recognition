# Hand Gesture Recognition - Quick Start

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Running the Application

### Option 1: Gradio Web Interface (Easiest)

```bash
python api/gradio_app.py
```

Open: http://localhost:7861

**Features:**
- Upload images or use webcam
- Real-time hand detection
- Gesture recognition
- Interactive interface

### Option 2: FastAPI Service

```bash
python api/main.py
```

API docs: http://localhost:8001/docs

**Test API:**
```bash
curl -X POST "http://localhost:8001/detect" \
  -F "file=@hand_image.jpg"
```

### Option 3: Python Script

```bash
cd src
python hand_detector.py
```

Press 'q' to quit webcam.

## Docker

```bash
docker-compose -f docker/docker-compose.yml up
```

- Gradio: http://localhost:7861
- API: http://localhost:8001

## Testing

```bash
pytest tests/ -v
```

## Project Structure

```
hand_detector/
├── src/              # Core modules
├── api/              # Web services  
├── tests/            # Unit tests
├── docker/           # Docker files
├── notebooks/        # Jupyter notebooks
└── outputs/          # Screenshots/videos
```

## Supported Gestures

- Fist (0 fingers)
- Pointing (1 finger)
- Peace (2 fingers)
- Three (3 fingers)
- Four (4 fingers)
- Five (5 fingers/open hand)
- Thumbs Up/Down
- OK sign
- Rock on 🤘

## Configuration

Edit `src/config.py` for:
- Detection confidence
- Tracking confidence
- Max hands
- Video settings
- API ports

## Need Help?

See the full [README.md](README.md) for detailed documentation.
