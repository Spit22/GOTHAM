#===Import GOTHAM's libs===#
import Gotham_link_BDD
import Gotham_check
import Gotham_SSH_SCP
import Gotham_replace

from . import state_functions

# Logging components
import json
import base64
import os
import configparser
import mariadb
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')



def adapt_state(DB_settings, obj_id, obj_type, link_id="", check_all=True, replace_auto=True):
    # Set the object state to appropriate status in the Internal Database after some checks
    #
    #
    # DB_settings (json) : auth information
    # obj_id (string) : id of the object
    # obj_type (string) : type of the object ("hp" or "serv")
    # link_id (string) - optional : id of a link that we don't want to consider (not updated in the database) 
    # check_all (boolean) - optional : check all is true, just the used state if false 
    # replace_auto (boolean) - optional : replace automaticaly object with bad state 
    #
    # Raise error if something failed
    # 
    # Return the state

    # Check obj_type
    if obj_type != "hp" and obj_type != "serv":
        error = "Error on object type in adapt_state function"
        logging.error(error)
        raise ValueError(error)

    
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    state_list=config['state'][obj_type+'_state'].split(",")

    # Retrieve datacenter settings from config file
    dc_ip = config['datacenter']['ip']
    dc_ssh_port = int(config['datacenter']['ssh_port'])
    try:
        dc_ssh_key = config['datacenter']['ssh_key']
        dc_ssh_key = base64.b64decode(dc_ssh_key)  # ssh_key is byte
        dc_ssh_key = dc_ssh_key.decode('ascii')  # ssh_key is ascii string
        dc_ssh_key_rsyslog = dc_ssh_key  #  ssh_key for rsyslog
    except Exception as e:
        print("Error loading datacenter's SSH key")
        sys.exit(1)

    # Put datacenter settings in a dictionary
    datacenter_settings = {"hostname": dc_ip, "ssh_key": dc_ssh_key,
                       "rsyslog_ssh_key": dc_ssh_key_rsyslog, "ssh_port": dc_ssh_port}

    # Checking length of states specified in config file
    if len(state_list)<4:
        error = "The config file needs 4 differents states for honeypot and server"
        logging.error(error)
        raise ValueError(error)


    # Get object infos
    if obj_type == "hp":
        object_infos = Gotham_link_BDD.get_honeypot_infos(
            DB_settings, id=str(obj_id))
        # Check if the honyepot exists in the IDB
        if object_infos == []:
            logging.error(
                f"You tried to adapt the state of a honeypot that doesn't exists with the id = {str(obj_id)}")
            error = "Unknown hp id" + str(obj_id)
            raise ValueError(error)
    elif obj_type == "serv":
        object_infos = Gotham_link_BDD.get_server_infos(
            DB_settings, id=str(obj_id))
        # Check if the server exists in the IDB
        if object_infos == []:
            logging.error(
                f"You tried to adapt the state of a server that doesn't exists with the id = {str(obj_id)}")
            error = "Unknown serv id " + str(obj_id)
            raise ValueError(error)

    # Take first dict
    object_infos = object_infos[0] 


    # Initialize variable
    final_state=""

    # Start all test to define appropriate state

    # Check all state, including DOWN and ERROR
    if check_all==True:
        # Check connection to define or not the state to 4th or 3rd of state_list (Default DOWN and ERROR) 
        if obj_type == "hp":
            # check docker liveness
            command='docker inspect --format="{{json .State}}" $(docker ps -a | grep '+object_infos["hp_id"]+' | cut -d " " -f1)'
            try:
                container_state=json.loads(Gotham_SSH_SCP.execute_command_with_return(dc_ip, dc_ssh_port, dc_ssh_key, command)[0][2:-1])
                print("DEBUG1")
                print(container_state)
            except ValueError as e:
                error = "Error while trying to execute ssh command for docker state check on hp (id: "+object_infos["hp_id"]+") : " + str(e)
                logging.error(error)
                raise ValueError(error)
            if str(container_state["OOMKilled"]).lower()=="true":
                final_state=str(state_list[2]).upper()
                logging.debug(
                f"Honeypot with id {str(obj_id)}, container state defined to OOMKilled, set state to {final_state}")
            elif str(container_state["Error"])!="":
                final_state=str(state_list[2]).upper()
                logging.debug(
                f"Honeypot with id {str(obj_id)}, container get some errors, set state to {final_state}")
            elif str(container_state["Restarting"]).lower()=="true":
                final_state=str(state_list[2]).upper()
                logging.debug(
                f"Honeypot with id {str(obj_id)}, container restarting, set state to {final_state}")
            elif str(container_state["Dead"]).lower()=="true":
                final_state=str(state_list[3]).upper()
                logging.debug(
                f"Honeypot with id {str(obj_id)}, container state defined to Dead, set state to {final_state}")
            elif str(container_state["Paused"]).lower()=="true":
                final_state=str(state_list[3]).upper()
                logging.debug(
                f"Honeypot with id {str(obj_id)}, container state defined to Paused, set state to {final_state}")
            elif str(container_state["Running"]).lower()=="true":
                final_state=""
                logging.debug(
                f"Honeypot with id {str(obj_id)}, container is running")
            

        elif obj_type == "serv":
            # Check ssh connection
            try:
                ssh_test=Gotham_check.check_ssh(object_infos["serv_ip"], object_infos["serv_ssh_port"], object_infos["serv_ssh_key"])
            except ValueError as e:
                    error = "Error while trying to execute ssh command for state check on serv (id: "+object_infos["serv_id"]+") : " + str(e)
                    logging.error(error)
                    raise ValueError(error)
            
            # Check ping
            try:
                ping_test=Gotham_check.check_ping(object_infos["serv_ip"])
            except ValueError as e:
                    error = "Error while trying to execute ping command for state check on serv (id: "+object_infos["serv_id"]+") : " + str(e)
                    logging.error(error)
                    raise ValueError(error)

            if ssh_test == False and ping_test == False:
                final_state=str(state_list[3]).upper()
                logging.debug(
                f"Server with id {str(obj_id)}, ssh and ping tests failed, set state to {final_state}")
            elif ssh_test == False:
                final_state=str(state_list[2]).upper()
                logging.debug(
                f"Server with id {str(obj_id)}, ssh test failed, set state to {final_state}")

            if final_state=="":
                # Check if nginx is running
                command='if [ -e /var/run/nginx.pid ]; then echo "OK";else echo "KO"; fi'
                try:
                    nginx_running=Gotham_SSH_SCP.execute_command_with_return(object_infos["serv_ip"], object_infos["serv_ssh_port"], object_infos["serv_ssh_key"], command)
                except ValueError as e:
                    error = "Error while trying to execute ssh command for nginx state check on serv (id: "+object_infos["serv_id"]+") : " + str(e)
                    logging.error(error)
                    raise ValueError(error)
                if nginx_running[0]=="KO":
                    final_state=str(state_list[2]).upper()
                    logging.debug(
                    f"Server with id {str(obj_id)}, test verifying that nginx is running failed, set state to {final_state}")
    
                   
    # If state is still not defined, check links
    if final_state=="":
        if str(object_infos["link_id"])==str(link_id) or str(object_infos["link_id"]) == "NULL":
            final_state=str(state_list[0]).upper()
            logging.debug(
            f"{str(obj_type).capitalize()} with id {str(obj_id)}, no link are using the object, set state to {final_state}")
        else:
            final_state=str(state_list[1]).upper()
            logging.debug(
            f"{str(obj_type).capitalize()} with id {str(obj_id)}, some link are using the object, set state to {final_state}")
        

    # Update the state
    try: 
        state_functions.change_state(DB_settings, object_infos[obj_type+"_id"], obj_type, final_state)
    except Exception as e:
        raise ValueError("Error while set state to "+final_state+" : "+str(e))

    # If replace_auto is set and object state is DOWN or ERROR, try to replace it
    if replace_auto==True and (final_state==str(state_list[2]).upper() or final_state==str(state_list[3]).upper()) and str(object_infos["link_id"]) != "NULL":
        if obj_type == "hp":
            try:
                Gotham_replace.replace_hp_for_rm(DB_settings, datacenter_settings, object_infos)
            except ValueError as e:
                error = "Error while trying to replace honeypot (id: "+object_infos[obj_type+"_id"]+") for bad state: " + str(e)
                logging.error(error)
                raise ValueError(error)

        elif obj_type == "serv":
            try:
                Gotham_replace.replace_serv_for_rm(DB_settings, datacenter_settings, object_infos)
            except ValueError as e:
                error = "Error while trying to replace server (id: "+object_infos[obj_type+"_id"]+") for bad state: " + str(e)
                logging.error(error)
                raise ValueError(error)

    return final_state
