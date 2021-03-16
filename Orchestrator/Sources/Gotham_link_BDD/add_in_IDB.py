# Import external libs
import mariadb
import configparser

# Import Gotham's libs
from . import get_infos
from Gotham_normalize import normalize_full_link_infos, normalize_full_lhs_infos, normalize_full_server_infos, normalize_full_honeypot_infos

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')

# Retrieve settings from config file
config = configparser.ConfigParser()
config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
_separator = config['tag']['separator']

############################### TAG SECTION ###############################


def tag(DB_connection, tag):
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Add the tag to the Tags table
    try:
        cur.execute("INSERT INTO Tags (tag) VALUES (?)", (tag,))
        DB_connection.commit()
        logging.info(f"'{tag}' added in the table 'Tags'")
    except mariadb.Error as e:
        error = str(tag) + " insertion in the table 'Tags' failed : " + str(e)
        logging.error(error)
        raise ValueError(error)

############################### SERVER SECTION ###############################


def server(DB_connection, server_infos):
    # Normalize server_infos
    try:
        server_infos = normalize_full_server_infos(server_infos)
    except Exception as e:
        error = "Bad server infos : " + str(e)
        logging.error(error)
        raise ValueError(error)

    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try:
        # Insert values in Server table
        cur.execute("INSERT INTO Server (id,name,descr,ip,ssh_key,ssh_port,state) VALUES (?,?,?,?,?,?,?)",
                    (server_infos["id"], server_infos["name"], server_infos["descr"],  server_infos["ip"],  server_infos["ssh_key"],  server_infos["ssh_port"],  server_infos["state"]))
        DB_connection.commit()
        # Then link the tags to the server
        tag_list = server_infos['tags'].split(_separator)
        for a_tag in tag_list:
            answer = get_infos.tag(DB_connection, tag=a_tag)
            if answer != []:
                tag_id = answer[0]['id']
            else:
                # Add the tag in the IDB
                try:
                    tag(DB_connection, a_tag)
                except Exception as e:
                    raise ValueError(e)
                # Then retrieve tag id
                answer = get_infos.tag(DB_connection, tag=a_tag)
                tag_id = answer[0]['id']
            # Add the relation between server and tag in Serv_Tags table
            try:
                serv_tags(DB_connection, tag_id, server_infos["id"])
            except Exception as e:
                raise ValueError(e)
        logging.info(f"'{server_infos['id']}' added in the table 'Server'")
    except mariadb.Error as e:
        error = str(server_infos['id']) + \
            " insertion in the table 'Server' failed : " + str(e)
        logging.error(error)
        raise ValueError(error)


def serv_tags(DB_connection, tag_id, id_serv):
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    try:
        cur.execute(
            "INSERT INTO Serv_Tags (id_tag,id_serv) VALUES (?,?)", (tag_id, id_serv))
        DB_connection.commit()
        logging.info(f"'{tag_id}' added in the table 'Serv_Tags'")
    except mariadb.Error as e:
        error = str(tag_id) + " --- " + str(id_serv) + \
            " insertion in the table 'Serv_Tags' failed : " + str(e)
        logging.error(error)
        raise ValueError(error)

############################### HONEYPOT SECTION ###############################


def honeypot(DB_connection, hp_infos):
    # Normalize honeypot_infos
    try:
        hp_infos = normalize_full_honeypot_infos(hp_infos)
    except Exception as e:
        error = "Bad hp infos : " + str(e)
        logging.error(error)
        raise ValueError(error)
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try:
        # Insert values in Honeypot table
        cur.execute("INSERT INTO Honeypot (id,name,descr,port,parser,logs,source,port_container,state) VALUES (?,?,?,?,?,?,?,?,?)",
                    (hp_infos["id"], hp_infos["name"], hp_infos["descr"],  hp_infos["port"], hp_infos["parser"],  hp_infos["logs"],  hp_infos["source"], hp_infos["port_container"], hp_infos["state"]))
        DB_connection.commit()
        # Then link the tags to the honeypot
        tag_list = hp_infos['tags'].split(_separator)
        for a_tag in tag_list:
            answer = get_infos.tag(DB_connection, tag=a_tag)
            if answer != []:
                tag_id = answer[0]['id']
            else:
                # Add the new tag in the IDB
                try:
                    tag(DB_connection, a_tag)
                except Exception as e:
                    raise ValueError(e)
                # Then retrieve the id of the tag
                answer = get_infos.tag(DB_connection, tag=a_tag)
                tag_id = answer[0]['id']
            # Add the relation between honeypot and tag in Hp_Tags table
            try:
                hp_tags(DB_connection, tag_id, hp_infos["id"])
            except Exception as e:
                raise ValueError(e)
        logging.info(f"'{hp_infos['id']}' added in the table 'Honeypot'")
    except mariadb.Error as e:
        error = str(hp_infos['name']) + \
            " insertion in the table 'Honeypot' failed : " + str(e)
        logging.error(error)
        raise ValueError(error)


def hp_tags(DB_connection, tag_id, id_hp):
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    try:
        cur.execute(
            "INSERT INTO Hp_Tags (id_tag,id_hp) VALUES (?,?)", (tag_id, id_hp))
        DB_connection.commit()
        logging.info(f"'{id_hp}' added in the table 'Hp_Tags'")
    except mariadb.Error as e:
        error = str(tag_id) + " --- " + str(id_hp) + \
            " insertion in the table 'Hp_Tags' failed : " + str(e)
        logging.error(error)
        raise ValueError(error)

############################### LINK SECTION ###############################


def link(DB_connection, lk_infos):
    # Normalize link_infos
    try:
        lk_infos = normalize_full_link_infos(lk_infos)
    except Exception as e:
        error = "Bad link infos : " + str(e)
        logging.error(error)
        raise ValueError(error)
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try:
        # Insert values in Link table
        cur.execute("INSERT INTO Link (id,nb_hp,nb_serv,ports) VALUES (?,?,?,?)",
                    (lk_infos["id"], lk_infos["nb_hp"], lk_infos["nb_serv"], lk_infos["ports"]))
        DB_connection.commit()
        # Then link the tags to the link
        tag_hp_list = lk_infos['tags_hp'].split(_separator)
        tag_serv_list = lk_infos['tags_serv'].split(_separator)
        # First, work on tag_hp_list
        for a_tag_hp in tag_hp_list:
            answer = get_infos.tag(DB_connection, tag=a_tag_hp)
            if answer != []:
                tag_id = answer[0]['id']
            # Ff it is a new tag -> add it in the Tags table
            else:
                # Add the new tag in the IDB
                try:
                    tag(DB_connection, a_tag_hp)
                except Exception as e:
                    raise ValueError(e)
                # Then retrieve the id of the new tag
                answer = get_infos.tag(DB_connection, tag=a_tag_hp)
                tag_id = answer[0]['id']
            # Add the relation between Link and hp_tag in Link_Tags_hp table
            link_tags_hp(DB_connection, tag_id, lk_infos["id"])
        # Then, work on tag_serv_list
        for a_tag_serv in tag_serv_list:
            answer = get_infos.tag(DB_connection, tag=a_tag_serv)
            if answer != []:
                tag_id = answer[0]['id']
            # if it is a new tag -> add it in the Tags table
            else:
                # Add the new tag in the IDB
                try:
                    tag(DB_connection, a_tag_serv)
                except Exception as e:
                    raise ValueError(e)
                # Then retrieve the id of the new tag
                answer = get_infos.tag(DB_connection, tag=a_tag_serv)
                tag_id = answer[0]['id']
            # Add the relation between Link and serv_tag in Link_Tags_serv table
            link_tags_serv(DB_connection, tag_id, lk_infos["id"])
        logging.info(f"'{lk_infos['id']}' added in the table 'Link' ")
    except mariadb.Error as e:
        error = str(lk_infos['id']) + \
            " insertion in the table 'Link' failed : " + str(e)
        logging.error(error)
        raise ValueError(error)


def link_tags_hp(DB_connection, tag_id, id_lk):
    cur = DB_connection.cursor()
    try:
        cur.execute(
            "INSERT INTO Link_Tags_hp (id_tag,id_link) VALUES (?,?)", (tag_id, id_lk))
        DB_connection.commit()
        logging.info(
            f"'{tag_id} -- {id_lk}' added in the table 'Link_Tags_hp'")
    except mariadb.Error as e:
        error = str(tag_id) + " --- " + str(id_lk) + \
            " insertion in the table 'Link_Tags_hp' failed : " + str(e)
        logging.error(error)
        raise ValueError(error)


def link_tags_serv(DB_connection, tag_id, id_lk):
    cur = DB_connection.cursor()
    try:
        cur.execute(
            "INSERT INTO Link_Tags_serv (id_tag,id_link) VALUES (?,?)", (tag_id, id_lk))
        DB_connection.commit()
        logging.info(
            f"'{tag_id} -- {id_lk}' added in the table 'Link_Tags_serv'")
    except mariadb.Error as e:
        error = str(tag_id) + " --- " + str(id_lk) + \
            " insertion in the table 'Link_Tags_serv' failed : " + str(e)
        logging.error(error)
        raise ValueError(error)


############################### LHS SECTION ###############################

def link_hp_serv(DB_connection, lhs_infos):
    # Normalize lhs_infos
    try:
        lhs_infos = normalize_full_lhs_infos(lhs_infos)
    except Exception as e:
        error = "Bad lhs infos : " + str(e)
        logging.error(error)
        raise ValueError(error)
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try:
        # Insert values in Link_Hp_Serv table
        cur.execute("INSERT INTO Link_Hp_Serv (id_link,id_hp,id_serv,port) VALUES (?,?,?,?)",
                    (lhs_infos["id_link"], lhs_infos["id_hp"], lhs_infos["id_serv"], lhs_infos["port"]))
        DB_connection.commit()
        logging.info(
            f"'{lhs_infos['id_link']} -- {lhs_infos['id_hp']} -- {lhs_infos['id_serv']}' added in the table 'Link_Hp_Serv'")
    except mariadb.Error as e:
        error = str(lhs_infos['id_link']) + " --- " + str(lhs_infos['id_hp']) + " --- " + str(
            lhs_infos['id_serv']) + " insertion in the table 'Link_Hp_Serv' : " + str(e)
        logging.error(error)
        raise ValueError(error)
