
import Gotham_replace
import configparser

from Gotham_SSH_SCP import execute_commands
from Gotham_link_BDD import remove_honeypot_DB, get_honeypot_infos
from Gotham_normalize import normalize_id_honeypot, normalize_display_object_infos


# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')

# Retrieve settings from configuration file
config = configparser.ConfigParser()
config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
tag_separator = config['tag']['separator']


def main(DB_settings, datacenter_settings, id):
    '''
    Execute the deletion attempt

    ARGUMENTS:
        DB_settings (dict) : all authentication information to connect to db
        datacenter_settings (dict) : all authentication information to
            connect to datacenter
        id (string) : id of the honeypot we want to delete

    Return true if deletion succeed, false in the other case
    '''

    # Check id format
    try:
        id = normalize_id_honeypot(id)
    except Exception:
        error = "Can't remove the honeypot : its id is invalid"
        logging.error(error)
        raise ValueError(error)

    # Check if the honyepot exists in the IDB
    result = get_honeypot_infos(DB_settings, id=id)
    if result == []:
        error = "You tried to remove a honeypot that doesn't exists with the id =" + \
            str(id)
        logging.error(error)
        raise ValueError(error)

    # Check if the honeypot is running
    if result[0]['link_id'] is not None and result[0]['link_id'] != "NULL":
        hp_infos = normalize_display_object_infos(result[0], "hp")
        # Try to replace
        try:
            succes = Gotham_replace.replace_hp_for_rm(
                DB_settings,
                datacenter_settings,
                hp_infos
            )
        except Exception as e:
            raise ValueError(e)

    if succes:
        # Remove the Honeypot from the datacenter
        commands = [f"docker container stop {id}",
                    f"docker container rm {id}", "docker network prune -f"]
        try:
            execute_commands(
                datacenter_settings['hostname'],
                datacenter_settings['ssh_port'],
                datacenter_settings['ssh_key'],
                commands
            )
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
    else:
        return False


def remove_rsyslog_configuration(datacenter_settings, id_hp):
    '''
    Delete the rsyslog configuration of the honeypot on datacenter

    ARGUMENTS:
        datacenter_settings (dict) : all authentication information
            to connect to datacenter
        id_hp (string) : id of the honeypot we are trying to
            delete configuration
    '''

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
        commands = ["rm " + remote_rulebase_path + ".rb", "rm " +
                    remote_hp_log_file_path + id_hp + ".log", "rm " +
                    rsyslog_conf_datacenter_remote_path + id_hp + ".conf"]
        execute_commands(
            datacenter_settings["hostname"],
            datacenter_settings["ssh_port"],
            datacenter_settings["ssh_key"],
            commands
        )
    except Exception as e:
        raise ValueError(e)
    # Remove local RSYSLOG configuration
    try:
        commands = ["rm " + local_rulebase_path + ".rb", "rm " +
                    local_hp_log_file_path + id_hp + ".log", "rm " +
                    rsyslog_conf_datacenter_local_path + id_hp +
                    ".conf", "rm " + rsyslog_conf_orchestrator_local_path +
                    id_hp + ".conf"]
        execute_commands(
            datacenter_settings["hostname"],
            datacenter_settings["ssh_port"],
            datacenter_settings["ssh_key"],
            commands
        )
    except Exception as e:
        raise ValueError(e)
