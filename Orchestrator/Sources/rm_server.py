#===Import external libs===#
#==========================#

#===Import GOTHAM's libs===#
from Gotham_SSH_SCP import execute_commands
from Gotham_normalize import normalize_server_infos, normalize_display_object_infos
from Gotham_link_BDD import get_server_infos, remove_server_DB
import Gotham_replace
#==========================#

#===Logging components===#
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
#=======================#


def main(DB_settings, datacenter_settings, id):
    # Execute a server deletion attempt
    #
    # DB_settings (dict) : all authentication information to connect to db
    # datacenter_settings (dict) : all authentication information to connect to datacenter
    # id (string) : id of the server we want to delete
    #
    # Return true if deletion succeed, false in the other case

    # Check id format
    try:
        serv_infos = {'id': id}
        serv_infos = normalize_server_infos(serv_infos)
    except Exception as e:
        logging.error(f"Can't remove the server : its id is invalid")
        raise ValueError(e)

    # Check if the server exists in the IDB

    result = get_server_infos(DB_settings, id=id)
    
    if result == []:
        logging.error(
            f"You tried to remove a server that doesn't exists with the id = {id}")
        raise ValueError(
            "You tried to remove a server that doesn't exists with the id ="+str(id))

    # Check if the server is running
    if result[0]['link_id'] != None and result[0]['link_id'] != "NULL":
        serv_infos = normalize_display_object_infos(result[0], "serv")
        try:
            succes = Gotham_replace.replace_serv_for_rm(
                DB_settings, datacenter_settings, serv_infos)
        except Exception as e:
            raise ValueError(e)

    if succes == True:
        # Remove Server from the server
        try:
            remove_nginx_on_server(
                result[0]['serv_ip'], result[0]['serv_ssh_port'], result[0]['serv_ssh_key'])
        except Exception as e:
            raise ValueError(e)

        # Remove Server from the IDB
        try:
            remove_server_DB(DB_settings, result[0]['serv_id'])
        except Exception as e:
            logging.error(f"Remove server failed : {e}")
            raise ValueError(e)
        return True
    else:
        return False


def remove_nginx_on_server(hostname, port, ssh_key):
    # Reomves nginx items on server
    #
    # hostname (string) : hostname or ip of the server
    # port (int) : ssh port to connect to
    # ssh_key (string) : ssh key to authenticate with

    commands = ["rm -rf /etc/nginx", "rm -r /usr/sbin/nginx", "rm -r /usr/lib/nginx/modules", "rm -r /var/log/nginx/error.log",
                "rm -r /var/log/nginx/access.log", "rm -r /run/nginx.pid", "rm -r /var/lock/nginx.lock"]
    try:
        print("bypassed")
        # execute_commands(hostname,port,ssh_key,commands)
    except Exception as e:
        logging.error(f"Remove server failed : {e}")
        raise ValueError(e)
