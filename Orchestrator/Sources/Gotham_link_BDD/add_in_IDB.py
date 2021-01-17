import mariadb
import sys

import sys
sys.path.append('/home/spitfire/GOTHAM/Orchestrator/Sources')

#from Gotham_check import check_doublon_tag
        

def server(DB_settings, server_infos):
    try:
        conn = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB server: {e}")
        sys.exit(1)
    # Get MariaDB cursor
    cur = conn.cursor()
    # Execute SQL request
    try:
        # Insert values in Server table
        cur.execute("INSERT INTO Server (id,name,descr,ip,ssh_key,ssh_port,state) VALUES (?,?,?,?,?,?,?)", (server_infos["id"], server_infos["name"], server_infos["descr"],  server_infos["ip"],  server_infos["ssh_key"],  server_infos["ssh_port"],  server_infos["state"]))
        # AUTRES REQUETES A FAIRE
        conn.commit()
        conn.close()
        return True
    except mariadb.Error as e:
        conn.close()
        print(f"Error inserting data in the database: {e}")
        return False

    
def tags(DB_settings, tags, separator=','):
    tag_list = tags.split(separator)
    try:
        conn = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB server: {e}")
        sys.exit(1)
    # Get MariaDB cursor
    cur = conn.cursor()
    for tag in tag_list:
        tag = tag.strip()
        #Check doublon
        #########################
        # Add the tag to the Tags table
        cur.execute("INSERT INTO Tags (tag) VALUES (?)", (tag))
        # Retrieve the ID of the tag just added
        cur.execute("INSERT INTO Tags (tag) VALUES (?)", (tag))