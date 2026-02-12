# damie-tracker-monitor

Automated tracker signup monitor for opentrackers.org - Get notified via email/WhatsApp when new private torrent tracker signups open

## Features

- Automated monitoring of opentrackers.org for new tracker signups
- Email and WhatsApp notifications when new opportunities are found
- Configurable check intervals (every 30 mins, hourly, daily, etc.)
- Ubuntu server optimized with systemd service support
- Easy one-command installation

## Installation

### Quick Install
```bash
curl -sSL https://raw.githubusercontent.com/damoojeje/damie-tracker-monitor/main/install.sh | bash
```

### Manual Install
```bash
git clone https://github.com/damoojeje/damie-tracker-monitor.git
cd damie-tracker-monitor
python3 setup-wizard.py
```

## Prerequisites

- Python 3.6+
- pip

## Configuration

The setup wizard will guide you through:
1. Virtual environment creation (recommended)
2. Email notification setup
3. WhatsApp notification setup (optional)
4. Check frequency configuration
5. Background service setup (systemd on Ubuntu)

## Usage

After setup, you can:
- Start the monitor: `python3 tracker_monitor.py`
- Start with scheduler: `python3 tracker_scheduler.py`
- If using systemd: `sudo systemctl start damie-monitor`

## Background Service (Ubuntu)

The setup wizard can configure a systemd service that:
- Starts automatically on boot
- Runs continuously in the background
- Logs to `/var/log/damie-monitor.log`

## Security Notes

- For Gmail users: Use app passwords, not your regular password
- Store credentials securely
- Review the code before running

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT