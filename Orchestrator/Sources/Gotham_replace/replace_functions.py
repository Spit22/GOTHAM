import sys
import re
import configparser
import os
import fileinput
import base64
import json
import requests

from Gotham_normalize import normalize_id_honeypot,normalize_honeypot_infos,normalize_server_infos, normalize_display_object_infos
#from Gotham_link_BDD import remove_honeypot_DB, get_honeypot_infos, get_server_infos, remove_server_DB, edit_lhs_DB, edit_link_DB, remove_lhs
import Gotham_link_BDD
import Gotham_SSH_SCP
import Gotham_normalize
import Gotham_check
import Gotham_choose
import add_link


# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')



def replace_honeypot_all_link(DB_settings, datacenter_settings, hp_infos):
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    tag_separator = config['tag']['separator']
    # Find a honeypot with same tags
    hp_tags = tag_separator.join(hp_infos["hp_tags"].split("||"))
    try:
        honeypots = Gotham_check.check_tags("hp", Gotham_link_BDD.get_honeypot_infos(DB_settings, tags=hp_tags), tags_hp=hp_tags)
    except Exception as e:
        raise ValueError("Error while checking tags : "+str(e))
    # Filter honeypots in error, and original hp by id
    honeypots = [hp for hp in honeypots if not(hp["hp_state"] == 'ERROR' or hp["hp_id"] == hp_infos["hp_id"])]
    if honeypots!=[]:
        # Choose best honeypots (the lower scored)
        honeypots = Gotham_choose.choose_honeypots(honeypots, 1, hp_tags)
        # Duplicate, and configure
        honeypot = duplicate_hp(DB_settings, honeypots[0])
        try:
            configure_honeypot_replacement(DB_settings, datacenter_settings, hp_infos, new_hp_infos = honeypot)
        except Exception as e:
            raise ValueError("Error while configuring honeypot replacement : "+str(e))

        modifs={"id_hp":honeypot["hp_id"]}
        conditions={"id_hp":hp_infos["hp_id"]}
        try:
            Gotham_link_BDD.edit_lhs_DB(DB_settings, modifs, conditions)
        except Exception as e:
            raise ValueError("Error while editing link hp server : "+str(e))
        return True
    
    return False


def replace_honeypot_in_link(DB_settings, datacenter_settings, hp_infos, link, duplicate_hp_list=[], new_tags=""):
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    tag_separator = config['tag']['separator']
    # Try to replace
    replaced = False
    link_tags_hp = tag_separator.join(link["link_tags_hp"].split("||")) if new_tags=="" else new_tags
    # Get all honeypots corresponding to tags
    honeypots = Gotham_check.check_tags("hp", Gotham_link_BDD.get_honeypot_infos(DB_settings, tags = link_tags_hp), tags_hp = link_tags_hp)
    # Filter honeypots in error, and original hp by id
    honeypots = [hp for hp in honeypots if not(hp["hp_state"] == 'ERROR' or hp["hp_id"] == hp_infos["hp_id"])]
    if honeypots != []:
        already_duplicate_weight = int(config['hp_weight']["already_duplicate"])
        honeypots = [dict(hp, **{'weight':already_duplicate_weight}) if hp["hp_id"] in duplicate_hp_list else hp for hp in honeypots]
        # Choose best honeypots (the lower scored)
        honeypots = Gotham_choose.choose_honeypots(honeypots, 1, link_tags_hp)
        # If already duplicate or no link configured, just edit the link to redirect to the hp
        if (honeypots[0]["hp_id"] in duplicate_hp_list or honeypots[0]["hp_state"] == "UNUSED") and link["link_id"] not in honeypots[0]["link_id"]:
            # Don't duplicate, just configure
            honeypot = honeypots[0]
        else:
            # Duplicate, and configure
            honeypot = duplicate_hp(DB_settings, honeypots[0])
            duplicate_hp_list.append(honeypot["hp_id"])
        try:
            configure_honeypot_replacement(DB_settings, datacenter_settings, hp_infos, new_hp_infos = honeypot, link = link)
        except Exception as e:
            raise ValueError(e)
        
        # Edit link hp_serv table, replace old hp by new hp
        modifs = {"id_hp":honeypot["hp_id"]}
        conditions = {"id_link":link["link_id"], "id_hp":hp_infos["hp_id"]}
        try:
            Gotham_link_BDD.edit_lhs_DB(DB_settings, modifs, conditions)
        except Exception as e:
            raise ValueError(e)
        replaced = True

    return {"replaced":replaced, "duplicate_hp_list":duplicate_hp_list}



def decrease_link(DB_settings, datacenter_settings, object_infos, link, type_obj):
    if type_obj != "hp" and type_obj != "serv":
        error = "Error on type object"
        logging.error(error)
        raise ValueError(error)
        
    if int(link["link_nb_"+type_obj]) > 1:
        if type_obj=="hp":
            # Configure all server to not redirect on hp
            try:
                configure_honeypot_replacement(DB_settings, datacenter_settings, object_infos, link = link)
            except Exception as e:
                raise ValueError(e)
        try:
            if type_obj == "hp":
                Gotham_link_BDD.remove_lhs(DB_settings, id_link = link["link_id"], id_hp = object_infos["hp_id"])
            elif type_obj == "serv":
                Gotham_link_BDD.remove_lhs(DB_settings, id_link = link["link_id"], id_serv = object_infos["serv_id"])
        except Exception as e:
            raise ValueError(e)
        try:
            modifs={"nb_"+type_obj:int(link["link_nb_"+type_obj])-1}
            conditions={"id":link["link_id"]}
            Gotham_link_BDD.edit_link_DB(DB_settings, modifs, conditions)
        except Exception as e:
            raise ValueError(e)
    else:        
        # If nb=1, error, we can't do nothing
        error = "You tried to remove a running "+str(type_obj)+" with the id ="+str(object_infos[type_obj+"_id"])+", and it can't be replaced or deleted"
        logging.error(error)
        raise ValueError(error)


def configure_honeypot_replacement(DB_settings, datacenter_settings, old_hp_infos, new_hp_infos = {}, link = None):
    # Edit one hp for all link
    if old_hp_infos != {} and new_hp_infos != {} and link == None :
        for link in old_hp_infos["links"]:
            already_update = []
            servers = []
            for server in link["servs"]:
                nginxRedirectionPath = "/data/template/" + str(link["link_id"]) + "-" + str(server["lhs_port"]) + ".conf"
                if not(nginxRedirectionPath in already_update):
                    with fileinput.FileInput(nginxRedirectionPath, inplace = True, backup = '.bak') as file:
                        first_line = False
                        for line in file:
                            if ("  # " + str(old_hp_infos["hp_id"])) in line:
                                line.replace(str(old_hp_infos["hp_id"]), str(new_hp_infos["hp_id"]))
                                first_line = True
                            elif first_line:
                                line.replace(str(old_hp_infos["hp_port"]), str(new_hp_infos["hp_port"]))
                                first_line = False
                            else:
                                print(line, end='')
                    already_update.append(nginxRedirectionPath)
                server["choosed_port"] = server["lhs_port"]
                servers.append(server)
            add_link.deploy_nginxConf(DB_settings, link["link_id"], servers)
    # Edit one hp for one link
    elif old_hp_infos != {} and new_hp_infos != {} and link != None :
        already_update = []
        servers = []
        interable_servs = link["servs"] if "servs" in link.keys() else old_hp_infos["servs"]
        for server in interable_servs:
            nginxRedirectionPath = "/data/template/" + str(link["link_id"]) + "-"+str(server["lhs_port"]) + ".conf"
            if not(nginxRedirectionPath in already_update):
                with fileinput.FileInput(nginxRedirectionPath, inplace = True, backup = '.bak') as file:
                    first_line = False
                    for line in file:
                        if ("  # " + str(old_hp_infos["hp_id"])) in line:
                            line.replace(str(old_hp_infos["hp_id"]), str(new_hp_infos["hp_id"]))
                            first_line = True
                        elif first_line:
                            line.replace(str(old_hp_infos["hp_port"]), str(new_hp_infos["hp_port"]))
                            first_line = False
                        else:
                            print(line, end='')
                already_update.append(nginxRedirectionPath)
            server["choosed_port"] = server["lhs_port"]
            servers.append(server)
        add_link.deploy_nginxConf(DB_settings, link["link_id"], servers)
    # Delete one hp for one link
    elif old_hp_infos != {} and new_hp_infos == {} and link != None :
        already_update = []
        servers = []
        interable_servs = link["servs"] if "servs" in link.keys() else old_hp_infos["servs"]
        for server in interable_servs:
            nginxRedirectionPath = "/data/template/" + str(link["link_id"]) + "-"+str(server["lhs_port"]) + ".conf"
            if not(nginxRedirectionPath in already_update):
                with fileinput.FileInput(nginxRedirectionPath, inplace = True, backup = '.bak') as file:
                    first_line = False
                    for line in file:
                        if ("  # " + str(old_hp_infos["hp_id"])) in line:
                            line.replace("  # " + str(old_hp_infos["hp_id"]) + "\n", "")
                            first_line = True
                        elif first_line:
                            line.replace("  server " + str(datacenter_settings["hostname"]) + ":" + str(old_hp_infos["hp_port"]) + ";\n", "")
                            first_line = False
                        else:
                            print(line, end='')
                already_update.append(nginxRedirectionPath)
            server["choosed_port"] = server["lhs_port"]
            servers.append(server)
        add_link.deploy_nginxConf(DB_settings, link["link_id"], servers)
    else:
        error = "Honeypot replacement configuration failed"
        logging.error(error)
        raise ValueError(error)

def duplicate_hp(DB_settings,honeypot_infos):
    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    tag_separator = config['tag']['separator']
    with open(honeypot_infos["hp_source"] + "/Dockerfile", 'r') as file:
        encoded_dockerfile = base64.b64encode(file.read().encode("ascii"))
    name = (honeypot_infos["hp_name"]+"_Duplicat" if len(honeypot_infos["hp_name"]+"_Duplicat")<=128 else honeypot_infos["hp_name"][:(128-len("_Duplicat"))]+"_Duplicat")
    descr = "Duplication of " + honeypot_infos["hp_descr"]
    duplicate_hp_infos={"name": str(name),"descr": str(descr),"tags": str(honeypot_infos["hp_tags"].replace("||", tag_separator)),"logs": str(honeypot_infos["hp_logs"]),"parser": str(honeypot_infos["hp_parser"]),"port": str(honeypot_infos["hp_port"]), "dockerfile": str(encoded_dockerfile.decode("utf-8"))}
    try:
        jsondata = json.dumps(duplicate_hp_infos)
        url = "http://localhost:5000/add/honeypot"
        headers = {'Content-type': 'application/json'}
        r = requests.post(url, data=jsondata, headers=headers)
        id_hp = r.text.split()[2]
    except Exception as e:
        error = "Error with hp duplication :"+str(honeypot_infos['hp_id'])+" - "+str(e)
        logging.error(error)
        raise ValueError(error)
    result = Gotham_link_BDD.get_honeypot_infos(DB_settings, id = id_hp)
    return result[0]


def replace_server_in_link(DB_settings,serv_infos,link, new_tags="", already_used=[]):

    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    tag_separator = config['tag']['separator']
    port_separator = config['port']['separator']

    
    link_tags_serv=tag_separator.join(link["link_tags_serv"].split("||")) if new_tags=="" else new_tags

    # Get all servers corresponding to tags
    servers = Gotham_check.check_tags("serv", Gotham_link_BDD.get_server_infos(DB_settings, tags=link_tags_serv), tags_serv=link_tags_serv)

    # Filter servers in those who have one of ports open
    servers = Gotham_check.check_servers_ports_matching(servers, link["link_ports"])

    # Filter servers in error, with same link, and original server by id
    servers = [server for server in servers if not(server["serv_state"]=='ERROR' or link["link_id"] in server["link_id"] or server["serv_id"] in already_used or server["serv_id"]==serv_infos["serv_id"])]
    if servers==[]:
        return False

    if "hps" in link.keys():
        ports_used_ls=[hp["lhs_port"] for hp in link["hps"]]
    elif "hps" in serv_infos.keys():
        ports_used_ls=[hp["lhs_port"] for hp in serv_infos["hps"]]
    else:
        error = "Hp not found in objects keys"
        logging.error(error)
        raise ValueError(error)

    ports_used_ls=list(set(ports_used_ls))

    servers_same_port=[server for server in servers if all(port in server["free_ports"].split(port_separator) for port in ports_used_ls)]

    if servers_same_port!=[]:
        replacement_server=Gotham_choose.choose_servers(servers_same_port, 1, link_tags_serv)

        already_deployed=[]
        if "hps" in link.keys():
            for hp in link["hps"]:
                if not(int(hp["lhs_port"]) in already_deployed):
                    replacement_server[0]["choosed_port"]=int(hp["lhs_port"])
                    add_link.deploy_nginxConf(DB_settings, link["link_id"], replacement_server)
                    already_deployed.append(int(replacement_server[0]["choosed_port"]))
                modifs={"id_serv":replacement_server[0]["serv_id"]}
                conditions={"id_link":link["link_id"],"id_hp":hp["hp_id"],"id_serv":serv_infos["serv_id"]}
                try:
                    Gotham_link_BDD.edit_lhs_DB(DB_settings,modifs,conditions)
                except Exception as e:
                    raise ValueError(e)

        elif "hps" in serv_infos.keys():
            for hp in serv_infos["hps"]:
                if not(int(hp["lhs_port"]) in already_deployed):
                    replacement_server[0]["choosed_port"]=int(hp["lhs_port"])
                    add_link.deploy_nginxConf(DB_settings, link["link_id"], replacement_server)
                    already_deployed.append(int(replacement_server[0]["choosed_port"]))
                modifs={"id_serv":replacement_server[0]["serv_id"]}
                conditions={"id_link":link["link_id"],"id_hp":hp["hp_id"],"id_serv":serv_infos["serv_id"]}
                try:
                    Gotham_link_BDD.edit_lhs_DB(DB_settings,modifs,conditions)
                except Exception as e:
                    raise ValueError(e)
        else:
            error = "Hp not found in objects keys"
            logging.error(error)
            raise ValueError(error)
        
        if already_used==[]:
            return True
        else:
            already_used.append(replacement_server[0]["serv_id"])
            return already_used

    else:
        print("Not implemented")
        return False

def distribute_servers_on_link_ports(DB_settings, link):
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    tag_separator = config['tag']['separator']
    is_possible=True
    i=0
    j=1
    while is_possible:
        links= Gotham_link_BDD.get_link_serv_hp_infos(DB_settings, id=link["link_id"])
        dsp_link=Gotham_normalize.normalize_display_object_infos(links[0],"link","serv")
        count_exposed_ports={str(key):0 for key in dsp_link["link_ports"].split(tag_separator)}
        for server in dsp_link["servs"]:
            exposed_ports=[hp["lhs_port"] for hp in server["hps"]]
            exposed_ports_unique=list(dict.fromkeys(exposed_ports))
            if len(exposed_ports_unique) == 1 :
                count_exposed_ports[str(exposed_ports_unique[0])] = 0 if str(exposed_ports_unique[0]) not in count_exposed_ports.keys() else count_exposed_ports[str(exposed_ports_unique[0])]+1
            else:
                error = "Not implemented"
                logging.error(error)
                raise ValueError(error)
        servers=[]

        # Get all honeypots used by links
        honeypots=[{key:value for key,value in hp.items() if key != "lhs_port"} for serv in dsp_link["servs"] for hp in serv["hps"]]
        # Remove duplicates
        honeypots=[dict(tuple_of_hp_items) for tuple_of_hp_items in {tuple(hp.items()) for hp in honeypots}]

        ports_sorted=sorted(count_exposed_ports, key = count_exposed_ports.get, reverse=True)
        port_max_used=str(ports_sorted[i])
        port_min_used=str(ports_sorted[-j])

        if port_max_used != port_min_used:
            for server in dsp_link["servs"]:
                exposed_ports=[hp["lhs_port"] for hp in server["hps"]]
                exposed_ports_unique=list(dict.fromkeys(exposed_ports))
                if len(exposed_ports_unique) == 1 :
                    if str(exposed_ports_unique[0]) == port_max_used:
                        servs=Gotham_link_BDD.get_server_infos(DB_settings, id=server["serv_id"])
                        servers.append(servs[0])
                else:
                    # Feature : multi port on multi honeypots (today : only HA)
                    error = "Not implemented"
                    logging.error(error)
                    raise ValueError(error)
            servers = Gotham_check.check_servers_ports_matching(servers, port_min_used)
            if servers!=[] and count_exposed_ports[str(port_max_used)]-count_exposed_ports[str(port_min_used)]>1:
                servers=[servers[0]]
            
                try:
                    commands = ["rm /etc/nginx/conf.d/links/" + dsp_link["link_id"] +"-*.conf", "/usr/sbin/nginx -t && /usr/sbin/nginx -s reload"]
                    Gotham_SSH_SCP.execute_commands(servers[0]["serv_ip"], servers[0]["serv_ssh_port"], servers[0]["serv_ssh_key"], commands)
                    Gotham_link_BDD.remove_lhs(DB_settings, id_link = dsp_link["link_id"], id_serv = servers[0]["serv_id"])
                except Exception as e:
                    error = str(dsp_link['link_id'])+" removal on servers failed : "+str(e)
                    logging.error(error)
                    raise ValueError(error)

                servers[0]["choosed_port"]=port_min_used
                # Deploy new reverse-proxies's configurations on servers
                add_link.deploy_nginxConf(DB_settings, dsp_link["link_id"], servers)

                for honeypot in honeypots:
                    # Create lhs_infos
                    lhs_infos = {"id_link":dsp_link["link_id"], "id_hp": honeypot["hp_id"], "id_serv": servers[0]["serv_id"], "port":servers[0]["choosed_port"]}
                    # Normalize infos
                    lhs_infos = Gotham_normalize.normalize_lhs_infos(lhs_infos)
                    # Store new link and tags in the internal database        
                    Gotham_link_BDD.add_lhs_DB(DB_settings, lhs_infos)
                i=0
                j=1


            elif str(ports_sorted[i+1])!=port_min_used and count_exposed_ports[str(ports_sorted[i+1])]-count_exposed_ports[port_min_used]>1:
                i+=1

            elif str(ports_sorted[-(j+1)])!=port_max_used and count_exposed_ports[port_max_used]-count_exposed_ports[str(ports_sorted[-(j+1)])]>1:
                j+=1
        
            else:
                is_possible = False
        else:
            is_possible = False
            # 80,100,300,1024
