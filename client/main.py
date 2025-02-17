"""
The entry point of the synchronization program. Sets up logging, initializes the
file monitoring observer, and periodically triggers synchronization with the server 
to keep local and server directories in sync.
"""

import time
import logging
from watchdog.observers import Observer
from config import SERVER_URL, LOCAL_FOLDER, ignore_patterns
from event_handler import ChangeHandler
from sync_manager import sync_with_server

# Set up logging configuration for the program, logging messages with a timestamp
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def monitor_folder():
    """
    Monitors the local folder for changes and synchronizes with the server.
    It starts an observer that watches for file system events in the specified directory.
    """
    
    # Initialize the event handler, passing the server URL and ignore patterns
    event_handler = ChangeHandler(SERVER_URL, ignore_patterns)

    # Initialize the observer to monitor the file system for changes
    observer = Observer()

    # Schedule the event handler to monitor the local folder for changes (recursive)
    observer.schedule(event_handler, LOCAL_FOLDER, recursive=True)

    # Start the observer to begin monitoring
    observer.start()
    
    try:
        while True:
            # Periodically synchronize with the server every 5 seconds
            sync_with_server(SERVER_URL, LOCAL_FOLDER, ignore_patterns)
            time.sleep(5)  # Wait for 5 seconds before the next sync
    except KeyboardInterrupt:
        # Stop the observer if interrupted
        observer.stop()
    
    observer.join()  # Wait for the observer to finish


if __name__ == "__main__":
    monitor_folder()  # Run the folder monitoring function
