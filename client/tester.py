import os
import time
import logging
from config import LOCAL_FOLDER

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_test_file(folder, filename, content="This is a test file."):
    try:
        file_path = os.path.join(folder, filename)
        with open(file_path, 'w') as f:
            f.write(content)
        logging.info(f"Created file: {file_path}")
    except Exception as e:
        logging.error(f"Could not create file {filename}. Error: {e}")


def modify_test_file(folder, filename, content="\nModified content."):
    try:
        file_path = os.path.join(folder, filename)
        with open(file_path, 'a') as f:
            f.write(content)
        logging.info(f"Modified file: {file_path}")
    except Exception as e:
        logging.error(f"Could not modify file {filename}. Error: {e}")


def rename_test_file(folder, old_filename, new_filename):
    try:
        old_file_path = os.path.join(folder, old_filename)
        new_file_path = os.path.join(folder, new_filename)
        os.rename(old_file_path, new_file_path)
        logging.info(f"Renamed file from {old_file_path} to {new_file_path}")
    except Exception as e:
        logging.error(f"Could not rename file {old_filename} to {new_filename}. Error: {e}")


def delete_test_file(folder, filename):
    try:
        file_path = os.path.join(folder, filename)
        os.remove(file_path)
        logging.info(f"Deleted file: {file_path}")
    except Exception as e:
        logging.error(f"Could not delete file {filename}. Error: {e}")


def create_large_file(folder, filename, size_mb):
    try:
        file_path = os.path.join(folder, filename)
        with open(file_path, 'wb') as f:
            f.write(os.urandom(size_mb * 1024 * 1024))  # Random binary data
        logging.info(f"Created large file: {file_path} ({size_mb} MB)")
    except Exception as e:
        logging.error(f"Could not create large file {filename}. Error: {e}")


def stress_test(folder, file_count=100, sync_wait=5):
    logging.info("Starting Multiple File Stress Test...")
    
    # Create multiple files
    for i in range(file_count):
        create_test_file(folder, f'small_test_file_{i}.txt', content=f"Test content {i}")
    time.sleep(sync_wait)

    # Rename multiple files
    for i in range(file_count):
        rename_test_file(folder, f'small_test_file_{i}.txt', f'renamed_test_file_{i}.txt')
    time.sleep(sync_wait)

    # Modify renamed files
    for i in range(file_count):
        modify_test_file(folder, f'renamed_test_file_{i}.txt', content="\nAdditional test content")
    time.sleep(sync_wait)

    # Delete renamed files
    for i in range(file_count):
        delete_test_file(folder, f'renamed_test_file_{i}.txt')
    time.sleep(sync_wait)

    logging.info("Multiple File Stress Test completed.")


def sync_large_files_test(folder, file_count=5, file_size_mb=50, sync_wait=10):
    logging.info("Starting Large File Sync Test...")

    # Create large files
    for i in range(file_count):
        create_large_file(folder, f'large_test_file_{i}', size_mb=file_size_mb)
    time.sleep(sync_wait)

    # Delete large files
    for i in range(file_count):
        delete_test_file(folder, f'large_test_file_{i}')
    time.sleep(sync_wait)

    logging.info("Large File Sync Test completed.")


if __name__ == "__main__":
    logging.info("Starting tests for file synchronization system...")

    # Stress test with many small files
    stress_test(LOCAL_FOLDER, file_count=100, sync_wait=5)

    # Test synchronization with large files
    sync_large_files_test(LOCAL_FOLDER, file_count=5, file_size_mb=50, sync_wait=10)

    logging.info("All tests completed.")
