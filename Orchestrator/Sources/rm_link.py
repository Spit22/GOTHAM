# Import external libs
import sys

# Import GOTHAM's libs
from Gotham_SSH_SCP import execute_commands
from Gotham_link_BDD import remove_link_DB, get_link_infos, get_link_serv_hp_infos
from Gotham_normalize import normalize_id_link

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')

def main(DB_settings, id):
    # Check id format
    try:
        id = normalize_id_link(id)
    except:
        logging.error(f"Can't remove the honeypot : its id is invalid")
        sys.exit(1)
    # Check if the link exists in the IDB
    infos = get_link_infos(DB_settings, id=id)
    if infos == []:
        logging.error(f"You tried to remove a honeypot that doesn't exists with the id = {id}")
        sys.exit(1)
    ##### REMOVE LINK ON SERVERS ###
    # List server
    # prendre serv_id dans infos; split avec |||||| ; split avec |||| ; check doublon id -> liste des id des serveurs liés par le link
    # For each servers, list the honeypots linked to it

    # Remove the Link from the IDB
    try:
        remove_link_DB(DB_settings,id)
    except Exception as e:
        logging.error(f"Remove link failed : {e}")
        sys.exit(1)
    return True

def remove_links_on_servers(DB_settings, id):
    # List servers
    infos = get_link_serv_hp_infos(DB_settings, id=id)
    serv_id_concat = infos[0]['serv_id']
    serv_id_list = serv_id_concat.split('||||||')