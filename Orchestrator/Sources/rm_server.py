from Gotham_SSH_SCP import execute_commands
from Gotham_normalize import normalize_server_infos, normalize_display_object_infos
from Gotham_link_BDD import get_server_infos, remove_server_DB, edit_lhs_DB, edit_link_DB, remove_lhs

import Gotham_check
import Gotham_choose
import Gotham_replace
import configparser
import sys
import add_link

# Logging components
import os
import logging
from io import StringIO

GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')

def main(DB_settings, id='sv-00000000000000000000000000000000', ip='255.255.255.255'):
    # Check id format
    try:
        serv_infos = {'id':id, 'ip':ip}
        serv_infos = normalize_server_infos(serv_infos)
    except:
        logging.error(f"Can't remove the server : its infos is invalid")
        sys.exit(1)
    # Check if the server exists in the IDB
    if id != 'sv-00000000000000000000000000000000':
        result = get_server_infos(DB_settings, id=id)
    elif ip != '255.255.255.255':
        result = get_server_infos(DB_settings, ip=ip)
    else:
        logging.error(f"Remove server failed : no arguments")
        sys.exit(1)
    if result == []:
        logging.error(f"You tried to remove a server that doesn't exists with the id = {id}")
        sys.exit(1)
    # Check if the server is running
    if result[0]['link_id'] != None and result[0]['link_id'] !="NULL":
        serv_infos=normalize_display_object_infos(result[0],"serv")
        try:
            Gotham_replace.replace_serv_for_rm(DB_settings, datacenter_settings, serv_infos)
        except:
            sys.exit(1)

    # Remove Server from the server
    try:
        remove_nginx_on_server(result[0]['serv_ip'],result[0]['serv_ssh_port'],StringIO(result[0]['serv_ssh_key']))
    except:
        sys.exit(1)
    # Remove Server from the IDB
    try:
        remove_server_DB(DB_settings,result[0]['serv_id'])
    except Exception as e:
        logging.error(f"Remove server failed : {e}")
        sys.exit(1)
    return True

def remove_nginx_on_server(hostname, port, ssh_key):
    commands=["rm -r /etc/nginx","rm -r /usr/sbin/nginx","rm -r /usr/lib/nginx/modules","rm -r /etc/nginx/nginx.conf","rm -r /var/log/nginx/error.log", "rm -r /var/log/nginx/access.log", "rm -r /run/nginx.pid","rm -r /var/lock/nginx.lock"]
    try:
        execute_commands(hostname,port,ssh_key,commands)
    except Exception as e:
        logging.error(f"Remove server failed : {e}")
        sys.exit(1)
