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

def server_in_serv_tag(DB_connection, id):
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try :
        cur.execute("DELETE FROM Serv_Tags WHERE id_serv = ?",(id,))
        DB_connection.commit()
        return True
    except mariadb.Error as e:
        logging.error(f"Can't remove the server in the internal database : {e}")
        return False

def server(DB_connection, id):
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try :
        cur.execute("DELETE FROM Serv_Tags WHERE id_serv = ?",(id,))
        cur.execute("DELETE FROM Server WHERE id = ?",(id,))
        DB_connection.commit()
        return True
    except mariadb.Error as e:
        logging.error(f"Can't remove the server in the internal database : {e}")
        return False