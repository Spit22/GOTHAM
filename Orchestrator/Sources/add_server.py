# Import external libs
from io import StringIO
import os
import base64

# Import Gotham's libs
from Gotham_SSH_SCP import send_file_and_execute_commands

#Gotham_home = os.environ.get("GOTHAM_HOME")

def deploy(ip, ssh_port, used_ssh_key):
    # Install and deploy an Nginx Reverse-Proxy on a given server
    #
    # ip (string): ip of remote server
    # ssh_port (int) : port the ssh service listen
    # used_ssh_key (file-like object) : ssh key used to connect to server
    #
    # Return True if succeed, False in the other case

    # Declare local vars
    installNginx_file = "/data/scripts/install_nginx.sh"
    installNginx_dest = "/tmp/"
    command_exec_install = ["/bin/sh /tmp/install_nginx.sh"]
    
    # On copie et exécute le script d'install nginx sur le serveur
    try:
        send_file_and_execute_commands(ip, ssh_port, used_ssh_key, installNginx_file, installNginx_dest, command_exec_install)
    except Exception as e:
        return False
    return True
