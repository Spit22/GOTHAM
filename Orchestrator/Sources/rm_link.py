from Gotham_SSH_SCP import execute_commands
from Gotham_link_BDD import remove_link_DB, get_link_infos
from Gotham_normalize import normalize_id_link

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')

def main(DB_settings, hostname, port, ssh_key, id_link):
    # Check id format
    try:
        id_link = normalize_id_link(id_link)
    except:
        logging.error(f"Can't remove the honeypot : its id is invalid")
        return False
    # Check if the link exists in the IDB
    result = get_link_infos(DB_settings, id=id_link)
    if result == []:
        logging.error(f"You tried to remove a honeypot that doesn't exists with the id = {id}")
        return False
    ##### REMOVE LINK ON SERVERS ###
    # Remove the Link from the IDB
    try:
        remove_link_DB(DB_settings,id_link)
    except Exception as e:
        logging.error(f"Remove link failed : {e}")
        return False
    return True