from Gotham_link_BDD import get_server_infos, get_tag_infos
import configparser

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logger = logging.getLogger('libraries-logger')


def server(DB_settings, ip):
    '''
    Check if a server is already present in database

    ARGUMENTS:
        DB_settings (json) : auth information
        ip (string) : ip of the server we want to check

    Return True if already exists, False in the other case
    '''
    try:
        response = get_server_infos(DB_settings, ip=ip)
    except Exception as e:
        error = f"[GOTHAM CHECK] get_server_infos failed : {e}"
        raise ValueError(error)
    return not(response == [])


def check_doublon_tag(DB_settings, tag, table=''):
    '''
    Check if a tag is already present in database

    ARGUMENTS:
        DB_settings (json) : auth information
        tag (string) : tag we want to check

    Return True if already exists, False in the other case
    '''
    try:
        response = get_tag_infos(DB_settings, tag=tag, table=table)
    except Exception as e:
        error = f"[GOTHAM CHECK] get_tag_infos failed : {e}"
        raise ValueError(error)
    return not(response == [])


def check_doublon_set_of_tag(DB_settings, tags, table=""):
    '''
    Check if a set of tags is already present in database

    ARGUMENTS:
        DB_settings (json) : auth information
        tags (string) : tags we want to check

    Raise error if tag does not exists
    '''
    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    separator = config['tag']['separator']
    tag_list = tags.split(separator)
    # For each tag in the set of tag, check if its
    # already in the database with tag function
    for a_tag in tag_list:
        try:
            check_a_tag = check_doublon_tag(DB_settings, tag=a_tag, table=table)
        except Exception as e:
            error = f"[GOTHAM CHECK] check_doublon_tag failed : {e}"
            raise ValueError(error)
        if not(check_a_tag):
            error = f"[GOTHAM CHECK] Tag does not exists : {a_tag}"
            logger.error(error)
            raise ValueError(error)
