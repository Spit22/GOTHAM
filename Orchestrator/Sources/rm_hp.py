# Import external libs
import Gotham_check
import Gotham_choose
import Gotham_replace
import configparser
import sys
import fileinput
import base64
import json
import requests
from io import StringIO

# Import GOTHAM's libs
from Gotham_SSH_SCP import execute_commands
from Gotham_link_BDD import remove_honeypot_DB, get_honeypot_infos, edit_lhs_DB, edit_link_DB, remove_lhs
from Gotham_normalize import normalize_id_honeypot,normalize_honeypot_infos, normalize_display_object_infos
#import api
import add_link

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')

# TO RETRIEVE FROM SECRET FILE !!!
#datacenter_settings = {'hostname':'42.42.42.42', 'ssh_port':22, 'ssh_key':'usidbvyr$pqsi'}
#dc_ip = "172.16.2.250"

def main(DB_settings, datacenter_settings, id):
    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    tag_separator = config['tag']['separator']

    # Check id format
    try:
        id = normalize_id_honeypot(id)
    except Exception as e:
        error = "Can't remove the honeypot : its id is invalid"
        logging.error(error)
        raise ValueError(error)

    # Check if the honyepot exists in the IDB
    result = get_honeypot_infos(DB_settings, id=id)
    if result == []:
        error = "You tried to remove a honeypot that doesn't exists with the id ="+str(id)
        logging.error(error)
        raise ValueError(error)

    # Check if the honeypot is running
    if result[0]['link_id'] != None and result[0]['link_id'] != "NULL":
        hp_infos=normalize_display_object_infos(result[0],"hp")
        # Try to replace
        try:
            Gotham_replace.replace_hp_for_rm(DB_settings, datacenter_settings, hp_infos)
        except Exception as e:
            raise ValueError(e)

    # Remove the Honeypot from the datacenter
    commands = [f"docker container stop {id}",f"docker container rm {id}", "docker network prune -f"]
    try:
        execute_commands(datacenter_settings['hostname'], datacenter_settings['ssh_port'], StringIO(datacenter_settings['ssh_key']), commands)
    except Exception as e:
        logging.error(f"Remove container failed : {e}")
        raise ValueError(e)
    # Remove the Honeypot from the IDB
    try:
        remove_honeypot_DB(DB_settings, id)
    except Exception as e:
        logging.error(f"Remove container failed : {e}")
        raise ValueError(e)
    return True

######### RSYSLOG SECTION ###########

def remove_rsyslog_configuration(datacenter_settings, id_hp):
    # Vars
    rsyslog_conf_datacenter_local_path = "/rsyslog/datacenter/"
    rsyslog_conf_orchestrator_local_path = "/rsyslog/orchestrator/"
    rsyslog_conf_datacenter_remote_path = "/rsyslog/"
    remote_hp_log_file_path = "TO BE DEFINED"
    local_hp_log_file_path = "/rsyslog/log/"
    local_rulebase_path = "/rsyslog/rulebase/"
    remote_rulebase_path = "/rsyslog/rulebase/"
    # Remove RSYSLOG configuration on the datacenter
    try:
        commands = ["sudo rm " + remote_rulebase_path + ".rb", "sudo rm " + remote_hp_log_file_path + id_hp + ".log", "sudo rm " + rsyslog_conf_datacenter_remote_path + id_hp + ".conf"]
        execute_commands(datacenter_settings["hostname"], datacenter_settings["ssh_port"], StringIO(datacenter_settings["ssh_key"]), commands)
    except Exception as e:
        raise ValueError(e)
    # Remove local RSYSLOG configuration
    try:
        commands = ["sudo rm " + local_rulebase_path + ".rb", "sudo rm " + local_hp_log_file_path + id_hp + ".log", "sudo rm " + rsyslog_conf_datacenter_local_path + id_hp + ".conf", "sudo rm " + rsyslog_conf_orchestrator_local_path + id_hp + ".conf"]
        execute_commands(datacenter_settings["hostname"], datacenter_settings["ssh_port"], StringIO(datacenter_settings["ssh_key"]), commands)
    except Exception as e:
        raise ValueError(e)
