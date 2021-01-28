# Import external libs
from io import StringIO
import base64

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


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
    installNginx_file = ["/data/scripts/install_nginx.sh"]
    installNginx_dest = "/tmp/"
    command_exec_install = ["/bin/sh /tmp/install_nginx.sh"]
    
    # On copie et exécute le script d'install nginx sur le serveur
    try:
        send_file_and_execute_commands(ip, ssh_port, used_ssh_key, installNginx_file, installNginx_dest, command_exec_install)
    except Exception as e:
        logging.error(f"Server deployement failed : {e}")
        return False
    return True
