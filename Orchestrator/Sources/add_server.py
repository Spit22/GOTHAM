#from gotham_server_communication import main
from Gotham_SSH_SCP import send_file, execute_commands
import os

Gotham_home = os.environ.get("GOTHAM_HOME")
print(Gotham_home)

# the data
#hostname = "192.168.1.38"
#port = "22"
#username = "rev"
#ssh_key = "INSERT KEY HERE"
#file_path = Gotham_home+"/Orchestrator/NGINX_scripts/blabla"
#remote_file_path = "/home/rev"
#commands = ["echo 'coucou' > /home/rev/coucou.txt","cat coucou.txt"]

def deploy(ip, ssh_port, ssh_key, proxyConfig_file, remote_dest):
    send_file(ip, ssh_port, ssh_key, proxyConfig_file, remote_dest)
    execute_commands(ip, ssh_port, ssh_key, commands)

if __name__ == '__main__':
    main(ip, ssh_port, ssh_key, proxyConfig_file, remote_dest):
