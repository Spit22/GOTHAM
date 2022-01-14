import mariadb

from . import get_infos
from . import add_in_IDB
from . import remove_in_IDB
from . import edit_in_IDB

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logger = logging.getLogger('libraries-logger')


def get_server_infos(DB_settings, mode=False, ip="%", id="%",
                     name="%", tags="%", state="%", descr="%", ssh_port="%"):
    '''
    Retrieve a JSON with all the data of one or several servers from the
    internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal
            database
        mode (bool, optional) : False means accurate answer, True means
            extended answer
        ip (string, optional) : ip address of the server whose information
            we want
        id (string, optional) : id of the server whose information we want
        name (string, optional) : name of the server whose information we want
        tags (string, optional) : tag(s) of the server whose information we
            want
        state (string, optional) : state of the server whose information we
            want
        descr (string, optional) : description of the server whose information
            we want
        ssh_port (string, optional) : SSH port of the server whose information
            we want
    '''
    # In case tags="all", replace it with "%"
    if tags.lower() == "all":
        tags = "%"
    # Try to connect to the internal database
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has started"
        )
    except mariadb.Error as e:
        error = f"[GOTHAM LINK BDD] Can't connect to the internal database : {e}"
        logging.error(error)
        raise ValueError(error)
    # Retrieve server information from the internal database
    result = get_infos.server(
        DB_connection,
        mode,
        ip,
        id,
        name,
        tags,
        state,
        descr,
        ssh_port
    )
    # Close the connection to the internal database
    DB_connection.close()
    logging.debug(
        "[GOTHAM LINK BDD] Connection to the internal database has been closed"
    )
    return result


def get_honeypot_infos(DB_settings, mode=False, id="%", name="%", tags="%",
                       state="%", descr="%", port="%", parser="%", logs="%",
                       source="%", port_container="%"):
    '''
    Retrieve a JSON with all the data of one or several honeypots from the
    internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal
            database
        mode (bool, optional) : False means accurate answer, True means
            extended answer
        id (string, optional) : id of the server whose information we want
        name (string, optional) : name of the honeypot whose information
            we want
        tags (string, optional) : tag(s) of the honeypot whose information
            we want
        state (string, optional) : state of the honeypot whose information
            we want
        descr (string, optional) : description of the honeypot whose
            information we want
        port (string, optional) : port of the honeypot whose information
            we want
        parser (string, optional) : parsing rules for the honeypot whose
            information we want
        logs (string, optional) : path of the log files of the honeypot whose
            information we want
        source (string, optional) : path of the dockerfile of the honeypot
            whose information we want
        port_container (string, optional) : container port of the the honeypot
            whose information we want
    '''

    # In case tags="all", replace it with "%"
    if tags.lower() == "all":
        tags = "%"
    # Try to connect to the internal database
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has started"
        )
    except mariadb.Error as e:
        error = f"[GOTHAM LINK BDD] Can't connect to the internal database : {e}"
        logging.error(error)
        raise ValueError(error)
    # Retrieve honeypot information from the internal database
    result = get_infos.honeypot(
        DB_connection,
        mode,
        id,
        name,
        tags,
        state,
        descr,
        port,
        parser,
        logs,
        source,
        port_container
    )
    # Close the connection to the internal database
    DB_connection.close()
    logging.debug(
        "[GOTHAM LINK BDD] Connection to the internal database has been closed"
    )
    return result


def get_link_infos(DB_settings, mode=False, id="%", nb_hp="%",
                   nb_serv="%", tags_hp="%", tags_serv="%"):
    '''
    Retrieve a JSON with all the data of one or several link from the
    internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal
            database
        mode (bool, optional) : False means accurate answer, True means
            extended answer
        id (string, optional) : id of the link whose information we want
        nb_hp (string, optional) : number of honeypots supported by the link
            whose information we want
        nb_serv (string, optional) : number of servers supported by the link
            whose information we want
        tags_hp (string, optional) : tags of the honeypots supported by the
            link whose information we want
        tags_serv (string, optional) : tags of the servers supported by the
            link whose information we want
    '''
    # In case tags_hp="all", replace it with "%"
    if tags_hp.lower() == "all":
        tags_hp = "%"
    # In case tags_serv="all", replace it with "%"
    if tags_serv.lower() == "all":
        tags_serv = "%"
    # Try to connect to the internal database
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has started"
        )
    except mariadb.Error as e:
        error = f"[GOTHAM LINK BDD] Can't connect to the internal database : {e}"
        logging.error(error)
        raise ValueError(error)
    # Retrieve link information from the internal database
    result = get_infos.link(
        DB_connection,
        mode,
        id,
        nb_hp,
        nb_serv,
        tags_hp,
        tags_serv
    )
    # Close the connection to the internal database
    DB_connection.close()
    logging.debug(
        "[GOTHAM LINK BDD] Connection to the internal database has been closed"
    )
    return result


def get_link_hp_serv_infos(DB_settings, mode=False, id="%",
                           nb_hp="%", nb_serv="%", tags_hp="%", tags_serv="%"):
    '''
    Retrieve a JSON with all the data of one or several servers from the
    internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal
            database
        mode (bool, optional) : False means accurate answer, True means
            extended answer
        id (string, optional) : id of the link whose information we want
        nb_hp (string, optional) : number of honeypots supported by the link
            whose information we want
        nb_serv (string, optional) : number of servers supported by the link
            whose information we want
        tags_hp (string, optional) : tags of the honeypots supported by the
            link whose information we want
        tags_serv (string, optional) : tags of the servers supported by the
            link whose information we want
    '''
    # In case tags_hp="all", replace it with "%"
    if tags_hp.lower() == "all":
        tags_hp = "%"
    # In case tags_serv="all", replace it with "%"
    if tags_serv.lower() == "all":
        tags_serv = "%"
    # Try to connect to the internal database
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has started"
        )
    except mariadb.Error as e:
        error = f"[GOTHAM LINK BDD] Can't connect to the internal database : {e}"
        logging.error(error)
        raise ValueError(error)
    # Retrieve link information from the internal database
    result = get_infos.link_force_hp_serv(
        DB_connection,
        mode,
        id,
        nb_hp,
        nb_serv,
        tags_hp,
        tags_serv
    )
    # Close the connection to the internal database
    DB_connection.close()
    logging.debug(
        "[GOTHAM LINK BDD] Connection to the internal database has been closed"
    )
    return result


def get_link_serv_hp_infos(DB_settings, mode=False, id="%",
                           nb_hp="%", nb_serv="%", tags_hp="%", tags_serv="%"):
    '''
    Retrieve a JSON with all the data of one or several servers from the
    internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal
            database
        mode (bool, optional) : False means accurate answer, True means
            extended answer
        id (string, optional) : id of the link whose information we want
        nb_hp (string, optional) : number of honeypots supported by the link
            whose information we want
        nb_serv (string, optional) : number of servers supported by the link
            whose information we want
        tags_hp (string, optional) : tags of the honeypots supported by the
            link whose information we want
        tags_serv (string, optional) : tags of the servers supported by the
            link whose information we want
    '''
    # In case tags_hp="all", replace it with "%"
    if tags_hp.lower() == "all":
        tags_hp = "%"
    # In case tags_serv="all", replace it with "%"
    if tags_serv.lower() == "all":
        tags_serv = "%"
    # Try to connect to the internal database
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has started"
        )
    except mariadb.Error as e:
        error = f"[GOTHAM LINK BDD] Can't connect to the internal database : {e}"
        logging.error(error)
        raise ValueError(error)
    # Retrieve link information from the internal database
    result = get_infos.link_force_serv_hp(
        DB_connection,
        mode,
        id,
        nb_hp,
        nb_serv,
        tags_hp,
        tags_serv
    )
    # Close the connection to the internal database
    DB_connection.close()
    logging.debug(
        "[GOTHAM LINK BDD] Connection to the internal database has been closed"
    )
    return result


def get_tag_infos(DB_settings, mode=False, tag="%", id="%", table=""):
    '''
    Retrieve a JSON with all the data of one or several tags from the internal
    database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal
            database
        mode (bool, optional) : False means accurate answer, True means
            extended answer
        id (string, optional) : id of the tag whose information we want
        tag (string, optional) : name of the tag whose information we want
        table (string, optional) : name of the table of the tag whose
            information we want
    '''
    # In case tag="all", replace it with "%"
    if tag.lower() == "all":
        tag = "%"
    # Try to connect to the internal database
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has started"
        )
    except mariadb.Error as e:
        error = f"[GOTHAM LINK BDD] Can't connect to the internal database : {e}"
        logging.error(error)
        raise ValueError(error)
    # Retrieve link information from the internal database according to the
    # chosen table
    if table == "":
        result = get_infos.tag(DB_connection, mode, tag, id)
    elif table == "hp":
        result = get_infos.tag_hp(DB_connection, mode, tag, id)
    elif table == "serv":
        result = get_infos.tag_serv(DB_connection, mode, tag, id)
    # Close the connection to the internal database
    DB_connection.close()
    logging.debug(
        "[GOTHAM LINK BDD] Connection to the internal database has been closed"
    )
    return result


def add_server_DB(DB_settings, server_infos):
    '''
    Add a server in the internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal
            database
        server_infos (dict) : the informations of the server we want to add
            in the internal database
    '''
    # Try to connect to the internal database
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has started"
        )
    except mariadb.Error as e:
        error = f"[GOTHAM LINK BDD] Can't connect to the internal database : {e}"
        logging.error(error)
        raise ValueError(error)
    # Try to add the server in the internal database
    try:
        add_in_IDB.server(DB_connection, server_infos)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
    except Exception as e:
        error = "Add server in IDB failed : " + str(e)
        logging.error(error)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
        raise ValueError(error)


def add_honeypot_DB(DB_settings, hp_infos):
    '''
    Add a honeypot in the internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal
            database
        hp_infos (dict) : the informations of the honeypot we want to add
            in the internal database
    '''
    # Try to connect to the internal database
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has started"
        )
    except mariadb.Error as e:
        error = f"[GOTHAM LINK BDD] Can't connect to the internal database : {e}"
        logging.error(error)
        raise ValueError(error)
    # Try to add the server in the internal database
    try:
        add_in_IDB.honeypot(DB_connection, hp_infos)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
    except Exception as e:
        error = f"[GOTHAM LINK BDD] Add honeypot in IDB failed : {e}"
        logging.error(error)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
        raise ValueError(error)


def add_link_DB(DB_settings, lk_infos):
    '''
    Add a link in the internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal
            database
        lk_infos (dict) : the informations of the link we want to add
            in the internal database
    '''
    # Try to connect to the internal database
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has started"
        )
    except mariadb.Error as e:
        error = f"[GOTHAM LINK BDD] Can't connect to the internal database : {e}"
        logging.error(error)
        raise ValueError(error)
    # Try to add the server in the internal database
    try:
        add_in_IDB.link(DB_connection, lk_infos)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
    except mariadb.Error as e:
        error = "[GOTHAM LINK BDD] Add link in IDB failed : " + str(e)
        logging.error(error)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
        raise ValueError(error)


def add_lhs_DB(DB_settings, lhs_infos):
    '''
    Add a link-honeypot-server combination in the internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal
            database
        lhs_infos (dict) : the informations of the combination we want to add
            in the internal database
    '''
    # Try to connect to the internal database
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database started"
        )
    except mariadb.Error as e:
        error = f"[GOTHAM LINK BDD] Can't connect to the internal database : {e}"
        logging.error(error)
        raise ValueError(error)
    # Try to add the server in the internal database
    try:
        add_in_IDB.link_hp_serv(DB_connection, lhs_infos)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
    except Exception as e:
        error = f"[GOTHAM LINK BDD] Add combination in IDB failed : {e}"
        logging.error(error)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
        raise ValueError(error)


def remove_server_DB(DB_settings, id):
    '''
    Remove a server from the internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal
            database
        id (string) : the id of the server we want to remove from the internal
            database
    '''
    # Try to connect to the internal database
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has started"
        )
    except mariadb.Error as e:
        error = f"[GOTHAM LINK BDD] Can't connect to the internal database : {e}"
        logging.error(error)
        raise ValueError(error)
    # Try to remove the server from the internal database
    try:
        remove_in_IDB.server(DB_connection, id)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
    except Exception as e:
        error = f"[GOTHAM LINK BDD] Remove server from the IDB failed : {e}"
        logging.error(error)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
        raise ValueError(e)


def remove_server_tags_DB(DB_settings, id="", tag=""):
    '''
    Remove a server tag from the internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal
            database
        id (string) : the id of the server tag we want to remove from
            the internal database
        tag (string) : name of the tag we want to remove from the
            internal database
    '''
    # Try to connect to the internal database
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has started"
        )
    except mariadb.Error as e:
        error = f"[GOTHAM LINK BDD] Can't connect to the internal database : {e}"
        logging.error(error)
        raise ValueError(error)
    # Try to remove the server tag from the internal database
    try:
        remove_in_IDB.server_in_serv_tag(DB_connection, id, tag)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
    except Exception as e:
        error = f"[GOTHAM LINK BDD] Remove server tag from the IDB failed : {e}"
        logging.error(error)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
        raise ValueError(e)


def remove_honeypot_DB(DB_settings, id):
    '''
    Remove a honeypot from the internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal
            database
        id (string) : the id of the honeypot we want to remove from
            the internal database
    '''
    # Try to connect to the internal database
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has started"
        )
    except mariadb.Error as e:
        error = f"[GOTHAM LINK BDD] Can't connect to the internal database : {e}"
        logging.error(error)
        raise ValueError(error)
    # Try to remove the honeypot from the internal database
    try:
        remove_in_IDB.honeypot(DB_connection, id)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
    except Exception as e:
        error = f"[GOTHAM LINK BDD] Remove honeypot from the IDB failed : {e}"
        logging.error(error)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
        raise ValueError(e)


def remove_link_DB(DB_settings, id):
    '''
    Remove a link from the internal database from

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal
            database
        id (string) : the id of the link we want to remove from the
            internal database
    '''
    # Try to connect to the database
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has started"
        )
    except mariadb.Error as e:
        error = f"[GOTHAM LINK BDD] Can't connect to the internal database : {e}"
        logging.error(error)
        raise ValueError(error)
    # Remove the link from the internal database
    try:
        remove_in_IDB.link(DB_connection, id)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
    except Exception as e:
        error = f"[GOTHAM LINK BDD] Remove link from the IDB failed : {e}"
        logging.error(error)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
        raise ValueError(e)


def remove_lhs(DB_settings, id_link="%", id_hp="%", id_serv="%"):
    '''
    Remove a Link/Honeypot/Server combination from the internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal
            database
        id_link (string, optional) : the id of the link we want to remove from
            the internal database
        id_hp (string, optional) : the id of the hp we want to remove from the
            internal database
        id_serv (string, optional) : the id of the serv we want to remove from
            the internal database
    '''
    # Try to connect to the database
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has started"
        )
    except mariadb.Error as e:
        error = f"[GOTHAM LINK BDD] Can't connect to the internal database : {e}"
        logging.error(error)
        raise ValueError(error)
    # Try to remove the link from the internal database
    try:
        remove_in_IDB.lhs(DB_connection, id_link, id_hp, id_serv)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
    except Exception as e:
        error = f"[GOTHAM LINK BDD] Remove combination from the IDB failed : {e}"
        logging.error(error)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
        raise ValueError(e)


def edit_link_DB(DB_settings, modifs, conditions):
    '''
    Edit a link in the internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal
            database
        modifs (dict) : dict of modifications with column:value syntax
        conditions (dict) : dict of conditions with column:value syntax
            (put here the id of the link we want to edit)
    '''
    # Try to connect to the database
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has started"
        )
    except mariadb.Error as e:
        error = f"[GOTHAM LINK BDD] Can't connect to the internal database : {e}"
        logging.error(error)
        raise ValueError(error)
    # Try to edit the link
    try:
        edit_in_IDB.link(DB_connection, modifs, conditions)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
    except Exception as e:
        error = f"[GOTHAM LINK BDD] Edit link in the IDB failed : {e}"
        logging.error(error)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
        raise ValueError(e)


def edit_lhs_DB(DB_settings, modifs, conditions):
    '''
    Edit Link_Hp_Serv table in the internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal
            database
        modifs (dict) : dict of modifications with column:value syntax
        conditions (dict) : dict of conditions with column:value syntax
    '''
    # Try to connect to the database
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has started"
        )
    except mariadb.Error as e:
        error = f"[GOTHAM LINK BDD] Can't connect to the internal database : {e}"
        logging.error(error)
        raise ValueError(error)
    # Try to edit the lhs
    try:
        edit_in_IDB.lhs(DB_connection, modifs, conditions)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
    except Exception as e:
        error = f"[GOTHAM LINK BDD] Edit combination in the IDB failed : {e}"
        logging.error(error)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
        raise ValueError(e)


def edit_honeypot_DB(DB_settings, modifs, conditions):
    '''
    Edit a honeypot in the internal database

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal
            database
        modifs (dict) : dict of modifications with column:value syntax
        conditions (dict) : dict of conditions with column:value syntax
            (put here the id of the honeypot we want to edit)
    '''
    # Try to connect to the database
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has started"
        )
    except mariadb.Error as e:
        error = f"[GOTHAM LINK BDD] Can't connect to the internal database : {e}"
        logging.error(error)
        raise ValueError(error)
    # Try to edit the honeypot
    try:
        edit_in_IDB.honeypot(DB_connection, modifs, conditions)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
    except Exception as e:
        error = f"[GOTHAM LINK BDD] Edit honeypot in the IDB failed : {e}"
        logging.error(error)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
        raise ValueError(e)


def edit_server_DB(DB_settings, modifs, conditions):
    '''
    Edit a server in the internal database from its id

    ARGUMENTS:
        DB_settings (dict) : all the settings to connect to the internal
            database
        modifs (dict) : dict of modifications with column:value syntax
        conditions (dict) : dict of conditions with column:value syntax
            (put here the id of the server we want to edit)
    '''
    # Try to connect to the database
    try:
        DB_connection = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has started"
        )
    except mariadb.Error as e:
        error = f"[GOTHAM LINK BDD] Can't connect to the internal database : {e}"
        logging.error(error)
        raise ValueError(error)
    # Try to edit the server
    try:
        edit_in_IDB.server(DB_connection, modifs, conditions)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
    except Exception as e:
        error = f"[GOTHAM LINK BDD] Edit server in the IDB failed : {e}"
        logging.error(error)
        DB_connection.close()
        logging.debug(
            "[GOTHAM LINK BDD] Connection to the internal database has been closed"
        )
        raise ValueError(e)
