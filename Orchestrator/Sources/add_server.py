#from gotham_server_communication import main
from Gotham_SSH_SCP import send_file, execute_commands
import os

Gotham_home = os.environ.get("GOTHAM_HOME")
print(Gotham_home)

# the data
ip = ""
ssh_port = "22"
ssh_key = ""

def deploy(ip, ssh_port, ssh_key):
    # Déclaration des variables globales
    proxyConfig_file = "/data/template/nginx_rp.conf"
    remote_dest = "/etc/nginx/sites-available/gotham_rp.conf"
    commands = ["nginx -t", "systemctl restart nginx"]
    # Features
    send_file(ip, ssh_port, ssh_key, proxyConfig_file, remote_dest)
    execute_commands(ip, ssh_port, ssh_key, commands)

if __name__ == '__main__':
    main(ip, ssh_port, ssh_key):
