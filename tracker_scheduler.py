import schedule
import time
from tracker_monitor import main
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('tracker_monitor.log'),
        logging.StreamHandler()
    ]
)

def run_tracker_monitor():
    """Run the tracker monitor and log the result"""
    try:
        logging.info("Starting tracker monitoring cycle...")
        main()
        logging.info("Tracker monitoring cycle completed")
    except Exception as e:
        logging.error(f"Error during tracker monitoring: {str(e)}")

# Schedule the monitor to run every hour
schedule.every().hour.do(run_tracker_monitor)

# Alternative: Run every 30 minutes
# schedule.every(30).minutes.do(run_tracker_monitor)

# Alternative: Run at specific times
# schedule.every().day.at("09:00").do(run_tracker_monitor)
# schedule.every().day.at("15:00").do(run_tracker_monitor)
# schedule.every().day.at("21:00").do(run_tracker_monitor)

if __name__ == "__main__":
    print("Tracker Monitor Scheduler Started")
    print("Checks will run every hour. Press Ctrl+C to stop.")
    
    # Run once immediately when starting
    run_tracker_monitor()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check for scheduled tasks every minute