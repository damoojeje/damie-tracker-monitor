#!/usr/bin/env python3
"""
DAMIE Tracker Monitor Setup Wizard - Optimized Edition
Automated tracker signup monitor for opentrackers.org
"""

import os
import sys
import subprocess
import json
import platform
from pathlib import Path
import re
import socket

try:
    from colorama import init, Fore, Back, Style
    init()  # Initialize colorama
except ImportError:
    # If colorama is not available, define dummy colors
    class DummyColor:
        RED = ''
        GREEN = ''
        YELLOW = ''
        BLUE = ''
        MAGENTA = ''
        CYAN = ''
        WHITE = ''
        RESET = ''
    Fore = DummyColor()
    Back = DummyColor()
    Style = DummyColor()

def print_header():
    """Print the DAMIE header"""
    print(Fore.CYAN + Style.BRIGHT)
    print("╔" + "═"*60 + "╗")
    print("║" + " "*20 + "DAMIE TRACKER MONITOR" + " "*19 + "║")
    print("║" + " "*18 + "Optimized Setup Wizard" + " "*20 + "║")
    print("║" + " "*15 + "Automated Tracker Signup Alerts" + " "*15 + "║")
    print("╚" + "═"*60 + "╝")
    print(Style.RESET_ALL)

def get_user_input(prompt, default=None, password=False, validate_func=None):
    """Get user input with optional default value and validation"""
    if default:
        prompt = f"{prompt} (default: {default}): "
    else:
        prompt = f"{prompt}: "

    while True:
        try:
            if password:
                import getpass
                user_input = getpass.getpass(prompt)
            else:
                user_input = input(prompt)
        except (KeyboardInterrupt, EOFError):
            print("\n\nOperation cancelled by user.")
            sys.exit(1)

        # Use default if input is empty
        if not user_input and default is not None:
            user_input = default

        if validate_func:
            if validate_func(user_input):
                return user_input
            else:
                print(Fore.RED + "Invalid input. Please try again." + Style.RESET_ALL)
        else:
            return user_input

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_phone(phone):
    """Basic phone number validation"""
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    # Check if it has at least 10 digits (basic validation)
    return len(digits_only) >= 10

def is_valid_url(url):
    """Basic URL validation"""
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return re.match(pattern, url) is not None

def test_smtp_connection(smtp_server, smtp_port, email, password):
    """Test SMTP connection"""
    try:
        import smtplib
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email, password)
        server.quit()
        return True
    except Exception as e:
        print(Fore.RED + f"SMTP connection test failed: {str(e)}" + Style.RESET_ALL)
        return False

def create_virtual_env():
    """Create and activate virtual environment"""
    print(Fore.YELLOW + "\nSetting up virtual environment..." + Style.RESET_ALL)

    venv_path = Path("./venv")

    # Check if venv already exists and ask if user wants to overwrite
    if venv_path.exists():
        overwrite = get_user_input("Virtual environment already exists. Overwrite it?", "no").lower() in ['yes', 'y', 'true', '1']
        if not overwrite:
            return str(venv_path), None  # Return existing path
        else:
            import shutil
            print(Fore.YELLOW + "Removing existing virtual environment..." + Style.RESET_ALL)
            shutil.rmtree(venv_path)

    try:
        subprocess.check_call([sys.executable, "-m", "venv", str(venv_path)])
        print(Fore.GREEN + "✓ Virtual environment created successfully" + Style.RESET_ALL)

        # Determine activation script based on OS
        if platform.system() == "Windows":
            activate_script = venv_path / "Scripts" / "activate"
        else:
            activate_script = venv_path / "bin" / "activate"

        return str(venv_path), str(activate_script)
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"✗ Error creating virtual environment: {e}" + Style.RESET_ALL)
        return None, None

def install_requirements(venv_path):
    """Install required packages in virtual environment"""
    print(Fore.YELLOW + "\nInstalling required packages..." + Style.RESET_ALL)

    if platform.system() == "Windows":
        pip_path = Path(venv_path) / "Scripts" / "pip"
    else:
        pip_path = Path(venv_path) / "bin" / "pip"

    try:
        # Use --break-system-packages flag for Ubuntu systems
        if platform.system() == "Linux":
            subprocess.check_call([str(pip_path), "install", "--break-system-packages", "-r", "requirements.txt"])
        else:
            subprocess.check_call([str(pip_path), "install", "-r", "requirements.txt"])
        print(Fore.GREEN + "✓ Packages installed successfully" + Style.RESET_ALL)
        return True
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"✗ Error installing packages: {e}" + Style.RESET_ALL)
        return False

def configure_email():
    """Configure email notifications"""
    print(Fore.CYAN + "\n" + "="*50 + Style.RESET_ALL)
    print(Fore.CYAN + "EMAIL NOTIFICATION SETUP" + Style.RESET_ALL)
    print(Fore.CYAN + "="*50 + Style.RESET_ALL)

    enable_email = get_user_input("Enable email notifications?", "yes").lower() in ['yes', 'y', 'true', '1']

    if not enable_email:
        return {
            'enabled': False,
            'smtp_server': '',
            'smtp_port': 587,
            'sender_email': '',
            'sender_password': '',
            'recipient_email': ''
        }

    print("\nCommon SMTP servers:")
    print("  1. Gmail: smtp.gmail.com")
    print("  2. Outlook: smtp-mail.outlook.com")
    print("  3. Yahoo: smtp.mail.yahoo.com")
    print("  4. Custom")

    smtp_choice = get_user_input("Choose SMTP server (1-4)", "1")

    smtp_servers = {
        "1": "smtp.gmail.com",
        "2": "smtp-mail.outlook.com",
        "3": "smtp.mail.yahoo.com"
    }

    if smtp_choice in smtp_servers:
        smtp_server = smtp_servers[smtp_choice]
    else:
        smtp_server = get_user_input("Enter custom SMTP server", "smtp.gmail.com")

    # Validate SMTP server
    while True:
        if smtp_server and '.' in smtp_server:
            break
        else:
            smtp_server = get_user_input("Invalid SMTP server. Enter valid SMTP server", "smtp.gmail.com")

    # Validate port
    while True:
        try:
            smtp_port = int(get_user_input("SMTP port", "587"))
            if 1 <= smtp_port <= 65535:
                break
            else:
                print(Fore.RED + "Port must be between 1 and 65535" + Style.RESET_ALL)
        except ValueError:
            print(Fore.RED + "Please enter a valid number" + Style.RESET_ALL)

    # Get and validate sender email
    while True:
        sender_email = get_user_input("Sender email address")
        if is_valid_email(sender_email):
            break
        else:
            print(Fore.RED + "Invalid email format. Please enter a valid email address." + Style.RESET_ALL)

    print("Note: For Gmail, use an App Password, not your regular password")
    sender_password = get_user_input("Sender password/App Password", password=True)

    # Get and validate recipient email
    while True:
        recipient_email = get_user_input("Recipient email address", sender_email)
        if is_valid_email(recipient_email):
            break
        else:
            print(Fore.RED + "Invalid email format. Please enter a valid email address." + Style.RESET_ALL)

    # Optionally test SMTP connection
    test_conn = get_user_input("Test SMTP connection? (requires valid credentials)", "no").lower() in ['yes', 'y', 'true', '1']
    if test_conn:
        if test_smtp_connection(smtp_server, smtp_port, sender_email, sender_password):
            print(Fore.GREEN + "✓ SMTP connection test successful!" + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + "⚠ SMTP connection test failed, but continuing setup." + Style.RESET_ALL)

    return {
        'enabled': True,
        'smtp_server': smtp_server,
        'smtp_port': smtp_port,
        'sender_email': sender_email,
        'sender_password': sender_password,
        'recipient_email': recipient_email
    }

def configure_whatsapp():
    """Configure WhatsApp notifications"""
    print(Fore.CYAN + "\n" + "="*50 + Style.RESET_ALL)
    print(Fore.CYAN + "WHATSAPP NOTIFICATION SETUP" + Style.RESET_ALL)
    print(Fore.CYAN + "="*50 + Style.RESET_ALL)

    enable_whatsapp = get_user_input("Enable WhatsApp notifications?", "no").lower() in ['yes', 'y', 'true', '1']

    if not enable_whatsapp:
        return {
            'enabled': False,
            'api_url': '',
            'access_token': '',
            'phone_number': ''
        }

    print("\nNote: You need a WhatsApp Business API account to use this feature")
    
    while True:
        api_url = get_user_input("WhatsApp Business API URL", "https://graph.facebook.com/v13.0/YOUR_PHONE_NUMBER_ID")
        if is_valid_url(api_url):
            break
        else:
            print(Fore.RED + "Invalid URL format. Please enter a valid URL." + Style.RESET_ALL)

    access_token = get_user_input("Access token", password=True)
    
    while True:
        phone_number = get_user_input("Recipient phone number (international format)")
        if is_valid_phone(phone_number):
            break
        else:
            print(Fore.RED + "Invalid phone number format. Please enter a valid phone number." + Style.RESET_ALL)

    return {
        'enabled': True,
        'api_url': api_url,
        'access_token': access_token,
        'phone_number': phone_number
    }

def configure_schedule():
    """Configure check schedule"""
    print(Fore.CYAN + "\n" + "="*50 + Style.RESET_ALL)
    print(Fore.CYAN + "SCHEDULE CONFIGURATION" + Style.RESET_ALL)
    print(Fore.CYAN + "="*50 + Style.RESET_ALL)

    print("\nHow often should the system check for new opportunities?")
    print("  1. Every 15 minutes")
    print("  2. Every 30 minutes")
    print("  3. Every hour")
    print("  4. Every 2 hours")
    print("  5. Every 6 hours")
    print("  6. Daily")
    print("  7. Custom interval")

    schedule_choice = get_user_input("Choose interval (1-7)", "3")

    intervals = {
        "1": 15,   # minutes
        "2": 30,   # minutes
        "3": 60,   # minutes
        "4": 120,  # minutes
        "5": 360,  # minutes
        "6": 1440  # minutes (daily)
    }

    if schedule_choice in intervals:
        minutes = intervals[schedule_choice]
    else:
        # Validate that the custom input is a number
        def validate_minutes(value):
            try:
                val = int(value)
                return 1 <= val <= 1440  # Between 1 minute and 1 day
            except (ValueError, TypeError):
                return False

        while True:
            minutes_str = get_user_input("Enter custom interval in minutes (1-1440)", "60")
            if validate_minutes(minutes_str):
                minutes = int(minutes_str)
                break
            else:
                print(Fore.RED + "Invalid input. Please enter a number between 1 and 1440." + Style.RESET_ALL)

    return {
        'interval_minutes': minutes
    }

def configure_service():
    """Configure background service"""
    print(Fore.CYAN + "\n" + "="*50 + Style.RESET_ALL)
    print(Fore.CYAN + "BACKGROUND SERVICE SETUP" + Style.RESET_ALL)
    print(Fore.CYAN + "="*50 + Style.RESET_ALL)

    print(f"\nDetected OS: {platform.system()}")

    if platform.system() == "Linux":
        print("Options for Linux:")
        print("  1. Systemd service (recommended for Ubuntu server)")
        print("  2. Run with screen/tmux")
        print("  3. Manual start only")

        service_choice = get_user_input("Choose service type (1-3)", "1")

        if service_choice == "1":
            return {
                'type': 'systemd',
                'enabled': True
            }
        elif service_choice == "2":
            return {
                'type': 'screen',
                'enabled': True
            }
        else:
            return {
                'type': 'manual',
                'enabled': False
            }
    else:
        print("Options:")
        print("  1. Run with task scheduler/screen")
        print("  2. Manual start only")

        service_choice = get_user_input("Choose service type (1-2)", "2")

        if service_choice == "1":
            return {
                'type': 'scheduler',
                'enabled': True
            }
        else:
            return {
                'type': 'manual',
                'enabled': False
            }

def save_config(config):
    """Save configuration to file"""
    config_path = Path("config.json")

    # Check if config file already exists and ask if user wants to overwrite
    if config_path.exists():
        overwrite = get_user_input("Configuration file already exists. Overwrite it?", "yes").lower() in ['yes', 'y', 'true', '1']
        if not overwrite:
            print(Fore.YELLOW + "Skipping configuration save." + Style.RESET_ALL)
            return

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(Fore.GREEN + f"✓ Configuration saved to {config_path}" + Style.RESET_ALL)

def create_systemd_service():
    """Create systemd service file for Ubuntu"""
    # Read the template from the file if it exists
    template_path = Path("systemd-service-template.txt")
    if template_path.exists():
        with open(template_path, 'r') as f:
            service_content = f.read()
    else:
        # Use default template
        service_content = """[Unit]
Description=DAMIE Tracker Monitor
After=network.target

[Service]
Type=simple
User=%i
WorkingDirectory={}
ExecStart={}/bin/python3 {}/tracker_scheduler.py
Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
""".format(
    str(Path.cwd()),
    str(Path("./venv/bin")),
    str(Path.cwd())
)

    # Create systemd directory if it doesn't exist
    systemd_dir = Path("/etc/systemd/system/")
    service_file = systemd_dir / "damie-monitor.service"

    try:
        # Write service file (this would normally require sudo)
        with open("damie-monitor.service", "w") as f:
            f.write(service_content)
        print(Fore.GREEN + "✓ Systemd service file created locally as damie-monitor.service" + Style.RESET_ALL)
        print(Fore.YELLOW + "\nTo install system-wide, run as root:" + Style.RESET_ALL)
        print(Fore.YELLOW + "  sudo cp damie-monitor.service /etc/systemd/system/" + Style.RESET_ALL)
        print(Fore.YELLOW + "  sudo systemctl daemon-reload && sudo systemctl enable damie-monitor" + Style.RESET_ALL)
        print(Fore.YELLOW + "  sudo systemctl start damie-monitor" + Style.RESET_ALL)
        return True
    except Exception as e:
        print(Fore.RED + f"Could not create systemd service: {e}" + Style.RESET_ALL)
        return False

def main():
    print_header()

    print(Fore.YELLOW + "Welcome to the DAMIE Tracker Monitor Setup Wizard!" + Style.RESET_ALL)
    print("This will guide you through setting up automated tracker signup monitoring.\n")

    # Step 1: Virtual environment
    create_venv = get_user_input("Create virtual environment? (Recommended)", "yes").lower() in ['yes', 'y', 'true', '1']

    venv_path = None
    if create_venv:
        venv_path, activate_script = create_virtual_env()
        if not venv_path:
            print(Fore.RED + "Failed to create virtual environment. Exiting." + Style.RESET_ALL)
            sys.exit(1)

        # Activate virtual environment for the rest of the setup
        if platform.system() != "Windows":
            # On Unix-like systems, we can't actually activate the venv in the current process
            # But we can install packages directly to it
            if not install_requirements(venv_path):
                print(Fore.RED + "Failed to install requirements. Exiting." + Style.RESET_ALL)
                sys.exit(1)
        else:
            # On Windows, we'll just install packages directly to the venv
            if not install_requirements(venv_path):
                print(Fore.RED + "Failed to install requirements. Exiting." + Style.RESET_ALL)
                sys.exit(1)
    else:
        # Install requirements to current environment
        if not install_requirements(sys.prefix):
            print(Fore.RED + "Failed to install requirements. Exiting." + Style.RESET_ALL)
            sys.exit(1)

    # Step 2: Email configuration
    email_config = configure_email()

    # Step 3: WhatsApp configuration
    whatsapp_config = configure_whatsapp()

    # Step 4: Schedule configuration
    schedule_config = configure_schedule()

    # Step 5: Service configuration
    service_config = configure_service()

    # Combine all configurations
    full_config = {
        'email': email_config,
        'whatsapp': whatsapp_config,
        'schedule': schedule_config,
        'service': service_config,
        'venv_path': venv_path
    }

    # Show summary
    print(Fore.CYAN + "\n" + "="*50 + Style.RESET_ALL)
    print(Fore.CYAN + "CONFIGURATION SUMMARY" + Style.RESET_ALL)
    print(Fore.CYAN + "="*50 + Style.RESET_ALL)

    print(f"Email notifications: {'ENABLED' if email_config['enabled'] else 'DISABLED'}")
    if email_config['enabled']:
        print(f"  - SMTP Server: {email_config['smtp_server']}")
        print(f"  - Port: {email_config['smtp_port']}")
        print(f"  - Sender: {email_config['sender_email']}")
        print(f"  - Recipient: {email_config['recipient_email']}")

    print(f"WhatsApp notifications: {'ENABLED' if whatsapp_config['enabled'] else 'DISABLED'}")
    if whatsapp_config['enabled']:
        print(f"  - API URL: {whatsapp_config['api_url']}")
        print(f"  - Phone: {whatsapp_config['phone_number']}")

    print(f"Check interval: {schedule_config['interval_minutes']} minutes")
    print(f"Background service: {service_config['type']}")

    # Confirm and save
    confirm = get_user_input("\nSave this configuration?", "yes").lower() in ['yes', 'y', 'true', '1']

    if confirm:
        save_config(full_config)

        # Create systemd service if requested (on Linux)
        if platform.system() == "Linux" and service_config['type'] == 'systemd':
            create_systemd_service()

        print(Fore.GREEN + "\n✓ Setup completed successfully!" + Style.RESET_ALL)
        print(Fore.GREEN + "To start the monitor:" + Style.RESET_ALL)
        if venv_path:
            print(Fore.GREEN + f"  source {venv_path}/bin/activate && python tracker_scheduler.py" + Style.RESET_ALL)
        else:
            print(Fore.GREEN + "  python tracker_scheduler.py" + Style.RESET_ALL)

        print(Fore.GREEN + "\nFor systemd service (Ubuntu):" + Style.RESET_ALL)
        print(Fore.GREEN + "  sudo cp damie-monitor.service /etc/systemd/system/" + Style.RESET_ALL)
        print(Fore.GREEN + "  sudo systemctl daemon-reload && sudo systemctl enable damie-monitor" + Style.RESET_ALL)
        print(Fore.GREEN + "  sudo systemctl start damie-monitor" + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + "\nConfiguration not saved. Exiting." + Style.RESET_ALL)

if __name__ == "__main__":
    main()