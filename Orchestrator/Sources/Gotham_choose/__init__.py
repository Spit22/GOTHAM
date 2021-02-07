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
    hps_infos=[dict(hp, **{'weight':0}) for hp in hps_infos]
    object_type="hp"

    return 

def choose_servers(servs_infos, nb_serv, tags_serv):
    '''
    Choose the best servers when creating a link according to the need  

    ARGUMENTS:
        servs_infos (list of dict) : list of potentials servers
        nb_serv (int) : number of server wanted
        tags_serv (string) : server tags mentioned in the link
    '''
    
    servs_infos=[dict(serv, **{'weight':0}) for serv in servs_infos]
    object_type="serv"
    
    return 
