# Import external libs
import sys

# Import GOTHAM's libs
from Gotham_SSH_SCP import execute_commands
from Gotham_link_BDD import remove_honeypot_DB, get_honeypot_infos
from Gotham_normalize import normalize_id_honeypot

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')

# TO RETRIEVE FROM SECRET FILE !!!
datacenter_settings = {'hostname':'42.42.42.42', 'ssh_port':22, 'ssh_key':'usidbvyr$pqsi'}

def main(DB_settings, id):
    # Check id format
    try:
        id = normalize_id_honeypot(id)
    except:
        logging.error(f"Can't remove the honeypot : its id is invalid")
        sys.exit(1)
    # Check if the honyepot exists in the IDB
    result = get_honeypot_infos(DB_settings, id=id)
    if result == []:
        logging.error(f"You tried to remove a honeypot that doesn't exists with the id = {id}")
        sys.exit(1)
    # Check if the honeypot is running
    if not(result[0]['link_id'] == None):
        logging.error(f"You tried to remove a running honeypot with the id = {id}")
        sys.exit(1)
    # Remove the Honeypot from the datacenter
    commands=[f"sudo docker container stop {id}",f"sudo docker container rm {id}"]
    try:
        execute_commands(datacenter_settings['hostname'],datacenter_settings['ssh_port'],datacenter_settings['ssh_key'],commands)
    except Exception as e:
        logging.error(f"Remove container failed : {e}")
        sys.exit(1)
    # Remove the Honeypot from the IDB
    try:
        remove_honeypot_DB(DB_settings,id)
    except Exception as e:
        logging.error(f"Remove container failed : {e}")
        sys.exit(1)
    return True