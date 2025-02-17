"""
This module contains utility functions for file-related operations, 
specifically for computing file hashes to ensure data integrity.
"""

import hashlib
import logging


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
