import mariadb
import sys
from . import get_infos
from . import add_in_IDB

########## READ IN THE INTERNAL DATABASE ##########
def get_server_infos(DB_settings, mode=False, ip="%", id="%", name="%", tag="%", state="%"):
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
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB server: {e}")
        sys.exit(1)
    result = get_infos.server(DB_connection, mode, ip, id, name, tag, state)
    DB_connection.close()
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
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB server: {e}")
        sys.exit(1)
    result = get_infos.tag(DB_connection, mode, tag, id)
    DB_connection.close()
    return result

#def get_honeypot_infos(DB_settings, ...):

#def get_link_infos(DB_settings, ...):


########## WRITE IN THE INTERNAL DATABASE ##########
def add_server_DB(DB_settings, server_infos):
    '''
    Add a server in the internal database and returns a boolean

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
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB server: {e}")
        sys.exit(1)
    return add_in_IDB.server(DB_connection, server_infos)


#def add_honeypot_DB(DB_settings, ...):

#def add_link_DB(DB_settings, ...):