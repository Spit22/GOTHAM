# -*- coding: utf-8 -*-
# Import external libs
import configparser
import sys
import base64
import requests
import json

# Import Gotham's libs
# GOTHAM'S LIB
import Gotham_link_BDD
import Gotham_check
import Gotham_choose
import Gotham_normalize
import Gotham_replace
import Gotham_SSH_SCP

import add_link

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


def edit_tags(DB_settings, datacenter_settings, link, tags, type_tag):

    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    tags_separator = config['tag']['separator']

    if type_tag!="hp" and type_tag!="serv":
        logging.error(f"type_tag is incorrect")
        sys.exit(1)

    new_tags=tags.split(tags_separator)
    
    dsp_link=Gotham_normalize.normalize_display_object_infos(link,"link",type_tag)

    already_used=[]
    for object_infos in dsp_link[type_tag+"s"]:
        not_present_in_obj=list(set(new_tags) - set(object_infos[type_tag+"_tags"].split("||")))
        if not_present_in_obj != []:
            links = Gotham_link_BDD.get_link_infos(DB_settings, id=dsp_link["link_id"])
            dsp_link=Gotham_normalize.normalize_display_object_infos(links[0],"link",type_tag)

            if type_tag=="serv":
                try:
                    already_used=Gotham_replace.replace_serv_for_added_tags_in_link(DB_settings, datacenter_settings, dsp_link, object_infos, tags, already_used)
                except:
                    sys.exit(1)
            
            elif type_tag=="hp":
                try:
                    Gotham_replace.replace_hp_for_added_tags_in_link(DB_settings, datacenter_settings, dsp_link, object_infos, tags)
                except:
                    sys.exit(1)


def edit_nb(DB_settings, datacenter_settings, link, nb, type_nb):

    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    tags_separator = config['tag']['separator']
    ports_separator = config['port']['separator']

    dsp_link=Gotham_normalize.normalize_display_object_infos(link,"link",type_nb)

    other_type_nb="hp" if type_nb == "serv" else 'serv'

    # Get already used objects
    present_objects=[]
    for object_infos in dsp_link[type_nb+"s"]:

        if type_nb=="hp":
            present_object=Gotham_link_BDD.get_honeypot_infos(DB_settings, id=object_infos[type_nb+"_id"])

        if type_nb=="serv":
            present_object=Gotham_link_BDD.get_server_infos(DB_settings, id=object_infos[type_nb+"_id"])

        present_objects.append(present_object)

    desired_ports=link["ports"].split(ports_separator)
    exposed_ports=[sec_obj["lhs_port"] for first_obj in link[type_nb+"s"] for sec_obj in first_obj[other_type_nb+"s"]]
    exposed_ports_unique=list(dict.fromkeys(exposed_ports))

    if str(nb).lower() == "all" or int(nb)> int(link["nb_"+type_nb]):
        tags=tags_separator.join(link["link_tags_"+type_nb].split("||"))
        tags_hp=tags if type_nb == "hp" else ''
        tags_serv=tags if type_nb == "serv" else ''        

        if str(nb).lower() != "all":
            nb_sup=int(nb)-int(link["nb_"+type_nb])

        if type_nb=="hp":
            # Get all honeypots corresponding to tags
            objects_infos = Gotham_link_BDD.get_honeypot_infos(DB_settings, tags=tags)
        
        if type_nb=="serv":
            # Get all servers corresponding to tags
            objects_infos = Gotham_link_BDD.get_server_infos(DB_settings, tags=tags)
            
            # Filter servers in those who have one of ports open
            objects_infos = Gotham_check.check_servers_ports_matching(objects_infos, dsp_link["ports"])

            
        if tags.lower()!="all":
            objects_infos = Gotham_check.check_tags(type_nb, objects_infos, tags_hp=tags_hp, tags_serv=tags_serv)

        # Filter objects in error and already present in link
        objects_infos = [object_infos for object_infos in objects_infos if not(object_infos[type_nb+"_state"]=='ERROR' or object_infos[type_nb+"_id"] in link[type_nb+"_id"])]


        if str(nb).lower() != "all":
            if type_nb=="hp":
                # Choose best honeypots (the lower scored)
                objects_infos = Gotham_choose.choose_honeypots(objects_infos, nb_sup, tags)

            if type_nb=="serv":
                # Checking we have enough servers for the nb_sup directive, otherwise return error
                if len(objects_infos) < nb_sup:
                    logging.error(f"Can't deploy link on {str(nb_sup)} servers while there is only {str(len(selected_objects))} servers available")
                    sys.exit(1)
                # Choose best servers (the lower scored)
                objects_infos = Gotham_choose.choose_servers(objects_infos, nb_sup, tags)
                
        selected_objects=present_objects+objects_infos

        # Checking we have enough honeypots for the nb directive
        if type_nb=="hp" and str(nb).lower() != "all" and len(selected_objects) < nb :
            added_hp=[]
            
            for i in range(nb-len(selected_objects)):
                
                with open(selected_objects[i%len(selected_objects)]["hp_source"]+"/Dockerfile", 'r') as file:
                    encoded_dockerfile = base64.b64encode(file.read().encode("ascii"))
                
                name = (selected_objects[i%len(selected_objects)]["hp_name"]+"_Duplicat" if len(selected_objects[i%len(selected_objects)]["hp_name"]+"_Duplicat")<=128 else selected_objects[i%len(selected_objects)]["hp_name"][:(128-len("_Duplicat"))]+"_Duplicat")
                descr = "Duplication of "+selected_objects[i%len(selected_objects)]["hp_descr"]
                duplicate_hp_infos={"name": name,"descr": descr,"tags": selected_objects[i%len(selected_objects)]["hp_tags"].replace("||",tags_separator),"logs": selected_objects[i%len(selected_objects)]["hp_logs"],"parser": selected_objects[i%len(selected_objects)]["hp_parser"],"port": selected_objects[i%len(selected_objects)]["hp_port_container"], "dockerfile": encoded_dockerfile}
                
                try:
                    jsondata = json.dumps(duplicate_hp_infos)
                    url = "http://localhost:5000/add/honeypot"
                    headers = {'Content-type': 'application/json'}
                    r = requests.post(url, data=jsondata, headers=headers)
                    id_hp = r.text.split()[2]
                    added_hp.append(id_hp)
                except Exception as e:
                    #logging.error(f"Error with hp duplication : {honeypot_infos['hp_id']} - " + str(e))
                    sys.exit(1)
                
            
            for id in added_hp:
                selected_objects.append(Gotham_link_BDD.get_honeypot_infos(DB_settings, id=id))
        
        if str(nb).lower() == "all":
            nb_obj=len(selected_objects)
        else:
            nb_obj=nb

        if type_nb=="hp":
            for exposed_port in exposed_ports_unique:
                nginxRedirectionPath = "/data/template/"+ str(link["link_id"]) +"-"+str(exposed_port)+".conf"
                try:
                    os.remove(nginxRedirectionPath)
                    add_link.generate_nginxConf(DB_settings, link["link_id"], datacenter_settings["hostname"], selected_objects, exposed_port)
                except Exception as e:
                    logging.error(f"Error with nginx conf modification : {nginxRedirectionPath} - " + str(e))
                    sys.exit(1)
            # Get all servers used by links
            servers=[serv for hp in link["hps"] for serv in hp["servs"]]
            # Remove duplicates
            servers=[dict(tuple_of_serv_items) for tuple_of_serv_items in {tuple(serv.items()) for serv in servers}]

            try:
                # Deploy new reverse-proxies's configurations on servers
                add_link.deploy_nginxConf(DB_settings, link["link_id"], servers)
            except:
                sys.exit(1)
            
            added_hp=[hp for hp in selected_objects if hp not in present_objects]
            
            for server in servers:
                for honeypot in added_hp:
                    # Create lhs_infos
                    lhs_infos = {"id_link":link["link_id"], "id_hp": honeypot["hp_id"], "id_serv": server["serv_id"], "port":server["lhs_port"]}
                    # Normalize infos
                    lhs_infos = Gotham_normalize.normalize_lhs_infos(lhs_infos)
                    try:
                        # Store new link and tags in the internal database        
                        Gotham_link_BDD.add_lhs_DB(DB_settings, lhs_infos)
                    except:
                        sys.exit(1)

        if type_nb=="serv":
            count_exposed_ports={str(port):0 for port in desired_ports}
            for port in exposed_ports:
                count_exposed_ports[str(port)]+=1

            # Associate servers and an port of exposition
            for i in range(len(objects_infos)):
                serv_i_free_ports=objects_infos[i]["free_ports"].split(ports_separator)
                servs_free_ports=(ports_separator.join([serv["free_ports"] for serv in objects_infos if serv["serv_id"]!=objects_infos[i]["serv_id"]])).split(ports_separator)
                port_available_only_for_this_server_new=list(set(serv_i_free_ports).difference(servs_free_ports))
                port_available_only_for_this_server=[port for port in port_available_only_for_this_server_new if port not in exposed_ports_unique]

                if len(objects_infos[i]["free_ports"].split(ports_separator))==1 :
                    objects_infos[i]["choosed_port"]=int(objects_infos[i]["free_ports"])
                    count_exposed_ports[str(objects_infos[i]["choosed_port"])]+=1
                
                elif port_available_only_for_this_server!=[]:
                    objects_infos[i]["choosed_port"]=int(port_available_only_for_this_server[0])
                    count_exposed_ports[str(objects_infos[i]["choosed_port"])]+=1
            
            for i in range(len(objects_infos)):
                if not("choosed_port" in objects_infos[i].keys()):
                    free_ports_for_serv_with_weight={port:count_exposed_ports[port] for port in objects_infos[i]["free_ports"].split(ports_separator)}
                    objects_infos[i]["choosed_port"]=int(min(free_ports_for_serv_with_weight, key=free_ports_for_serv_with_weight.get))
                    count_exposed_ports[str(objects_infos[i]["choosed_port"])]+=1

            final_exposed_ports_new_servs=list(filter(None,dict.fromkeys([server["choosed_port"] for server in objects_infos])))

            new_exposed_ports=[port for port in final_exposed_ports_new_servs if port not in exposed_ports_unique]

            # Get all honeypots used by links
            honeypots=[hp for serv in link["servs"] for hp in serv["hps"]]
            # Remove duplicates
            honeypots=[dict(tuple_of_hp_items) for tuple_of_hp_items in {tuple(hp.items()) for hp in honeypots}]


            # Generate NGINX configurations for each redirection on a specific exposed_port
            for exposed_port in new_exposed_ports:
                try:
                    add_link.generate_nginxConf(DB_settings, link["link_id"], datacenter_settings["hostname"], honeypots, exposed_port)
                except:
                    sys.exit(1)

            try:
                # Deploy new reverse-proxies's configurations on servers
                add_link.deploy_nginxConf(DB_settings, link["link_id"], objects_infos)
            except:
                sys.exit(1)
            
            for server in objects_infos:
                for honeypot in honeypots:
                    # Create lhs_infos
                    lhs_infos = {"id_link":link["link_id"], "id_hp": honeypot["hp_id"], "id_serv": server["serv_id"], "port":server["choosed_port"]}
                    # Normalize infos
                    lhs_infos = Gotham_normalize.normalize_lhs_infos(lhs_infos)
                    try:
                        # Store new link and tags in the internal database        
                        Gotham_link_BDD.add_lhs_DB(DB_settings, lhs_infos)
                    except:
                        sys.exit(1)


    elif int(nb) < int(link["nb_"+type_nb]):
    
        if type_nb=="hp":
            selected_objects = Gotham_choose.choose_honeypots(present_objects, nb, dsp_link["link_tags_hp"])

        if type_nb=="serv":
            selected_objects = Gotham_choose.choose_servers(present_objects, nb, dsp_link["link_tags_serv"])


        del_objects=[obj for obj in present_objects if obj not in selected_objects]

        for del_object in del_objects:
            if type_nb=="hp":
                index_hp_in_link=next((index for (index, hp) in enumerate(dsp_link["hps"]) if hp["hp_id"] == del_object["hp_id"]), None)
                # Configure all server to not redirect on hp
                try:
                    configure_honeypot_replacement(DB_settings, datacenter_settings, dsp_link["hps"][index_hp_in_link], link = dsp_link)
                except:
                    sys.exit(1)
            if type_nb=="serv":
                try:
                  commands = ["sudo rm /etc/nginx/conf.d/links/" + dsp_link["link_id"] +"-*.conf"]
                  Gotham_SSH_SCP.execute_commands(del_object["serv_ip"], del_object["serv_ssh_port"], del_object["serv_ssh_key"], commands)
                  
                except Exception as e:
                  logging.error(f"{link['link_id']} removal on servers failed : {e}")
                  sys.exit(1)

            try:
                if type_nb == "hp":
                    Gotham_link_BDD.remove_lhs(DB_settings, id_link = dsp_link["link_id"], id_hp = del_object["hp_id"])
                elif type_nb == "serv":
                    Gotham_link_BDD.remove_lhs(DB_settings, id_link = dsp_link["link_id"], id_serv = del_object["serv_id"])
            except:
                sys.exit(1)
            try:
                modifs={"nb_"+type_nb:int(dsp_link["link_nb_"+type_nb])-1}
                conditions={"id":dsp_link["link_id"]}
                Gotham_link_BDD.edit_link_DB(DB_settings, modifs, conditions)
            except:
                sys.exit(1)