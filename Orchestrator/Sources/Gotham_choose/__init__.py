from . import check_SSH
from . import check_PING
from . import check_TAGS
# Import libraries
import configparser
import mariadb
import sys

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')

def choose_honeypots(hps_infos, nb_hp, tags_hp):
    '''
    Choose the best honeypots when creating a link according to the need  

    ARGUMENTS:
        hps_infos (list of dict) : list of potentials honeypots
        nb_hp (int) : number of honeypot wanted
        tags_hp (string) : Honeypot tags mentioned in the link
    '''
    
    return 

