
import mariadb
import sys
import os
import configparser
import sys

from . import get_infos

#sys.path.append('/home/spitfire/GOTHAM/Orchestrator/Sources')

# Retrieve settings from config file
config = configparser.ConfigParser()
config.read('Orchestrator/Config/config.ini')
_separator = config['tag']['separator']

def server(DB_connection, server_infos):
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