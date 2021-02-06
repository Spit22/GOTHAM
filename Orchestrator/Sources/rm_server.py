from Gotham_SSH_SCP import execute_commands
from Gotham_normalize import normalize_server_infos
from Gotham_link_BDD import get_server_infos, remove_server_DB

import sys

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')

def main(DB_settings, id_server='sv-00000000000000000000000000000000', ip_server='255.255.255.255'):
    # Check id format
    try:
        serv_infos = {'id':id_server, 'ip':ip_server}
        serv_infos = normalize_server_infos(serv_infos)
    except:
        logging.error(f"Can't remove the server : its infos is invalid")
        sys.exit(1)
    # Check if the server exists in the IDB
    if id_server != 'sv-00000000000000000000000000000000':
        result = get_server_infos(DB_settings, id=id_server)
    elif ip_server != '255.255.255.255':
        result = get_server_infos(DB_settings, ip=ip_server)
    else:
        logging.error(f"Remove server failed : no arguments")
        sys.exit(1)
    if result == []:
        logging.error(f"You tried to remove a server that doesn't exists with the id = {id}")
        sys.exit(1)
    # Check if the server is running
    if not(result[0]['link_id'] == None):
        logging.error(f"You tried to remove a running server with the id = {id}")
        sys.exit(1)
    # Remove Server from the server
    try:
        remove_nginx_on_server(result[0]['serv_ip'],result[0]['serv_ssh_port'],result[0]['serv_ssh_key'])
    except:
        sys.exit(1)
    # Remove Server from the IDB
    try:
        remove_server_DB(DB_settings,result[0]['serv_id'])
    except Exception as e:
        logging.error(f"Remove server failed : {e}")
        sys.exit(1)
    return True

def remove_nginx_on_server(hostname,port,ssh_key):
    commands=["sudo rm -r /etc/nginx","sudo rm -r /usr/sbin/nginx","sudo rm -r /usr/lib/nginx/modules","sudo rm -r /etc/nginx/nginx.conf","sudo rm -r /var/log/nginx/error.log", "sudo rm -r /var/log/nginx/access.log", "sudo rm -r /run/nginx.pid","sudo rm -r /var/lock/nginx.lock"]
    try:
        execute_commands(hostname,port,ssh_key,commands)
    except Exception as e:
        logging.error(f"Remove server failed : {e}")
        sys.exit(1)
