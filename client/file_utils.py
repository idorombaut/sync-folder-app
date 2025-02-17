"""
This module provides functions for synchronizing files between a local client and a server. 
It includes functionalities for uploading, downloading, and deleting files, as well as checking 
file modification times, computing file hashes, and handling temporary or ignored files. 
The module communicates with the server using HTTP requests and handles errors with logging.
"""

import os
import hashlib
import requests
import logging


def is_ignored_file(filename, ignore_patterns):
    """
    Checks if a file is temporary based on ignore patterns.

    Args:
        filename (str): The name of the file to check.
        ignore_patterns (list): List of patterns for files to ignore.

    Returns:
        bool: True if the file is temporary, False otherwise.
    """
    return any(filename.startswith(pattern) or filename.endswith(pattern) for pattern in ignore_patterns)


def compute_file_hash(file_path):
    """
    Compute SHA-256 hash of a file.

    Args:
        file_path (str): The path to the file to compute the hash for.

    Returns:
        str: The SHA-256 hash of the file as a hexadecimal string.
    """
    
    # Create a new SHA-256 hash object
    hash_sha256 = hashlib.sha256()

    try:
        # Open the specified file in binary read mode
        with open(file_path, 'rb') as f:
            # Read the file in chunks of 4096 bytes until the end of the file is reached
            for chunk in iter(lambda: f.read(4096), b""):
                # Update the hash object with the current chunk of data
                hash_sha256.update(chunk)
    except Exception as e:
        logging.error(f'Error reading file {file_path}: {e}')

    return hash_sha256.hexdigest()


def fetch_server_file_mod_time(server_url, filename):
    """
    Fetches the modification time of a file from the server.

    Args:
        server_url (str): The URL of the server.
        filename (str): The name of the file to check.

    Returns:
        float: The modification time of the file as a Unix timestamp, or 'None' if an error occurs.
    """
    try:
        # Send a GET request to the server to fetch file information
        response = requests.get(f"{server_url}/file_info/{filename}")
        response.raise_for_status()

        # Parse the server's response (expected to be in JSON format)
        file_info = response.json()
        
        # Extract the 'mod_time' (modification time) from the response
        mod_time = file_info['mod_time']

        return mod_time
    
    except requests.RequestException as e:
        logging.error(f'Error fetching file modification time for \'{filename}\': {e}')
        return None


def upload_file(server_url, file_path):
    """
    Uploads a file to the server if it does not already exist or if its hash is different.

    Args:
        server_url (str): The URL of the server to upload the file to.
        file_path (str): The path of the file to upload.

    Returns:
        bool: True if the upload was successful, False otherwise.
    """
    filename = os.path.basename(file_path)
    try:
        # Send a GET request to the server to fetch the list of files already on the server
        response = requests.get(f"{server_url}/files")
        response.raise_for_status()

        # Get the list of files from the server's response
        files_data = response.json()['files']
        
        # Parse the server response to get a dictionary of filenames and their hashes
        server_files = {file['filename']: file['hash'] for file in files_data}
        
        # Calculate the local file's hash using SHA-256
        local_hash = compute_file_hash(file_path)

        if filename in server_files:
            # Case 1: File exists on the server with the same hash
            if server_files[filename] == local_hash:
                logging.info(f"File \'{filename}\' already exists on server with matching hash. Skipping upload")
                return False
            
            # Case 2: The file exists but the hashes are different, check modification times
            local_mod_time = os.path.getmtime(file_path)
            server_mod_time = fetch_server_file_mod_time(server_url, filename)
            
            if server_mod_time is None:
                logging.error(f'Could not fetch modification time for \'{filename}\'. Skipping')
                return False
            
            # If the local file is newer, upload the file
            if local_mod_time > server_mod_time:
                logging.info(f'Local version of \'{filename}\' is newer. Uploading to server')
                with open(file_path, 'rb') as f:
                    # Send the file to the server using a POST request
                    upload_response = requests.post(f"{server_url}/upload", files={'file': f})
                    upload_response.raise_for_status()
                    response_data = upload_response.json()
                    logging.info(f"{response_data['message']}")
                    return True
            else:
                logging.info(f"Server version of \'{filename}\' is newer or the same. Skipping upload")
                return False
        
        else:
            # Case 3: File does not exist on the server, proceed with upload
            with open(file_path, 'rb') as f:
                # Send the file to the server using a POST request
                upload_response = requests.post(f"{server_url}/upload", files={'file': f})
                upload_response.raise_for_status()
                response_data = upload_response.json()
                logging.info(f"{response_data['message']}")
                return True

    except requests.HTTPError as http_err:
        logging.error(f'HTTP error occurred while uploading {file_path}: {http_err}')
    except FileNotFoundError:
        logging.error(f'File not found: {file_path}')
    except Exception as e:
        logging.error(f'Error uploading {file_path}: {e}')
    
    return False


def delete_file(server_url, filename):
    """
    Deletes a file from the server if it exists.

    Args:
        server_url (str): The URL of the server to delete the file from.
        filename (str): The name of the file to delete.

    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    try:
        # Send a GET request to the server to fetch the list of files on the server
        response = requests.get(f"{server_url}/files")
        response.raise_for_status()

        # Get the list of files from the server's response
        files_data = response.json()['files']

        # Parse the server's response to get a list of filenames on the server
        server_files = [file['filename'] for file in files_data]
        
        # Check if the file exists on the server
        if filename not in server_files:
            logging.info(f"File \'{filename}\' does not exist on server. Skipping deletion")
        else:
            # If the file exists, send a DELETE request to remove the file
            delete_response = requests.delete(f"{server_url}/delete/{filename}")
            delete_response.raise_for_status()
            response_data = delete_response.json()
            logging.info(f"{response_data['message']}")
            return True

    except requests.HTTPError as http_err:
        logging.error(f'HTTP error occurred while deleting \'{filename}\': {http_err}')
    except Exception as e:
        logging.error(f'Error deleting \'{filename}\' from server: {e}')

    return False


def download_file(server_url, filename, local_folder):
    """
    Downloads a file from the server to a local folder.

    Args:
        server_url (str): The URL of the server to download the file from.
        filename (str): The name of the file to download.
        local_folder (str): The local directory where the file should be saved.

    Returns:
        bool: True if the download was successful, False otherwise.
    """
    try:
        # Send a GET request to the server to fetch the file
        # 'stream=True' allows the file to be downloaded in chunks instead of loading it all into memory at once
        response = requests.get(f"{server_url}/download/{filename}", stream=True)
        response.raise_for_status()
        file_path = os.path.join(local_folder, filename)
        with open(file_path, 'wb') as f:
            # Iterate over the response content in chunks of the specified size
            for chunk in response.iter_content(chunk_size=8192):  # 8KB chunks
                f.write(chunk)  # Write each chunk to the file
        logging.info(f'Downloaded \'{filename}\' to {file_path}')
        return True

    except requests.HTTPError as http_err:
        logging.error(f'HTTP error occurred while downloading \'{filename}\': {http_err}')
    except Exception as e:
        logging.error(f'Error downloading \'{filename}\': {e}')

    return False
