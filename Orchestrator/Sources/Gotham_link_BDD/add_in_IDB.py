
import mariadb
import sys
import os
import configparser
import sys

from . import get_infos

#sys.path.append('/home/spitfire/GOTHAM/Orchestrator/Sources')

############################### TAG SECTION ###############################

# Retrieve settings from config file
config = configparser.ConfigParser()
config.read('Orchestrator/Config/config.ini')
_separator = config['tag']['separator']

def tag(DB_connection, tag):
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Add the tag to the Tags table
    try:
        cur.execute("INSERT INTO Tags (tag) VALUES (?)",(tag,))
        DB_connection.commit()
        return True
    except mariadb.Error as e:
        print(f"[+]Error inserting data in the database: {e}")
        return False


############################### SERVER SECTION ###############################

def normalize_dico_server_infos(server_infos):
    default_server_infos = config['server_infos_default']
    for key, value in default_server_infos.items():
        if value == 'NOT NULL':
            if not(key in server_infos):
                sys.exit("Database error: you must fill this field: "+key)
            elif(server_infos[key] == '' or server_infos[key] == 0):
                sys.exit("Database error: you must fill this field: "+key)
        else:
            if not(key in server_infos):
                server_infos[key] = value
    return server_infos

def server(DB_connection, server_infos):
    # Normalize server_infos
    server_infos = normalize_dico_server_infos(server_infos)
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try:
        # Insert values in Server table
        cur.execute("INSERT INTO Server (id,name,descr,ip,ssh_key,ssh_port,state) VALUES (?,?,?,?,?,?,?)", (server_infos["id"], server_infos["name"], server_infos["descr"],  server_infos["ip"],  server_infos["ssh_key"],  server_infos["ssh_port"],  server_infos["state"]))
        # Then link the tags to the server
        tag_list = server_infos['tag'].split(_separator)
        for a_tag in tag_list:
            answer = get_infos.tag(DB_connection, tag=a_tag)
            if answer != []:
                tag_id = answer[0]['id']
            else:
                if tag(DB_connection, a_tag):
                    answer = get_infos.tag(DB_connection, tag=a_tag)
                    tag_id = answer[0]['id']
                else:
                    sys.exit("Error trying to insert tag in internal database")
            serv_tags(DB_connection, tag_id, server_infos["id"])
            DB_connection.commit()
        return True
    except mariadb.Error as e:
        print(f"Error inserting data in the database: {e}")
        return False

def serv_tags(DB_connection, tag_id, id_serv):
    cur = DB_connection.cursor()
    try:
        cur.execute("INSERT INTO Serv_Tags (id_tag,id_serv) VALUES (?,?)", (tag_id,id_serv))
        DB_connection.commit()
        return True
    except mariadb.Error as e:
        print(f"Error inserting data in the database: {e}")
        return False

############################### HONEYPOT SECTION ###############################

def normalize_dico_honeypot_infos(hp_infos):
    default_hp_infos = config['honeypot_infos_default']
    for key, value in default_hp_infos.items():
        if value == 'NOT NULL':
            if not(key in hp_infos):
                sys.exit("Database error: you must fill this field: "+key)
            elif(hp_infos[key] == '' or hp_infos[key] == 0):
                sys.exit("Database error: you must fill this field: "+key)
        else:
            if not(key in hp_infos):
                hp_infos[key] = value
    return hp_infos

def honeypot(DB_connection, hp_infos):
    # Normalize honeypot_infos
    hp_infos = normalize_dico_honeypot_infos(hp_infos)
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try:
        # Insert values in Honeypot table
        cur.execute("INSERT INTO Honeypot (id,name,descr,port,parser,logs,source,id_container,state) VALUES (?,?,?,?,?,?,?,?,?)", (hp_infos["id"], hp_infos["name"], hp_infos["descr"],  hp_infos["port"], hp_infos["parser"],  hp_infos["logs"],  hp_infos["source"], hp_infos["id_container"], hp_infos["state"]))
        # Then link the tags to the honeypot
        tag_list = hp_infos['tag'].split(_separator)
        for a_tag in tag_list:
            answer = get_infos.tag(DB_connection, tag=a_tag)
            if answer != []:
                tag_id = answer[0]['id']
            else:
                if tag(DB_connection, a_tag):
                    answer = get_infos.tag(DB_connection, tag=a_tag)
                    tag_id = answer[0]['id']
                else:
                    sys.exit("Error trying to insert tag in internal database")
            hp_tags(DB_connection, tag_id, hp_infos["id"])
            DB_connection.commit()
        return True
    except mariadb.Error as e:
        print(f"Error inserting data in the database: {e}")
        return False

def hp_tags(DB_connection, tag_id, id_hp):
    cur = DB_connection.cursor()
    try:
        cur.execute("INSERT INTO Hp_Tags (id_tag,id_hp) VALUES (?,?)", (tag_id,id_hp))
        DB_connection.commit()
        return True
    except mariadb.Error as e:
        print(f"Error inserting data in the database: {e}")
        return False

############################### LINK SECTION ###############################

def normalize_dico_link_infos(lk_infos):
    default_lk_infos = config['link_infos_default']
    for key, value in default_lk_infos.items():
        if value == 'NOT NULL':
            if not(key in lk_infos):
                sys.exit("Database error: you must fill this field: "+key)
            elif(lk_infos[key] == '' or lk_infos[key] == 0):
                sys.exit("Database error: you must fill this field: "+key)
        else:
            if not(key in lk_infos):
                lk_infos[key] = value
    return lk_infos

def link(DB_connection, lk_infos):
    # Normalize link_infos
    lk_infos = normalize_dico_link_infos(lk_infos)
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try:
        # Insert values in Link table
        cur.execute("INSERT INTO Link (id,nb_hp,nb_serv) VALUES (?,?,?)", (lk_infos["id"], lk_infos["nb_hp"], lk_infos["nb_serv"]))
        # Then link the tags to the link
        tag_hp_list = lk_infos['tag_hp'].split(_separator)
        tag_serv_list = lk_infos['tag_serv'].split(_separator)
        # Work on tag_hp_list
        for a_tag_hp in tag_hp_list:
            answer = get_infos.tag(DB_connection, tag=a_tag_hp)
            if answer != []:
                tag_id = answer[0]['id']
            # if it is a new tag -> add it in the Tags table
            else:
                if tag(DB_connection, a_tag_hp):
                    answer = get_infos.tag(DB_connection, tag=a_tag_hp)
                    tag_id = answer[0]['id']
                else:
                    sys.exit("Error trying to insert tag_hp in internal database")
            link_tags_hp(DB_connection, tag_id, lk_infos["id"])
            DB_connection.commit()
        # work on tag_serv_list
        for a_tag_serv in tag_serv_list:
            answer = get_infos.tag(DB_connection, tag=a_tag_serv)
            if answer != []:
                tag_id = answer[0]['id']
            # if it is a new tag -> add it in the Tags table
            else:
                if tag(DB_connection, a_tag_serv):
                    answer = get_infos.tag(DB_connection, tag=a_tag_serv)
                    tag_id = answer[0]['id']
                else:
                    sys.exit("Error trying to insert tag_serv in internal database")
            link_tags_serv(DB_connection, tag_id, lk_infos["id"])
            DB_connection.commit()
        return True
    except mariadb.Error as e:
        print(f"Error inserting data in the database: {e}")
        return False

def link_tags_hp(DB_connection, tag_id, id_lk):
    cur = DB_connection.cursor()
    try:
        cur.execute("INSERT INTO Link_Tags_hp (id_tag,id_link) VALUES (?,?)", (tag_id,id_lk))
        DB_connection.commit()
        return True
    except mariadb.Error as e:
        print(f"Error inserting data in the database: {e}")
        return False
    
def link_tags_serv(DB_connection, tag_id, id_lk):
    cur = DB_connection.cursor()
    try:
        cur.execute("INSERT INTO Link_Tags_serv (id_tag,id_link) VALUES (?,?)", (tag_id,id_lk))
        DB_connection.commit()
        return True
    except mariadb.Error as e:
        print(f"Error inserting data in the database: {e}")
        return False

