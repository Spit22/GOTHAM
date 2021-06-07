from . import selection_function

import configparser

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


def choose_honeypots(hps_infos, nb_hp, tags_hp, del_weight=False):
    '''
    Choose the best honeypots when creating a link according to the need

    ARGUMENTS:
        hps_infos (list of dict) : list of potentials honeypots
        nb_hp (int) : number of honeypot wanted
        tags_hp (string) : Honeypot tags mentioned in the link
        del_weight (boolean) : Allows you to delete the weight field in the
            object if set to True

    Return list of dict of hp sort by weight, with nb_hp length
    '''
    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    # Retrieve the base weight
    base_weight = int(config['weight_base']["hp"])

    # Adds the weight field in all hp dictionaries that do not have this field
    weighted_hps_infos = []
    for hp_infos in hps_infos:
        if not('weight' in hp_infos.keys()):
            weighted_hps_infos.append(
                dict(hp_infos, **{'weight': base_weight}))
        else:
            weighted_hps_infos.append(
                {**hp_infos,
                 **{"weight": int(hp_infos["weight"]) + (base_weight)}}
            )

    object_type = "hp"

    # Add weight based on link number using each hp
    weighted_hps_infos = selection_function.weighting_nb_link(
        object_type, weighted_hps_infos)

    # Add weight based on port number used by each hp
    weighted_hps_infos = selection_function.weighting_nb_port(
        weighted_hps_infos)

    # Add weight if the hp is a duplicat
    weighted_hps_infos = selection_function.weighting_duplicat(
        weighted_hps_infos)

    # Add weight based on the state of each hp
    weighted_hps_infos = selection_function.weighting_state(
        object_type, weighted_hps_infos)

    # Add weight based on useless tag number of each hp for the link
    weighted_hps_infos = selection_function.weighting_nb_useless_tags(
        object_type, weighted_hps_infos, tags_hp)

    # Add weight based on created time of each hp
    weighted_hps_infos = selection_function.weighting_time(
        object_type, weighted_hps_infos, "created_at")

    # Add weight based on updated time of each hp
    weighted_hps_infos = selection_function.weighting_time(
        object_type, weighted_hps_infos, "updated_at")

    # Reduces the number if not enough hp
    if len(weighted_hps_infos) < nb_hp:
        nb_hp = len(weighted_hps_infos)

    # Sort hp by weight
    result = sorted(weighted_hps_infos, key=lambda k: k['weight'])[0:nb_hp]

    # Clean Weight if bool is set to True
    if del_weight:
        for i in range(len(result)):
            del result[i]["weight"]

    return result


def choose_servers(servs_infos, nb_serv, tags_serv, del_weight=False):
    '''
    Choose the best servers when creating a link according to the need

    ARGUMENTS:
        servs_infos (list of dict) : list of potentials servers
        nb_serv (int) : number of server wanted
        tags_serv (string) : server tags mentioned in the link
        del_weight (boolean) : Allows you to delete the weight field in
            the object if set to True

    Return list of dict of serv sort by weight, with nb_serv length
    '''

    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    # Retrieve the base weight
    base_weight = int(config['weight_base']["serv"])

    # Adds the weight field in all serv dictionaries that do not have this
    # field
    weighted_servs_infos = []
    for serv_infos in servs_infos:
        if not('weight' in serv_infos.keys()):
            weighted_servs_infos.append(
                dict(serv_infos, **{'weight': base_weight}))
        else:
            weighted_servs_infos.append(
                {**serv_infos,
                 **{"weight": int(serv_infos["weight"]) + (base_weight)}}
            )

    object_type = "serv"

    # Add weight based on link number using each serv
    weighted_servs_infos = selection_function.weighting_nb_link(
        object_type, weighted_servs_infos)

    # Add weight based on port number used by each serv
    weighted_servs_infos = selection_function.weighting_nb_port(
        weighted_servs_infos)

    # Add weight based on the state of each serv
    weighted_servs_infos = selection_function.weighting_state(
        object_type, weighted_servs_infos)

    # Add weight based on useless tag number of each serv for the link
    weighted_servs_infos = selection_function.weighting_nb_useless_tags(
        object_type, weighted_servs_infos, tags_serv)

    # Add weight based on free port number of each serv for the link
    weighted_servs_infos = selection_function.weighting_nb_free_port(
        weighted_servs_infos)

    # Add weight based on created time of each serv
    weighted_servs_infos = selection_function.weighting_time(
        object_type, weighted_servs_infos, "created_at")

    # Add weight based on updated time of each serv
    weighted_servs_infos = selection_function.weighting_time(
        object_type, weighted_servs_infos, "updated_at")

    # Sort serv by weight
    result = sorted(weighted_servs_infos, key=lambda k: k['weight'])[0:nb_serv]

    # Clean Weight if bool is set to True
    if del_weight:
        for i in range(len(result)):
            del result[i]["weight"]

    return result
