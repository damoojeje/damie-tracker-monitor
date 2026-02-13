import unittest
from unittest.mock import patch, MagicMock
import json
import tempfile
import os
from tracker_monitor import TrackerMonitor, find_new_trackers, load_previous_trackers, save_trackers_to_file


class TestTrackerMonitor(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.monitor = TrackerMonitor()
        
    def test_find_new_trackers(self):
        """Test the find_new_trackers function."""
        current_trackers = [
            {
                'name': 'Test Tracker',
                'abbreviation': 'TT',
                'date': 'Jan 1 2025',
                'description': 'A test tracker',
                'tags': ['hd', 'movies']
            },
            {
                'name': 'Another Tracker',
                'abbreviation': 'AT',
                'date': 'Feb 1 2025',
                'description': 'Another test tracker',
                'tags': ['tv', 'general']
            }
        ]
        
        previous_trackers = [
            {
                'name': 'Old Tracker',
                'abbreviation': 'OT',
                'date': 'Dec 1 2024',
                'description': 'An old tracker',
                'tags': ['general']
            }
        ]
        
        new_trackers = find_new_trackers(current_trackers, previous_trackers)
        
        # Both current trackers should be new since they weren't in previous
        self.assertEqual(len(new_trackers), 2)
        
        # Test with overlapping trackers
        previous_with_overlap = [
            {
                'name': 'Test Tracker',
                'abbreviation': 'TT',
                'date': 'Jan 1 2025',  # Same name and date - should be considered same
                'description': 'A test tracker',
                'tags': ['hd', 'movies']
            }
        ]
        
        new_trackers = find_new_trackers(current_trackers, previous_with_overlap)
        # Only 'Another Tracker' should be new
        self.assertEqual(len(new_trackers), 1)
        self.assertEqual(new_trackers[0]['name'], 'Another Tracker')
    
    @patch('builtins.open')
    @patch('json.load')
    def test_load_previous_trackers(self, mock_json_load, mock_open):
        """Test loading previous trackers from file."""
        expected_data = [
            {
                'name': 'Test Tracker',
                'abbreviation': 'TT',
                'date': 'Jan 1 2025',
                'description': 'A test tracker',
                'tags': ['hd', 'movies']
            }
        ]
        
        mock_json_load.return_value = expected_data
        
        result = load_previous_trackers('test_file.json')
        
        self.assertEqual(result, expected_data)
        mock_open.assert_called_once_with('test_file.json', 'r', encoding='utf-8')
    
    @patch('builtins.open')
    @patch('json.dump')
    def test_save_trackers_to_file(self, mock_json_dump, mock_open):
        """Test saving trackers to file."""
        trackers = [
            {
                'name': 'Test Tracker',
                'abbreviation': 'TT',
                'date': 'Jan 1 2025',
                'description': 'A test tracker',
                'tags': ['hd', 'movies']
            }
        ]
        
        save_trackers_to_file(trackers, 'test_output.json')
        
        mock_open.assert_called_once_with('test_output.json', 'w', encoding='utf-8')
        mock_json_dump.assert_called_once_with(trackers, mock_open().__enter__(), indent=2, ensure_ascii=False)


class TestEmailNotification(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.email_config = {
            'enabled': True,
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': 'test@example.com',
            'sender_password': 'password',
            'recipient_email': 'recipient@example.com'
        }
        self.monitor = TrackerMonitor(email_config=self.email_config)
    
    @patch('smtplib.SMTP')
    def test_send_email_notification(self, mock_smtp):
        """Test sending email notification."""
        new_trackers = [
            {
                'name': 'Test Tracker',
                'abbreviation': 'TT',
                'date': 'Jan 1 2025',
                'description': 'A test tracker',
                'tags': ['hd', 'movies']
            }
        ]
        
        self.monitor.send_email_notification(new_trackers)
        
        # Verify that SMTP methods were called
        mock_smtp_instance = mock_smtp.return_value
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with('test@example.com', 'password')
        mock_smtp_instance.sendmail.assert_called_once()
        mock_smtp_instance.quit.assert_called_once()


class TestWhatsAppNotification(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.whatsapp_config = {
            'enabled': True,
            'api_url': 'https://graph.facebook.com/v13.0/YOUR_PHONE_NUMBER_ID',
            'access_token': 'YOUR_ACCESS_TOKEN',
            'phone_number': 'RECIPIENT_PHONE_NUMBER'
        }
        self.monitor = TrackerMonitor(whatsapp_config=self.whatsapp_config)
    
    def test_send_whatsapp_notification(self):
        """Test sending WhatsApp notification (placeholder)."""
        new_trackers = [
            {
                'name': 'Test Tracker',
                'abbreviation': 'TT',
                'date': 'Jan 1 2025',
                'description': 'A test tracker',
                'tags': ['hd', 'movies']
            }
        ]
        
        # This should not raise an exception
        self.monitor.send_whatsapp_notification(new_trackers)


if __name__ == '__main__':
    # Create a temporary directory for test files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to temp dir for test files
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            unittest.main(verbosity=2)
        finally:
            os.chdir(original_cwd)