@echo off
cd /d "C:\Users\rohit\My Code Work\Chrome\ai_system"
echo Installing dependencies...
py -m pip install -r requirements.txt
echo.
echo Starting AI System...
py main_ai.py