# Import external libs
import Gotham_check
import Gotham_choose
import configparser
import sys
import fileinput
import base64
import json
import requests

# Import GOTHAM's libs
from Gotham_SSH_SCP import execute_commands
from Gotham_link_BDD import remove_honeypot_DB, get_honeypot_infos, edit_lhs_DB, edit_link_DB, remove_lhs
from Gotham_normalize import normalize_id_honeypot,normalize_honeypot_infos, normalize_display_object_infos
import add_hp
import add_link

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')



# TO RETRIEVE FROM SECRET FILE !!!
#datacenter_settings = {'hostname':'42.42.42.42', 'ssh_port':22, 'ssh_key':'usidbvyr$pqsi'}
#dc_ip = "172.16.2.250"


def main(DB_settings, datacenter_settings, id):
    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    tag_separator = config['tag']['separator']

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
    if result[0]['link_id'] != None and result[0]['link_id'] != "NULL":
        # Find a honeypot with same tags
        hp_tags=tag_separator.join(result[0]["hp_tags"].split("||"))
        honeypots = Gotham_check.check_tags("hp",get_honeypot_infos(DB_settings, tags=hp_tags), tags_hp=hp_tags)
        # Filter honeypots in error, and original hp by id
        honeypots = [hp for hp in honeypots if not(hp["hp_state"]=='ERROR' or hp["hp_id"]==result[0]["hp_id"])]

        if honeypots!=[]:
            # Choose best honeypots (the lower scored)
            honeypots = Gotham_choose.choose_honeypots(honeypots, 1, hp_tags)

            # Duplicate, and configure
            honeypot=duplicate_hp(DB_settings,honeypots)
            hp_infos=normalize_display_object_infos(result[0],"hp")
            try:
                configure_honeypot_replacement(DB_settings,hp_infos,new_hp_infos=honeypot)
            except:
                sys.exit(1)

            modifs={"id_hp":honeypot["hp_id"]}
            conditions={"id_hp":hp_infos["hp_id"]}
            try:
                edit_lhs_DB(DB_settings,modifs,conditions)
            except:
                sys.exit(1)


        else:
            # if not, just find a honeypot per link
            hp_infos=normalize_display_object_infos(result[0],"hp")
            duplicate_hp_list=[]
            for i in range(len(hp_infos["links"])):
                # Try to replace
                replaced=False
                link=hp_infos["links"][i]
                link_tags_hp=tag_separator.join(link["link_tags_hp"].split("||"))

                # Get all honeypots corresponding to tags
                honeypots = Gotham_check.check_tags("hp",get_honeypot_infos(DB_settings, tags=link_tags_hp), tags_hp=link_tags_hp)

                # Filter honeypots in error, and original hp by id
                honeypots = [hp for hp in honeypots if not(hp["hp_state"]=='ERROR' or hp["hp_id"]==hp_infos["hp_id"])]

                if honeypots!=[]:
                    already_duplicate_weight=int(config['hp_weight']["already_duplicate"])
                    honeypots=[dict(hp, **{'weight':already_duplicate_weight}) if hp["hp_id"] in duplicate_hp_list else hp for hp in honeypots]
                    # Choose best honeypots (the lower scored)
                    honeypots = Gotham_choose.choose_honeypots(honeypots, 1, link_tags_hp)

                    if honeypots[0]["hp_id"] in duplicate_hp_list:
                        # Don't duplicate, just configure
                        honeypot=honeypots[0]
                    else:
                        # Duplicate, and configure
                        honeypot=duplicate_hp(DB_settings,honeypots)
                        duplicate_hp_list.append(honeypot["hp_id"])
                    try:
                        configure_honeypot_replacement(DB_settings,hp_infos,new_hp_infos=honeypot,num_link=i)
                    except:
                        sys.exit(1)
                        
                    modifs={"id_hp":honeypot["hp_id"]}
                    conditions={"id_link":link["link_id"],"id_hp":honeypot["hp_id"]}
                    try:
                        edit_lhs_DB(DB_settings,modifs,conditions)
                    except:
                        sys.exit(1)
                    replaced=True

                # If we can't replace, just edit link to decrease nb hp
                if replaced==False:
                    if int(hp_infos["links"][i]["link_nb_hp"]) > 1:
                        # Configure all server to not redirect on hp
                        try:
                            configure_honeypot_replacement(DB_settings,hp_infos,num_link=i)
                        except:
                            sys.exit(1)

                        try:
                            remove_lhs(DB_settings,id_link=hp_infos["links"][i]["link_id"], id_hp=hp_infos["hp_id"])
                        except:
                            sys.exit(1)
                        try:
                            modifs={"nb_hp":int(hp_infos["links"][i]["link_nb_hp"])-1}
                            conditions={"id":hp_infos["links"][i]["link_id"]}
                            edit_link_DB(DB_settings, modifs, conditions)
                        except:
                            sys.exit(1)
                    else:        
                        # If nb hp=1, error, we can't do nothing
                        logging.error(f"You tried to remove a running honeypot with the id = {id}, and it can't be replaced or deleted")
                        sys.exit(1)


    # Remove the Honeypot from the datacenter
    commands=[f"docker container stop {id}",f"docker container rm {id}", "docker network prune -f"]
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

def configure_honeypot_replacement(DB_settings,old_hp_infos,new_hp_infos={},num_link=None):

    if old_hp_infos!={} and new_hp_infos!={} and num_link==None :
        for link in old_hp_infos["links"]:
            already_update=[]
            servers=[]
            for server in link["servs"]:
                nginxRedirectionPath = "/data/template/"+ str(link["link_id"]) +"-"+str(server["lhs_port"])+".conf"
                if not(nginxRedirectionPath in already_update):
                    with fileinput.FileInput(nginxRedirectionPath, inplace=True, backup='.bak') as file:
                        first_line = False
                        for line in file:
                            if ("  # "+ str(old_hp_infos["hp_id"])) in line:
                                line.replace(str(old_hp_infos["hp_id"]), str(new_hp_infos["hp_id"]))
                                first_line = True
                            elif first_line:
                                line.replace(str(old_hp_infos["hp_port"]), str(new_hp_infos["hp_port"]))
                    already_update.append(nginxRedirectionPath)
                server["choosed_port"]=server["lhs_port"]
                servers.append(server)
            add_link.deploy_nginxConf(DB_settings, link["link_id"], servers)

    elif old_hp_infos!={} and new_hp_infos!={} and num_link!=None :
        already_update=[]
        servers=[]
        for server in old_hp_infos["links"][num_link]["servs"]:
            nginxRedirectionPath = "/data/template/"+ str(old_hp_infos["links"][num_link]["link_id"]) +"-"+str(server["lhs_port"])+".conf"
            if not(nginxRedirectionPath in already_update):
                with fileinput.FileInput(nginxRedirectionPath, inplace=True, backup='.bak') as file:
                    first_line = False
                    for line in file:
                        if ("  # "+ str(old_hp_infos["hp_id"])) in line:
                            line.replace(str(old_hp_infos["hp_id"]), str(new_hp_infos["hp_id"]))
                            first_line = True
                        elif first_line:
                            line.replace(str(old_hp_infos["hp_port"]), str(new_hp_infos["hp_port"]))
                already_update.append(nginxRedirectionPath)
            server["choosed_port"]=server["lhs_port"]
            servers.append(server)
        add_link.deploy_nginxConf(DB_settings, old_hp_infos["links"][num_link]["link_id"], servers)


    elif old_hp_infos!={} and new_hp_infos=={} and num_link!=None :
        already_update=[]
        servers=[]
        for server in old_hp_infos["links"][num_link]["servs"]:
            nginxRedirectionPath = "/data/template/"+ str(old_hp_infos["links"][num_link]["link_id"]) +"-"+str(server["lhs_port"])+".conf"
            if not(nginxRedirectionPath in already_update):
                with fileinput.FileInput(nginxRedirectionPath, inplace=True, backup='.bak') as file:
                    first_line = False
                    for line in file:
                        if ("  # "+ str(old_hp_infos["hp_id"])) in line:
                            line.replace("  # "+ str(old_hp_infos["hp_id"]) +"\n", "")
                            first_line = True
                        elif first_line:
                            line.replace("  server "+ str(datacenter_settings["hostname"]) +":"+ str(old_hp_infos["hp_port"]) +";\n", "")
                already_update.append(nginxRedirectionPath)
            server["choosed_port"]=server["lhs_port"]
            servers.append(server)
        add_link.deploy_nginxConf(DB_settings, old_hp_infos["links"][num_link]["link_id"], servers)
    else:
        logging.error(f"Honeypot replacement configuration failed")
        sys.exit(1)


def duplicate_hp(DB_settings,honeypots):
    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    tag_separator = config['tag']['separator']
    with open(honeypots[0]["hp_source"]+"/Dockerfile", 'r') as file:
        encoded_dockerfile = base64.b64encode(file.read().encode("ascii"))
    name = (honeypots[0]["hp_name"]+"_Duplicat" if len(honeypots[0]["hp_name"]+"_Duplicat")<=128 else honeypots[0]["hp_name"][:(128-len("_Duplicat"))]+"_Duplicat")
    descr = "Duplication of "+honeypots[0]["hp_descr"]
    duplicate_hp_infos={"name": str(name),"descr": str(descr),"tags": str(honeypots[0]["hp_tags"].replace("||",tag_separator)),"logs": str(honeypots[0]["hp_logs"]),"parser": str(honeypots[0]["hp_parser"]),"port": str(honeypots[0]["hp_port"]), "dockerfile": str(encoded_dockerfile.decode("utf-8"))}
    try:
        jsondata = json.dumps(duplicate_hp_infos)
        url = "http://localhost:5000/add/honeypot"
        headers = {'Content-type': 'application/json'}
        r = requests.post(url, data=jsondata, headers=headers)
        id_hp = r.text.split()[2]
    except Exception as e:
        logging.error(f"Error with hp duplication : {honeypots[0]['hp_id']} - "+str(e))
        ssy.exit(1)
    result = get_honeypot_infos(DB_settings, id=id_hp)
    return result[0]
