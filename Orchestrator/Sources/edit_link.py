# -*- coding: utf-8 -*-
# Import Gotham's libs
# GOTHAM'S LIB
import Gotham_link_BDD
import Gotham_check
import Gotham_choose
import Gotham_normalize
import Gotham_replace

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


def edit_tags(DB_settings, link, tags, type_tag):

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


def edit_nb(DB_settings, link, nb, type_nb):

    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    tags_separator = config['tag']['separator']

    dsp_link=Gotham_normalize.normalize_display_object_infos(link,"link",type_nb)

    if str(nb).lower() == "all":
        if type_nb=="hp":
            tags=tags_separator.join(link["link_tags_hp"].split("||"))

            # Get all honeypots corresponding to tags
            honeypots = Gotham_link_BDD.get_honeypot_infos(DB_settings, tags=tags)

            if tags.lower()!="all":
                honeypots = Gotham_check.check_tags("hp", honeypots, tags_hp=tags)
        
            # Filter honeypots in error
            honeypots = [honeypot for honeypot in honeypots if not(honeypot["hp_state"]=='ERROR' or honeypot["hp_id"] in link["hp_id"])]

            #nb_hp=len(honeypots)

        if type_nb=="serv"

            tags=tags_separator.join(link["link_tags_hp"].split("||"))


            # Get all servers corresponding to tags
            servers = Gotham_link_BDD.get_server_infos(DB_settings, tags=tags)
            
            if tags.lower()!="all":
                servers = Gotham_check.check_tags("serv",servers, tags_serv=tags)

            # Filter servers in those who have one of ports open
            servers = Gotham_check.check_servers_ports_matching(servers, exposed_ports)
            
            # Filter servers in error
            servers = [server for server in servers if not(server["serv_state"]=='ERROR' or honeypot["serv_id"] in link["serv_id"])]
            

            #nb_srv=len(servers)
        


    elif int(nb) < int(link["nb_"+type_nb]):
        present_objects=[]
        for object_infos in dsp_link[type_nb+"s"]:

            if type_nb=="hp":
                present_object=Gotham_link_BDD.get_honeypot_infos(DB_settings, id=object_infos[type_nb+"_id"])

            if type_nb=="serv":
                present_object=Gotham_link_BDD.get_server_infos(DB_settings, id=object_infos[type_nb+"_id"])

            present_objects.append(present_object)

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
                    remove_lhs(DB_settings, id_link = dsp_link["link_id"], id_hp = del_object["hp_id"])
                elif type_nb == "serv":
                    remove_lhs(DB_settings, id_link = dsp_link["link_id"], id_serv = del_object["serv_id"])
            except:
                sys.exit(1)
            try:
                modifs={"nb_"+type_nb:int(dsp_link["link_nb_"+type_nb])-1}
                conditions={"id":dsp_link["link_id"]}
                edit_link_DB(DB_settings, modifs, conditions)
            except:
                sys.exit(1)