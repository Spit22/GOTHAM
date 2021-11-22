
import configparser
from . import normalization_functions

import os
import logging

# Logging components
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


def normalize_honeypot_infos(hp_infos):
    '''
    Normalize honeypots information

    ARGUMENTS:
        hp_infos (dict) : honeypot information
    '''
    for key, value in hp_infos.items():
        # Choose the right function based on the key (id, name, descr...)
        normalize_key = getattr(normalization_functions, 'normalize_' + key)
        # Normalization of the id or states are special : we need to indicate
        # the object (honeypot, server or link) we are working with
        # In this case it's honeypots
        if (key == "id" or key == "state"):
            hp_infos[key] = normalize_key("hp", value)
        # Normalization of the others information
        else:
            hp_infos[key] = normalize_key(value)
    return hp_infos


def normalize_server_infos(serv_infos):
    '''
    Normalize server information

    ARGUMENTS:
        serv_infos (dict) : server information
    '''
    for key, value in serv_infos.items():
        # Choose the right function based on the key (id, name, descr...)
        normalize_key = getattr(normalization_functions, 'normalize_' + key)
        # Normalization of the id or states are special : we need to indicate
        # the object (honeypot, server or link) we are working with
        # In this case it's servers
        if (key == "id"):
            serv_infos[key] = normalize_key("sv", value)
        elif (key == "state"):
            serv_infos[key] = normalize_key("serv", value)
        # Normalization of the others information
        else:
            serv_infos[key] = normalize_key(value)
    return serv_infos


def normalize_link_infos(lk_infos):
    '''
    Normalize link information

    ARGUMENTS:
        lk_infos (dict) : link information
    '''
    for key, value in lk_infos.items():
        # Whether with honeypots or server tags, the function is the same
        if (key == "tags_hp" or key == "tags_serv"):
            normalize_key = getattr(normalization_functions, 'normalize_tags')
        # Choose the right function based on the key (id, name, descr...)
        else:
            normalize_key = getattr(
                normalization_functions,
                'normalize_' + key
            )
        # Normalization of the id or states are special : we need to indicate
        # the object (honeypot, server or link) we are working with
        # In this case it's links
        if (key == "id" or key == "state"):
            lk_infos[key] = normalize_key("lk", value)
        # Normalization of the others information
        else:
            lk_infos[key] = normalize_key(value)
    return lk_infos


def normalize_lhs_infos(lhs_infos):
    '''
    Normalize Link/Honeypot/Server combination information

    ARGUMENTS:
        lhs_infos (dict) : combination information
    '''
    for key, value in lhs_infos.items():
        # Choose the right function based on the object
        # (honeypot, server or link)
        if (key == "id_hp"):
            normalize_key = getattr(normalization_functions, 'normalize_id')
            lhs_infos[key] = normalize_key("hp", value)
        elif (key == "id_serv"):
            normalize_key = getattr(normalization_functions, 'normalize_id')
            lhs_infos[key] = normalize_key("sv", value)
        elif (key == "id_link"):
            normalize_key = getattr(normalization_functions, 'normalize_id')
            lhs_infos[key] = normalize_key("lk", value)
        # Normalization of the others information
        else:
            normalize_key = getattr(
                normalization_functions,
                'normalize_' + key
            )
            lhs_infos[key] = normalize_key(value)
    return lhs_infos


def normalize_full_honeypot_infos(hp_infos):
    '''
    TODO
    '''
    # Retrieve settings from config file
    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    default_hp_infos = config['honeypot_infos_default']
    # Normalize honeypot information
    hp_infos = normalize_honeypot_infos(hp_infos)
    # For each piece of information, check that mandatory ones
    # are defined, then set to default undefined information that
    # are not required
    for key, value in default_hp_infos.items():
        # Mandatory information -> must be defined
        if value == 'NOT NULL':
            if not(key in hp_infos):
                error = "Missing value of " + str(key)
                logging.error(error)
                raise ValueError(error)
            elif(hp_infos[key] == ''
                 or hp_infos[key] == 0
                 or hp_infos[key] is None):
                error = str(id) + "Missing value of " + str(key)
                logging.error(error)
                raise ValueError(error)
        # Optional information -> set to default if undefined
        else:
            if not(key in hp_infos):
                hp_infos[key] = value
    return normalize_honeypot_infos(hp_infos)


def normalize_full_server_infos(server_infos):
    '''
    TODO
    '''
    # Retrieve settings from config file
    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    default_server_infos = config['server_infos_default']
    # Normalize server information
    server_infos = normalize_server_infos(server_infos)
    # For each piece of information, check that mandatory ones
    # are defined, then set to default undefined information that
    # are not required
    for key, value in default_server_infos.items():
        # Mandatory information -> must be defined
        if value == 'NOT NULL':
            if not(key in server_infos):
                error = str(id) + "Missing value of " + str(key)
                logging.error(error)
                raise ValueError(error)
            elif(server_infos[key] == ''
                 or server_infos[key] == 0
                 or server_infos[key] is None):
                error = str(id) + "Missing value of " + str(key)
                logging.error(error)
                raise ValueError(error)
        # Optional information -> set to default if undefined
        else:
            if not(key in server_infos):
                server_infos[key] = value
    return normalize_server_infos(server_infos)


def normalize_full_link_infos(lk_infos):
    '''
    TODO
    '''
    # Retrieve settings from config file
    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    default_lk_infos = config['link_infos_default']
    # Normalize link information
    lk_infos = normalize_link_infos(lk_infos)
    # For each piece of information, check that mandatory ones
    # are defined, then set to default undefined information that
    # are not required
    for key, value in default_lk_infos.items():
        # Mandatory information -> must be defined
        if value == 'NOT NULL':
            if not(key in lk_infos):
                error = str(id) + "Missing value of " + str(key)
                logging.error(error)
                raise ValueError(error)
            elif(lk_infos[key] == ''
                 or lk_infos[key] == 0
                 or lk_infos[key] is None):
                error = str(id) + "Missing value of " + str(key)
                logging.error(error)
                raise ValueError(error)
        # Optional information -> set to default if undefined
        else:
            if not(key in lk_infos):
                lk_infos[key] = value
    return normalize_link_infos(lk_infos)


def normalize_full_lhs_infos(lhs_infos):
    '''
    TODO
    '''
    # Define default information for lhs combination
    default_lhs_infos = {
        "id_link": "NOT NULL",
        "id_hp": "NOT NULL",
        "id_serv": "NOT NULL",
        "port": "NOT NULL"
    }
    # Normalize lhs information
    lhs_infos = normalize_lhs_infos(lhs_infos)
    # For each piece of information, check that mandatory ones
    # are defined, then set to default undefined information that
    # are not required
    for key, value in default_lhs_infos.items():
        # Mandatory information -> must be defined
        if value == 'NOT NULL':
            if not(key in lhs_infos):
                error = str(id) + "Missing value of " + str(key)
                logging.error(error)
                raise ValueError(error)
            elif(lhs_infos[key] == '' or lhs_infos[key] == 0):
                error = str(id) + "Missing value of " + str(key)
                logging.error(error)
                raise ValueError(error)
        # Optional information -> set to default if undefined
        else:
            if not(key in lhs_infos):
                lhs_infos[key] = value
    return normalize_lhs_infos(lhs_infos)


def normalize_display_object_infos(object_infos, obj_type, next_type=''):
    '''
    TODO
    '''
    obj_types_possible = ["hp", "serv", "link"]
    if not(obj_type in obj_types_possible
           and (next_type in obj_types_possible or next_type == '')):
        error = str(id) + "Wrong value of " + str(obj_type)
        logging.error(error)
        raise ValueError(error)
    if obj_type != "link":
        next_type = "link"
    elif next_type == '':
        if object_infos["link_nb_hp"] <= object_infos["link_nb_serv"]:
            next_type = "hp"
        else:
            next_type = "serv"
    resultat = normalization_functions.normalize_display(
        object_infos, obj_type, "||||||", next_type)
    last_type = list(set(obj_types_possible) - set([obj_type, next_type]))[0]
    for i in range(len(resultat[next_type + 's'])):
        resultat[next_type + 's'][i] = normalization_functions.normalize_display(
            resultat[next_type + 's'][i],
            next_type,
            "||||",
            last_type
        )
    return resultat


def normalize_display_object_infos_with_tags(
        object_infos,
        obj_type,
        next_type=''):
    '''
    TODO
    '''
    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    separator = config['tag']["separator"]

    obj_types_possible = ["hp", "serv", "link"]
    if not(obj_type in obj_types_possible and (
            next_type in obj_types_possible or next_type == '')):
        error = str(id) + "Wrong value of " + str(obj_type)
        logging.error(error)
        raise ValueError(error)
    if obj_type != "link":
        next_type = "link"
        object_infos[obj_type + "_tags"] = object_infos[
            obj_type +
            "_tags"
        ].replace("||", separator + " ")
    elif next_type == '':
        if object_infos["link_nb_hp"] <= object_infos["link_nb_serv"]:
            next_type = "hp"
        else:
            next_type = "serv"
    if obj_type == "link":
        object_infos[obj_type + "_tags_hp"] = object_infos[
            obj_type + "_tags_hp"
        ].replace("||", separator + " ")
        object_infos[obj_type + "_tags_serv"] = object_infos[
            obj_type + "_tags_serv"
        ].replace("||", separator + " ")

    last_type = list(set(obj_types_possible) - set([obj_type, next_type]))[0]

    for i in range(len(object_infos[next_type + "s"])):
        if next_type != "link":
            object_infos[next_type + "s"][i][next_type + "_tags"] = object_infos[
                next_type + "s"
            ][i][next_type + "_tags"].replace("||", separator + " ")
        else:
            object_infos[next_type + "s"][i][next_type + "_tags_hp"] = object_infos[
                next_type + "s"
            ][i][next_type + "_tags_hp"].replace("||", separator + " ")
            object_infos[next_type + "s"][i][next_type + "_tags_serv"] = object_infos[
                next_type + "s"
            ][i][next_type + "_tags_serv"].replace("||", separator + " ")
        for j in range(len(object_infos[next_type + "s"][i][last_type + "s"])):
            object_infos[next_type + "s"][i][last_type + "s"][j][last_type + "_tags"] = object_infos[
                next_type + "s"
            ][i][last_type + "s"][j][last_type + "_tags"].replace("||", separator + " ")

    return object_infos


def normalize_id_server(id):
    '''
    Normalize server id

    ARGUMENT:
        id (string) : the server id to normalize
    '''
    return normalization_functions.normalize_id('sv', id)


def normalize_id_honeypot(id):
    '''
    Normalize honeypot id

    ARGUMENT:
        id (string) : the honeypot id to normalize
    '''
    return normalization_functions.normalize_id('hp', id)


def normalize_id_link(id):
    '''
    Normalize link id

    ARGUMENT:
        id (string) : the link id to normalize
    '''
    return normalization_functions.normalize_id('lk', id)


def normalize_modif_to_str(modifs):
    '''
    TODO
    '''
    replacement_dict = {"': ": "=", "{'": "", "}": "", ", '": ", "}
    result = str(modifs)
    for key, value in replacement_dict.items():
        result = result.replace(key, value)
    return result


def normalize_conditions_to_str(conditions):
    '''
    TODO
    '''
    replacement_dict = {"': ": "=", "{'": "", "}": "", ", '": " and "}
    result = str(conditions)
    for key, value in replacement_dict.items():
        result = result.replace(key, value)
    return result
