"""
This module implements a basic HTTP server using Python's built-in 'http.server' module. 
The server listens for incoming HTTP requests on a specified port and handles them using a custom 
request handler class ('RequestHandler').
"""

import logging
from http.server import ThreadingHTTPServer
from handlers import RequestHandler

# Configure logging to capture application logs at the INFO level
logging.basicConfig(level=logging.INFO)


def run(server_class=ThreadingHTTPServer, handler_class=RequestHandler, port=8080):
    """
    Initialize and run the HTTP server with multithreading.
    
    Args:
        server_class (type): The class used for the HTTP server (default: ThreadingHTTPServer).
        handler_class (type): The request handler class to process HTTP requests (default: RequestHandler).
        port (int): The port on which the server will listen for incoming requests (default: 8080).
    """

    # Define the server address: '0.0.0.0' listens on all available network interfaces
    server_address = ('0.0.0.0', port)

    # Create an instance of the HTTP server with the specified address and handler class
    httpd = server_class(server_address, handler_class)

    # Display server startup messages
    print('Starting server on all addresses (0.0.0.0)')
    print(f'Running on http://127.0.0.1:{port}')
    print("Press CTRL+C to quit")

    try:
        # Start the server to handle requests indefinitely
        httpd.serve_forever()
    except KeyboardInterrupt:
        # Handle user interruption (e.g., pressing CTRL+C) gracefully
        print("Server stopped by user")
    finally:
        # Ensure the server socket is closed properly when stopping the server
        httpd.server_close()
        print("Server shutdown complete")


if __name__ == '__main__':
    # Call the 'run' function to start the server
    run()
