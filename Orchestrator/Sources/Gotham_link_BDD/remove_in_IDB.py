import mariadb
import os
import logging

# Logging components
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG,
                    format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


# Server Section

def server(DB_connection, id):
    '''
    Remove a server from the internal database

    ARGUMENTS:
        DB_connection (<mariadb connection object>) = connection with
            the internal database
        id (string) : the id of the server we want to remove from
            the internal database
    '''
    # First, remove the relation between the server and its tags
    try:
        server_in_serv_tag(DB_connection, id)
    except Exception as e:
        raise ValueError(e)
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try:
        # Delete the the server itself
        cur.execute("DELETE FROM Server WHERE id = ?", (id,))
        # Apply the changes
        DB_connection.commit()
        # Logs
        logging.info(f"'{id}' deleted from the table 'Server'")
    except mariadb.Error as e:
        error = str(id) + " removal from the table 'Server' failed : " + str(e)
        logging.error(error)
        raise ValueError(error)


def server_in_serv_tag(DB_connection, id="", tag=""):
    '''
    Remove a server tag from the internal database

    ARGUMENTS:
        DB_connection (<mariadb connection object>) = connection with the
            internal database
        id (string) : the id of the server tag we want to remove from the
            internal database
        tag (string) : name of the tag we want to remove from the internal
            database
    '''
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try:
        if tag == "" and id != "":
            cur.execute("DELETE FROM Serv_Tags WHERE id_serv = ?", (id,))
        elif id == "" and tag != "":
            cur.execute(
                "DELETE Serv_Tags FROM Serv_Tags LEFT JOIN Tags on Serv_Tags.id_tag=Tags.id WHERE tag = ?", (tag,))
        elif id != "" and tag != "":
            cur.execute(
                "DELETE Serv_Tags FROM Serv_Tags LEFT JOIN Tags on Serv_Tags.id_tag=Tags.id WHERE id_serv = ? and tag = ?", (id, tag))
        else:
            raise ValueError("server in serv tag failed")
        # Apply the changes
        DB_connection.commit()
        # Logs
        logging.info(f"'{id}' deleted from the table 'Serv_Tags'")
    except mariadb.Error as e:
        error = str(id) + \
            " removal from the table 'Serv_Tags' failed : " + str(e)
        logging.error(error)
        raise ValueError(error)

    # Check if tag is still used
    # tag_info=tag if tag !="" else "%"
    # id_tag=id if id !="" else "%"
    # tag_infos=get_infos.tag(DB_connection, tag=tag_info, id=id_tag)

    # tag_used=check_TAGS.check_tag_still_used(DB_connection, id=tag_infos[0]["id"])

    # if tag_used==[]:
    #    tag(DB_connection,id_tag=tag_infos[0]["id"])


# Honeypot section

def honeypot(DB_connection, id):
    '''
    Remove a honeypot from the internal database

    ARGUMENTS:
        DB_connection (<mariadb connection object>) = connection with the
            internal database
        id (string) : the id of the honeypot we want to remove from the
            internal database
    '''
    # First, delete the relations between the honeypot and its tags
    honeypot_in_hp_tag(DB_connection, id)
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try:
        # Delete the the honeypot itself
        cur.execute("DELETE FROM Honeypot WHERE id = ?", (id,))
        # Apply the changes
        DB_connection.commit()
        # Logs
        logging.info(
            f"'{id}' deleted from the table 'Honeypot' of the internal database")
    except mariadb.Error as e:
        # If an error occurs, log it and exit
        error = str(id) + \
            " removal from the table 'Honeypot' failed : " + str(e)
        logging.error(error)
        raise ValueError(error)


def honeypot_in_hp_tag(DB_connection, id="", tag=""):
    '''
    Remove a honeypot tag from the internal database

    ARGUMENTS:
        DB_connection (<mariadb connection object>) = connection with the
            internal database
        id (string) : the id of the honeypot tag we want to remove from the
            internal database
        tag (string) : name of the tag we want to remove from the internal
            database
    '''
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try:
        if tag == "" and id != "":
            cur.execute("DELETE FROM Hp_Tags WHERE id_hp = ?", (id,))
        elif id == "" and tag != "":
            cur.execute(
                "DELETE Hp_Tags FROM Hp_Tags LEFT JOIN Tags on Hp_Tags.id_tag=Tags.id WHERE tag = ?", (tag,))
        elif id != "" and tag != "":
            cur.execute(
                "DELETE Hp_Tags FROM Hp_Tags LEFT JOIN Tags on Hp_Tags.id_tag=Tags.id WHERE id_hp = ? and tag = ?", (id, tag))
        else:
            raise ValueError("honeypot in hp tag failed")
        # Apply the changes
        DB_connection.commit()
        # Logs
        logging.info(f"'{id}' deleted from the table 'Hp_Tags'")
    except mariadb.Error as e:
        error = str(id) + \
            " removal from the table 'Hp_Tags' failed : " + str(e)
        logging.error(error)
        raise ValueError(error)

    # Check if tag is still used
    # tag_info=tag if tag !="" else "%"
    # id_tag=id if id !="" else "%"
    # tag_infos=get_infos.tag(DB_connection, tag=tag_info, id=id_tag)
    # tag_used=check_TAGS.check_tag_still_used(DB_connection, id=tag_infos[0]["id"])
    # if tag_used==[]:
    #    tag(DB_connection,id_tag=tag_infos[0]["id"])


# Link section

def link(DB_connection, id):
    '''
    Remove a link from the internal database from

    ARGUMENTS:
        DB_connection (<mariadb connection object>) = connection with the
            internal database
        id (string) : the id of the link we want to remove from the internal
            database
    '''
    # Remove the relation between the link and the serv_tag
    try:
        link_in_link_tags_serv(DB_connection, id)
    except Exception as e:
        raise ValueError(e)
    # Remove the relation between the link and the hp_tag
    try:
        link_in_link_tags_hp(DB_connection, id)
    except Exception as e:
        raise ValueError(e)
    # Remove the relations between the link, the honeypots and the servers
    try:
        lhs(DB_connection, id_link=id)
    except Exception as e:
        raise ValueError(e)
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try:
        # Finally, delete the the link itself
        cur.execute("DELETE FROM Link WHERE id = ?", (id,))
        # Apply the changes
        DB_connection.commit()
        # Logs
        logging.info(f"'{id}' deleted from the table 'Link'")
    except mariadb.Error as e:
        # If an error occurs, log it and return False
        error = str(id) + " removal from the table 'Link' failed : " + str(e)
        logging.error(error)
        raise ValueError(error)


def link_in_link_tags_hp(DB_connection, id="", tag_hp=""):
    '''
    Remove a honeypot tag of the link from the internal database

    ARGUMENTS:
        DB_connection (<mariadb connection object>) = connection with the
            internal database
        id (string) : the id of the honeypot tag we want to remove from the
            internal database
        tag (string) : name of the honeypot tag we want to remove from the
            internal database
    '''
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try:
        if tag_hp == "" and id != "":
            cur.execute("DELETE FROM Link_Tags_hp WHERE id_link = ?", (id,))
        elif id == "" and tag_hp != "":
            cur.execute(
                "DELETE Link_Tags_hp FROM Link_Tags_hp LEFT JOIN Tags on Link_Tags_hp.id_tag=Tags.id WHERE tag = ?", (tag_hp,))
        elif id != "" and tag_hp != "":
            cur.execute(
                "DELETE Link_Tags_hp FROM Link_Tags_hp LEFT JOIN Tags on Link_Tags_hp.id_tag=Tags.id WHERE id_link = ? and tag = ?", (id, tag_hp))
        else:
            raise ValueError("link in link tags hp failed")

        # Apply the changes
        DB_connection.commit()
        # Logs
        logging.info(f"'{id}' deleted from the table 'Link_Tags_hp'")
    except mariadb.Error as e:
        error = str(id) + \
            " removal from the table 'Link_Tags_hp' failed : " + str(e)
        logging.error(error)
        raise ValueError(error)


def link_in_link_tags_serv(DB_connection, id="", tag_serv=""):
    '''
    Remove a server tag of the link from the internal database

    ARGUMENTS:
        DB_connection (<mariadb connection object>) = connection with the
            internal database
        id (string) : the id of the server tag we want to remove from the
            internal database
        tag (string) : name of the server tag we want to remove from the
            internal database
    '''
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try:
        if tag_serv == "" and id != "":
            cur.execute("DELETE FROM Link_Tags_serv WHERE id_link = ?", (id,))
        elif id == "" and tag_serv != "":
            cur.execute(
                "DELETE Link_Tags_serv FROM Link_Tags_serv LEFT JOIN Tags on Link_Tags_serv.id_tag=Tags.id WHERE tag = ?", (tag_serv,))
        elif id != "" and tag_serv != "":
            cur.execute(
                "DELETE Link_Tags_serv FROM Link_Tags_serv LEFT JOIN Tags on Link_Tags_serv.id_tag=Tags.id WHERE id_link = ? and tag = ?", (id, tag_serv))
        else:
            raise ValueError("link in link tags serv failed")

        # Apply the changes
        DB_connection.commit()
        # Logs
        logging.info(f"'{id}' deleted from the table 'Link_Tags_serv'")
    except mariadb.Error as e:
        error = str(
            id) + " removal from the table 'Link_Tags_serv' failed : " + str(e)
        logging.error(error)
        raise ValueError(error)


def lhs(DB_connection, id_link="%", id_hp="%", id_serv="%"):
    '''
    Remove a Link/Honeypot/Server combination from the internal database

    ARGUMENTS:
        DB_connection (<mariadb connection object>) = connection with the
            internal database
        id_link (string, optional) : the id of the link we want to remove from
            the internal database
        id_hp (string, optional) : the id of the hp we want to remove from the
            internal database
        id_serv (string, optional) : the id of the serv we want to remove from
            the internal database
    '''
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try:
        cur.execute("DELETE FROM Link_Hp_Serv WHERE id_link LIKE ? AND id_hp LIKE ? AND id_serv LIKE ?",
                    (id_link, id_hp, id_serv))
        # Apply the changes
        DB_connection.commit()
        # Logs
        logging.info(f"'{id}' deleted from the table 'Link_Hp_Serv'")
    except mariadb.Error as e:
        error = str(id) + \
            " removal from the table 'Link_Hp_Serv' failed : " + str(e)
        logging.error(error)
        raise ValueError(error)


# Tag section

def tag(DB_connection, id_tag="%", tag="%"):
    '''
    Remove a tag from the internal database from

    ARGUMENTS:
        DB_connection (<mariadb connection object>) = connection with the
            internal database
        id (string) : the id of the tag we want to remove from the internal
            database
        tag (string) : name of the tag we want to remove from the internal
            database
    '''
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try:
        cur.execute(
            "DELETE FROM Tags WHERE id LIKE ? AND tag LIKE ?", (id_tag, tag))
        # Apply the changes
        DB_connection.commit()
        # Logs
        logging.info(f"'{id}' deleted from the table 'Tags'")
    except mariadb.Error as e:
        error = str(id) + " removal from the table 'Tags' failed : " + str(e)
        logging.error(error)
        raise ValueError(error)
