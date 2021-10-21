from . import check_SSH
from . import check_PING
from . import check_TAGS
from . import check_DOUBLON
from . import check_USED_PORT
from . import check_SERVER_PORTS
from . import check_SERVER_REDIRECTS

import mariadb

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


def check_ssh(ip, ssh_port, ssh_key):
    '''
    Check if the orchestrator is able to connect to the server

    ARGUMENTS:
        ip (string) : ip address of the server you want to check
        ssh_port (string) : ssh port of the server you want to check
        ssh_key (string) : ssh key that allow the orchestrator to connect
            to the server you want to check

    Return True if connection succeed, false in the other case
    '''

    return check_SSH.main(ip, ssh_port, ssh_key)


def check_ping(hostname):
    '''
    Check if a host is alive on the network

    ARGUMENTS:
        hostname (string) : ip or hostname of the checked server

    Return True if server is alive, False in the other case
    '''
    return check_PING.main(hostname)


def check_tags(object_type, objects_infos,
               tags_hp='', tags_serv='', mode=False):
    '''
    Determine if tags are really present for a given object

    ARGUMENTS:
        object_type (string) : "hp" or "serv" or "link"
        object_infos (list of dicts) : all information on given object
        tags_hp (string) : honeypot tags
        tags_serv (string) : server tags
        mode (bool) : true for an exact research (there is no other tags),
            false in the other case (it can has other tags)

    Return items of objects_infos which have good tags
    '''
    return check_TAGS.check_tags(
        object_type, objects_infos, tags_hp, tags_serv, mode)


def check_server_ports_is_free(serv_infos, ports):
    '''
    Determine available ports on a server from a specified list

    ARGUMENTS:
        serv_infos (dict) : all informations of the server
        ports (string) : ports we want to check for

    Return the list of available ports presents in the list of given ports
    '''
    return check_SERVER_PORTS.check_server_ports(serv_infos, ports)


def check_servers_ports_matching(servs_infos, ports):
    '''
    Determine available ports on a server from a specified list

    ARGUMENTS:
        serv_infos (dict) : all informations of the server
        ports (string) : ports we want to check for

    Return the list of available ports presents in the list of given ports
    with server information concatenated
    '''
    result = []
    for serv_infos in servs_infos:
        free_ports = check_server_ports_is_free(serv_infos, ports)
        if free_ports != '':
            result.append(dict(
                serv_infos,
                **{"free_ports": free_ports}
            ))

    return result


def check_doublon_server(DB_settings, ip):
    '''
    Check if a server doesn't already exists in the internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal database
        ip (string) : ip of the server you want to check

    Return True if already exists, False in the other case
    '''
    return check_DOUBLON.server(DB_settings, ip)


def check_doublon_tag(DB_settings, tag, table=''):
    '''
    Check if a tag doesn't already exists in the internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal database
        tag (string) : name of the tag you want to check

    Return True if already exists, False in the other case
    '''
    return check_DOUBLON.tag(DB_settings, tag, table=table)


def check_doublon_tags(DB_settings, tags, table=""):
    '''
    Check if all tags already exists in the internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal database
        tags (string) : tags you want to check

    Raise error if tag does not exists
    '''
    try:
        check_DOUBLON.tags(DB_settings, tags, table=table)
    except Exception as e:
        raise ValueError("Error while check doublon tags : " + str(e))


def check_tag_still_used(DB_settings, tag="%", id="%"):
    '''
    Determine where a tag is used

    ARGUMENTS:
        DB_connection (string) : all information to connect to db
        tag (string) : Tag wa want to check for
        id (string) : id of the at gwe want to check

    Return a json containing information on where the tag is used
    '''
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
    except mariadb.Error as e:
        error = "Can't connect to the internal database : " + str(e)
        logging.error(error)
        raise ValueError(error)
    try:
        result = check_TAGS.check_tag_still_used(DB_connection, tag, id)
    except Exception as e:
        raise ValueError(e)
    DB_connection.close()
    return result


def check_used_port(DB_settings):
    '''
    Determine used ports on datacenter side

    ARGUMENTS:
        DB_settings (dict) : all information to connect to db

    Return a list of ports used on the datacenter
    '''
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
    except mariadb.Error as e:
        error = "Can't connect to the internal database : " + str(e)
        logging.error(error)
        raise ValueError(error)
    result = check_USED_PORT.get_used_port(DB_connection)
    DB_connection.close()
    return result


def check_server_redirects(ip_srv, port):
    return check_SERVER_REDIRECTS.main(ip_srv, port)
