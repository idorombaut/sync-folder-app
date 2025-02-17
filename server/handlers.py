"""
This module implements an HTTP server to manage file synchronization in a local network.
It supports various HTTP methods to handle file uploads, downloads, listing files, fetching file metadata,
and deleting files in a synchronized folder.
"""

import os
import json
import cgi
import logging
from http.server import BaseHTTPRequestHandler
from config import SYNC_FOLDER
from file_utils import compute_file_hash


class RequestHandler(BaseHTTPRequestHandler):
    """
    This class extends the BaseHTTPRequestHandler to handle various HTTP requests for
    managing files in the synchronized folder. It supports file uploads (POST), downloads (GET),
    listing files (GET), fetching file information (GET), and deleting files (DELETE).
    """
    def _send_response(self, status_code, message, content_type='application/json'):
        """
        Helper function to send JSON responses.

        Args:
            status_code (int): HTTP status code to send (e.g., 200, 404).
            message (dict): The message to send in the response body.
            content_type (str): The content type of the response (default is 'application/json').
        """

        # Send the HTTP status code (e.g., 200 for success, 404 for not found)
        self.send_response(status_code)

        # Add a header specifying the content type of the response (default is JSON)
        self.send_header('Content-type', content_type)

        # End the headers section, indicating that the header information is complete
        self.end_headers()

        # Write the JSON-encoded message to the response body
        # The message is serialized into a JSON string and then encoded into bytes
        self.wfile.write(json.dumps(message).encode())

    def do_POST(self):
        """
        Handle POST requests for file uploads.

        This method processes incoming file uploads. It checks if the request is a
        multipart form data, extracts the file, and saves it to the synchronized folder.
        """

        # Check if the request path is '/upload' to handle file upload requests
        if self.path == '/upload':

            # Parse the Content-Type header to check if it's 'multipart/form-data', typically used for file uploads
            content_type, _ = cgi.parse_header(self.headers['Content-Type'])

            # Ensure that the content type is 'multipart/form-data', which indicates a file upload
            if content_type == 'multipart/form-data':

                # Parse the request body to extract the file data
                # 'rfile' contains the body of the POST request, including the file content
                request_data = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})

                # Retrieve the file data from the request
                file_item = request_data['file']

                # Check if the file was uploaded (i.e., filename is not empty)
                if file_item.filename:

                    # Extract the filename and read the file content
                    filename = file_item.filename
                    file_data = file_item.file.read()

                    # Construct the full file path where the file should be saved (in the sync folder)
                    file_path = os.path.join(SYNC_FOLDER, filename)

                    # Open the destination file in write-binary mode and save the uploaded content
                    with open(file_path, 'wb') as f:
                        f.write(file_data)

                    logging.info(f"Uploaded \'{filename}\'")
                    self._send_response(200, {'message': f'File \'{filename}\' uploaded successfully'})

                else:
                    self._send_response(400, {'error': 'No file uploaded'})

    def do_GET(self):
        """
        Handle GET requests.

        This method processes various GET requests:
        - '/download/filename': Initiates file download.
        - '/files': Lists all files in the synchronized folder with their hashes.
        - '/file_info/filename': Fetches the modification time of the specified file.
        """

        # Check if the request path starts with '/download/' to handle file download requests
        if self.path.startswith('/download/'):
            self.handle_download()  # Call the method to handle file download

        # Check if the request path is '/files' to list all files in the synchronized folder
        elif self.path == '/files':
            self.handle_files_list()  # Call the method to list the files and their hashes

        # Check if the request path starts with '/file_info/' to handle file information requests
        elif self.path.startswith('/file_info/'):
            self.handle_file_info()  # Call the method to fetch and return the file's modification time

    def handle_download(self):
        """
        Handle file download requests.

        This method serves a file for download if it exists in the synchronized folder.
        If the file does not exist, it sends a 404 error.
        """

        # Extract the filename from the URL by splitting the path and getting the last part
        filename = self.path.split('/')[-1]

        # Create the full file path by joining the synchronized folder path with the filename
        file_path = os.path.join(SYNC_FOLDER, filename)

        # Check if the file exists at the specified path
        if os.path.exists(file_path):

            # Send a 200 OK response indicating the file is available for download
            self.send_response(200)

            # Set the content type to 'application/octet-stream' to indicate binary file data
            self.send_header('Content-type', 'application/octet-stream')

            # Set the Content-Disposition header to specify that the file should be downloaded 
            # with the original filename
            self.send_header('Content-Disposition', f'attachment; filename={filename}')

            # End the headers section of the response
            self.end_headers()

            # Open the file in read-binary mode and write the file content to the response body
            with open(file_path, 'rb') as file:
                self.wfile.write(file.read())

        else:
            self._send_response(404, {'error': 'File not found'})

    def handle_files_list(self):
        """
        List all files in the synchronized folder with their hashes.

        This method scans the synchronized folder, computes the hash of each file,
        and sends a JSON response with the file names and corresponding hashes.
        """

        # Initialize an empty list to store the information about each file
        files_info = []

        # Iterate over all files in the synchronized folder
        for filename in os.listdir(SYNC_FOLDER):

            # Construct the full path to the file
            file_path = os.path.join(SYNC_FOLDER, filename)

            # Compute the hash of the file
            file_hash = compute_file_hash(file_path)

            # Append the filename and its corresponding hash to the files_info list
            files_info.append({'filename': filename, 'hash': file_hash})

        # Wrap the list in a dictionary before sending the response
        self._send_response(200, {'files': files_info})

    def handle_file_info(self):
        """
        Fetch the modification time of a file.

        This method retrieves and returns the modification time of the specified file.
        If the file does not exist, it returns a 404 error.
        """

        # Extract the filename from the URL by splitting the path and getting the last part
        filename = self.path.split('/')[-1]

        # Create the full file path by joining the synchronized folder path with the filename
        file_path = os.path.join(SYNC_FOLDER, filename)

        # Check if the file exists at the specified path
        if os.path.exists(file_path):

            # Get the file's modification time
            mod_time = os.path.getmtime(file_path)

            self._send_response(200, {'filename': filename, 'mod_time': mod_time})

        else:
            self._send_response(404, {'error': 'File not found'})

    def do_DELETE(self):
        """
        Handle DELETE requests to remove a file from the synchronized folder.

        This method processes file deletion requests. If the file exists, it is deleted.
        If the file is not found, a 404 error is returned.
        """

        # Check if the request path starts with '/delete/' to handle file deletion requests
        if self.path.startswith('/delete/'):

            # Extract the filename from the URL by splitting the path and getting the last part
            filename = self.path.split('/')[-1]

            # Create the full file path by joining the synchronized folder path with the filename
            file_path = os.path.join(SYNC_FOLDER, filename)

            # Check if the file exists at the specified path
            if os.path.exists(file_path):

                # If the file exists, remove it
                os.remove(file_path)

                logging.info(f"Deleted \'{filename}\'")
                self._send_response(200, {'message': f'File \'{filename}\' deleted successfully'})

            else:
                self._send_response(404, {'error': 'File not found'})
