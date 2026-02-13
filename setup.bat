@echo off
echo Setting up Opentrackers.org Monitor - Optimized Edition...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH. Please install Python 3.6+.
    pause
    exit /b 1
)

REM Install dependencies
echo Installing required packages...
pip install -r requirements.txt

echo.
echo Setup complete!
echo.
echo To run manually: python tracker_monitor.py
echo To run with scheduler: python tracker_scheduler.py
echo.
echo Remember to configure your email settings in tracker_monitor.py before using!
echo.
pause