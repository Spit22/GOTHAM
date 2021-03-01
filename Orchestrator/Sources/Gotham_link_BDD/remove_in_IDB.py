# Import external libs
import mariadb
import sys
import configparser

# Import GOTHAM's libs
from . import get_infos
from Gotham_check import check_TAGS

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

def server_in_serv_tag(DB_connection, id="", tag=""):
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try :
        if tag=="" and id!="":
            cur.execute("DELETE FROM Serv_Tags WHERE id_serv = ?",(id,))
        elif id=="" and tag!="":
            cur.execute("DELETE FROM Serv_Tags LEFT JOIN Tags on Serv_Tags.id_tag=Tags.id WHERE tag = ?",(tag,))
        elif id!="" and tag!="":
            cur.execute("DELETE FROM Serv_Tags LEFT JOIN Tags on Serv_Tags.id_tag=Tags.id WHERE id_serv = ? and tag = ?",(id,tag))
        else:
            sys.exit(1)
        # Apply the changes
        DB_connection.commit()
        # Logs
        logging.info(f"'{id}' deleted from the table 'Serv_Tags'")
    except mariadb.Error as e:
        logging.error(f"'{id}' removal from the table 'Serv_Tags' failed : {e}")
        sys.exit(1)

    # Check if tag is still used
    #tag_info=tag if tag !="" else "%"
    #id_tag=id if id !="" else "%"
    #tag_infos=get_infos.tag(DB_connection, tag=tag_info, id=id_tag)

    #tag_used=check_TAGS.check_tag_still_used(DB_connection, id=tag_infos[0]["id"])

    #if tag_used==[]:
    #    tag(DB_connection,id_tag=tag_infos[0]["id"])


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

def honeypot_in_hp_tag(DB_connection, id="", tag=""):
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try :
        if tag == "" and id != "":
            cur.execute("DELETE FROM Hp_Tags WHERE id_hp = ?",(id,))
        elif id == "" and tag != "":
            cur.execute("DELETE FROM Hp_Tags LEFT JOIN Tags on Hp_Tags.id_tag=Tags.id WHERE tag = ?",(tag,))
        elif id != "" and tag != "":
            cur.execute("DELETE FROM Hp_Tags LEFT JOIN Tags on Hp_Tags.id_tag=Tags.id WHERE id_hp = ? and tag = ?",(id,tag))
        else:
            sys.exit(1)
        # Apply the changes
        DB_connection.commit()
        # Logs
        logging.info(f"'{id}' deleted from the table 'Hp_Tags'")
    except mariadb.Error as e:
        logging.error(f"'{id}' removal from the table 'Hp_Tags' failed : {e}")
        sys.exit(1)

    # Check if tag is still used
    #tag_info=tag if tag !="" else "%"
    #id_tag=id if id !="" else "%"
    #tag_infos=get_infos.tag(DB_connection, tag=tag_info, id=id_tag)
    #tag_used=check_TAGS.check_tag_still_used(DB_connection, id=tag_infos[0]["id"])
    #if tag_used==[]:
    #    tag(DB_connection,id_tag=tag_infos[0]["id"])


############################### LINK SECTION ###############################

def link(DB_connection, id):
    # Remove the relation between the link and the serv_tag
    try:
        link_in_link_tags_serv(DB_connection, id)
    except:
        sys.exit(1)
    # Remove the relation between the link and the hp_tag
    try:
        link_in_link_tags_hp(DB_connection, id)
    except:
        sys.exit(1)
    #Remove the relations between the link, the honeypots and the servers
    try:
        lhs(DB_connection, id_link=id)
    except:
        sys.exit(1)
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try :
        # Finally, delete the the link itself
        cur.execute("DELETE FROM Link WHERE id = ?",(id,))
        # Apply the changes
        DB_connection.commit()
        # Logs
        logging.info(f"'{id}' deleted from the table 'Link'")
    except mariadb.Error as e:
        # If an error occurs, log it and return False
        logging.error(f"'{id}' removal from the table 'Link' failed : {e}")
        sys.exit(1)

def link_in_link_tags_hp(DB_connection, id="", tag_hp=""):
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try :
        if tag_hp == "" and id != "":
            cur.execute("DELETE FROM Link_Tags_hp WHERE id_link = ?",(id,))
        elif id == "" and tag_hp != "":
            cur.execute("DELETE FROM Link_Tags_hp LEFT JOIN Tags on Link_Tags_hp.id_tag=Tags.id WHERE tag = ?",(tag_hp,))
        elif id != "" and tag_hp != "":
            cur.execute("DELETE FROM Link_Tags_hp LEFT JOIN Tags on Link_Tags_hp.id_tag=Tags.id WHERE id_link = ? and tag = ?",(id,tag_hp))
        else:
            sys.exit(1)
        
        # Apply the changes
        DB_connection.commit()
        # Logs
        logging.info(f"'{id}' deleted from the table 'Link_Tags_hp'")
    except mariadb.Error as e:
        logging.error(f"'{id}' removal from the table 'Link_Tags_hp' failed : {e}")
        sys.exit(1)

def link_in_link_tags_serv(DB_connection, id="", tag_serv=""):
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try :
        if tag_serv == "" and id != "":
            cur.execute("DELETE FROM Link_Tags_serv WHERE id_link = ?",(id,))
        elif id == "" and tag_serv != "":
            cur.execute("DELETE FROM Link_Tags_serv LEFT JOIN Tags on Link_Tags_serv.id_tag=Tags.id WHERE tag = ?",(tag_serv,))
        elif id != "" and tag_serv != "":
            cur.execute("DELETE FROM Link_Tags_serv LEFT JOIN Tags on Link_Tags_serv.id_tag=Tags.id WHERE id_link = ? and tag = ?",(id,tag_serv))
        else:
            sys.exit(1)
        
        # Apply the changes
        DB_connection.commit()
        # Logs
        logging.info(f"'{id}' deleted from the table 'Link_Tags_serv'")
    except mariadb.Error as e:
        logging.error(f"'{id}' removal from the table 'Link_Tags_serv' failed : {e}")
        sys.exit(1)

def lhs(DB_connection,id_link="%",id_hp="%",id_serv="%"):
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try :
        cur.execute("DELETE FROM Link_Hp_Serv WHERE id_link LIKE ? AND id_hp LIKE ? AND id_serv LIKE ?",(id_link,id_hp,id_serv))
        # Apply the changes
        DB_connection.commit()
        # Logs
        logging.info(f"'{id}' deleted from the table 'Link_Hp_Serv'")
    except mariadb.Error as e:
        logging.error(f"'{id}' removal from the table 'Link_Hp_Serv' failed : {e}")
        sys.exit(1)


############################### TAG SECTION ###############################

def tag(DB_connection,id_tag="%", tag="%"):
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try :
        cur.execute("DELETE FROM Tags WHERE id LIKE ? AND tag LIKE ?",(id_tag,tag))
        # Apply the changes
        DB_connection.commit()
        # Logs
        logging.info(f"'{id}' deleted from the table 'Tags'")
    except mariadb.Error as e:
        logging.error(f"'{id}' removal from the table 'Tags' failed : {e}")
        sys.exit(1)

