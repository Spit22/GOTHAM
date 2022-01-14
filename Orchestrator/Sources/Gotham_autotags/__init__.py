import configparser

import Gotham_link_BDD

from . import autotags_functions

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logger = logging.getLogger('libraries-logger')


def honeypot(hp_id):
    '''
    Find tags automatically for honeypot

    ARGUMENTS:
        hp_id (string) : id of the honeypot

    Return tags list (string)
    '''

    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    separator = config['tag']['separator']

    # Set tags with trivy
    try:
        trivy_tags = autotags_functions.autotag_by_trivy(hp_id)
        logger.debug(f"[GOTHAM AUTOTAGS] Trivy check executed on honeypot {hp_id}")
    except ValueError as e:
        error = f"[GOTHAM AUTOTAGS] Error while trying to execute ssh command for trivy check on honeypot object (id: {hp_id}) : {e}"
        logger.error(error)
        raise ValueError(error)

    # Set tags with docker top
    try:
        docker_tags = autotags_functions.autotag_by_docker_top(hp_id)
        logger.debug(f"[GOTHAM AUTOTAGS] Tags settings with docker top executed on honeypot {hp_id}")
    except ValueError as e:
        error = f"[GOTHAM AUTOTAGS] Error while trying to execute ssh command for docker top on honeypot object (id: {hp_id}) : {e}"
        logger.error(error)
        raise ValueError(error)

    tags_list = list(set(trivy_tags + docker_tags))
    tags = separator.join(tags_list)
    return tags


def server(DB_settings, serv_id="", serv_ip=""):
    '''
    Find tags automatically for server

    ARGUMENTS:
        DB_settings (json) : auth information
        serv_id (string) : id of the server
        serv_ip (string) : ip of the server

    Return tags list (string)
    Retrieve settings from config file
    '''
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    separator = config['tag']['separator']

    # Case where both arguments are empty
    if serv_id == "" and serv_ip == "":
        error = "[GOTHAM AUTOTAGS] ID or IP address of the server is missing in autotags_server function"
        logger.error(error)
        raise ValueError(error)
    # Case where one of the arguments is empty
    elif (serv_id != "" and serv_ip == "") or (serv_id == "" and serv_ip != ""):
        # Case where server ip is empty
        if serv_id != "" and serv_ip == "":
            try:
                # Retrieve server information with its id
                object_infos = Gotham_link_BDD.get_server_infos(
                    DB_settings,
                    id=str(serv_id)
                )
            except ValueError as e:
                logger.error(e)
                raise ValueError(e)
        # Case where server id is empty
        elif serv_id == "" and serv_ip != "":
            try:
                # Retrieve server information with its ip address
                object_infos = Gotham_link_BDD.get_server_infos(
                    DB_settings,
                    ip=str(serv_ip)
                )
            except ValueError as e:
                logger.error(e)
                raise ValueError(e)
        # Check if the server exists in the IDB
        if object_infos == []:
            logger.error(
                "[GOTHAM AUTOTAGS] You tried to apply autotag to a server that doesn't exists (" + str(serv_id if serv_id != "" else serv_ip) + ")"
            )
            error = "Unknown serv " + \
                str(serv_id if serv_id != "" else serv_ip)
            raise ValueError(error)
        else:
            serv_id = object_infos[0]["serv_id"]
            serv_ip = object_infos[0]["serv_ip"]
    # Set tags with ipstack
    try:
        ipstack_tags = autotags_functions.autotag_by_ipstack(serv_ip)
        logger.debug("[GOTHAM AUTOTAGS] Tags settings with ipstack executed on server " + str(serv_id if serv_id != "" else serv_ip))
    except ValueError as e:
        error = "[GOTHAM AUTOTAGS] Error while trying to get geolocation informations on serv (" + str(serv_id if serv_id != "" else serv_ip) + ") : " + str(e)
        logger.error(error)
        raise ValueError(error)
    tags_list = list(set(ipstack_tags))
    tags = separator.join(tags_list)
    return tags
