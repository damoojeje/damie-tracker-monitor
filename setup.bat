@echo off
echo Setting up Opentrackers.org Monitor...
pip install -r requirements.txt

echo.
echo Setup complete! 
echo.
echo To run manually: python tracker_monitor.py
echo To run with scheduler: python tracker_scheduler.py
echo.
echo Remember to configure your email settings in tracker_monitor.py before using!
pause