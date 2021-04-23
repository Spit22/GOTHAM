# GOTHAM'S LIB
import Gotham_link_BDD

# Logging components
import configparser
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


def change_state(DB_settings, obj_id, obj_type, new_state):
    # Change the object state in the Internal Database
    #
    #
    # DB_settings (json) : auth information
    # obj_id (string) : id of the object
    # obj_type (string) : type of the object ("hp" or "serv")
    # new_state (string) : new state of the object (need to be in the config file)
    #
    # Raise error if something failed

    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    
    # Check obj_type
    if obj_type != "hp" and obj_type != "serv":
        error = "Error on object type in set_to_healthy function"
        logging.error(error)
        raise ValueError(error)

    modifs = {"state": new_state.upper()}
    conditions = {"id": obj_id}
    
    if obj_type == "serv":
        state_list=config['state']['serv_state'].split(",")
        if modifs["state"] in state_list:      
            try:
                Gotham_link_BDD.edit_server_DB(DB_settings, modifs, conditions)
            except Exception as e:
                raise ValueError("Error while set server (id: "+obj_id+") state to "+ modifs["state"]+" : "+str(e))
        else:
            raise ValueError(modifs["state"]+" is not defined in the config file for server")
    elif obj_type == "hp":
        state_list=config['state']['hp_state'].split(",")
        if modifs["state"] in state_list:
            try:
                Gotham_link_BDD.edit_honeypot_DB(DB_settings, modifs, conditions)
            except Exception as e:
                raise ValueError("Error while set honeypot (id: "+obj_id+") state to "+ modifs["state"]+" : "+str(e))
        else:
            raise ValueError(modifs["state"]+" is not defined in the config file for honeypot")


