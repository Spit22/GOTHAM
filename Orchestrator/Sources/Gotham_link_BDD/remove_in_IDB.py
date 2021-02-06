import mariadb
import sys
import configparser

from . import get_infos

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


############################### SERVER SECTION ###############################

def server(DB_connection, id):
    # First, remove the relation between the server and its tags
    try:
        server_in_serv_tag(DB_connection, id)
    except:
        sys.exit(1)
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try :
        # Delete the the server itself
        cur.execute("DELETE FROM Server WHERE id = ?",(id,))
        # Apply the changes
        DB_connection.commit()
        # Logs
        logging.info(f"'{id}' deleted from the table 'Server'")
    except mariadb.Error as e:
        logging.error(f"'{id}' removal from the table Server failed : {e}")
        sys.exit(1)

def server_in_serv_tag(DB_connection, id):
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try :
        cur.execute("DELETE FROM Serv_Tags WHERE id_serv = ?",(id,))
        # Apply the changes
        DB_connection.commit()
        # Logs
        logging.info(f"'{id}' deleted from the table 'Serv_Tags'")
    except mariadb.Error as e:
        logging.error(f"'{id}' removal from the table 'Serv_Tags' failed : {e}")
        sys.exit(1)

############################### HONEYPOT SECTION ###############################

def honeypot(DB_connection, id):
    # First, delete the relations between the honeypot and its tags
    honeypot_in_hp_tag(DB_connection, id)
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try :
        # Delete the the honeypot itself
        cur.execute("DELETE FROM Honeypot WHERE id = ?",(id,))
        # Apply the changes
        DB_connection.commit()
        # Logs
        logging.info(f"'{id}' deleted from the table 'Honeypot' of the internal database")
    except mariadb.Error as e:
        # If an error occurs, log it and exit
        logging.error(f"'{id}' removal from the table 'Honeypot' : {e}")
        sys.exit(1)

def honeypot_in_hp_tag(DB_connection, id):
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try :
        cur.execute("DELETE FROM Hp_Tags WHERE id_hp = ?",(id,))
        # Apply the changes
        DB_connection.commit()
        # Logs
        logging.info(f"Honeypot with the id '{id}' has just been deleted from the table Hp_Tags of the internal database")
        return True
    except mariadb.Error as e:
        logging.error(f"Can't remove the relation between the honeypot and his tag with the id '{id}' in the internal database : {e}")
        return False

############################### LINK SECTION ###############################

def link(DB_connection, id):
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try :
        # First, delete every relations between the link and the server tags it takes care
        cur.execute("DELETE FROM Link_Tags_serv WHERE id_link = ?",(id,))
        # Then, delete the relations between the link and the honeypot tags it takes care
        cur.execute("DELETE FROM Link_Tags_hp WHERE id_link = ?",(id,))
        # Finally, delete the the link itself
        cur.execute("DELETE FROM Link WHERE id = ?",(id,))
        # Apply the changes
        DB_connection.commit()
        # Logs
        logging.info(f"Link with the id '{id}' has just been deleted from the table Link_Tags_serv of the internal database")
        logging.info(f"Link with the id '{id}' has just been deleted from the table Link_Tags_hp of the internal database")
        logging.info(f"Link with the id '{id}' has just been deleted from the table Link of the internal database")
        return True
    except mariadb.Error as e:
        # If an error occurs, log it and return False
        logging.error(f"Can't remove the link with the id '{id}' in the internal database : {e}")
        return False