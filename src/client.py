import socket
import os
import struct

# Network configuration
SERVER_IP = "192.168.1.216"  # Change to your actual server IP address
SERVER_PORT = 5001
BUFFER_SIZE = 4096

def send_file(filename):
    if not os.path.exists(filename):
        print("[-] Error: Local file does not exist.")
        return

    filesize = os.path.getsize(filename)
    # Extract only the base name (e.g., 'document.pdf' instead of 'C:/path/document.pdf')
    base_filename = os.path.basename(filename)
    filename_encoded = base_filename.encode('utf-8')
    filename_len = len(filename_encoded)

    # Establish TCP connection
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"[*] Connecting to {SERVER_IP}:{SERVER_PORT}...")
    client_socket.connect((SERVER_IP, SERVER_PORT))

    try:
        # 1. Pack metadata: filename length (4 bytes) + file size (8 bytes)
        # '!IQ' uses network byte order (big-endian)
        header = struct.pack("!IQ", filename_len, filesize)
        client_socket.sendall(header)

        # 2. Send the file name string
        client_socket.sendall(filename_encoded)

        # 3. Open the file in binary mode and send it in chunks
        print(f"[*] Sending {base_filename}...")
        with open(filename, "rb") as f:
            while True:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break  # Reached end of file
                client_socket.sendall(chunk)
                
        print("[+] File sent successfully!")
        
    except Exception as e:
        print(f"[-] Error sending file: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    send_file("test.exe")  # Replace with the path to your file

