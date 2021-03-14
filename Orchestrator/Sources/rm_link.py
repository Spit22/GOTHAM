#===Import external libs===#
import subprocess
#==========================#

#===Import GOTHAM's libs===#
from Gotham_SSH_SCP import execute_commands
from Gotham_link_BDD import remove_link_DB, get_link_infos, get_link_serv_hp_infos
from Gotham_normalize import normalize_id_link, normalize_display_object_infos
#==========================#

#===Logging components===#
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
#=======================#


def main(DB_settings, id):
    # Check id format
    try:
        id = normalize_id_link(id)
    except Exception as e:
        error = "Can't remove the link : " + str(e)
        logging.error(error)
        raise ValueError(error)
    # Check if the link exists in the IDB
    result = get_link_serv_hp_infos(DB_settings, id=id)
    if result == []:
        error = "You tried to remove a link that doesn't exists with the id = " + \
            str(id)
        logging.error(error)
        raise ValueError(error)
    # Remove link on the servers affected by the link
    try:
        remove_links_on_servers(DB_settings, result[0])
    except Exception as e:
        raise ValueError(e)
    # Remove NGINX file of the link on the Orchestrator
    try:
        subprocess.check_call(["rm /data/template/"+str(id)+"*"], shell=True,
                              stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except Exception as e:
        error = "Remove NGINX scripts of link failed : " + str(e)
        logging.error(error)
        raise ValueError(error)
    # Remove the Link from the IDB
    try:
        remove_link_DB(DB_settings, id)
    except Exception as e:
        error = "Remove link failed : " + str(e)
        logging.error(error)
        raise ValueError(error)
    return True


def remove_links_on_servers(DB_settings, result):
    try:
        lk_display = normalize_display_object_infos(result, "link", "serv")
    except Exception as e:
        error = "Display object failed : " + str(e)
        logging.error(error)
        raise ValueError(error)
    servs = lk_display['servs']
    # For each servers
    for serv_dico in servs:
        # Delete the configuration file of the link we want to delete
        hostname = serv_dico['serv_ip']
        port = serv_dico['serv_ssh_port']
        ssh_key = serv_dico['serv_ssh_key']
        try:
            commands = ["rm /etc/nginx/conf.d/links/" +
                        result['link_id'] + "-*.conf", "nginx -s reload"]
            execute_commands(hostname, port, ssh_key, commands)
        except Exception as e:
            error = str(result['link_id']) + \
                " removal on servers failed : " + str(e)
            logging.error(error)
            raise ValueError(error)
