import paramiko
import os
import traceback
import sys

def retrieve_all_files(remote_directory, local_directory):
    # SFTP connection details
    host = "149.28.156.48"
    port = 7040
    username = "sftp_user"
    password = "Dusky@2024"

    try:
        # Establish an SFTP connection
        print(f"Connecting to {host}:{port} as {username}...")
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)

        # Ensure the local directory exists, create it if not
        if not os.path.exists(local_directory):
            os.makedirs(local_directory)

        # List files in the remote directory
        print(f"Attempting to list files in: {remote_directory}")
        remote_files = sftp.listdir(remote_directory)

        # Filter and download each file (ZIP and PDF)
        for file in remote_files:
            if file.endswith('.zip') or file.endswith('.pdf'):
                remote_file_path = f"{remote_directory}/{file}"  # Corrected path construction
                local_file_path = os.path.join(local_directory, file)

                # Debugging output for file paths
                print(f"Remote file path: {remote_file_path}")
                print(f"Local file path: {local_file_path}")

                # Download the file
                print(f"Downloading {remote_file_path} to {local_file_path}...")
                sftp.get(remote_file_path, local_file_path)

        sftp.close()
        transport.close()
        print(f"All files retrieved successfully into: {local_directory}")

    except Exception as e:
        print(f"Error retrieving files: {e}")
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    remote_directory = "/002"  # The remote directory containing files
    local_directory = "retrieved_files"  # Folder where files will be saved

    retrieve_all_files(remote_directory, local_directory)
