"""
Skill for monitoring tracker signups
"""
import subprocess
import sys
import os
from pathlib import Path

def run_tracker_monitor():
    """Run the tracker monitor script"""
    try:
        # Add the project directory to Python path
        project_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(project_dir))
        
        # Import and run the main function
        from tracker_monitor import main
        main()
        return {"status": "success", "message": "Tracker monitor completed successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Error running tracker monitor: {str(e)}"}

def run_tracker_scheduler():
    """Run the tracker scheduler script"""
    try:
        # Add the project directory to Python path
        project_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(project_dir))
        
        # Import and run the scheduler
        from tracker_scheduler import main_loop
        main_loop()
        return {"status": "success", "message": "Tracker scheduler completed successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Error running tracker scheduler: {str(e)}"}

def run_setup_wizard():
    """Run the setup wizard"""
    try:
        # Add the project directory to Python path
        project_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(project_dir))
        
        # Import and run the setup wizard
        from setup_wizard import main
        main()
        return {"status": "success", "message": "Setup wizard completed successfully"}
    except Exception as e:
        return {"status": "error", "message": f"Error running setup wizard: {str(e)}"}

def run_tests():
    """Run the test suite"""
    try:
        result = subprocess.run([sys.executable, '-m', 'unittest', 'test_tracker_monitor'], 
                              capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        if result.returncode == 0:
            return {"status": "success", "message": "All tests passed", "output": result.stdout}
        else:
            return {"status": "error", "message": "Some tests failed", "output": result.stderr}
    except Exception as e:
        return {"status": "error", "message": f"Error running tests: {str(e)}"}