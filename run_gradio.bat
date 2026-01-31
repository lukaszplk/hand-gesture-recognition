@echo off
echo Starting Hand Gesture Recognition App...
cd /d "%~dp0"
call venv\Scripts\activate.bat
python api\gradio_app.py
pause
