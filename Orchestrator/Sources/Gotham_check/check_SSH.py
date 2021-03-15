#from gotham_server_communication import main
from Gotham_SSH_SCP import execute_commands
import sys

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


def main(ip, ssh_port, used_ssh_key):
    # Check if the SSH server is operational
    #
    # ip (string) : ip of the remote server
    # ssh_port (int) : port on which the SSH service listen
    # used_ssh_key (file-like object) : Key used to auth to the server
    #
    # Return True if succeed, False in the other case
    command_exec_check = [
        "echo 'alive' > /tmp/gotham_status && rm -rf /tmp/gotham_status"]
    # Try to execute the commands to the remote server
    try:
        execute_commands(ip, ssh_port, used_ssh_key, command_exec_check)
    except Exception as e:
        error = "Can't execute commands on " + str(ip) + " : " + str(e)
        logging.error(error)
        raise ValueError(error)
    # If we were able to execute the commands, return True
    return True
