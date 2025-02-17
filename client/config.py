"""
Defines configuration settings for the synchronization client, including the server URL, 
local folder path, and patterns for ignoring temporary or unwanted files during synchronization.
"""

# Defines the URL of the synchronization server that the client will communicate with
SERVER_URL = 'http://:8080'

# Defines the local folder path on the client machine to be synchronized
LOCAL_FOLDER = ''

# List of file and folder patterns to ignore during synchronization
# These patterns typically correspond to temporary, system, or unnecessary files
ignore_patterns = [
    '.goutputstream-', '~', '.swp', '.tmp', '.part', '.DS_Store', '.git', 
    '.gitignore', '.env', '.venv', '.idea', '.vscode', '.svn', '.cache', 
    '.local', '.npm', '.yarn', 'Thumbs.db', 'desktop.ini'
]
