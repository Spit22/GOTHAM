from . import check_SSH
from . import check_PING
from . import check_TAGS
from . import check_DOUBLON
from . import check_USED_PORT
from . import check_SERVER_PORTS
from . import check_SERVER_REDIRECTS
import mariadb
import sys

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')

def check_ssh(ip, ssh_port, ssh_key):
    '''
    Check if the orchestrator is able to connect to the server

    ARGUMENTS:
        ip (string) : ip address of the server you want to check
        ssh_port (string) : ssh port of the server you want to check
        ssh_key (string) : ssh key that allow the orchestrator to connect to the server you want to check
    '''
    return check_SSH.main(ip, ssh_port, ssh_key)

def check_ping(hostname):
    return check_PING.main(hostname)

def check_tags(object_type, objects_infos, tags_hp='', tags_serv='', mode=False):
    return check_TAGS.check_tags(object_type, objects_infos, tags_hp, tags_serv, mode)

def check_server_ports_is_free(serv_infos, ports):
    return check_SERVER_PORTS.check_server_ports(serv_infos, ports)

def check_servers_ports_matching(servs_infos, ports):
    result=[]
    for serv_infos in servs_infos:
        free_ports=check_server_ports_is_free(serv_infos, ports)
        if free_ports!='':
            result.append(dict(serv_infos,**{"free_ports":free_ports}))

    return result

def check_doublon_server(DB_settings, ip):
    '''
    Check if a server doesn't already exists in the internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal database
        ip (string) : ip of the server you want to check
    '''
    return check_DOUBLON.server(DB_settings, ip)

def check_doublon_tag(DB_settings, tag):
    '''
    Check if a tag doesn't already exists in the internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal database
        tag (string) : name of the tag you want to check
    '''
    return check_DOUBLON.tag(DB_settings, tag)

def check_doublon_tags(DB_settings, tags):
    '''
    Check if all tags already exists in the internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal database
        tags (string) : tags you want to check
    '''
    try:
        check_DOUBLON.tags(DB_settings, tags)
    except:
        sys.exit(1)

def check_tag_still_used(DB_settings, tag="%", id="%"):
    '''
    Check if tag is still used by a honeypot or a server

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal database
        tag (string): tag
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
        logging.error(f"Can't connect to the internal database : {e}")
        sys.exit(1)
    try:
        result = check_TAGS.check_tag_still_used(DB_connection, tag,id)
    except:
        sys.exit(1)
    DB_connection.close()
    return result

def check_used_port(DB_settings):
    '''
    Retrieve a list of all used port by honeypots from the internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal database
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
        logging.error(f"Can't connect to the internal database : {e}")
        sys.exit(1)
    result = check_USED_PORT.get_used_port(DB_connection)
    DB_connection.close()
    return result

def check_server_redirects(ip_srv, port):
    return check_SERVER_REDIRECTS.main(ip_srv, port)
    
