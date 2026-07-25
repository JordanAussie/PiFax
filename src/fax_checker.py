import socket
import os
import struct
import time

# Network configuration
SERVER_IP = "192.168.1.216"
SERVER_PORT = 5001
BUFFER_SIZE = 4096

id = 'none'

def connect_and_auth():
    global client_socket, id
    if not os.path.exists("/token/token.txt"):
        print("[-] Error: No token.txt found. Please run client.py first to register.")
        exit(1)
        
    with open("/token/token.txt", "r") as file:
        secret_token = file.read().strip()
        
    if 'none' in secret_token.lower() or not secret_token:
        print("[-] Error: token.txt is empty or invalid. Run client.py first.")
        exit(1)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"[*] [Fax Checker] Connecting to {SERVER_IP}:{SERVER_PORT}...")
    client_socket.connect((SERVER_IP, SERVER_PORT))
    
    # Authenticate via token
    login_message = f"LOGIN:{secret_token}"
    client_socket.sendall(login_message.encode('utf-8'))
    
    response = client_socket.recv(32).decode('utf-8')
    if response.startswith("AUTH_OK:"):
        _, assigned_id = response.split(":", 1)
        id = assigned_id
        print(f"[+] [Fax Checker] Authenticated successfully as ID: {id}")
    else:
        print("[-] [Fax Checker] Server rejected authentication token.")
        client_socket.close()
        exit(1)

def check_for_faxes():
    try:
        # Send check command to the server
        client_socket.sendall(b"CHECK_FAX")
        
        # Server will reply with "NO_FAX" or a metadata header if a fax exists
        status_or_header = client_socket.recv(12)
        if not status_or_header:
            return False
            
        if status_or_header.startswith(b"NO_FAX"):
            return True # Connected, but no mail
            
        # If it wasn't NO_FAX, it's our 12-byte structural metadata header
        filename_len, filesize = struct.unpack("!IQ", status_or_header)
        
        # Read filename string
        filename_bytes = client_socket.recv(filename_len)
        filename = filename_bytes.decode('utf-8')
        
        print(f"\n[+] Incoming fax detected: '{filename}' ({filesize} bytes)")
        
        # Stream the fax data down from the server
        save_filename = f"downloaded_{filename}"
        bytes_received = 0
        with open(f"/pifax-python/{save_filename}", "wb") as f:
            while bytes_received < filesize:
                remaining = filesize - bytes_received
                chunk_to_read = min(BUFFER_SIZE, remaining)
                chunk = client_socket.recv(chunk_to_read)
                if not chunk:
                    break
                f.write(chunk)
                bytes_received += len(chunk)
                
        print(f"[+] Fax saved locally as: {save_filename}\n")
        print("[+] Printing fax now...")
        os.system(f'lp /pifax-python/downloaded_{filename}')
        time.sleep(5)
        os.system(f'rm /pifax-python/downloaded_{filename}')
        return True
        
    except (socket.error, ConnectionResetError, BrokenPipeError):
        print("[-] Connection lost to server. Attempting reconnect...")
        return False

if __name__ == "__main__":
    try:
        connect_and_auth()
        while True:
            success = check_for_faxes()
            if not success:
                # Give it a moment before trying to re-establish broken socket
                time.sleep(5)
                try:
                    connect_and_auth()
                except Exception:
                    pass
            time.sleep(3) # Polling interval: Check for new files every 3 seconds
    except KeyboardInterrupt:
        print("\n[-] Shutting down Fax Checker background utility.")
    finally:
        if 'client_socket' in globals():
            client_socket.close()
