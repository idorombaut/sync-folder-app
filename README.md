# Synchronized Folder Application

## Overview
This project implements a synchronized folder application using a client-server architecture. It enables automatic file synchronization between a local folder on the client and a centralized server, ensuring that files remain up-to-date across multiple devices.

The application combines polling and event-driven methods for real-time synchronization. It uses HTTP APIs for communication, supporting file upload, download, deletion, and listing.

## Features
- **Automatic file synchronization** between client and server
- **Real-time file monitoring** using `watchdog`
- **Efficient data transfer** with SHA-256 hashing to prevent redundant uploads/downloads
- **Conflict resolution** based on file modification timestamps
- **Secure and lightweight API-based communication** using `requests`
- **Cross-platform support** (Windows, Linux, macOS)

## Architecture
- The client monitors a local folder for file changes and syncs updates with the server via HTTP.
- The server handles file storage, metadata management, and API requests for synchronization.

### Synchronization Mechanism
1. **Event-driven monitoring**: The client detects file changes in real time using `watchdog`.
2. **Polling mechanism**: Periodically checks the server for missing or outdated files.
3. **File integrity verification**: SHA-256 hashes are used to detect modifications.
4. **Conflict resolution**: The latest version of a file (based on timestamps) is retained.

## Libraries Used
- **http.server** – Lightweight server implementation
- **requests** – HTTP client for API communication
- **watchdog** – Real-time file monitoring
- **hashlib** – File integrity verification via SHA-256
- **os & logging** – File operations and debugging

## Installation

### Step 1: Clone the Repository
```
git clone https://github.com/idorombaut/sync-folder-app.git
cd sync-folder-app
```

### Step 2: Set Up a Virtual Environment
1. **Create a Virtual Environment**
   ```
   python -m venv venv
   ```

2. **Activate the Virtual Environment**
   - **Windows**:
     ```
     .\venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```
     source venv/bin/activate
     ```

3. **Install Dependencies**
   ```
   pip install -r requirements.txt
   ```

### Step 3: Set Up Configuration
1. **Client Configuration**
   Open the `config.py` file and configure the following parameters:
   - **SERVER_URL**: Set this to the address of your synchronization server (the server where the files will be stored).
   - **LOCAL_FOLDER**: Set this to the path where the client’s files to be synchronized are stored. This is the directory that the client will monitor for changes.

2. **Server Configuration**
   On the server-side, configure the `config.py` file as follows:
   - **SYNC_FOLDER**: Set this to the directory where files from clients will be uploaded and stored.

### Step 4: Start the Server
```
python server.py
```

### Step 5: Start the Client
```
python client.py
```

## How It Works
1. **File Change Detection**
   - The `watchdog` library detects events such as file creation, modification, or deletion.
   - When a change occurs, the client triggers an appropriate API request to sync with the server.

2. **File Uploads & Downloads**
   - The client computes a SHA-256 hash of files to detect changes.
   - If a file is modified, it is uploaded to the server.
   - If the server has a newer version, the client downloads it.

3. **Polling for Updates**
   - The client periodically checks the server for missing or outdated files and syncs accordingly.
