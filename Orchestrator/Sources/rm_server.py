from Gotham_SSH_SCP import execute_commands
from Gotham_normalize import normalize_id_server
from Gotham_link_BDD import get_server_infos, remove_server_DB


# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


def main(DB_settings, id_server, hostname, port, ssh_key):
    # Check id format
    try:
        id_server = normalize_id_server(id_server)
    except:
        logging.error(f"Can't remove the server : its id is invalid")
        return False
    # Check if the server exists in the IDB
    result = get_server_infos(DB_settings, id=id_server)
    if result == []:
        logging.error(f"You tried to remove a server that doesn't exists with the id = {id}")
        return False
    # Check if the server is running
    if not(result[0]['link_id'] == None):
        logging.error(f"You tried to remove a running server with the id = {id}")
        return False
    # Remove Server from the server
    commands=["sudo rm -r /etc/nginx","sudo rm -r /usr/sbin/nginx","sudo rm -r /usr/lib/nginx/modules","sudo rm -r /etc/nginx/nginx.conf","sudo rm -r /var/log/nginx/error.log", "sudo rm -r /var/log/nginx/access.log", "sudo rm -r /run/nginx.pid","sudo rm -r /var/lock/nginx.lock"]
    try:
        execute_commands(hostname,port,ssh_key,commands)
    except Exception as e:
        logging.error(f"Remove server failed : {e}")
        return False
    # Remove Server from the IDB
    try:
        remove_server_DB(DB_settings,id_server)
    except Exception as e:
        logging.error(f"Remove server failed : {e}")
        return False
    return True