import socket
import os
import struct

# Network configuration
SERVER_IP = "192.168.1.216"  # Change to your actual server IP address
SERVER_PORT = 5001
BUFFER_SIZE = 4096

id = 'none'

def sign_on():
    global client_socket
    os.system('clear')
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"[*] Connecting to {SERVER_IP}:{SERVER_PORT}...")
    client_socket.connect((SERVER_IP, SERVER_PORT))

def get_id():
    global id
    # Check if we have a secret token saved locally
    if not os.path.exists("token.txt"):
        with open("token.txt", "w") as file:
            file.write("none")

    with open("token.txt", "r") as file:
        secret_token = file.read().strip()

    # If no token exists, register a brand new system identity
    if 'none' in secret_token.lower() or not secret_token:
        print('[-] Warning: No existing authentication token found!')
        print('[*] Requesting identity assets from server...')
        client_socket.sendall(b"GET_ID")
        
        # Expect payload structured as "ID:TOKEN"
        response = client_socket.recv(64).decode('utf-8')
        assigned_id, new_token = response.split(":", 1)
        
        id = assigned_id
        
        # Save secret security key locally
        with open("token.txt", "w") as file:
            file.write(new_token)
            
        print(f'[+] System ID registration complete!')
        print(f'[+] Friendly ID : {id}')
        print(f'[+] Secret Token: {new_token} (Saved to token.txt)')
        
    else:
        print('[*] Secret authentication token located locally.')
        print('[*] Transmitting login key sequence to server...')
        
        # Login using the secure token
        login_message = f"LOGIN:{secret_token}"
        client_socket.sendall(login_message.encode('utf-8'))
        
        # Wait for authentication status evaluation response
        response = client_socket.recv(32).decode('utf-8')
        if response.startswith("AUTH_OK:"):
            _, assigned_id = response.split(":", 1)
            id = assigned_id
            print(f"[+] Login successful! Server assigned your active session profile to ID: {id}")
        else:
            print("[-] Server rejected connection profile authentication token.")
            client_socket.close()
            exit(1)

def user_input(user_id):
    global filename
    print(f"""
PiFax-{user_id}  | Rev 1.1
=============================
Welcome to PiFax, the modern
fax system for Raspberry Pi!
-----------------------------
Please type the file you want
to send below.
*****************************""")
    filename = input("Filename: ")

def send_file(filename):
    if not filename.strip():
        return
        
    if not os.path.exists(filename):
        print("[-] Error: Local file does not exist.")
        return

    filesize = os.path.getsize(filename)
    base_filename = os.path.basename(filename)
    filename_encoded = base_filename.encode('utf-8')
    filename_len = len(filename_encoded)

    try:
        header = struct.pack("!IQ", filename_len, filesize)
        client_socket.sendall(header)
        client_socket.sendall(filename_encoded)

        print(f"[*] Transferring data stream for {base_filename}...")
        with open(filename, "rb") as f:
            while True:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break  
                client_socket.sendall(chunk)
        print("[+] File sent successfully!\n")
    except (socket.error, ConnectionResetError, BrokenPipeError) as e:
        print(f"[-] Connection stream split or closed by host: {e}")
        raise e
    except Exception as e:
        print(f"[-] Error parsing transfer: {e}")

if __name__ == "__main__":
    try:
        sign_on()
        get_id()
        while True:
            user_input(id)
            send_file(filename)
    except KeyboardInterrupt:
        print("\n[-] Shutting down connection safely. Goodbye.")
    finally:
        if 'client_socket' in globals():
            client_socket.close()
