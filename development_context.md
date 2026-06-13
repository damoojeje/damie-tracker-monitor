# DAMIE Tracker Monitor - Development Context

## Project Overview
DAMIE Tracker Monitor is an automated system that monitors opentrackers.org for new private torrent tracker signup opportunities and sends notifications via email or WhatsApp when new opportunities are detected.

## Repository
- URL: https://github.com/damoojeje/damie-tracker-monitor.git
- Primary Language: Python 3
- Target Platform: Ubuntu Server (with cross-platform support)

## Architecture

### Core Components

#### 1. tracker_monitor.py
- Main monitoring script that scrapes opentrackers.org
- Uses requests and BeautifulSoup4 for web scraping
- Implements change detection algorithm
- Handles notification sending (email/WhatsApp)
- Stores data in JSON format

#### 2. tracker_scheduler.py
- Scheduling script using the 'schedule' library
- Runs tracker_monitor.py at configurable intervals
- Includes logging functionality
- Runs as a continuous service

#### 3. setup-wizard.py
- Interactive setup wizard with colorful terminal UI
- Creates "DAMIE" header display
- Guides users through configuration:
  * Virtual environment setup
  * Email notification configuration
  * WhatsApp notification configuration (optional)
  * Scheduling preferences
  * Background service setup
- Handles input validation and error handling
- Creates config.json with user preferences

#### 4. install.sh
- Bash installation script for Linux/Ubuntu
- Handles virtual environment creation
- Manages dependencies installation
- Handles existing directory cases
- Uses --break-system-packages for Ubuntu compatibility

## Key Features

### Web Scraping Logic
- Monitors opentrackers.org for tracker listings
- Parses WordPress-based site structure (Montezuma theme)
- Identifies tracker entries with pattern: "NAME (ABBR) IS OPEN FOR LIMITED SIGNUP!"
- Extracts:
  * Tracker name and abbreviation
  * Closing date
  * Description
  * Tags/categories
- Handles pagination to scan multiple pages

### Change Detection Algorithm
- Compares current tracker listings with previously stored data
- Uses unique identifiers: "{name}_{date}_{abbreviation}"
- Detects new opportunities by set difference
- Stores historical data in trackers.json

### Notification System
- Email notifications via SMTP
- WhatsApp notifications via WhatsApp Business API (template)
- Configurable notification preferences
- Rich notification content with tracker details

### Scheduling Options
- Configurable intervals: 30 min, 1 hour, 2 hours, 6 hours, daily, custom
- Background service options:
  * systemd service (Ubuntu)
  * screen/tmux sessions
  * manual start

## Technical Implementation Details

### Dependencies (requirements.txt)
- requests==2.31.0
- beautifulsoup4==4.12.2
- schedule==1.2.0
- colorama==0.4.6

### Configuration Structure
- config.json stores all user preferences
- Virtual environment isolation
- Separate credential storage

### Error Handling
- Input validation for numeric values
- Keyboard interrupt (Ctrl+C) handling
- EOF error handling
- Network error resilience
- Rate limiting compliance

### Cross-Platform Compatibility
- Windows and Linux support
- Platform-specific path handling
- OS detection for service configuration

## Development Environment Setup

### Local Development
1. Clone repository: `git clone https://github.com/damoojeje/damie-tracker-monitor.git`
2. Navigate to directory: `cd damie-tracker-monitor`
3. Create virtual environment: `python3 -m venv venv`
4. Activate environment: `source venv/bin/activate`
5. Install dependencies: `pip install --break-system-packages -r requirements.txt`

### Testing Process
1. Run setup wizard: `python setup-wizard.py`
2. Configure with test settings
3. Run monitor manually: `python tracker_monitor.py`
4. Verify scheduling: `python tracker_scheduler.py`

### Debugging Tools
- debug_page.py: Analyzes website structure
- Logging in tracker_scheduler.py
- Console output in all modules

## Current Known Issues & Improvements Needed

### Issues Fixed
- Input validation crashes (ValueError for invalid numeric input)
- EOFError when users exit with Ctrl+C
- Installation script directory conflicts
- Ubuntu external package management conflicts

### Potential Enhancements
1. **Enhanced Error Recovery**
   - Retry logic for network failures
   - Backup configuration storage
   - Graceful degradation when services are unavailable

2. **Advanced Scheduling**
   - Time-based scheduling (specific hours/days)
   - Adaptive polling based on activity
   - Multiple notification windows

3. **Monitoring Improvements**
   - Additional tracker sites
   - Different signup types (application, donation)
   - Priority scoring for opportunities

4. **Notification Enhancements**
   - Multiple notification channels simultaneously
   - Notification templates
   - Urgency-based notifications

5. **System Integration**
   - Docker containerization
   - Configuration via environment variables
   - REST API for remote management
   - Web dashboard for configuration

6. **Performance Optimization**
   - Caching mechanisms
   - Parallel processing for multiple sites
   - Memory usage optimization

## File Structure
```
damie-tracker-monitor/
├── tracker_monitor.py          # Core monitoring logic
├── tracker_scheduler.py        # Scheduling service
├── setup-wizard.py            # Interactive setup
├── install.sh                 # Installation script
├── requirements.txt           # Dependencies
├── README.md                  # Documentation
├── LICENSE                    # MIT License
├── .gitignore                 # Git exclusions
├── systemd-service-template.txt # Service template
├── debug_page.py              # Debugging utility
└── config.json                # User configuration (generated)
```

## Security Considerations
- Credentials stored locally in config.json
- Use app passwords for email services
- WhatsApp Business API tokens handled securely
- Input sanitization implemented
- Rate limiting to respect target servers

## Deployment Notes
- Designed for Ubuntu server with systemd
- Virtual environment isolation recommended
- Log rotation should be configured separately
- Firewall rules may need adjustment for notifications

## Future Development Ideas
1. Mobile app notifications
2. Browser extension integration
3. Machine learning for opportunity scoring
4. Community sharing features
5. Advanced filtering options
6. Historical statistics and analytics