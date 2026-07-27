import os
import time
import socket

SERVER_IP = "69.23.63.226"
SERVER_PORT = 5001

id = 'none'

def check_sudo():
    if os.geteuid() == 0:
        os.system('clear')
        startup()
    else:
        print('Message from PiFax Installer: Please run installer.py as sudo...')
        exit()

def sign_on():
    global client_socket
    os.system('clear')
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"[*] Connecting to {SERVER_IP}:{SERVER_PORT}...")
    client_socket.connect((SERVER_IP, SERVER_PORT))

def get_id():
    global id
    if not os.path.exists("/token/token.txt"):
        with open("/token/token.txt", "w") as file:
            file.write("none")

    with open("/token/token.txt", "r") as file:
        secret_token = file.read().strip()

    if 'none' in secret_token.lower() or not secret_token:
        print('[-] Warning: No existing authentication token found!')
        print('[*] Requesting identity from server...')
        client_socket.sendall(b"GET_ID")

        response = client_socket.recv(64).decode('utf-8')
        assigned_id, new_token = response.split(":", 1)

        id = assigned_id
        with open("/token/token.txt", "w") as file:
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

def startup():
    print("""+=================================PiFax Installer | Rev 1.0=================================+
|Hello, and thank you for choosing PiFax, the modern fax system for Raspberry Pi!           |
+-------------------------------------------------------------------------------------------+
|In this installer I will ask you some questions about getting setup.                       |
+===========================================================================================+
""")
    start = input('Do you wish to start the installer? Y|N: ')
    if start == "Y" or start == "y":
        print('Installing dependancies: CUPS...')
        os.system('sudo apt install cups -y')
        os.system('sudo mkdir /token/ && sudo chmod 777 /token/ && mv ../src/token.txt /token/')
        os.system('sudo mkdir /pifax-python && sudo chmod 777 /pifax-python && mv ../src/client.py /pifax-python/')
        print('Getting a new auth token from server...')
        sign_on()
        get_id()
        user_input()
    else:
        print('Exiting installer, goodbye...')
        exit()

def user_input():
    print('=======================================Systemd Configs=======================================')
    mkesysd = input('Would you like to create a systemd file for fax_checker.py? Y|N: ')
    if mkesysd == "Y" or mkesysd == "y":
        print('Creating service...')
        os.system('touch ../src/pifax.service')
        os.system('echo "[Unit]" >> ../src/pifax.service')
        os.system('echo "Description=PiFax Fax Listener" >> ../src/pifax.service')
        os.system('echo "After=network-online.target" >> ../src/pifax.service')
        os.system('echo "Wants=network-online.target" >> ../src/pifax.service')
        os.system('echo " " >> ../src/pifax.service')
        os.system('echo "[Service]" >> ../src/pifax.service')
        os.system('echo "Type=simple" >> ../src/pifax.service')
        os.system('echo "User=$USER" >> ../src/pifax.service')
        os.system('echo "WorkingDirectory=/pifax-python/" >> ../src/pifax.service')
        os.system('echo "ExecStart=/usr/bin/python3 -u /pifax-python/fax_checker.py" >> ../src/pifax.service')
        os.system('echo "Restart=always" >> ../src/pifax.service')
        os.system('echo "RestartSec=10" >> ../src/pifax.service')
        os.system('echo " " >> ../src/pifax.service')
        os.system('echo "[Install]" >> ../src/pifax.service')
        os.system('echo "WantedBy=multi-user.target" >> ../src/pifax.service')
        os.system('sudo mv ../src/pifax.service /etc/systemd/system/')
        os.system('sudo systemctl daemon-reload')
        os.system('mv ../src/fax_checker.py /pifax-python/')
        enbsysd = input('Would you like to enable this service at startup? Y|N: ')
        if enbsysd == "Y" or enbsysd == "y":
            print('Enabling service...')
            os.system('sudo systemctl enable pifax')
        else:
            pass
        srtsysd = input('Would you like to start this service now? Y|N: ')
        if srtsysd == "Y" or srtsysd == "y":
            print('Starting service now...')
            time.sleep(3)
            os.system('sudo systemctl start pifax')
        else:
            pass
    else:
        pass
    print('=======================================Making Commands=======================================')
    mkecmd = input('Would you like to make any custom commands? Y|N: ')
    if mkecmd == "Y" or mkecmd == "y":
        pfxcmd = input('Would you like to make a PiFax command? Y|N: ')
        if pfxcmd == "Y" or pfxcmd == "y":
            os.system('touch /pifax-python/PiFax')
            os.system('echo "python3 /pifax-python/client.py" > /pifax-python/PiFax')
            os.system('sudo mv /pifax-python/PiFax /usr/local/bin/')
            os.system('sudo chmod 777 /usr/local/bin/PiFax')
        else:
            pass
        adptrcmd = input('Would you like to make an add-printer command? Y|N: ')
        if adptrcmd == "Y" or adptrcmd == "y":
            os.system('touch /pifax-python/add-printer')
            os.system('echo "chromium http://localhost:631/admin" > /pifax-python/add-printer')
            os.system('sudo mv /pifax-python/add-printer /usr/local/bin/')
            os.system('sudo chmod 777 /usr/local/bin/add-printer')
        else:
            pass
    print('=========================================CUPS Config=========================================')
    os.system('cupsctl WebInterface=yes')
    enbcups = input('Would you like to enable CUPS? Y|N: ')
    if enbcups == "Y" or enbcups == "y":
        os.system('sudo systemctl enable cups')
    else:
        pass
    srtcups = input('Would you like to start CUPS? Y|N: ')
    if srtcups == "Y" or srtcups == "y":
        os.system('sudo systemctl start cups')
    else:
        pass
    print('Warning: Systsem will restart...')
    time.sleep(3)
    os.system('sudo reboot now')

if __name__ == '__main__':
    check_sudo()
