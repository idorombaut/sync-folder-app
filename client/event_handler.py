"""
Implements a file system event handler using the Watchdog library to detect and handle 
file changes (creation, modification, deletion, and movement). It interacts with the server 
to synchronize these events based on defined rules and ignore patterns.
"""

import os
import time
import logging
from watchdog.events import FileSystemEventHandler
from file_utils import upload_file, delete_file, is_ignored_file


class ChangeHandler(FileSystemEventHandler):
    """
    Handles file system events such as creation, deletion, modification, and moving of files.
    It processes events and interacts with the server to keep the file system in sync.
    """
    def __init__(self, server_url, ignore_patterns):
        """
        Initializes the ChangeHandler with server URL and ignore patterns.

        Args:
            server_url (str): The URL of the server for synchronization.
            ignore_patterns (list): List of patterns for temporary files to ignore.
        """
        super().__init__()
        self.server_url = server_url
        self.ignore_patterns = ignore_patterns
        self.last_modified_time = {}  # Track the last modified timestamp of files
        self.debounce_time = 1  # 1 second debounce time

    def on_created(self, event):
        """
        Handles file creation events.

        Args:
            event (FileSystemEvent): The event containing details about the created file.
        """
        if not event.is_directory and not is_ignored_file(os.path.basename(event.src_path), self.ignore_patterns):
            logging.info(f"File created: {event.src_path}")
            upload_file(self.server_url, event.src_path)

    def on_deleted(self, event):
        """
        Handles file deletion events.

        Args:
            event (FileSystemEvent): The event containing details about the deleted file.
        """
        if not event.is_directory and not is_ignored_file(os.path.basename(event.src_path), self.ignore_patterns):
            logging.info(f"File deleted: {event.src_path}")
            delete_file(self.server_url, os.path.basename(event.src_path))

    def on_modified(self, event):
        """
        Handles file modification events with a debounce mechanism.

        Args:
            event (FileSystemEvent): The event containing details about the modified file.
        """
        if not event.is_directory and not is_ignored_file(os.path.basename(event.src_path), self.ignore_patterns):
            current_time = time.time()
            last_time = self.last_modified_time.get(event.src_path, 0)

            # Check if enough time has passed since the last modification to avoid redundant uploads
            if current_time - last_time > self.debounce_time:
                logging.info(f"File modified: {event.src_path}")
                upload_file(self.server_url, event.src_path)
                self.last_modified_time[event.src_path] = current_time  # Update the last modified time

    def on_moved(self, event):
        """
        Handles file movement events.

        Args:
            event (FileSystemEvent): The event containing details about the moved file.
        """
        if not event.is_directory and not is_ignored_file(os.path.basename(event.src_path), self.ignore_patterns):
            logging.info(f"File moved from {event.src_path} to {event.dest_path}")
            delete_file(self.server_url, os.path.basename(event.src_path))
            upload_file(self.server_url, event.dest_path)
