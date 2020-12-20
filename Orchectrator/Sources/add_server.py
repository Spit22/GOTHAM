#from gotham_server_communication import main
from Gotham_SSH_SCP import send_file, execute_commands

# the data
hostname = "192.168.1.38"
port = "22"
username = "rev"
password = "pass"
file_path = "/home/spitfire/test.txt"
remote_file_path = "/home/rev"
commands = ["echo 'coucou' > /home/rev/coucou.txt","cat coucou.txt"]

if __name__ == '__main__':
    send_file(hostname, port, username, password, file_path, remote_file_path)
    execute_commands(hostname, port, username, password, commands)