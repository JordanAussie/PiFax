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
    if not os.path.exists("token.txt"):
        with open("token.txt", "w") as file:
            file.write("none")

    with open("token.txt", "r") as file:
        secret_token = file.read().strip()

    if 'none' in secret_token.lower() or not secret_token:
        print('[-] Warning: No existing authentication token found!')
        print('[*] Requesting identity from server...')
        client_socket.sendall(b"GET_ID")
        
        response = client_socket.recv(64).decode('utf-8')
        assigned_id, new_token = response.split(":", 1)
        
        id = assigned_id
        with open("token.txt", "w") as file:
            file.write(new_token)
            
        print(f'[+] System registration complete!')
        print(f'[+] Friendly ID : {id}')
    else:
        print('[*] Secret authentication token located locally.')
        login_message = f"LOGIN:{secret_token}"
        client_socket.sendall(login_message.encode('utf-8'))
        
        response = client_socket.recv(32).decode('utf-8')
        if response.startswith("AUTH_OK:"):
            _, assigned_id = response.split(":", 1)
            id = assigned_id
            print(f"[+] Login successful! System ID: {id}")
        else:
            print("[-] Server rejected connection authentication token.")
            client_socket.close()
            exit(1)

def user_input(user_id):
    global filename
    print(f"""
PiFax-{user_id}        Rev 1.1
=============================
Welcome to PiFax, the modern
fax system for Raspberry Pi!
-----------------------------
Please type the file you want
to send below.
*****************************""")
    filename = input("Filename: ")

def send_file(filename):
    if not filename.strip() or not os.path.exists(filename):
        print("[-] Error: Local file does not exist.")
        return

    recipient_id = input("Enter Recipient System ID (XXX-XXXX-XXX): ").strip()
    if not recipient_id:
        print("[-] Transmission canceled. Recipient ID required.")
        return

    filesize = os.path.getsize(filename)
    base_filename = os.path.basename(filename)
    filename_encoded = base_filename.encode('utf-8')
    filename_len = len(filename_encoded)

    try:
        fax_command = f"SEND_FAX:{recipient_id}"
        client_socket.sendall(fax_command.encode('utf-8'))
        
        status = client_socket.recv(16).decode('utf-8')
        if status != "READY":
            print(f"[-] Server rejected transfer setup: {status}")
            return

        header = struct.pack("!IQ", filename_len, filesize)
        client_socket.sendall(header)
        client_socket.sendall(filename_encoded)

        print(f"[*] Transmitting file to {recipient_id}...")
        with open(filename, "rb") as f:
            while True:
                chunk = f.read(BUFFER_SIZE)
                if not chunk:
                    break  
                client_socket.sendall(chunk)
        print("[+] Fax sent successfully!\n")
    except Exception as e:
        print(f"[-] Error sending fax: {e}")

if __name__ == "__main__":
    try:
        sign_on()
        get_id()
        while True:
            user_input(id)
            send_file(filename)
    except KeyboardInterrupt:
        print("\n[-] Exiting PiFax client.")
    finally:
        if 'client_socket' in globals():
            client_socket.close()
