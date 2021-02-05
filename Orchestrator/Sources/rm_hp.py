from Gotham_SSH_SCP import execute_commands
from Gotham_link_BDD import remove_honeypot_DB, get_honeypot_infos
from Gotham_normalize import normalize_id_honeypot

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


def main(DB_settings, hostname, port, ssh_key, id_container):
    # Check id format
    try:
        id_container = normalize_id_honeypot(id_container)
    except:
        logging.error(f"Can't remove the honeypot : its id is invalid")
        return False
    # Check if the honyepot exists in the IDB
    result = get_honeypot_infos(DB_settings, id=id_container)
    if result == []:
        logging.error(f"You tried to remove a honeypot that doesn't exists with the id = {id}")
        return False
    # Check if the honeypot is running
    if not(result[0]['link_id'] == None):
        logging.error(f"You tried to remove a running honeypot with the id = {id}")
        return False
    # Remove the Honeypot from the datacenter
    commands=[f"sudo docker container stop {id_container}",f"sudo docker container rm {id_container}"]
    try:
        execute_commands(hostname,port,ssh_key,commands)
    except Exception as e:
        logging.error(f"Remove container failed : {e}")
        return False
    # Remove the Honeypot from the IDB
    try:
        remove_honeypot_DB(DB_settings,id_container)
    except Exception as e:
        logging.error(f"Remove container failed : {e}")
        return False
    return True