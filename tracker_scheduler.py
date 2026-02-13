import schedule
import time
from tracker_monitor import main
import logging
import signal
import sys
import threading
import traceback

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('tracker_monitor.log'),
        logging.StreamHandler()
    ]
)

class GracefulKiller:
    """Handle graceful shutdown of the scheduler"""
    kill_now = False
    
    def __init__(self):
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def _handle_signal(self, signum, frame):
        logging.info(f"Received signal {signum}, shutting down gracefully...")
        self.kill_now = True

def run_tracker_monitor():
    """Run the tracker monitor and log the result"""
    try:
        logging.info("Starting tracker monitoring cycle...")
        main()
        logging.info("Tracker monitoring cycle completed")
    except Exception as e:
        logging.error(f"Error during tracker monitoring: {str(e)}")
        logging.error(traceback.format_exc())

def main_loop():
    """Main loop for the scheduler"""
    killer = GracefulKiller()
    
    print("Tracker Monitor Scheduler Started")
    print("Checks will run every hour. Press Ctrl+C to stop.")

    # Run once immediately when starting
    run_tracker_monitor()

    # Keep the script running
    while not killer.kill_now:
        schedule.run_pending()
        time.sleep(60)  # Check for scheduled tasks every minute
        
        # Optional: Log status periodically
        if int(time.time()) % 3600 == 0:  # Log every hour
            logging.info("Scheduler is running...")

    print("Scheduler stopped gracefully.")

if __name__ == "__main__":
    # Schedule the monitor to run every hour
    schedule.every().hour.do(run_tracker_monitor)

    # Alternative: Run every 30 minutes
    # schedule.every(30).minutes.do(run_tracker_monitor)

    # Alternative: Run at specific times
    # schedule.every().day.at("09:00").do(run_tracker_monitor)
    # schedule.every().day.at("15:00").do(run_tracker_monitor)
    # schedule.every().day.at("21:00").do(run_tracker_monitor)

    main_loop()