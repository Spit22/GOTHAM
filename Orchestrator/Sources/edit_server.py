# Import external libs
from io import StringIO
import base64
import sys
import configparser

# GOTHAM'S LIB
import Gotham_link_BDD
import Gotham_check
import Gotham_choose
import Gotham_replace
import Gotham_normalize
import Gotham_SSH_SCP
import add_link

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


def edit_tags(DB_settings, server, tags):

    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    tags_separator = config['tag']['separator']
    port_separator = config['port']['separator']

    old_tags=server["serv_tags"].split("||")
    new_tags=tags.split(tags_separator)

    deleted_tags=list(set(old_tags)-set(new_tags))

    dsp_server=Gotham_normalize.normalize_display_object_infos(server,"serv")

    try:
        Gotham_replace.replace_serv_for_deleted_tags(DB_settings, datacenter_settings, dsp_server, deleted_tags)
    except:
        sys.exit(1)


def edit_connection(DB_settings, server, ip, ssh_port, ssh_key):

    # First check the ip not already exists in database
    exists = Gotham_check.check_doublon_server(DB_settings, ip)
    if exists:
        logging.error(f"Provided ip already exists in database")
        sys.exit(1)

    # Check given auth information are ok
    connected = Gotham_check.check_ssh(ip, ssh_port, ssh_key) 
    if not connected:
        logging.error(f"Provided ssh_key or ssh_port is wrong")
        sys.exit(1)

    return