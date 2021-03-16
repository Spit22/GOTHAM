#===Import external libs===#
import configparser
#==========================#

#===Import GOTHAM's libs===#
import Gotham_check
import Gotham_replace
import Gotham_normalize
#==========================#

#===Logging components===#
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
#=======================#

#===Retrieve settings from configuration file===#
config = configparser.ConfigParser()
config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
tags_separator = config['tag']['separator']
ports_separator = config['port']['separator']
#===============================================#


def edit_tags(DB_settings, datacenter_settings, server, tags):
    # Edit server's tags
    #
    # DB_settings (dict) : all authentication information to connect to db
    # datacenter_settings (dict): all authentication information to connect to datacenter
    # server (dict) : server information
    # tags (string) : new server's tags

    old_tags = server["serv_tags"].split("||")
    new_tags = tags.split(tags_separator)

    deleted_tags = list(set(old_tags)-set(new_tags))

    dsp_server = Gotham_normalize.normalize_display_object_infos(
        server, "serv")

    try:
        Gotham_replace.replace_serv_for_deleted_tags(
            DB_settings, datacenter_settings, dsp_server, deleted_tags)
    except Exception as e:
        raise ValueError(e)


def check_edited_connection(DB_settings, server, ip, ssh_port, ssh_key):
    # Check if we can connect to the server with given informations
    #
    # DB_settings (dict) : all authentication information to connect to db
    # server (dict) : server information
    # ip (string) : new ip we have to check
    # ssh_port (int) : new ssh port we have to check
    # ssh_key (string) : new ssh key we have to check

    if server["serv_ip"] != ip:
        # First check the ip not already exists in database
        exists = Gotham_check.check_doublon_server(DB_settings, ip)
        if exists:
            error = "Provided ip already exists in database"
            logging.error(error)
            raise ValueError(error)

    # Check given auth information are ok
    connected = Gotham_check.check_ssh(ip, ssh_port, ssh_key)
    if not connected:
        error = "Provided ssh_key or ssh_port is wrong"
        logging.error(error)
        raise ValueError(error)

    return
