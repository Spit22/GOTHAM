# Import external libs
import mariadb
import sys

# Import GOTHAM's libs
from . import get_infos
from . import add_in_IDB
from . import remove_in_IDB
from Gotham_normalize import normalize_id_server,normalize_id_honeypot,normalize_id_link

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')

########## READ THINGS IN THE INTERNAL DATABASE ##########

def get_server_infos(DB_settings, mode=False, ip="%", id="%", name="%", tags="%", state="%", descr="%", ssh_port="%"):
    '''
    Retrieve a JSON with all the data of one or several servers from the internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal database
        mode (bool, optional) : False means accurate answer, True means extended answer
        ip (string, optional) : ip address of the server whose data we want
        id (string, optional) : id of the server whose data we want
        name (string, optional) : name of the server whose data we want
        tag (string, optional) : tag of the server whose data we want
        state (string, optional) : state of the server whose data we want
    '''
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(f"[+] Connection to the internal database started")
    except mariadb.Error as e:
        logging.error(f"Can't connect to the internal database : {e}")
        sys.exit(1)
    result = get_infos.server(DB_connection, mode, ip, id, name, tags, state, descr, ssh_port)
    DB_connection.close()
    logging.debug(f"[-] Connection to the internal database closed")
    return result

def get_honeypot_infos(DB_settings, mode=False, id="%", name="%", tags="%", state="%", descr="%", port="%", parser="%", logs="%", source="%", port_container="%"):
    '''
    Retrieve a JSON with all the data of one or several servers from the internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal database
        mode (bool, optional) : False means accurate answer, True means extended answer
        ip (string, optional) : ip address of the server whose data we want
        id (string, optional) : id of the server whose data we want
        name (string, optional) : name of the server whose data we want
        tag (string, optional) : tag of the server whose data we want
        state (string, optional) : state of the server whose data we want
    '''
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(f"[+] Connection to the internal database started")
    except mariadb.Error as e:
        logging.error(f"Can't connect to the internal database : {e}")
        sys.exit(1)
    result = get_infos.honeypot(DB_connection, mode, id, name, tags, state, descr, port, parser, logs, source, port_container)
    DB_connection.close()
    logging.debug(f"[-] Connection to the internal database closed")
    return result

def get_link_infos(DB_settings, mode=False, id="%", nb_hp="%", nb_serv="%", tags_hp="%", tags_serv="%"):
    '''
    Retrieve a JSON with all the data of one or several servers from the internal database

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
        logging.debug(f"[+] Connection to the internal database started")
    except mariadb.Error as e:
        logging.error(f"Can't connect to the internal database : {e}")
        sys.exit(1)
    result = get_infos.link(DB_connection, mode, id, nb_hp, nb_serv, tags_hp, tags_serv)
    DB_connection.close()
    logging.debug(f"[-] Connection to the internal database closed")
    return result

def get_link_hp_serv_infos(DB_settings, mode=False, id="%", nb_hp="%", nb_serv="%", tags_hp="%", tags_serv="%"):
    '''
    Retrieve a JSON with all the data of one or several servers from the internal database

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
        logging.debug(f"[+] Connection to the internal database started")
    except mariadb.Error as e:
        logging.error(f"Can't connect to the internal database : {e}")
        sys.exit(1)
    result = get_infos.link_force_hp_serv(DB_connection, mode, id, nb_hp, nb_serv, tags_hp, tags_serv)
    DB_connection.close()
    logging.debug(f"[-] Connection to the internal database closed")
    return result

def get_link_serv_hp_infos(DB_settings, mode=False, id="%", nb_hp="%", nb_serv="%", tags_hp="%", tags_serv="%"):
    '''
    Retrieve a JSON with all the data of one or several servers from the internal database

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
        logging.debug(f"[+] Connection to the internal database started")
    except mariadb.Error as e:
        logging.error(f"Can't connect to the internal database : {e}")
        sys.exit(1)
    result = get_infos.link_force_serv_hp(DB_connection, mode, id, nb_hp, nb_serv, tags_hp, tags_serv)
    DB_connection.close()
    logging.debug(f"[-] Connection to the internal database closed")
    return result

def get_tag_infos(DB_settings, mode=False, tag="%", id="%"):
    '''
    Retrieve a JSON with all the data of one or several tags from the internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal database
        mode (bool, optional) : False means accurate answer, True means extended answer
        id (string, optional) : id of the tag whose data we want
        tag (string, optional) : name of the tag whose data we want
    '''
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(f"[+] Connection to the internal database started")
    except mariadb.Error as e:
        logging.error(f"Can't connect to the internal database : {e}")
        sys.exit(1)
    result = get_infos.tag(DB_connection, mode, tag, id)
    DB_connection.close()
    logging.debug(f"[-] Connection to the internal database closed")
    return result

########## ADD THINGS IN THE INTERNAL DATABASE ##########

def add_server_DB(DB_settings, server_infos):
    '''
    Add a server in the internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal database
        server_infos (dict) : the informations of the server we want to add in the internal database
    '''
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(f"[+] Connection to the internal database started")
    except mariadb.Error as e:
        logging.error(f"Can't connect to the internal database : {e}")
        sys.exit(1)
    try:
        add_in_IDB.server(DB_connection, server_infos)
        DB_connection.close()
        logging.debug(f"[-] Connection to the internal database closed")
    except:
        sys.exit(1)

def add_honeypot_DB(DB_settings, hp_infos):
    '''
    Add a honeypot in the internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal database
        hp_infos (dict) : the informations of the honeypot we want to add in the internal database
    '''
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(f"[+] Connection to the internal database started")
    except mariadb.Error as e:
        logging.error(f"Can't connect to the internal database : {e}")
        sys.exit(1)
    try:
        add_in_IDB.honeypot(DB_connection, hp_infos)
        DB_connection.close()
        logging.debug(f"[-] Connection to the internal database closed")
    except:
        sys.exit(1)

def add_link_DB(DB_settings, lk_infos):
    '''
    Add a link in the internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal database
        lk_infos (dict) : the informations of the honeypot we want to add in the internal database
    '''
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(f"[+++++] Connection to the internal database started")
    except mariadb.Error as e:
        logging.error(f"Can't connect to the internal database : {e}")
        sys.exit(1)
    try:
        add_in_IDB.link(DB_connection, lk_infos)
        DB_connection.close()
        logging.debug(f"[------] Connection to the internal database closed")
    except:
        logging.error(f"Add link DB failed : {e}")
        sys.exit(1)

def add_lhs_DB(DB_settings, lhs_infos):
    '''
    Add a link-honeypot-server combination in the internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal database
        lhs_infos (dict) : the informations of the combination we want to add in the internal database
    '''
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(f"[+] Connection to the internal database started")
    except mariadb.Error as e:
        logging.error(f"Can't connect to the internal database : {e}")
        sys.exit(1)
    try:
        add_in_IDB.link_hp_serv(DB_connection, lhs_infos)
        DB_connection.close()
        logging.debug(f"[-] Connection to the internal database closed")
    except:
        sys.exit(1)

########## REMOVE IN THE INTERNAL DATABASE ##########

def remove_server_DB(DB_settings, id):
    '''
    Remove a server in the internal database from its id
    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal database
        id (string) : the id of the server we want to remove in the internal database
    '''
    # Connect to the database
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(f"[+] Connection to the internal database started")
    except mariadb.Error as e:
        logging.error(f"Can't connect to the internal database : {e}")
        sys.exit(1)
    # Remove the server in the IDB
    try:
        remove_in_IDB.server(DB_connection, id)
        DB_connection.close()
        logging.debug(f"[-] Connection to the internal database closed")
    except:
        sys.exit(1)

def remove_honeypot_DB(DB_settings, id):
    '''
    Remove a honeypot in the internal database from its id

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal database
        id (string) : the id of the honeypot we want to remove in the internal database
    '''
    # Connect to the database
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(f"[+] Connection to the internal database started")
    except mariadb.Error as e:
        logging.error(f"Can't connect to the internal database : {e}")
        sys.exit(1)
    # Remove the Honeypot
    try:
        remove_in_IDB.honeypot(DB_connection, id)
        DB_connection.close()
        logging.debug(f"[-] Connection to the internal database closed")
    except:
        sys.exit(1)

def remove_link_DB(DB_settings, id):
    '''
    Remove a link in the internal database from its id

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal database
        id (string) : the id of the link we want to remove in the internal database
    '''
    # Connect to the database
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(f"[+] Connection to the internal database started")
    except mariadb.Error as e:
        logging.error(f"Can't connect to the internal database : {e}")
        sys.exit(1)
    # Remove the link
    try:
        remove_in_IDB.link(DB_connection, id)
        DB_connection.close()
        logging.debug(f"[-] Connection to the internal database closed")
    except:
        sys.exit(1)
