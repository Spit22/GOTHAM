#from gotham_server_communication import main
from Gotham_SSH_SCP import send_file, execute_commands
import os

Gotham_home = os.environ.get("GOTHAM_HOME")
print(Gotham_home)

# the data
hostname = "192.168.1.38"
port = "22"
username = "rev"
ssh_key_path = Gotham_home+"/Orchestrator/Safe/test_key"
file_path = Gotham_home+"/Orchestrator/NGINX_scripts/blabla"
remote_file_path = "/home/rev"
commands = ["echo 'coucou' > /home/rev/coucou.txt","cat coucou.txt"]

if __name__ == '__main__':
    send_file(hostname, port, username, ssh_key_path, file_path, remote_file_path)
    execute_commands(hostname, port, username, ssh_key_path, commands)