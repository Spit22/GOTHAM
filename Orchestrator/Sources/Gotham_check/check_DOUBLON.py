# Import libraries
from Gotham_link_BDD import get_server_infos, get_tag_infos
import configparser

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


def server(DB_settings, ip):
    # Check if a server is already present in database
    #
    # DB_settings (json) : auth information
    # ip (string) : ip of the server we want to check
    #
    # Return True if already exists, False in the other case

    response = get_server_infos(DB_settings, ip=ip)
    return not(response == [])


def tag(DB_settings, tag, table=''):
    # Check if a tag is already present in database
    #
    # DB_settings (json) : auth information
    # tag (string) : tag we want to check
    #
    # Return True if already exists, False in the other case

    response = get_tag_infos(DB_settings, tag=tag, table=table)
    return not(response == [])


def tags(DB_settings, tags, table=""):
    # Check if tags is already present in database
    #
    # DB_settings (json) : auth information
    # tags (string) : tags we want to check
    #
    # Raise error if tag does not exists

    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    separator = config['tag']['separator']
    tags_list = tags.split(separator)
    for a_tag in tags_list:
        if not(tag(DB_settings, tag=a_tag, table=table)):
            error = str(a_tag) + " : tag does not exists"
            logging.error(error)
            raise ValueError(error)
