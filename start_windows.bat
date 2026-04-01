@echo off
REM Navigate to the directory where this script is located
cd /d "%~dp0"

REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Run the main program
echo Starting Blind Assist Hat...
python -m core.main

REM Pause so the window doesn't close immediately if there's an error
pause
