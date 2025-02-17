"""
This module provides functionality to synchronize a local folder with a remote server.
It fetches the file list from the server, compares it with the local files, and handles 
necessary file downloads or deletions, resolving conflicts based on file hashes and modification times.
"""

import os
import requests
import logging
from file_utils import is_ignored_file, compute_file_hash, fetch_server_file_mod_time, download_file


def sync_with_server(server_url, local_folder, ignore_patterns):
    """
    Synchronizes the local folder with the server by fetching the server's file list,
    comparing it with the local files, and handling the necessary file downloads or deletions.

    Args:
        server_url (str): The URL of the server.
        local_folder (str): The path to the local folder to be synchronized.
        ignore_patterns (list): List of filename patterns to ignore during synchronization.
    """
    try:
        # Send a request to the server to fetch the list of files
        response = requests.get(f"{server_url}/files")
        response.raise_for_status()
        
        # Get the list of files from the server's response
        files_data = response.json()['files']
        
        # Create a dictionary of server files (filename: hash) while ignoring files based on patterns
        server_files = {
            f['filename']: f['hash']
            for f in files_data
            if not is_ignored_file(f['filename'], ignore_patterns)
        }

        # List all the files in the local folder
        all_files = os.listdir(local_folder)
        
        # Create a dictionary of local files (filename: hash) while ignoring files based on patterns
        local_files = {
            f: compute_file_hash(os.path.join(local_folder, f))
            for f in all_files
            if not is_ignored_file(f, ignore_patterns)
        }
        
        # Remove local files that are not present on the server
        remove_local_files(local_files, server_files, local_folder)
        
        # Handle downloading files from the server to the local folder
        handle_downloads(server_files, local_files, server_url, local_folder)
        
    except requests.RequestException as e:
        logging.error(f'Failed to sync with server: {e}')


def handle_downloads(server_files, local_files, server_url, local_folder):
    """
    Handles downloading files from the server to the local folder when necessary.
    This includes downloading missing files and resolving conflicts based on file hash
    and modification times.

    Args:
        server_files (dict): A dictionary of server file names and their corresponding hashes.
        local_files (dict): A dictionary of local file names and their corresponding hashes.
        server_url (str): The URL of the server to download files from.
        local_folder (str): The path to the local folder where files will be downloaded.
    """
    for filename, server_hash in server_files.items():
        local_file_path = os.path.join(local_folder, filename)

        # Case 1: File is missing locally, so download from server
        if filename not in local_files:
            logging.info(f'Downloading \'{filename}\' from server (not found locally)')
            if not download_file(server_url, filename, local_folder):
                logging.error(f'Failed to download \'{filename}\'')

        else:
            # Case 2: File exists locally, check for hash mismatch
            local_hash = local_files[filename]
            if local_hash != server_hash:
                logging.info(f'Hash mismatch for \'{filename}\', checking modification times to resolve conflict')

                # Fetch modification times
                local_mod_time = os.path.getmtime(local_file_path)
                server_mod_time = fetch_server_file_mod_time(server_url, filename)

                if server_mod_time is None:
                    logging.error(f'Could not fetch modification time for \'{filename}\'. Skipping')
                    continue  # Skip to the next file

                # If server version is newer, download it
                if local_mod_time < server_mod_time:
                    logging.info(f'Server version of \'{filename}\' is newer. Downloading to local folder')
                    if not download_file(server_url, filename, local_folder):
                        logging.error(f'Failed to download \'{filename}\'')


def remove_local_files(local_files, server_files, local_folder):
    """
    Removes local files that are not present on the server.

    Args:
        local_files (dict): A dictionary of local file names and their corresponding hashes.
        server_files (dict): A dictionary of server file names and their corresponding hashes.
        local_folder (str): The path to the local folder where files will be removed from.
    """
    for filename in local_files:

        # If a file is present locally but not on the server, remove it
        if filename not in server_files:
            logging.info(f'Local file \'{filename}\' not on server. Removing it')
            try:
                os.remove(os.path.join(local_folder, filename))
                logging.info(f'Successfully removed \'{filename}\' from local folder')
            except Exception as e:
                logging.error(f'Error removing \'{filename}\': {e}')
