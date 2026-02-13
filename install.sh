#!/bin/bash
# DAMIE Tracker Monitor Installation Script - Optimized Edition

set -e  # Exit on any error

echo "==========================================="
echo "    DAMIE Tracker Monitor Installer - Optimized"
echo "==========================================="

# Function to print colored output
print_success() {
    echo -e "\\033[32m$1\\033[0m"
}

print_error() {
    echo -e "\\033[31m$1\\033[0m"
}

print_warning() {
    echo -e "\\033[33m$1\\033[0m"
}

print_info() {
    echo -e "\\033[34m$1\\033[0m"
}

# Check if running on Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macos"
else
    print_error "Unsupported platform: $OSTYPE"
    exit 1
fi

print_info "Detected platform: $PLATFORM"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.6+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_info "Python version: $PYTHON_VERSION"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    print_warning "pip3 is not installed. Installing..."
    if [[ "$PLATFORM" == "linux" ]]; then
        sudo apt update
        sudo apt install -y python3-pip
    else
        print_error "Please install pip3 manually for your platform."
        exit 1
    fi
fi

print_info "pip3 is installed."

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_warning "Git is not installed. Installing..."
    if [[ "$PLATFORM" == "linux" ]]; then
        sudo apt update
        sudo apt install -y git
    else
        print_error "Please install git manually for your platform."
        exit 1
    fi
fi

# Determine the parent directory where the script is located
SCRIPT_DIR="$(pwd)"

# Check if we're already in the repository directory by checking for setup-wizard.py in the current directory
if [ -f "$SCRIPT_DIR/setup-wizard.py" ] && [ -f "$SCRIPT_DIR/README.md" ]; then
    print_info "Already in the repository directory ($SCRIPT_DIR)."
    REPO_DIR="$SCRIPT_DIR"
else
    REPO_DIR="$SCRIPT_DIR/damie-tracker-monitor"

    # Check if the damie-tracker-monitor directory already exists
    if [ -d "$REPO_DIR" ]; then
        print_warning "damie-tracker-monitor directory already exists at: $REPO_DIR"
        read -p "Do you want to remove the existing directory and reinstall? (y/N): " -n 1 -r overwrite
        echo
        if [[ $overwrite =~ ^[Yy]$ ]]; then
            print_info "Removing existing directory..."
            rm -rf "$REPO_DIR"
            print_info "Cloning DAMIE Tracker Monitor repository..."
            git clone https://github.com/damoojeje/damie-tracker-monitor.git "$REPO_DIR"
        else
            print_info "Using existing directory..."
        fi
    else
        print_info "Cloning DAMIE Tracker Monitor repository..."
        git clone https://github.com/damoojeje/damie-tracker-monitor.git "$REPO_DIR"
    fi

    # Change to the repository directory
    cd "$REPO_DIR"
fi

# Create a virtual environment
print_info "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip to latest version
print_info "Upgrading pip..."
pip install --upgrade pip

# Install colorama for the setup wizard in the virtual environment
print_info "Installing colorama for setup wizard..."
pip install colorama

print_info "Starting setup wizard..."
python setup-wizard.py

print_success "==========================================="
print_success "    Installation Complete!"
print_success "==========================================="
echo ""
print_success "To start the monitor manually:"
print_success "  cd damie-tracker-monitor && source venv/bin/activate && python tracker_scheduler.py"
echo ""
print_success "For systemd service (Ubuntu):"
print_success "  sudo cp damie-monitor.service /etc/systemd/system/"
print_success "  sudo systemctl daemon-reload && sudo systemctl enable damie-monitor"
print_success "  sudo systemctl start damie-monitor"
echo ""
print_success "For more information, check the README.md file."