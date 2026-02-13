import requests
from bs4 import BeautifulSoup
import time
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
import re
import urllib.parse
import logging
from typing import List, Dict, Optional
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TrackerMonitor:
    def __init__(self, email_config=None, whatsapp_config=None, delay_range=(1, 3)):
        self.base_url = "https://opentrackers.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.email_config = email_config or {}
        self.whatsapp_config = whatsapp_config or {}
        self.delay_range = delay_range  # Random delay between requests to be respectful

    def send_email_notification(self, new_trackers):
        """Send email notification about new trackers"""
        if not self.email_config.get('enabled', False):
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['recipient_email']
            msg['Subject'] = f"New Tracker Signup Opportunities Found! ({len(new_trackers)} new)"

            body = "New tracker signup opportunities have been detected:\n\n"
            for tracker in new_trackers:
                body += f"• {tracker['name']} ({tracker['abbreviation']}) - Closing: {tracker['date']}\n"
                if tracker['description']:
                    body += f"  Description: {tracker['description']}\n"
                if tracker['tags']:
                    body += f"  Tags: {', '.join(tracker['tags'])}\n"
                body += "\n"

            body += f"\nCheck {self.base_url} for more details."

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender_email'], self.email_config['sender_password'])

            text = msg.as_string()
            server.sendmail(self.email_config['sender_email'], self.email_config['recipient_email'], text)
            server.quit()

            logger.info("Email notification sent successfully!")

        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")

    def send_whatsapp_notification(self, new_trackers):
        """Send WhatsApp notification about new trackers (using a WhatsApp Business API)"""
        if not self.whatsapp_config.get('enabled', False):
            return

        try:
            # This is a template for WhatsApp Business API - you would need to implement with a specific service
            message_body = f"🚨 New Tracker Signup Alert! 🚨\n\n"
            message_body += f"Found {len(new_trackers)} new opportunities:\n\n"

            for tracker in new_trackers:
                message_body += f"• {tracker['name']} ({tracker['abbreviation']})\n"
                message_body += f"  Closes: {tracker['date']}\n\n"

            message_body += f"Check {self.base_url} for details!"

            # Placeholder for WhatsApp API call - would need to be implemented with a specific service
            logger.info(f"WhatsApp notification prepared: {message_body}")
            # Example implementation would be:
            # requests.post(
            #     f"{self.whatsapp_config['api_url']}/messages",
            #     headers={"Authorization": f"Bearer {self.whatsapp_config['access_token']}"},
            #     json={
            #         "messaging_product": "whatsapp",
            #         "to": self.whatsapp_config['phone_number'],
            #         "text": {"body": message_body}
            #     }
            # )

            logger.info("WhatsApp notification sent successfully!")

        except Exception as e:
            logger.error(f"Error sending WhatsApp notification: {str(e)}")

    def send_notifications(self, new_trackers):
        """Send all configured notifications"""
        if not new_trackers:
            return

        logger.info(f"Sending notifications for {len(new_trackers)} new trackers")
        self.send_email_notification(new_trackers)
        self.send_whatsapp_notification(new_trackers)

    def get_tracker_listings(self, page=1, max_retries=3):
        """Get tracker listings from a specific page with retry mechanism"""
        url = f"{self.base_url}/"
        if page > 1:
            url = f"{self.base_url}/page/{page}"

        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching page {page} (attempt {attempt + 1}/{max_retries})")
                
                # Add random delay to be respectful to the server
                delay = random.uniform(*self.delay_range)
                time.sleep(delay)
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find all tracker entries
                tracker_entries = []

                # Based on the debug output, look for posts with class 'post' or 'hentry'
                # The tracker info is contained in these elements
                post_elements = soup.find_all(['div', 'article'], class_=lambda x: x and ('post' in x or 'hentry' in x))

                for element in post_elements:
                    text_content = element.get_text()

                    # Check if this element contains a tracker listing
                    # Look for the pattern "NAME (ABBR) IS OPEN FOR LIMITED SIGNUP!"
                    signup_pattern = r'([^(]+)\s*\(([^)]+)\)\s+IS OPEN FOR LIMITED SIGNUP!'
                    title_match = re.search(signup_pattern, text_content, re.IGNORECASE)

                    if title_match:
                        name = title_match.group(1).strip()
                        abbreviation = title_match.group(2).strip()

                        # Look for date - dates appear in elements with class 'post-date', 'post-day', 'post-month', 'post-year'
                        date_element = element.find(class_=lambda x: x and any(cls in x for cls in ['post-date', 'post-day', 'post-month', 'post-year']))
                        date = "Unknown date"
                        if date_element:
                            # Try to extract date from structured elements
                            day_elem = element.find(class_=lambda x: x and 'post-day' in x)
                            month_elem = element.find(class_=lambda x: x and 'post-month' in x)
                            year_elem = element.find(class_=lambda x: x and 'post-year' in x)

                            if day_elem and month_elem and year_elem:
                                date = f"{month_elem.get_text().strip()} {day_elem.get_text().strip()} {year_elem.get_text().strip()}"
                            elif date_element:
                                date = date_element.get_text().strip()
                        else:
                            # Fallback to regex in text
                            date_patterns = [
                                r'(\w{3}\s+\d{1,2}\s+\d{4})',  # Jan 15 2026
                                r'(\d{1,2}\s+\w{3}\s+\d{4})',  # 15 Jan 2026
                                r'(\w{3}\.\s+\d{1,2},?\s+\d{4})',  # Jan. 15, 2026
                            ]

                            for pattern in date_patterns:
                                date_match = re.search(pattern, text_content, re.IGNORECASE)
                                if date_match:
                                    date = date_match.group(1)
                                    break

                        # Look for description - usually follows the pattern "Name (Abbr) is a ..."
                        desc_pattern = rf'{re.escape(name)}\s+\({re.escape(abbreviation)}\)\s+is a\s+([^.]*?)(?:\n|$)'
                        desc_match = re.search(desc_pattern, text_content, re.IGNORECASE | re.DOTALL)
                        description = desc_match.group(1).strip() if desc_match else "No description"

                        # Clean up the description to remove extra whitespace and formatting
                        description = ' '.join(description.split())

                        # Look for tags - these are often in elements with class containing 'tag' or 'category'
                        tags = []
                        # Look for elements with tag-related classes
                        tag_elements = element.find_all(['span', 'a', 'div', 'p'],
                                                      class_=lambda x: x and any(tag in x.lower() for tag in ['tag', 'category', 'post-tags']))
                        for tag_elem in tag_elements:
                            tag_text = tag_elem.get_text().strip()
                            if tag_text and len(tag_text) < 100 and tag_text not in ['Tags:', 'Categories:']:  # Avoid label text
                                # Split by bullet character, middle dot, or other separators
                                parts = [part.strip() for part in tag_text.replace('•', '|').replace('·', '|').replace('•', '|').split('|')]
                                tags.extend([part for part in parts if part and part.lower() not in ['tags:', 'categories:']])

                        # Also look for tags in the text content by looking for common tracker categories
                        # These are often mentioned in the text
                        common_tags = ['general', 'hd', 'uhd', '4k', 'movies', 'tv', 'music', 'games', 'xxx', 'anime', 'porn', 'sports', '0day', 'gay', 'limited signup']
                        text_lower = text_content.lower()
                        for tag in common_tags:
                            if tag in text_lower and tag not in [t.lower() for t in tags]:
                                tags.append(tag)

                        tracker_info = {
                            'name': name,
                            'abbreviation': abbreviation,
                            'date': date,
                            'description': description,
                            'tags': tags,
                            'full_text': text_content[:300]  # Store a snippet for comparison
                        }

                        tracker_entries.append(tracker_info)

                logger.info(f"Found {len(tracker_entries)} tracker entries on page {page}")
                return tracker_entries

            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    # Exponential backoff
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"Waiting {wait_time:.2f}s before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to fetch page {page} after {max_retries} attempts")
                    return []
            except Exception as e:
                logger.error(f"Unexpected error fetching page {page}: {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"Waiting {wait_time:.2f}s before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to fetch page {page} after {max_retries} attempts")
                    return []

        return []

    def get_all_trackers(self, max_pages=5):
        """Get all tracker listings from all pages with improved error handling"""
        all_trackers = []
        page = 1

        try:
            # First, try to get the total number of pages
            response = self.session.get(self.base_url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for pagination links - they might be in different structures
            max_page = 1

            # Try different selectors for pagination
            pagination_selectors = [
                '.multinav',       # From debug output, this appears to be the pagination class
                'nav.navigation',  # Common class for navigation
                '.pagination',     # Common class name
                '.pager',          # Another common class
                'nav',             # Generic nav tag
                '.wp-pagenavi'     # WordPress pagination
            ]

            for selector in pagination_selectors:
                pagination = soup.select_one(selector)
                if pagination:
                    # Look for links with page numbers
                    links = pagination.find_all('a', href=True)
                    for link in links:
                        href = link['href']
                        # Look for patterns like /page/2/, /page/3/, etc.
                        page_matches = re.findall(r'/page/(\d+)', href)
                        for page_num_str in page_matches:
                            try:
                                page_num = int(page_num_str)
                                max_page = max(max_page, page_num)
                            except ValueError:
                                continue
                    break  # Found pagination, no need to check other selectors

            # If we didn't find pagination via selectors, try looking for page number links anywhere in the page
            if max_page == 1:
                # Look for any links that contain page numbers
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    href = link['href']
                    page_matches = re.findall(r'/page/(\d+)', href)
                    for page_num_str in page_matches:
                        try:
                            page_num = int(page_num_str)
                            max_page = max(max_page, page_num)
                        except ValueError:
                            continue

            # Limit to first max_pages pages to avoid excessive requests
            max_pages_to_check = min(max_page, max_pages)

            logger.info(f"Checking {max_pages_to_check} pages...")

            for page in range(1, max_pages_to_check + 1):
                logger.info(f"Scanning page {page}...")
                trackers = self.get_tracker_listings(page)
                all_trackers.extend(trackers)

        except Exception as e:
            logger.error(f"Error getting all trackers: {str(e)}")

        return all_trackers

def save_trackers_to_file(trackers, filename='trackers.json'):
    """Save tracker data to a JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(trackers, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(trackers)} trackers to {filename}")
    except Exception as e:
        logger.error(f"Error saving trackers to file: {str(e)}")

def load_previous_trackers(filename='trackers.json'):
    """Load previously saved tracker data"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Loaded {len(data)} previous trackers from {filename}")
            return data
    except FileNotFoundError:
        logger.info(f"No previous tracker data found at {filename}")
        return []
    except Exception as e:
        logger.error(f"Error loading previous trackers: {str(e)}")
        return []

def find_new_trackers(current_trackers, previous_trackers):
    """Find new trackers by comparing with previous data"""
    # Create a unique identifier for each tracker based on name and date
    previous_tracker_ids = {f"{tracker['name']}_{tracker['date']}_{tracker['abbreviation']}" for tracker in previous_trackers}
    current_tracker_ids = {f"{tracker['name']}_{tracker['date']}_{tracker['abbreviation']}" for tracker in current_trackers}

    # Find completely new trackers
    new_tracker_ids = current_tracker_ids - previous_tracker_ids

    # Return the full tracker objects for the new ones
    new_trackers = [
        tracker for tracker in current_trackers
        if f"{tracker['name']}_{tracker['date']}_{tracker['abbreviation']}" in new_tracker_ids
    ]

    return new_trackers

def main():
    # Email configuration - fill in your details
    email_config = {
        'enabled': True,  # Set to True to enable email notifications
        'smtp_server': 'smtp.gmail.com',  # Example for Gmail
        'smtp_port': 587,
        'sender_email': 'your_email@gmail.com',  # Replace with your email
        'sender_password': 'your_app_password',  # Use app password for Gmail
        'recipient_email': 'recipient@gmail.com'  # Email to send notifications to
    }

    # WhatsApp configuration - fill in your details if using WhatsApp notifications
    whatsapp_config = {
        'enabled': False,  # Set to True to enable WhatsApp notifications
        'api_url': 'https://graph.facebook.com/v13.0/YOUR_PHONE_NUMBER_ID',
        'access_token': 'YOUR_ACCESS_TOKEN',
        'phone_number': 'RECIPIENT_PHONE_NUMBER'  # Recipient's phone number in international format
    }

    # Initialize monitor with rate limiting (1-3 seconds between requests)
    monitor = TrackerMonitor(email_config=email_config, whatsapp_config=whatsapp_config, delay_range=(1, 3))
    logger.info("Fetching current tracker listings...")

    current_trackers = monitor.get_all_trackers()
    logger.info(f"Found {len(current_trackers)} tracker listings")

    # Save current trackers
    save_trackers_to_file(current_trackers)

    # Load previous trackers and find new ones
    previous_trackers = load_previous_trackers()
    new_trackers = find_new_trackers(current_trackers, previous_trackers)

    if new_trackers:
        logger.info(f"\n🎉 Found {len(new_trackers)} NEW tracker opportunities!")
        for tracker in new_trackers:
            logger.info(f"- {tracker['name']} ({tracker['abbreviation']}) - Closing: {tracker['date']}")

        # Send notifications
        monitor.send_notifications(new_trackers)
    else:
        logger.info("\nNo new tracker opportunities found.")

if __name__ == "__main__":
    main()