# -*- coding: utf-8 -*-
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
import rm_hp

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')

# Import Gotham's libs
from Gotham_SSH_SCP import send_file_and_execute_commands

def edit_tags(DB_settings, datacenter_settings, honeypot, tags):

    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    tags_separator = config['tag']['separator']
    
    #port_separator = config['port']['separator']
    #mod_honeypot=honeypot
    
    old_tags=honeypot["hp_tags"].split("||")
    new_tags=tags.split(tags_separator)

    deleted_tags=list(set(old_tags)-set(new_tags))

    dsp_honeypot=Gotham_normalize.normalize_display_object_infos(honeypot,"hp")

    try:
        Gotham_replace.replace_hp_for_deleted_tags(DB_settings, datacenter_settings, dsp_honeypot, deleted_tags)
    except Exception as e:
        raise ValueError(e)