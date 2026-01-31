@echo off
echo Starting Hand Detection Gradio App...
cd /d "%~dp0"
call venv\Scripts\activate.bat
python api\gradio_app.py
pause
