# Import libraries
import configparser

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


def weighting_nb_link(object_type, objects_infos):
    '''
    Add a weight corresponding to the number of links associated with each object 

    ARGUMENTS:
        objects_infos (list of dict) : list of potentials objects
    '''

    if (object_type != "hp" and object_type != "serv"):
        error = str(object_type) + " is uncorrect"
        logging.error(error)
        raise ValueError(error)

    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')

    weight = int(config[object_type+'_weight']["nb_link"])

    objects_infos = [{**object_infos, **{"weight": int(object_infos["weight"])+(weight*int(len(object_infos["link_id"].split("||||||"))))}} if (
        object_infos["link_id"] != '' and not(object_infos["link_id"] is None) and object_infos["link_id"] != 'NULL') else object_infos for object_infos in objects_infos]

    return objects_infos


def weighting_nb_port(servs_infos):
    '''
    Add a weight corresponding to the number of port used by each server 

    ARGUMENTS:
        servs_infos (list of dict) : list of potentials server
    '''

    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')

    weight = int(config['serv_weight']["nb_port_used"])

    servs_infos = [{**serv_infos, **{"weight": int(serv_infos["weight"])+(weight*int(len(serv_infos["lhs_port"].replace("||||||", "||||").split("||||"))))}} if (
        serv_infos["lhs_port"] != '' and not(serv_infos["lhs_port"] is None) and serv_infos["lhs_port"] != 'NULL') else serv_infos for serv_infos in servs_infos]

    return servs_infos


def weighting_state(object_type, objects_infos):
    '''
    Add a weight corresponding to the state associated with each object 

    ARGUMENTS:
        object_type (string) : hp or serv ; define the object type
        objects_infos (list of dict) : list of potentials objects
    '''
    if (object_type != "hp" and object_type != "serv"):
        error = str(object_type) + " is uncorrect"
        logging.error(error)
        raise ValueError(error)

    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')

    weights = dict(config.items(object_type+'_weight'))

    objects_infos = [{**object_infos, **{"weight": int(object_infos["weight"])+int(weights[object_infos[object_type+"_state"].lower()])}} if object_infos[object_type+"_state"].lower(
    ) in weights else {**object_infos, **{"weight": int(object_infos["weight"])+int(max([int(i) for i in weights.values()]))}} for object_infos in objects_infos]

    return objects_infos


def weighting_nb_useless_tags(object_type, objects_infos, tags):
    '''
    Add a weight corresponding to the number of useless tags associated with each object 

    ARGUMENTS:
            object_type (string) : hp or serv ; define the object type
            objects_infos (list of dict) : list of potentials objects
            tags (string) : list of desired tags
    '''
    if (object_type != "hp" and object_type != "serv"):
        error = str(object_type) + " is uncorrect"
        logging.error(error)
        raise ValueError(error)

    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')

    weight = int(config[object_type+'_weight']["nb_useless_tag"])

    separator = config['tag']['separator']
    tags_list = tags.lower().split(separator)

    objects_infos = [{**object_infos, **{"weight": int(object_infos["weight"])+(weight*int(int(len(object_infos[object_type+"_tags"].lower().split(
        '||')))-int(len(set(object_infos[object_type+"_tags"].lower().split('||')).intersection(tags_list)))))}} for object_infos in objects_infos]

    return objects_infos


def weighting_nb_free_port(servs_infos):
    '''
    Add a weight corresponding to the number of useless tags associated with each object 

    ARGUMENTS:
        servs_infos (list of dict) : list of potentials servs
    '''

    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')

    weight = int(config['serv_weight']["nb_free_port"])

    separator = config['port']['separator']

    servs_infos = [{**serv_infos, **{"weight": int(serv_infos["weight"])+(weight*int(
        len(serv_infos["free_ports"].split(separator))))}} for serv_infos in servs_infos]

    return servs_infos


def weighting_time(object_type, objects_infos, column):
    '''
    Add a weight corresponding to the created at and updated at associated with each object 

    ARGUMENTS:
            object_type (string) : hp or serv ; define the object type
            objects_infos (list of dict) : list of potentials objects
            column (string) : created_at or updated_at
    '''

    if (object_type != "hp" and object_type != "serv"):
        error = str(object_type) + " is uncorrect"
        logging.error(error)
        raise ValueError(error)

    if (column != "created_at" and column != "updated_at"):
        error = str(object_type) + " is uncorrect"
        logging.error(error)
        raise ValueError(error)

    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')

    weight = int(config[object_type+'_weight'][column])

    timestamp_list = [float(object_infos[object_type+"_"+column].timestamp()) for object_infos in objects_infos if (object_infos[object_type +
                                                                                                                                 '_'+column] != '' and not(object_infos[object_type+'_'+column] is None) and object_infos[object_type+'_'+column] != 'NULL')]
    max_time = max(timestamp_list)
    min_time = min(timestamp_list)
    if max_time > min_time:
        objects_infos = [{**object_infos, **{"weight": int(object_infos["weight"])+round(float(weight)*(float(object_infos[object_type+'_'+column].timestamp())-min_time)/(max_time-min_time))}} if (object_infos[object_type+'_'+column] != '' and not(
            object_infos[object_type+'_'+column] is None) and object_infos[object_type+'_'+column] != 'NULL') else {**object_infos, **{"weight": int(object_infos["weight"])+round(float(weight)/2)}} for object_infos in objects_infos]

    return objects_infos
