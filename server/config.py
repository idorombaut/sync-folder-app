"""
This file configures the application by specifying the directory path (sync_folder) where uploaded files will be stored. 
It creates the directory if it does not already exist.
"""

import os

# Path to the shared folder where files will be stored
SYNC_FOLDER = ''

os.makedirs(SYNC_FOLDER, exist_ok=True)
