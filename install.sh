#!/bin/bash
# DAMIE Tracker Monitor Installation Script

set -e  # Exit on any error

echo "==========================================="
echo "    DAMIE Tracker Monitor Installer"
echo "==========================================="

# Check if running on Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macos"
else
    echo "Unsupported platform: $OSTYPE"
    exit 1
fi

echo "Detected platform: $PLATFORM"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.6+ first."
    exit 1
fi

echo "Python 3 is installed."

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Installing..."
    python3 -m ensurepip --upgrade
fi

echo "pip3 is installed."

# Clone the repository if not already in it
if [ ! -f "setup-wizard.py" ]; then
    echo "Cloning DAMIE Tracker Monitor repository..."
    git clone https://github.com/damoojeje/damie-tracker-monitor.git
    cd damie-tracker-monitor
else
    echo "Already in the repository directory."
fi

# Install colorama for the setup wizard
echo "Installing colorama for setup wizard..."
pip3 install colorama

echo "Starting setup wizard..."
python3 setup-wizard.py

echo "==========================================="
echo "    Installation Complete!"
echo "==========================================="
echo ""
echo "To start the monitor manually:"
echo "  python3 tracker_scheduler.py"
echo ""
echo "For systemd service (Ubuntu):"
echo "  sudo cp damie-monitor.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload && sudo systemctl enable damie-monitor"
echo "  sudo systemctl start damie-monitor"
echo ""
echo "For more information, check the README.md file."