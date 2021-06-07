# -*- coding: utf-8 -*-

import configparser
import base64
import requests
import json

import Gotham_link_BDD
import Gotham_check
import Gotham_choose
import Gotham_normalize
import Gotham_replace
import Gotham_SSH_SCP
import Gotham_state
import add_link

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')

# Retrieve settings from configuration file
config = configparser.ConfigParser()
config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
tags_separator = config['tag']['separator']
ports_separator = config['port']['separator']


def edit_tags(DB_settings, datacenter_settings, link, tags, type_tag):
    '''
    Edit tags for a specified link

    ARGUMENTS:
        DB_settings (dict) : all authentication information to connect to db
        datacenter_settings (dict) : all authentication information to connect to datacenter
        link (dict) : link information
        tags (string) : new desired tags
        type_tag (string) : "hp" or "serv"
    '''

    all_ok = True

    if type_tag != "hp" and type_tag != "serv":
        logging.error(f"type_tag is incorrect")
        raise ValueError("typ_tag incorrect")

    new_tags = tags.lower().split(tags_separator)

    dsp_link = Gotham_normalize.normalize_display_object_infos(
        link,
        "link",
        type_tag
    )

    if type_tag == "serv":
        already_used = []
        already_used.append("OK")

    for object_infos in dsp_link[type_tag + "s"]:
        not_present_in_obj = list(
            set(new_tags) - set(object_infos[type_tag + "_tags"].lower().split("||")))
        if not_present_in_obj != []:
            links = Gotham_link_BDD.get_link_infos(
                DB_settings,
                id=dsp_link["link_id"]
            )[0]
            dsp_link = Gotham_normalize.normalize_display_object_infos(
                links,
                "link",
                type_tag
            )

            if type_tag == "serv":
                try:
                    already_used = Gotham_replace.replace_serv_for_added_tags_in_link(
                        DB_settings,
                        datacenter_settings,
                        dsp_link,
                        object_infos,
                        tags,
                        already_used
                    )
                except Exception as e:
                    raise ValueError(e)
                if str(already_used[0]).upper() == "KO":
                    all_ok = False

            elif type_tag == "hp":
                try:
                    result = Gotham_replace.replace_hp_for_added_tags_in_link(
                        DB_settings,
                        datacenter_settings,
                        dsp_link,
                        object_infos,
                        tags
                    )
                except Exception as e:
                    raise ValueError(e)
                if not(result):
                    all_ok = False
    return all_ok


def edit_nb(DB_settings, datacenter_settings, link, nb, type_nb):
    '''
    Edit honeypot number or server number for a specified link

    ARGUMENTS:
        DB_settings (dict) : all authentication information to connect to db
        datacenter_settings (dict) : all authentication information to connect to datacenter
        link (dict): link information
        nb (int) : new number of objects
        type_nb (string) : "hp" or "serv"
    '''

    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    # Retrieve State list
    state_list_serv = config['state']['serv_state'].split(",")
    state_list_hp = config['state']['hp_state'].split(",")

    if len(state_list_serv) < 4 or len(state_list_hp) < 4:
        error = "The config file needs 4 differents states for honeypot and server"
        logging.error(error)
        raise ValueError(error)

    dsp_link = Gotham_normalize.normalize_display_object_infos(
        link, "link", type_nb)

    other_type_nb = "hp" if type_nb == "serv" else 'serv'

    # Get already used objects
    present_objects = []
    for object_infos in dsp_link[type_nb + "s"]:
        # Check objects state
        try:
            # Update state of object
            present_object = Gotham_state.adapt_state(
                DB_settings,
                object_infos[type_nb + "_id"], 
                type_nb,
                replace_auto=False
            )
        except Exception as e:
            logging.error(
                "Error while configuring object " + type_nb + " state : " + str(e))

            if type_nb == "hp":
                present_object = Gotham_link_BDD.get_honeypot_infos(
                    DB_settings,
                    id=object_infos[type_nb + "_id"]
                )[0]

            if type_nb == "serv":
                present_object = Gotham_link_BDD.get_server_infos(
                    DB_settings,
                    id=object_infos[type_nb + "_id"]
                )[0]

        present_objects.append(present_object)
    desired_ports = link["link_ports"].split(ports_separator)
    exposed_ports = [sec_obj["lhs_port"] for first_obj in dsp_link[type_nb + "s"]
                     for sec_obj in first_obj[other_type_nb + "s"]]
    exposed_ports_unique = list(dict.fromkeys(exposed_ports))

    if str(nb).lower() == "all" or int(nb) > int(link["link_nb_" + type_nb]):
        tags = tags_separator.join(link["link_tags_" + type_nb].split("||"))
        tags_hp = tags if type_nb == "hp" else ''
        tags_serv = tags if type_nb == "serv" else ''

        if str(nb).lower() != "all":
            nb_sup = int(nb) - int(link["link_nb_" + type_nb])

        if type_nb == "hp":
            # Get all honeypots corresponding to tags
            objects_infos = Gotham_link_BDD.get_honeypot_infos(
                DB_settings, tags=tags)

        if type_nb == "serv":
            # Get all servers corresponding to tags
            objects_infos = Gotham_link_BDD.get_server_infos(
                DB_settings, tags=tags)

            # Filter servers in those who have one of ports open
            objects_infos = Gotham_check.check_servers_ports_matching(
                objects_infos, dsp_link["link_ports"])

        if tags.lower() != "all":
            # update state
            try:
                objects_infos = [Gotham_state.adapt_state(DB_settings,
                                                          object_infos[type_nb + "_id"], type_nb) for object_infos in objects_infos]
            except Exception as e:
                logging.error(
                    "Error while configuring object state : " + str(e))
            objects_infos = Gotham_check.check_tags(
                type_nb, objects_infos, tags_hp=tags_hp, tags_serv=tags_serv)

        # Filter objects in error and already present in link
        objects_infos = [object_infos for object_infos in objects_infos if not(
            object_infos[type_nb + "_state"] == (str(state_list_hp[2]).upper() if type_nb == "hp" else str(state_list_serv[2]).upper()) or object_infos[type_nb + "_state"] == (str(state_list_hp[3]).upper() if type_nb == "hp" else str(state_list_serv[3]).upper()) or object_infos[type_nb + "_id"] in link[type_nb + "_id"])]

        if str(nb).lower() != "all":
            if type_nb == "hp":
                if len(objects_infos) > 0:
                    # Choose best honeypots (the lower scored)
                    objects_infos = Gotham_choose.choose_honeypots(
                        objects_infos, nb_sup, tags)

            if type_nb == "serv":
                #  Checking we have enough servers for the nb_sup directive,
                # otherwise return error
                if len(objects_infos) < nb_sup:
                    error = "Can't deploy link on " + \
                        str(nb_sup) + " others servers while there is only " + \
                        str(len(objects_infos)) + " servers available"
                    logging.error(error)
                    raise ValueError(error)

                # Choose best servers (the lower scored)
                objects_infos = Gotham_choose.choose_servers(
                    objects_infos, nb_sup, tags)

        selected_objects = present_objects + objects_infos

        # Checking we have enough honeypots for the nb directive
        if type_nb == "hp" and str(nb).lower(
        ) != "all" and len(selected_objects) < nb:
            added_hp = []

            for i in range(nb - len(selected_objects)):

                with open(selected_objects[i % len(selected_objects)]["hp_source"] + "/Dockerfile", 'r') as file:
                    encoded_dockerfile = base64.b64encode(
                        file.read().encode("ascii"))

                name = (selected_objects[i % len(selected_objects)]["hp_name"] + "_Duplicat" if len(selected_objects[i % len(selected_objects)]
                                                                                                    ["hp_name"] + "_Duplicat") <= 128 else selected_objects[i % len(selected_objects)]["hp_name"][:(128 - len("_Duplicat"))] + "_Duplicat")
                descr = "Duplication of " + \
                    selected_objects[i % len(selected_objects)]["hp_descr"]
                duplicate_hp_infos = {"name": str(name), "descr": str(descr), "tags": str(selected_objects[i % len(selected_objects)]["hp_tags"].replace("||", tags_separator)), "logs": str(selected_objects[i % len(selected_objects)]["hp_logs"]), "parser": str(
                    selected_objects[i % len(selected_objects)]["hp_parser"]), "port": str(selected_objects[i % len(selected_objects)]["hp_port_container"]), "dockerfile": str(encoded_dockerfile.decode("utf-8")), "duplicat": 1}

                try:
                    jsondata = json.dumps(duplicate_hp_infos)
                    url = "http://localhost:5000/add/honeypot"
                    headers = {'Content-type': 'application/json'}
                    r = requests.post(url, data=jsondata, headers=headers)
                    jsonresponse = r.json()
                    id_hp = jsonresponse["id"]
                    added_hp.append(id_hp)
                except Exception as e:
                    #logging.error(f"Error with hp duplication : {honeypot_infos['hp_id']} - " + str(e))
                    raise ValueError(e)

            for id in added_hp:
                selected_objects.append(
                    Gotham_link_BDD.get_honeypot_infos(DB_settings, id=id)[0])

        # if str(nb).lower() == "all":
        #    nb_obj=len(selected_objects)
        # else:
        #    nb_obj=nb

        if type_nb == "hp":
            for exposed_port in exposed_ports_unique:
                nginxRedirectionPath = "/data/template/" + \
                    str(link["link_id"]) + "-" + str(exposed_port) + ".conf"
                try:
                    os.remove(nginxRedirectionPath)
                    add_link.generate_nginxConf(
                        DB_settings, link["link_id"], datacenter_settings["hostname"], selected_objects, exposed_port)
                except Exception as e:
                    logging.error(
                        f"Error with nginx conf modification : {nginxRedirectionPath} - " + str(e))
                    raise ValueError(e)
            # Get all servers used by links
            servers = [serv for hp in dsp_link["hps"] for serv in hp["servs"]]
            # Remove duplicates
            servers = [dict(tuple_of_serv_items) for tuple_of_serv_items in {
                tuple(serv.items()) for serv in servers}]

            try:
                # Deploy new reverse-proxies's configurations on servers
                add_link.deploy_nginxConf(
                    DB_settings, link["link_id"], servers)
            except Exception as e:
                raise ValueError(e)

            for i in range(len(selected_objects)):
                if "weight" in selected_objects[i].keys():
                    del selected_objects[i]["weight"]

            added_hp = [
                hp for hp in selected_objects if hp not in present_objects]

            # Insert data in Link_Hp_Serv
            for server in servers:
                for honeypot in added_hp:
                    # Create lhs_infos
                    lhs_infos = {"id_link": link["link_id"], "id_hp": honeypot["hp_id"],
                                 "id_serv": server["serv_id"], "port": server["lhs_port"]}
                    # Normalize infos
                    lhs_infos = Gotham_normalize.normalize_lhs_infos(lhs_infos)
                    try:
                        # Store new link and tags in the internal database
                        Gotham_link_BDD.add_lhs_DB(DB_settings, lhs_infos)
                    except Exception as e:
                        raise ValueError(e)

                    try:
                        # Update state of honeypot
                        Gotham_state.adapt_state(
                            DB_settings, honeypot["hp_id"], "hp")
                    except Exception as e:
                        logging.error(
                            "Error while configuring honeypot state : " + str(e))

                try:
                    # Update state of server
                    Gotham_state.adapt_state(
                        DB_settings, server["serv_id"], "serv")
                except Exception as e:
                    logging.error(
                        "Error while configuring server state : " + str(e))

        if type_nb == "serv":
            count_exposed_ports = {str(port): 0 for port in desired_ports}
            for port in exposed_ports:
                count_exposed_ports[str(port)] += 1

            # Associate servers and an port of exposition
            for i in range(len(objects_infos)):
                serv_i_free_ports = objects_infos[i]["free_ports"].split(
                    ports_separator)
                servs_free_ports = (ports_separator.join(
                    [serv["free_ports"] for serv in objects_infos if serv["serv_id"] != objects_infos[i]["serv_id"]])).split(ports_separator)
                port_available_only_for_this_server_new = list(
                    set(serv_i_free_ports).difference(servs_free_ports))
                port_available_only_for_this_server = [
                    port for port in port_available_only_for_this_server_new if port not in exposed_ports_unique]

                if len(objects_infos[i]["free_ports"].split(
                        ports_separator)) == 1:
                    objects_infos[i]["choosed_port"] = int(
                        objects_infos[i]["free_ports"])
                    count_exposed_ports[str(
                        objects_infos[i]["choosed_port"])] += 1

                elif port_available_only_for_this_server != []:
                    free_ports_available_only_for_this_server_with_weight = {
                        key: value for key, value in count_exposed_ports.items() if key in port_available_only_for_this_server}
                    objects_infos[i]["choosed_port"] = int(min(
                        free_ports_available_only_for_this_server_with_weight, key=free_ports_available_only_for_this_server_with_weight.get))
                    count_exposed_ports[str(
                        objects_infos[i]["choosed_port"])] += 1

            for i in range(len(objects_infos)):
                if not("choosed_port" in objects_infos[i].keys()):
                    free_ports_for_serv_with_weight = {
                        port: count_exposed_ports[port] for port in objects_infos[i]["free_ports"].split(ports_separator)}
                    objects_infos[i]["choosed_port"] = int(
                        min(free_ports_for_serv_with_weight, key=free_ports_for_serv_with_weight.get))
                    count_exposed_ports[str(
                        objects_infos[i]["choosed_port"])] += 1

            final_exposed_ports_new_servs = list(filter(None, dict.fromkeys(
                [server["choosed_port"] for server in objects_infos])))

            new_exposed_ports = [
                port for port in final_exposed_ports_new_servs if port not in exposed_ports_unique]

            # Get all honeypots used by links
            honeypots = [hp for serv in dsp_link["servs"]
                         for hp in serv["hps"]]
            for i in range(len(honeypots)):
                del honeypots[i]["lhs_port"]
            # Remove duplicates
            honeypots = [dict(tuple_of_hp_items) for tuple_of_hp_items in {
                tuple(hp.items()) for hp in honeypots}]

            # Generate NGINX configurations for each redirection on a specific
            # exposed_port
            for exposed_port in new_exposed_ports:
                try:
                    add_link.generate_nginxConf(
                        DB_settings, link["link_id"], datacenter_settings["hostname"], honeypots, exposed_port)
                except Exception as e:
                    raise ValueError(e)

            try:
                # Deploy new reverse-proxies's configurations on servers
                add_link.deploy_nginxConf(
                    DB_settings, link["link_id"], objects_infos)
            except Exception as e:
                raise ValueError(e)

            # Insert data in Link_Hp_Serv
            for server in objects_infos:
                for honeypot in honeypots:
                    # Create lhs_infos
                    lhs_infos = {"id_link": link["link_id"], "id_hp": honeypot["hp_id"],
                                 "id_serv": server["serv_id"], "port": server["choosed_port"]}
                    # Normalize infos
                    lhs_infos = Gotham_normalize.normalize_lhs_infos(lhs_infos)
                    try:
                        # Store new link and tags in the internal database
                        Gotham_link_BDD.add_lhs_DB(DB_settings, lhs_infos)
                    except Exception as e:
                        raise ValueError(e)

                    try:
                        # Update state of honeypot
                        Gotham_state.adapt_state(
                            DB_settings, honeypot["hp_id"], "hp")
                    except Exception as e:
                        logging.error(
                            "Error while configuring honeypot state : " + str(e))

                try:
                    # Update state of server
                    Gotham_state.adapt_state(
                        DB_settings, server["serv_id"], "serv")
                except Exception as e:
                    logging.error(
                        "Error while configuring server state : " + str(e))

    elif int(nb) < int(link["link_nb_" + type_nb]):

        if type_nb == "hp":
            selected_objects = Gotham_choose.choose_honeypots(
                present_objects, nb, dsp_link["link_tags_hp"], del_weight=True)

        if type_nb == "serv":
            selected_objects = Gotham_check.check_servers_ports_matching(
                present_objects, dsp_link["link_ports"])
            selected_objects = Gotham_choose.choose_servers(
                selected_objects, nb, dsp_link["link_tags_serv"], del_weight=True)
            # Clean free_ports
            for i in range(len(selected_objects)):
                del selected_objects[i]["free_ports"]

        del_objects = [
            obj for obj in present_objects if obj not in selected_objects]

        for del_object in del_objects:
            if type_nb == "hp":
                index_hp_in_link = next((index for (index, hp) in enumerate(
                    dsp_link["hps"]) if hp["hp_id"] == del_object["hp_id"]), None)
                # Configure all server to not redirect on hp
                try:
                    Gotham_replace.config_honeypot_replacement(
                        DB_settings, datacenter_settings, dsp_link["hps"][index_hp_in_link], link=dsp_link)
                except ValueError as e:
                    raise ValueError(e)
            if type_nb == "serv":
                try:
                    commands = ["rm /etc/nginx/conf.d/links/" + dsp_link["link_id"] +
                                "-*.conf", "/usr/sbin/nginx -t && /usr/sbin/nginx -s reload"]
                    Gotham_SSH_SCP.execute_commands(
                        del_object["serv_ip"], del_object["serv_ssh_port"], del_object["serv_ssh_key"], commands)

                except Exception as e:
                    logging.error(
                        f"{link['link_id']} removal on servers failed : {e}")
                    raise ValueError(e)
            try:
                if type_nb == "hp":
                    Gotham_link_BDD.remove_lhs(
                        DB_settings, id_link=dsp_link["link_id"], id_hp=del_object["hp_id"])
                elif type_nb == "serv":
                    Gotham_link_BDD.remove_lhs(
                        DB_settings, id_link=dsp_link["link_id"], id_serv=del_object["serv_id"])
            except Exception as e:
                raise ValueError(e)

            try:
                # Update state of object
                Gotham_state.adapt_state(
                    DB_settings, del_object[type_nb + "_id"], type_nb)
            except Exception as e:
                logging.error(
                    "Error while configuring object state : " + str(e))

            try:
                modifs = {
                    "nb_" + type_nb: int(dsp_link["link_nb_" + type_nb]) - 1}
                conditions = {"id": dsp_link["link_id"]}
                Gotham_link_BDD.edit_link_DB(DB_settings, modifs, conditions)
            except Exception as e:
                raise ValueError(e)

    return len(selected_objects)


def edit_ports(DB_settings, datacenter_settings, link, new_ports):
    '''
    Edit ports exposed by a link

    ARGUMENTS:
        DB_settings (dict) : all authentication information to connect to db
        datacenter_settings (dict) : all authentication information to connect to datacenter
        link (dict) : link information
        new_pors (string) : new desired ports
    '''

    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    # Retrieve State list
    state_list = config['state']['serv_state'].split(",")

    if len(state_list) < 4:
        error = "The config file needs 4 differents states for honeypot and server"
        logging.error(error)
        raise ValueError(error)

    dsp_link = Gotham_normalize.normalize_display_object_infos(
        link,
        "link",
        "serv"
    )

    tags_serv = tags_separator.join(dsp_link["link_tags_serv"].split("||"))

    old_desired_ports = link["link_ports"].split(ports_separator)
    new_desired_ports = new_ports.split(ports_separator)

    count_exposed_ports = {str(port): 0 for port in new_desired_ports}

    deleted_ports = [
        str(port) for port in old_desired_ports if port not in new_desired_ports]
    added_ports = [str(port)
                   for port in new_desired_ports if port not in old_desired_ports]

    # Get all honeypots used by links
    honeypots = [{key: value for key, value in hp.items() if key != "lhs_port"}
                 for serv in dsp_link["servs"] for hp in serv["hps"]]
    # Remove duplicates
    honeypots = [dict(tuple_of_hp_items) for tuple_of_hp_items in {
        tuple(hp.items()) for hp in honeypots}]

    # update state
    try:
        honeypots = [Gotham_state.adapt_state(
            DB_settings,
            honeypot["hp_id"],
            "hp",
            replace_auto=False) for honeypot in honeypots]
    except Exception as e:
        logging.error(
            "Error while configuring honeypot state : " + str(e))

    # Generate NGINX configurations for each redirection on a specific
    # exposed_port
    for exposed_port in added_ports:
        add_link.generate_nginxConf(
            DB_settings,
            dsp_link["link_id"],
            datacenter_settings["hostname"],
            honeypots,
            exposed_port
        )
    nb_del = 0
    servs_keeps = []
    for server in dsp_link["servs"]:
        # Check objects state
        try:
            # Update state of object
            Gotham_state.adapt_state(
                DB_settings,
                server["serv_id"],
                "serv",
                replace_auto=False)
        except Exception as e:
            logging.error(
                "Error while configuring server state : " + str(e))

        exposed_ports = [hp["lhs_port"] for hp in server["hps"]]
        exposed_ports_unique = list(dict.fromkeys(exposed_ports))
        if len(exposed_ports_unique) == 1:
            if str(exposed_ports_unique[0]) in deleted_ports:
                # Remove server
                try:
                    commands = ["rm /etc/nginx/conf.d/links/" +
                                dsp_link["link_id"] +
                                "-*.conf", "/usr/sbin/nginx -t && /usr/sbin/nginx -s reload"]
                    Gotham_SSH_SCP.execute_commands(
                        server["serv_ip"],
                        server["serv_ssh_port"],
                        server["serv_ssh_key"],
                        commands
                    )
                    Gotham_link_BDD.remove_lhs(
                        DB_settings,
                        id_link=dsp_link["link_id"],
                        id_serv=server["serv_id"]
                    )
                except Exception as e:
                    logging.error(
                        f"{link['link_id']} removal on servers failed : {e}")
                    raise ValueError(e)
                try:
                    # Update state of the server
                    Gotham_state.adapt_state(
                        DB_settings, server["serv_id"], "serv")
                except Exception as e:
                    logging.error(
                        "Error while configuring server state : " + str(e))
                nb_del += 1
            else:
                count_exposed_ports[str(exposed_ports_unique[0])] += 1
                servs_keeps.append(server["serv_id"])
        else:
            # Feature : multi ports on multi hp (today : only HA)
            logging.error(f"Not implemented")
            raise ValueError("Not implemented")

    if nb_del > 0:
        # Get all servers corresponding to tags
        servers = Gotham_link_BDD.get_server_infos(
            DB_settings,
            tags=tags_serv
        )

        if tags_serv.lower() != "all":
            # update state
            try:
                servers = [Gotham_state.adapt_state(
                    DB_settings,
                    server["serv_id"],
                    "serv"
                ) for server in servers]
            except Exception as e:
                logging.error(
                    "Error while configuring server state : " + str(e))
            servers = Gotham_check.check_tags(
                "serv",
                servers,
                tags_serv=tags_serv
            )

        servers = Gotham_check.check_servers_ports_matching(servers, new_ports)

        # Filter servers in error and already used by link
        servers = [server for server in servers if not(
            server["serv_state"] == str(state_list[2]).upper() or server["serv_state"] == str(state_list[3]).upper() or server["serv_id"] in servs_keeps)]
        if len(servers) < nb_del:
            try:
                modifs = {"nb_serv": int(dsp_link["link_nb_serv"]) - nb_del}
                conditions = {"id": dsp_link["link_id"]}
                Gotham_link_BDD.edit_link_DB(DB_settings, modifs, conditions)
            except Exception as e:
                raise ValueError(e)

        # Choose best servers (the lower scored)
        servers = Gotham_choose.choose_servers(servers, nb_del, tags_serv)
        # Associate servers and an port of exposition
        for i in range(len(servers)):
            serv_i_free_ports = servers[i]["free_ports"].split(ports_separator)
            servs_free_ports = (ports_separator.join(
                [serv["free_ports"] for serv in servers if serv["serv_id"] != servers[i]["serv_id"]])).split(ports_separator)
            port_available_only_for_this_server = list(
                set(serv_i_free_ports).difference(servs_free_ports))

            if len(servers[i]["free_ports"].split(ports_separator)) == 1:
                servers[i]["choosed_port"] = int(servers[i]["free_ports"])
                count_exposed_ports[str(servers[i]["choosed_port"])] += 1

            elif port_available_only_for_this_server != []:
                free_ports_available_only_for_this_server_with_weight = {
                    key: value for key, value in count_exposed_ports.items() if key in port_available_only_for_this_server}
                servers[i]["choosed_port"] = int(
                    min(
                        free_ports_available_only_for_this_server_with_weight,
                        key=free_ports_available_only_for_this_server_with_weight.get
                    )
                )
                count_exposed_ports[str(servers[i]["choosed_port"])] += 1

        for i in range(len(servers)):
            if not("choosed_port" in servers[i].keys()):
                free_ports_for_serv_with_weight = {
                    port: count_exposed_ports[port] for port in servers[i]["free_ports"].split(ports_separator)}
                servers[i]["choosed_port"] = int(
                    min(
                        free_ports_for_serv_with_weight,
                        key=free_ports_for_serv_with_weight.get
                    )
                )
                count_exposed_ports[str(servers[i]["choosed_port"])] += 1

        # Deploy new reverse-proxies's configurations on servers
        add_link.deploy_nginxConf(DB_settings, dsp_link["link_id"], servers)
        # Insert data in Link_Hp_Serv
        for server in servers:
            for honeypot in honeypots:
                # Create lhs_infos
                lhs_infos = {"id_link": dsp_link["link_id"],
                             "id_hp": honeypot["hp_id"],
                             "id_serv": server["serv_id"],
                             "port": server["choosed_port"]
                }
                # Normalize infos
                lhs_infos = Gotham_normalize.normalize_lhs_infos(lhs_infos)
                # Store new link and tags in the internal database
                Gotham_link_BDD.add_lhs_DB(DB_settings, lhs_infos)

                try:
                    # Update state of honeypot
                    Gotham_state.adapt_state(
                        DB_settings, honeypot["hp_id"], "hp")
                except Exception as e:
                    logging.error(
                        "Error while configuring honeypot state : " + str(e))

            try:
                # Update state of server
                Gotham_state.adapt_state(
                    DB_settings, server["serv_id"], "serv")
            except Exception as e:
                logging.error(
                    "Error while configuring server state : " + str(e))
