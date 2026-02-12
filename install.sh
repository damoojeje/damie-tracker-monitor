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
    sudo apt update
    sudo apt install -y python3-pip
fi

echo "pip3 is installed."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Git is not installed. Installing..."
    sudo apt update
    sudo apt install -y git
fi

# Check if we're already in the repository directory
if [ -f "setup-wizard.py" ]; then
    echo "Already in the repository directory."
else
    # Check if the damie-tracker-monitor directory already exists
    if [ -d "damie-tracker-monitor" ]; then
        echo "damie-tracker-monitor directory already exists."
        read -p "Do you want to remove the existing directory and reinstall? (y/N): " -n 1 -r overwrite
        echo
        if [[ $overwrite =~ ^[Yy]$ ]]; then
            echo "Removing existing directory..."
            rm -rf damie-tracker-monitor
            echo "Cloning DAMIE Tracker Monitor repository..."
            git clone https://github.com/damoojeje/damie-tracker-monitor.git
            cd damie-tracker-monitor
        else
            echo "Changing to existing directory..."
            cd damie-tracker-monitor
        fi
    else
        echo "Cloning DAMIE Tracker Monitor repository..."
        git clone https://github.com/damoojeje/damie-tracker-monitor.git
        cd damie-tracker-monitor
    fi
fi

# Create a virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install colorama for the setup wizard in the virtual environment
echo "Installing colorama for setup wizard..."
pip install colorama

echo "Starting setup wizard..."
python setup-wizard.py

echo "==========================================="
echo "    Installation Complete!"
echo "==========================================="
echo ""
echo "To start the monitor manually:"
echo "  cd damie-tracker-monitor && source venv/bin/activate && python tracker_scheduler.py"
echo ""
echo "For systemd service (Ubuntu):"
echo "  sudo cp damie-monitor.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload && sudo systemctl enable damie-monitor"
echo "  sudo systemctl start damie-monitor"
echo ""
echo "For more information, check the README.md file."