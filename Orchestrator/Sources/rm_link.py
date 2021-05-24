#===Import external libs===#
import subprocess
#==========================#

#===Import GOTHAM's libs===#
import Gotham_state
from Gotham_SSH_SCP import execute_commands
from Gotham_link_BDD import remove_link_DB, get_link_serv_hp_infos
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
    # Execute a link deletion attemps
    #
    # DB_settings (dict) : all authentication information to connect to db
    # id (string) : id of the link we are trying to delete
    #
    # Return true if deletion succeed, false in the other case

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
        obj_linked=remove_links_on_servers(DB_settings, result[0])
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
    
    for id_obj, type_obj in obj_linked.items():
        try:
            # Update state of objext
            Gotham_state.adapt_state(DB_settings, id_obj, type_obj)
        except Exception as e:
            logging.error(
                    "Error while configuring server state : "+str(e))
    return True


def remove_links_on_servers(DB_settings, result):
    # Delete link on nginx configuration of each server
    #
    # DB_settings (dict) : all authentication information to connect to db
    # result ?

    try:
        lk_display = normalize_display_object_infos(result, "link", "serv")
    except Exception as e:
        error = "Display object failed : " + str(e)
        logging.error(error)
        raise ValueError(error)
    servs = lk_display['servs']
    # Save linked object
    obj_linked={}

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
            remove_rsyslog_configuration(serv_dico, result['link_id'])
        except Exception as e:
            error = str(result['link_id']) + \
                " removal on servers failed : " + str(e)
            logging.error(error)
            raise ValueError(error)
        obj_linked[serv_dico["serv_id"]]="serv"
        for hp_dico in serv_dico["hps"]:
            obj_linked[hp_dico["hp_id"]]="hp"

    return obj_linked


def remove_rsyslog_configuration(server_settings, id_lk):
    # Delete the rsyslog configuration of the link on the given server
    #
    # datacenter_settings (dict) : all authentication information to connect to datacenter
    # id_hp (string) : id of the honeypot we are trying to delete configuration

    # Vars
    rsyslog_conf_server_local_path = "/data/rsyslog/servers-configuration/" + str(id_lk) + ".conf"
    rsyslog_conf_orchestrator_local_path = "/etc/rsyslog.d/" + str(id_lk) + ".conf"
    rsyslog_conf_server_remote_path = "/etc/rsyslog.d/" + str(id_lk) + ".conf"
    local_lk_log_file_path = "/data/link-log/" + str(id_lk) + ".conf"
    remote_lk_log_file_path = "/var/log/nginx/" + str(id_lk) + ".log"

    # Remove RSYSLOG configuration on the remote server
    try:
        commands = ["rm " + rsyslog_conf_server_remote_path, "rm " + remote_lk_log_file_path]
        execute_commands(
            server_settings["serv_ip"], server_settings["serv_ssh_port"], server_settings["serv_ssh_key"], commands)
    except Exception as e:
        raise ValueError(e)
    # Remove local RSYSLOG configuration
    try:
        for fileToDelete in [rsyslog_conf_server_local_path, rsyslog_conf_orchestrator_local_path, local_lk_log_file_path]:
            os.remove(fileToDelete)
    except Exception as e:
        raise ValueError(e)