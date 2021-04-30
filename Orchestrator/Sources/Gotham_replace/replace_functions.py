# GOTHAM'S LIB
import Gotham_link_BDD
import Gotham_SSH_SCP
import Gotham_normalize
import Gotham_check
import Gotham_choose
import Gotham_state
import add_link

# Logging components
import configparser
import fileinput
import base64
import json
import requests
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


def replace_honeypot_all_link(DB_settings, datacenter_settings, hp_infos):
    # Try to replace the honeypot for all of its links by only one honeypot
    #
    #
    # DB_settings (json) : auth information
    # datacenter_settings (json) : datacenter auth information
    # hp_infos (dict) : honeypot information subject to replacement 
    #
    # Return True if the honeypot has been replaced, return false otherwise

    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    # Retrieve tag separator in config file
    tag_separator = config['tag']['separator']
    # Retrieve State list
    state_list = config['state']['hp_state'].split(",")
    
    if len(state_list)<4:
        error = "The config file needs 4 differents states for honeypot and server"
        logging.error(error)
        raise ValueError(error)

    
    # Format honeypot tags to be separate by the tag separator
    hp_tags = tag_separator.join(hp_infos["hp_tags"].split("||"))
    
    try:
        # Find a honeypot with same tags
        honeypots = Gotham_check.check_tags("hp", Gotham_link_BDD.get_honeypot_infos(
            DB_settings, tags=hp_tags), tags_hp=hp_tags)
    except Exception as e:
        raise ValueError("Error while checking tags : "+str(e))
    
     # update state
    try:
        honeypots = [Gotham_state.adapt_state(DB_settings,
            honeypot["hp_id"], "hp") for honeypot in honeypots]
    except Exception as e:
        logging.error(
            "Error while configuring honeypot state : "+str(e))

    # Filter honeypots in error, and original hp by id
    honeypots = [hp for hp in honeypots if not(
        hp["hp_state"] == str(state_list[2]).upper() or hp["hp_state"] == str(state_list[3]).upper() or hp["hp_id"] == hp_infos["hp_id"])]
    # If at least one honeypot matches
    if honeypots != []:
        # Choose best honeypots (the lower scored)
        honeypots = Gotham_choose.choose_honeypots(honeypots, 1, hp_tags)
        # Duplicate the honeypot to avoid overload
        honeypot = duplicate_hp(DB_settings, honeypots[0])
        try:
            # Configure servers to replace old honeypot by the new one
            configure_honeypot_replacement(
                DB_settings, datacenter_settings, hp_infos, new_hp_infos=honeypot)
        except Exception as e:
            raise ValueError(
                "Error while configuring honeypot replacement : "+str(e))

        # Prepare Database modification
        # Define the modifications in Internal Database
        modifs = {"id_hp": honeypot["hp_id"]}
        # Define the conditions of  modifications in Internal Database
        conditions = {"id_hp": hp_infos["hp_id"]}
        
        try:
            # Edit the Link_Hp_Serv table in Internal Database
            Gotham_link_BDD.edit_lhs_DB(DB_settings, modifs, conditions)
        except Exception as e:
            raise ValueError("Error while editing link hp server : "+str(e))
        
        try:
            # Update state of new honeypot
            Gotham_state.adapt_state(DB_settings, honeypot["hp_id"], "hp")
        except Exception as e:
            logging.error(
                "Error while configuring honeypot state : "+str(e))
        
        try:
            # Update state of old honeypot
            Gotham_state.adapt_state(DB_settings, hp_infos["hp_id"], "hp")
        except Exception as e:
            logging.error(
                "Error while configuring honeypot state : "+str(e))
        
        return True

    return False


def replace_honeypot_in_link(DB_settings, datacenter_settings, hp_infos, link, duplicate_hp_list=[], new_tags=""):
    # Try to replace the honeypot for a link by another honeypot
    #
    #
    # DB_settings (json) : auth information
    # datacenter_settings (json) : datacenter auth information
    # hp_infos (dict) : honeypot information subject to replacement 
    # link (dict) : link information subject of the replacement 
    # duplicate_hp_list (list) - optional : list of honeypot that have been already duplicated for the replacement of this honeypot
    # new_tags (string) - optional : list of new honeypot tag for the link
    #
    # Return a dict : "replaced" is a boolean set to true if the honeypot has been replaced, false otherwise ; "duplicate_hp_list" is a list of honeypot that have been duplicated for the replacement of this honeypot
    
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    # Retrieve tag separator in config file
    tag_separator = config['tag']['separator']
    # Retrieve State list
    state_list = config['state']['hp_state'].split(",")
    
    if len(state_list)<4:
        error = "The config file needs 4 differents states for honeypot and server"
        logging.error(error)
        raise ValueError(error)

    
    # Variable declaration and initialisation
    replaced = False

    # Define link honeypot tags either by the new ones if they exist, or by taking those defined in the information of the link and fomat them to be separate by the tag separator
    link_tags_hp = tag_separator.join(
        link["link_tags_hp"].split("||")) if new_tags == "" else new_tags
    
    # Get all honeypots corresponding to tags
    try:
        honeypots = Gotham_check.check_tags("hp", Gotham_link_BDD.get_honeypot_infos(
            DB_settings, tags=link_tags_hp), tags_hp=link_tags_hp)
    except Exception as e:
        raise ValueError("Error while checking tags : "+str(e))
    
     # update state
    try:
        honeypots = [Gotham_state.adapt_state(DB_settings,
            honeypot["hp_id"], "hp") for honeypot in honeypots]
    except Exception as e:
        logging.error(
            "Error while configuring honeypot state : "+str(e))

    
    # Filter honeypots in error, and original hp by id
    honeypots = [hp for hp in honeypots if not(
        hp["hp_state"] == str(state_list[2]).upper() or hp["hp_state"] == str(state_list[3]).upper() or hp["hp_id"] == hp_infos["hp_id"])]
    
    # If at least one honeypot matches
    if honeypots != []:
        # Retrieve weight for duplicate honeypot in config file
        already_duplicate_weight = int(
            config['hp_weight']["already_duplicate"])
        # Favor already duplicated honeypots to replace this honeypot in other links by reducing a customizable weight 
        honeypots = [dict(hp, **{'weight': already_duplicate_weight})
                     if hp["hp_id"] in duplicate_hp_list else hp for hp in honeypots]
        # Choose best honeypots (the lower scored)
        honeypots = Gotham_choose.choose_honeypots(honeypots, 1, link_tags_hp)
        # If already duplicate or no link configured, just edit the link to redirect to the hp
        if (honeypots[0]["hp_id"] in duplicate_hp_list or honeypots[0]["hp_state"] == str(state_list[0]).upper()) and link["link_id"] not in honeypots[0]["link_id"]:
            # Don't duplicate
            honeypot = honeypots[0]
        else:
            # Duplicate the honeypot to avoid overload
            honeypot = duplicate_hp(DB_settings, honeypots[0])
            # Add it to the list of duplicate honeypots 
            duplicate_hp_list.append(honeypot["hp_id"])
        try:
            # Configure servers to replace old honeypot by the new one
            configure_honeypot_replacement(
                DB_settings, datacenter_settings, hp_infos, new_hp_infos=honeypot, link=link)
        except Exception as e:
            raise ValueError(e)

        # Prepare Database modification
        # Define the modifications in Internal Database
        modifs = {"id_hp": honeypot["hp_id"]}
        # Define the conditions of  modifications in Internal Database
        conditions = {"id_link": link["link_id"], "id_hp": hp_infos["hp_id"]}
        try:
            # Edit the Link_Hp_Serv table in Internal Database
            Gotham_link_BDD.edit_lhs_DB(DB_settings, modifs, conditions)
        except Exception as e:
            raise ValueError(e)
        
        try:
            # Update state of new honeypot
            Gotham_state.adapt_state(DB_settings, honeypot["hp_id"], "hp")
        except Exception as e:
            logging.error(
                "Error while configuring honeypot state : "+str(e))
        
        try:
            # Update state of old honeypot
            Gotham_state.adapt_state(DB_settings, hp_infos["hp_id"], "hp")
        except Exception as e:
            logging.error(
                "Error while configuring honeypot state : "+str(e))
        
        replaced = True

    return {"replaced": replaced, "duplicate_hp_list": duplicate_hp_list}


def decrease_link(DB_settings, datacenter_settings, object_infos, link, type_obj):
    # Try to decrease the object (honeypot or server) number specified un a link
    #
    #
    # DB_settings (json) : auth information
    # datacenter_settings (json) : datacenter auth information
    # object_infos (dict) : object information subject to removal
    # link (dict) : link information subject to decrease
    # type_obj (string) : "hp" or "serv", specify the type of object requiring decrease 
    #
    # Raise error if something failed

    # Check type_obj
    if type_obj != "hp" and type_obj != "serv":
        error = "Error on type object"
        logging.error(error)
        raise ValueError(error)
    
    # Check that the number of objects is greater than 1 and can therefore be decrease 
    if int(link["link_nb_"+type_obj]) > 1:
        if type_obj == "hp":
            try:
                # Configure all server to not redirect on hp
                configure_honeypot_replacement(
                    DB_settings, datacenter_settings, object_infos, link=link)
            except Exception as e:
                raise ValueError(e)
        try:
            if type_obj == "hp":
                # Remove the combinaison Hp-Link in the Link_Hp_Serv table in Internal Database
                Gotham_link_BDD.remove_lhs(
                    DB_settings, id_link=link["link_id"], id_hp=object_infos["hp_id"])
            elif type_obj == "serv":
                # Remove the combinaison Serv-Link in the Link_Hp_Serv table in Internal Database
                Gotham_link_BDD.remove_lhs(
                    DB_settings, id_link=link["link_id"], id_serv=object_infos["serv_id"])
        except Exception as e:
            raise ValueError(e)
        try:
            # Prepare Database modification
            # Define the modifications in Internal Database : decrease the object number in the link
            modifs = {"nb_"+type_obj: int(link["link_nb_"+type_obj])-1}
            # Define the conditions of  modifications in Internal Database
            conditions = {"id": link["link_id"]}
            # Edit the Link table in Internal Database
            Gotham_link_BDD.edit_link_DB(DB_settings, modifs, conditions)
        except Exception as e:
            raise ValueError(e)
        try:
            # Update state of object
            Gotham_state.adapt_state(DB_settings, object_infos[type_obj+"_id"], type_obj)
        except Exception as e:
            logging.error(
                "Error while adapt object state : "+str(e))
        return True
    else:
        # If nb=1, error, we can't do nothing, just raise an error
        error = "You tried to remove a running "+str(type_obj)+" with the id ="+str(
            object_infos[type_obj+"_id"])+", and it can't be replaced or deleted"
        logging.error(error)
        return False


def configure_honeypot_replacement(DB_settings, datacenter_settings, old_hp_infos, new_hp_infos={}, link=None):
    # Configure servers to remove or replace by new one, the old honeypot for one link or for all, by modifying the Nginx conf
    #
    #
    # DB_settings (json) : auth information
    # datacenter_settings (json) : datacenter auth information
    # old_hp_infos (dict) : old honeypot information subject to removal or replacement
    # new_hp_infos (dict) - optional : new honeypot information for replacement
    # link (dict) - optional : link information subject to reconfiguration
    #
    # Raise error if something failed   


    # Configure servers to replace by new one, the old honeypot for all of its link
    if old_hp_infos != {} and new_hp_infos != {} and link == None:
        # Loop through all of the links using the old hp  
        for link in old_hp_infos["links"]:
            # Variable declaration and initialisation to save servers and the already modified configs  
            already_update = []
            servers = []
            # Loop through all of the servers used by the link  
            for server in link["servs"]:
                # Find the path of the configuration used by the server for the link 
                nginxRedirectionPath = "/data/template/" + \
                    str(link["link_id"]) + "-" + \
                    str(server["lhs_port"]) + ".conf"
                # If the configuration has not already been modified 
                if not(nginxRedirectionPath in already_update):
                    # Modify the nginx conf to replace the old honeypot by the new one
                    with fileinput.FileInput(nginxRedirectionPath, inplace=True, backup='.bak') as file:
                        first_line = False
                        for line in file:
                            if ("  # " + str(old_hp_infos["hp_id"])) in line:
                                print(line.replace(str(old_hp_infos["hp_id"]), str(
                                    new_hp_infos["hp_id"])), end='')
                                first_line = True
                            elif first_line:
                                print(line.replace(str(old_hp_infos["hp_port"]), str(
                                    new_hp_infos["hp_port"])), end='')
                                first_line = False
                            else:
                                print(line, end='')
                    # Add the config to the list of already updated configs
                    already_update.append(nginxRedirectionPath)
                # Prepare the deploiment of nginx config
                server["choosed_port"] = server["lhs_port"]
                servers.append(server)
            # Deploy the new Nginx config
            add_link.deploy_nginxConf(DB_settings, link["link_id"], servers)
    
    # Configure servers to replace by new one, the old honeypot for one of its link
    elif old_hp_infos != {} and new_hp_infos != {} and link != None:
        # Variable declaration and initialisation to save servers and the already modified configs  
        already_update = []
        servers = []

        # Finds the information of the servers used for the link, either directly in the link, or in the information of the old honeypot 
        interable_servs = link["servs"] if "servs" in link.keys() else old_hp_infos["servs"]
        
        # Loop through all of the servers used by the link  
        for server in interable_servs:
            # Find the path of the configuration used by the server for the link 
            nginxRedirectionPath = "/data/template/" + \
                str(link["link_id"]) + "-"+str(server["lhs_port"]) + ".conf"
            # If the configuration has not already been modified 
            if not(nginxRedirectionPath in already_update):
                # Modify the nginx conf to replace the old honeypot by the new one
                with fileinput.FileInput(nginxRedirectionPath, inplace=True, backup='.bak') as file:
                    first_line = False
                    for line in file:
                        if ("  # " + str(old_hp_infos["hp_id"])) in line:
                            print(line.replace(str(old_hp_infos["hp_id"]), str(
                                new_hp_infos["hp_id"])), end='')
                            first_line = True
                        elif first_line:
                            print(line.replace(str(old_hp_infos["hp_port"]), str(
                                new_hp_infos["hp_port"])), end='')
                            first_line = False
                        else:
                            print(line, end='')
                # Add the config to the list of already updated configs
                already_update.append(nginxRedirectionPath)
            # Prepare the deploiment of nginx config
            server["choosed_port"] = server["lhs_port"]
            servers.append(server)
        # Deploy the new Nginx config
        add_link.deploy_nginxConf(DB_settings, link["link_id"], servers)
    
    # Configure servers to remove the old honeypot for one of its link
    elif old_hp_infos != {} and new_hp_infos == {} and link != None:
        # Variable declaration and initialisation to save servers and the already modified configs  
        already_update = []
        servers = []

        # Finds the information of the servers used for the link, either directly in the link, or in the information of the old honeypot 
        interable_servs = link["servs"] if "servs" in link.keys() else old_hp_infos["servs"]

        # Loop through all of the servers used by the link  
        for server in interable_servs:
            # Find the path of the configuration used by the server for the link 
            nginxRedirectionPath = "/data/template/" + \
                str(link["link_id"]) + "-"+str(server["lhs_port"]) + ".conf"
            # If the configuration has not already been modified 
            if not(nginxRedirectionPath in already_update):
                # Modify the nginx conf to remove the old honeypot
                with fileinput.FileInput(nginxRedirectionPath, inplace=True, backup='.bak') as file:
                    first_line = False
                    for line in file:
                        if ("  # " + str(old_hp_infos["hp_id"])) in line:
                            print(line.replace(
                                "  # " + str(old_hp_infos["hp_id"]) + "\n", ""), end='')
                            first_line = True
                        elif first_line:
                            print(line.replace("  server " + str(datacenter_settings["hostname"]) + ":" + str(
                                old_hp_infos["hp_port"]) + ";\n", ""), end='')
                            first_line = False
                        else:
                            print(line, end='')
                # Add the config to the list of already updated configs
                already_update.append(nginxRedirectionPath)
            # Prepare the deploiment of nginx config
            server["choosed_port"] = server["lhs_port"]
            servers.append(server)
        # Deploy the new Nginx config
        add_link.deploy_nginxConf(DB_settings, link["link_id"], servers)
    
    # If we are not in one of the previous cases, the call to the function and/or the passing of the arguments are not correct, 
    # Then raise an error 
    else:
        error = "Honeypot replacement configuration failed"
        logging.error(error)
        raise ValueError(error)


def duplicate_hp(DB_settings, honeypot_infos):
    # Duplicate a honeypot by an api call
    #
    #
    # DB_settings (json) : auth information
    # honeypot_infos (dict) : honeypot information subject to duplication
    #
    # Return result[0] (dict) : duplicate honeypot information
    

    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    # Retrieve tag separator in config file
    tag_separator = config['tag']['separator']

    # Retrieving the dockerfile of the honeypot subject to duplication
    with open(honeypot_infos["hp_source"] + "/Dockerfile", 'r') as file:
        # Encoding the dockerfile (Base64)
        encoded_dockerfile = base64.b64encode(file.read().encode("ascii"))

    # Prepare the name of the new honeypot
    name = (honeypot_infos["hp_name"]+"_Duplicat" if len(honeypot_infos["hp_name"]+"_Duplicat")
            <= 128 else honeypot_infos["hp_name"][:(128-len("_Duplicat"))]+"_Duplicat")
    # Prepare the description of the new honeypot
    descr = "Duplication of " + honeypot_infos["hp_descr"]
    # Prepare information of the new honeypot as a dict
    duplicate_hp_infos = {"name": str(name), "descr": str(descr), "tags": str(honeypot_infos["hp_tags"].replace("||", tag_separator)), "logs": str(
        honeypot_infos["hp_logs"]), "parser": str(honeypot_infos["hp_parser"]), "port": str(honeypot_infos["hp_port"]), "dockerfile": str(encoded_dockerfile.decode("utf-8")), "duplicat":1}
    
    # Send all information to the api for duplication
    try:
        jsondata = json.dumps(duplicate_hp_infos)
        url = "http://localhost:5000/add/honeypot"
        headers = {'Content-type': 'application/json'}
        r = requests.post(url, data=jsondata, headers=headers)
        jsonresponse = r.json()
        id_hp = jsonresponse["id"]
    except Exception as e:
        error = "Error with hp duplication :" + \
            str(honeypot_infos['hp_id'])+" - "+str(e)
        logging.error(error)
        raise ValueError(error)

    # Get all information of the new honeypot
    result = Gotham_link_BDD.get_honeypot_infos(DB_settings, id=id_hp)
    # Return duplicate honeypot information
    return result[0]


def replace_server_in_link(DB_settings, serv_infos, link, new_tags="", already_used=[]):
    # Try to replace the server for a link by another server
    #
    #
    # DB_settings (json) : auth information
    # serv_infos (dict) : server information subject to replacement 
    # link (dict) : link information subject of the replacement 
    # new_tags (string) - optional : list of new server tag for the link
    # already_used (list) - optional : list of server that have been already used for the replacement of this server
    #
    # Return either a boolean : set to true if the server has been replaced, false otherwise
    #               or a list : list of servers used for remplacement in the link
    
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    # Retrieve tag separator in config file
    tag_separator = config['tag']['separator']
    # Retrieve port separator in config file
    port_separator = config['port']['separator']
    # Retrieve tag separator in config file
    tag_separator = config['tag']['separator']
    # Retrieve State list
    state_list = config['state']['serv_state'].split(",")
    
    if len(state_list)<4:
        error = "The config file needs 4 differents states for honeypot and server"
        logging.error(error)
        raise ValueError(error)


    # Define link servers tags either by the new ones if they exist, or by taking those defined in the information of the link and fomat them to be separate by the tag separator
    link_tags_serv = tag_separator.join(
        link["link_tags_serv"].split("||")) if new_tags == "" else new_tags

    # Get all servers corresponding to tags
    servers = Gotham_check.check_tags("serv", Gotham_link_BDD.get_server_infos(
        DB_settings, tags=link_tags_serv), tags_serv=link_tags_serv)

    try:
        # Update state of server
        servers = [Gotham_state.adapt_state(DB_settings, server["serv_id"], "serv") for server in servers]
    except Exception as e:
        logging.error(
            "Error while configuring server state : "+str(e))

    # Filter servers in those who have one of ports open
    servers = Gotham_check.check_servers_ports_matching(
        servers, link["link_ports"])

   
    # Filter servers in error, with same link, and original server by id
    servers = [server for server in servers if not(
        server["serv_state"] == str(state_list[2]).upper() or server["serv_state"] == str(state_list[3]).upper() or link["link_id"] in server["link_id"] or server["serv_id"] in already_used or server["serv_id"] == serv_infos["serv_id"])]
    
    # If there is not even a matching server, just return false 
    if servers == []:
        return False

    # Find ports used by server, by going through the list of honeypots linked to the server, either in the link or in the server information 
    if "hps" in link.keys():
        ports_used_ls = [hp["lhs_port"] for hp in link["hps"]]
    elif "hps" in serv_infos.keys():
        ports_used_ls = [hp["lhs_port"] for hp in serv_infos["hps"]]
    # If no list of honeypot is found, raise an error 
    else:
        error = "Hp not found in objects keys"
        logging.error(error)
        raise ValueError(error)

    # Get a list of unique ports used 
    ports_used_ls = list(set(ports_used_ls))

    # Find a server in the previous selection with all of ports used by the old one free
    servers_same_port = [server for server in servers if all(
        port in server["free_ports"].split(port_separator) for port in ports_used_ls)]

    # If at least one server matching
    if servers_same_port != []:
        # Choose the best
        replacement_server = Gotham_choose.choose_servers(
            servers_same_port, 1, link_tags_serv)

        # Variable declaration and initialisation to save configs which has already been modified and deployed  
        already_deployed = []

        # If honeypots information are in the link information
        if "hps" in link.keys():
            # Loop through all of the honeypots used by the link  
            for hp in link["hps"]:
                # If the nginx config for this port has'nt been already deployed
                if not(int(hp["lhs_port"]) in already_deployed):
                    replacement_server[0]["choosed_port"] = int(hp["lhs_port"])
                    # Deploy the nginx config
                    add_link.deploy_nginxConf(
                        DB_settings, link["link_id"], replacement_server)
                    # Add the exposure port in the concerned variable
                    already_deployed.append(
                        int(replacement_server[0]["choosed_port"]))
                
                # Prepare Database modification
                # Define the modifications in Internal Database : edit the server id in the link
                modifs = {"id_serv": replacement_server[0]["serv_id"]}
                # Define the conditions of  modifications in Internal Database
                conditions = {
                    "id_link": link["link_id"], "id_hp": hp["hp_id"], "id_serv": serv_infos["serv_id"]}
                try:
                    # Edit the Link_Hp_Serv table in Internal Database
                    Gotham_link_BDD.edit_lhs_DB(
                        DB_settings, modifs, conditions)
                except Exception as e:
                    raise ValueError(e)



        # If honeypots information are in the server information
        elif "hps" in serv_infos.keys():
            # Loop through all of the honeypots used by the link  
            for hp in serv_infos["hps"]:
                # If the nginx config for this port has'nt been already deployed
                if not(int(hp["lhs_port"]) in already_deployed):
                    replacement_server[0]["choosed_port"] = int(hp["lhs_port"])
                    # Deploy the nginx config
                    add_link.deploy_nginxConf(
                        DB_settings, link["link_id"], replacement_server)
                    # Add the exposure port in the concerned variable
                    already_deployed.append(
                        int(replacement_server[0]["choosed_port"]))
                
                # Prepare Database modification
                # Define the modifications in Internal Database : edit the server id in the link
                modifs = {"id_serv": replacement_server[0]["serv_id"]}
                # Define the conditions of  modifications in Internal Database
                conditions = {
                    "id_link": link["link_id"], "id_hp": hp["hp_id"], "id_serv": serv_infos["serv_id"]}
                try:
                    # Edit the Link_Hp_Serv table in Internal Database
                    Gotham_link_BDD.edit_lhs_DB(
                        DB_settings, modifs, conditions)
                except Exception as e:
                    raise ValueError(e)
        
        # If we are not in one of the previous cases, the call to the function and/or the passing of the arguments are not correct, 
        # Then raise an error 
        else:
            error = "Hp not found in objects keys"
            logging.error(error)
            raise ValueError(error)

        try:
            # Update state of old server
            Gotham_state.adapt_state(DB_settings, serv_infos["serv_id"], "serv")
        except Exception as e:
            logging.error(
                "Error while configuring server state : "+str(e))
        
        try:
            # Update state of new server
            Gotham_state.adapt_state(DB_settings, replacement_server[0]["serv_id"], "serv")
        except Exception as e:
            logging.error(
                "Error while configuring server state : "+str(e))


        # If the optional variable is not used
        if already_used == []:
            return True
        # If the optional variable is used
        else:
            # Add the new server to concerned variable and return
            already_used.append(replacement_server[0]["serv_id"])
            return already_used

    # If all the honeypots do not use the same exposure ports on the same server 
    else:
        print("Not implemented")
        return False


def distribute_servers_on_link_ports(DB_settings, link):
    # distribution function allowing fair use of the possible ports of the link on the servers 
    #
    #
    # DB_settings (json) : auth information
    # link (dict) : link information subject of the redistribution 
    #
    # Raise an error if something failed
    
    # Retrieve settings from config file    
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    # Retrieve tag separator in config file
    tag_separator = config['tag']['separator']
    
    # Variable declaration and initialisation
    is_possible = True
    # Iterable browsing the list in common way
    i = 0
    # Iterable browsing the list in reverse way
    j = 1

    # Variable for infinite loop prevent
    cpt=0
    
    # As long as we can equalize the number of servers using the same port on all the ports specified by the link 
    while is_possible and cpt<100:
        cpt+=1
        # Update link information
        links = Gotham_link_BDD.get_link_serv_hp_infos(
            DB_settings, id=link["link_id"])
        # Formalizes the classification of information 
        dsp_link = Gotham_normalize.normalize_display_object_infos(
            links[0], "link", "serv")

        # Variable to count the occurrence of exposure ports declaration and initialisation
        count_exposed_ports = {
            str(key): 0 for key in dsp_link["link_ports"].split(tag_separator)}
        
        # Loop through all of the servers used by the link  
        for server in dsp_link["servs"]:
            # Get all exposed ports by looping through
            exposed_ports = [hp["lhs_port"] for hp in server["hps"]]
            # Eliminate duplicates
            exposed_ports_unique = list(dict.fromkeys(exposed_ports))

            # If all honeypots are exposed on same port
            if len(exposed_ports_unique) == 1:
                # Count servers using each port
                count_exposed_ports[str(exposed_ports_unique[0])] = 0 if str(
                    exposed_ports_unique[0]) not in count_exposed_ports.keys() else count_exposed_ports[str(exposed_ports_unique[0])]+1
            # If all the honeypots do not use the same exposure ports on the same server 
            else:
                error = "Not implemented"
                logging.error(error)
                raise ValueError(error)
        
        # Variable declaration and initialisation
        servers = []

        # Get all honeypots used by links
        honeypots = [{key: value for key, value in hp.items() if key != "lhs_port"}
                     for serv in dsp_link["servs"] for hp in serv["hps"]]
        # Remove duplicates
        honeypots = [dict(tuple_of_hp_items) for tuple_of_hp_items in {
            tuple(hp.items()) for hp in honeypots}]

        # Sort exposed ports from most used to least used 
        ports_sorted = sorted(count_exposed_ports,
                              key=count_exposed_ports.get, reverse=True)
        # Get one of the most used port
        port_max_used = str(ports_sorted[i])
        # Get one of the least used port
        port_min_used = str(ports_sorted[-j])

        # If both ports selected are not the same
        if port_max_used != port_min_used:
            # Loop through all servers used by the link
            for server in dsp_link["servs"]:
                # Get exposure ports by looping through honeypots
                exposed_ports = [hp["lhs_port"] for hp in server["hps"]]
                # Remove duplicates
                exposed_ports_unique = list(dict.fromkeys(exposed_ports))
                
                # If all honeypots are exposed on the same port
                if len(exposed_ports_unique) == 1:
                    # If the port used is the max port selected
                    if str(exposed_ports_unique[0]) == port_max_used:
                        # Get server information
                        servs = Gotham_link_BDD.get_server_infos(
                            DB_settings, id=server["serv_id"])
                        # Add it to the list
                        servers.append(servs[0])
                
                # If all the honeypots do not use the same exposure ports on the same server 
                else:
                    # Feature : multi port on multi honeypots (today : only HA)
                    error = "Not implemented"
                    logging.error(error)
                    raise ValueError(error)
            
            # Select servers which have the least used port free
            servers = Gotham_check.check_servers_ports_matching(
                servers, port_min_used)
            
            # If some servers match and the selected max port is at least used on two more servers than the least used port 
            if servers != [] and count_exposed_ports[str(port_max_used)]-count_exposed_ports[str(port_min_used)] > 1:
                # Take the first server
                servers = [servers[0]]

                # Replace the nginx config to expose the min port selected instead of the max port selected
                try:
                    # Remove the nginx conf for the max port selected
                    commands = ["rm /etc/nginx/conf.d/links/" + dsp_link["link_id"] +
                                "-*.conf", "/usr/sbin/nginx -t && /usr/sbin/nginx -s reload"]
                    Gotham_SSH_SCP.execute_commands(
                        servers[0]["serv_ip"], servers[0]["serv_ssh_port"], servers[0]["serv_ssh_key"], commands)
                    # Apply modification in Internal Database
                    Gotham_link_BDD.remove_lhs(
                        DB_settings, id_link=dsp_link["link_id"], id_serv=servers[0]["serv_id"])
                except Exception as e:
                    error = str(dsp_link['link_id']) + \
                        " removal on servers failed : "+str(e)
                    logging.error(error)
                    raise ValueError(error)

                # Prepare deployment
                servers[0]["choosed_port"] = port_min_used
                # Deploy new reverse-proxies's configurations on servers
                add_link.deploy_nginxConf(
                    DB_settings, dsp_link["link_id"], servers)

                # Loop through concerned honeypots to update Internal Database
                for honeypot in honeypots:
                    # Create lhs_infos
                    lhs_infos = {"id_link": dsp_link["link_id"], "id_hp": honeypot["hp_id"],
                                 "id_serv": servers[0]["serv_id"], "port": servers[0]["choosed_port"]}
                    # Normalize infos
                    lhs_infos = Gotham_normalize.normalize_lhs_infos(lhs_infos)
                    # Store new link and tags in the internal database
                    Gotham_link_BDD.add_lhs_DB(DB_settings, lhs_infos)
                
                # Resetting iterable variables to try to redistribute on all ports (in case the previous changes have unlocked other possible changes) 
                i = 0
                j = 1

            # If the next most used port isn't the same that the min port selected, and their difference in terms of number of servers exposing them is greater than 1 
            elif str(ports_sorted[i+1]) != port_min_used and count_exposed_ports[str(ports_sorted[i+1])]-count_exposed_ports[port_min_used] > 1:
                # Use the next most used port for the next loop
                i += 1

            # If the next least used port isn't the same that the max port selected, and their difference in terms of number of servers exposing them is greater than 1 
            elif str(ports_sorted[-(j+1)]) != port_max_used and count_exposed_ports[port_max_used]-count_exposed_ports[str(ports_sorted[-(j+1)])] > 1:
                # Use the next least used port for the next loop
                j += 1

            # Can't equalize more the number of servers using the same port on all the ports specified by the link
            else:
                is_possible = False
        else:
            # Can't equalize more the number of servers using the same port on all the ports specified by the link
            is_possible = False
        
    for server in dsp_link["servs"]:
        for honeypot in server["hps"]:
            try:
                # Update state of hp
                Gotham_state.adapt_state(DB_settings, honeypot["hp_id"], "hp")
            except Exception as e:
                logging.error(
                    "Error while configuring honeypot state : "+str(e))
        try:
            # Update state of server
            Gotham_state.adapt_state(DB_settings, server["serv_id"], "serv")
        except Exception as e:
            logging.error(
                "Error while configuring server state : "+str(e))