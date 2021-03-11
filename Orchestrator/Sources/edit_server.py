#===Import external libs===#
import base64
import sys
import configparser
#==========================#

#===Import GOTHAM's libs===#
import Gotham_link_BDD
import Gotham_check
import Gotham_choose
import Gotham_replace
import Gotham_normalize
import Gotham_SSH_SCP
import add_link
#==========================#

#===Logging components===#
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log', level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
#=======================#

#===Retrieve settings from configuration file===#
config = configparser.ConfigParser()
config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
tags_separator = config['tag']['separator']
ports_separator = config['port']['separator']
#===============================================#

def edit_tags(DB_settings, datacenter_settings, server, tags):

    old_tags=server["serv_tags"].split("||")
    new_tags=tags.split(tags_separator)

    deleted_tags=list(set(old_tags)-set(new_tags))

    dsp_server=Gotham_normalize.normalize_display_object_infos(server,"serv")

    try:
        Gotham_replace.replace_serv_for_deleted_tags(DB_settings, datacenter_settings, dsp_server, deleted_tags)
    except Exception as e:
        raise ValueError(e)


def check_edited_connection(DB_settings, server, ip, ssh_port, ssh_key):

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
