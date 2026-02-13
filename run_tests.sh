#!/bin/bash
# Test runner for DAMIE Tracker Monitor

echo "Running tests for DAMIE Tracker Monitor..."

# Create a virtual environment for testing
python3 -m venv test_env
source test_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run unit tests
python -m unittest test_tracker_monitor.py -v

# Run basic functionality test
echo "Running basic functionality test..."
python -c "
from tracker_monitor import TrackerMonitor
print('TrackerMonitor class imported successfully')
monitor = TrackerMonitor()
print('TrackerMonitor instance created successfully')
print('All basic tests passed!')
"

# Deactivate virtual environment
deactivate

echo "Tests completed."