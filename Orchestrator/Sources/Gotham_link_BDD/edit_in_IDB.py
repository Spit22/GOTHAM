import mariadb
import configparser
import os
import logging

from . import get_infos, remove_in_IDB, add_in_IDB
from Gotham_normalize import normalize_honeypot_infos, normalize_server_infos, normalize_link_infos
from Gotham_normalize import normalize_lhs_infos, normalize_modif_to_str, normalize_conditions_to_str

# Logging components
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')

# Retrieve settings from configuration file
config = configparser.ConfigParser()
config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
tag_separator = config['tag']['separator']


def server(DB_connection, modifs, conditions):
    '''
    Edit Server table in the internal database

    ARGUMENTS:
        DB_connection : Connection to the internal database
        modifs (dict) : dict of modifications with column:value syntax
        conditions (dict) : dict of conditions with column:value syntax
    '''
    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    tag_separator = config['tag']['separator']

    # Normalize modifications
    try:
        modifs = normalize_server_infos(modifs)
    except Exception as e:
        error = "Bad server modification : " + str(e)
        logging.error(error)
        raise ValueError(error)

    # Normalize conditions
    try:
        conditions = normalize_server_infos(conditions)
    except Exception as e:
        error = "Bad server modification's conditions : " + str(e)
        logging.error(error)
        raise ValueError(error)

    # Case where we want to modify tags of the server
    if "tags" in modifs.keys():
        # Filter with the id of the server
        if "id" in conditions.keys():
            # Retrieve tags
            tags = modifs.pop("tags")
            new_tag_list = tags.split(tag_separator)
            # Get server infos from its id
            servers = get_infos.server(DB_connection, id=conditions["id"])
            # Compare existing and required tags for the server
            old_tag_list = servers[0]["serv_tags"].split("||")
            deleted_tags = list(set(old_tag_list) - set(new_tag_list))
            added_tags = list(set(new_tag_list) - set(old_tag_list))
            # Remove obsolete tags
            for tag in deleted_tags:
                remove_in_IDB.server_in_serv_tag(
                    DB_connection,
                    id=servers[0]["serv_id"],
                    tag=tag
                )
            # Add new tags
            for tag in added_tags:
                # Check if the tag exists in the IDB
                answer = get_infos.tag(DB_connection, tag=tag)
                if answer != []:
                    tag_id = answer[0]['id']
                # If it doesn't exists, add the tag in the IDB
                else:
                    try:
                        add_in_IDB.tag(DB_connection, tag)
                    except Exception as e:
                        raise ValueError(e)
                    # Then retrieve the new tag id
                    answer = get_infos.tag(DB_connection, tag=tag)
                    tag_id = answer[0]['id']
                # Add the relation between server and tag in Serv_Tags table
                try:
                    add_in_IDB.serv_tags(
                        DB_connection,
                        tag_id,
                        servers[0]["serv_id"]
                    )
                except Exception as e:
                    raise ValueError(e)
        else:
            error = "Tags modification without id in conditions not implemented"
            logging.error(error)
            raise ValueError(error)

    if [val for key, val in conditions.items() if 'tags' in key] != []:
        error = "Modification by tag not implemented"
        logging.error(error)
        raise ValueError(error)

    if modifs != {}:
        # Prepare modifs
        try:
            modifs = normalize_modif_to_str(modifs)
        except Exception as e:
            error = "Can't prepare server modification : " + str(e)
            logging.error(error)
            raise ValueError(error)
        # Prepare conditions
        try:
            conditions = normalize_conditions_to_str(conditions)
        except Exception as e:
            error = "Can't prepare server modification's conditions : " + \
                str(e)
            logging.error(error)
            raise ValueError(error)
        # Create the query
        if conditions != {}:
            query = "UPDATE Server SET " + modifs + " WHERE " + conditions
        else:
            query = "UPDATE Server SET " + modifs
        # Get MariaDB cursor
        cur = DB_connection.cursor()
        # Execute SQL request
        try:
            # Edit values in Server table
            cur.execute(query)
            DB_connection.commit()
            logging.info(
                f"Modification ok -- SET {modifs}  WHERE {conditions} -- in the table 'Server'")
        except mariadb.Error as e:
            error = "Modification failed -- SET " + \
                str(modifs) + " WHERE " + str(conditions) + \
                "--  in the table 'Server' : " + str(e)
            logging.error(error)
            raise ValueError(error)


def honeypot(DB_connection, modifs, conditions):
    '''
    Edit Honeypot table in the internal database

    ARGUMENTS:
        DB_connection : Connection to the internal database
        modifs (dict) : dict of modifications with column:value syntax
        conditions (dict) : dict of conditions with column:value syntax
    '''
    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    tag_separator = config['tag']['separator']

    # Normalize modifs
    try:
        modifs = normalize_honeypot_infos(modifs)
    except Exception as e:
        error = "Bad honeypot modification : " + str(e)
        logging.error(error)
        raise ValueError(error)

    # Normalize conditions
    try:
        conditions = normalize_honeypot_infos(conditions)
    except Exception as e:
        error = "Bad honeypot modification's conditions : " + str(e)
        logging.error(error)
        raise ValueError(error)

    # Case where we want to modify tags of the honeypot
    if "tags" in modifs.keys():
        # Filter with the id of the honeypot
        if "id" in conditions.keys():
            # Retrieve tags
            tags = modifs.pop("tags")
            new_tag_list = tags.split(tag_separator)
            # Get honeypot infos from its id
            honeypots = get_infos.honeypot(DB_connection, id=conditions["id"])
            # Compare existing and required tags for the honeypot
            old_tag_list = honeypots[0]["hp_tags"].split("||")
            deleted_tags = list(set(old_tag_list) - set(new_tag_list))
            added_tags = list(set(new_tag_list) - set(old_tag_list))
            # Remove obsolete tags
            for tag in deleted_tags:
                remove_in_IDB.honeypot_in_hp_tag(
                    DB_connection,
                    id=honeypots[0]["hp_id"],
                    tag=tag
                )
            # Add new tags
            for tag in added_tags:
                # Check if the tag exists in the IDB
                answer = get_infos.tag(DB_connection, tag=tag)
                if answer != []:
                    tag_id = answer[0]['id']
                # If it doesn't exists, add the tag in the IDB
                else:
                    try:
                        add_in_IDB.tag(DB_connection, tag)
                    except Exception as e:
                        raise ValueError(e)
                    # Then retrieve the new tag id
                    answer = get_infos.tag(DB_connection, tag=tag)
                    tag_id = answer[0]['id']
                # Add the relation between honeypot and tag in hp_Tags table
                try:
                    add_in_IDB.hp_tags(
                        DB_connection,
                        tag_id,
                        honeypots[0]["hp_id"]
                    )
                except Exception as e:
                    raise ValueError(e)
        else:
            error = "Tags modification without id in conditions not implemented"
            logging.error(error)
            raise ValueError(error)

    if [val for key, val in conditions.items() if 'tags' in key] != []:
        error = "Modification by tag not implemented"
        logging.error(error)
        raise ValueError(error)

    if modifs != {}:
        # Prepare query
        # Prepare modifs
        try:
            modifs = normalize_modif_to_str(modifs)
        except Exception as e:
            error = "Can't prepare honeypot modification : " + str(e)
            logging.error(error)
            raise ValueError(error)
        # Prepare conditions
        try:
            conditions = normalize_conditions_to_str(conditions)
        except Exception as e:
            error = "Can't prepare honeypot modification's conditions : " + \
                str(e)
            logging.error(error)
            raise ValueError(error)
        # Create the query
        if conditions != {}:
            query = "UPDATE Honeypot SET " + modifs + " WHERE " + conditions
        else:
            query = "UPDATE Honeypot SET " + modifs
        # Get MariaDB cursor
        cur = DB_connection.cursor()
        # Execute SQL request
        try:
            # Edit values in Honeypot table
            cur.execute(query)
            DB_connection.commit()
            logging.info(
                f"Modification ok -- SET {modifs}  WHERE {conditions} -- in the table 'Honeypot'")
        except mariadb.Error as e:
            error = "Modification failed -- SET " + \
                str(modifs) + " WHERE " + str(conditions) + \
                "--  in the table 'Honeypot' : " + str(e)
            logging.error(error)
            raise ValueError(error)


def link(DB_connection, modifs, conditions):
    '''
    Edit Link table in the internal database

    ARGUMENTS:
        DB_connection : Connection to the internal database
        modifs (dict) : dict of modifications with column:value syntax
        conditions (dict) : dict of conditions with column:value syntax
    '''
    # Normalize modifs
    try:
        modifs = normalize_link_infos(modifs)
    except Exception as e:
        error = "Bad link modification : " + str(e)
        logging.error(error)
        raise ValueError(error)
    # Normalize conditions
    try:
        conditions = normalize_link_infos(conditions)
    except Exception as e:
        error = "Bad link modification's conditions : " + str(e)
        logging.error(error)
        raise ValueError(error)

    # Case where we want to modify honeypot tags of the link
    if "tags_hp" in modifs.keys():
        # Filter with the id of the link
        if "id" in conditions.keys():
            # Retrieve honeypot tags
            tags = modifs.pop("tags_hp")
            new_tag_list = tags.split(tag_separator)
            # Get link infos from its id
            links = get_infos.link(DB_connection, id=conditions["id"])
            # Compare existing and required honeypot tags for the link
            old_tag_list = links[0]["link_tags_hp"].split("||")
            deleted_tags = list(set(old_tag_list) - set(new_tag_list))
            added_tags = list(set(new_tag_list) - set(old_tag_list))
            # Remove obsolete honeypot tags
            for tag in deleted_tags:
                remove_in_IDB.link_in_link_tags_hp(
                    DB_connection,
                    id=links[0]["link_id"],
                    tag_hp=tag
                )
            # Add new honeypot tags
            for tag in added_tags:
                # Check if the honeypot tag exists in the IDB
                answer = get_infos.tag(DB_connection, tag=tag)
                if answer != []:
                    tag_id = answer[0]['id']
                # If it doesn't exists, add the honeypot tag in the IDB
                else:
                    error = "Error with tags: some honeypot tags do not exists"
                    logging.error(error)
                    raise ValueError(error)
                # Add the relation between link and tag in hp_Tags table
                try:
                    add_in_IDB.link_tags_hp(
                        DB_connection, tag_id, links[0]["link_id"])
                except Exception as e:
                    raise ValueError(e)
        else:
            error = "Tags modification without id in conditions not implemented"
            logging.error(error)
            raise ValueError(error)

    # Case where we want to modify server tags of the link
    if "tags_serv" in modifs.keys():
        # Filter with the id of the link
        if "id" in conditions.keys():
            # Retrieve server tags
            tags = modifs.pop("tags_serv")
            new_tag_list = tags.split(tag_separator)
            # Get link infos from its id
            links = get_infos.link(DB_connection, id=conditions["id"])
            # Compare existing and required server tags for the link
            old_tag_list = links[0]["link_tags_serv"].split("||")
            deleted_tags = list(set(old_tag_list) - set(new_tag_list))
            added_tags = list(set(new_tag_list) - set(old_tag_list))
            # Remove obsolete server tags
            for tag in deleted_tags:
                remove_in_IDB.link_in_link_tags_serv(
                    DB_connection,
                    id=links[0]["link_id"],
                    tag_serv=tag
                )
            # Add new server tags
            for tag in added_tags:
                # Check if the server tag exists in the IDB
                answer = get_infos.tag(DB_connection, tag=tag)
                if answer != []:
                    tag_id = answer[0]['id']
                # If it doesn't exists, add the server tag in the IDB
                else:
                    error = "Error with tags: some server tags do not exists"
                    logging.error(error)
                    raise ValueError(error)
                # Add the relation between link and tag in hp_Tags table
                try:
                    add_in_IDB.link_tags_serv(
                        DB_connection, tag_id, links[0]["link_id"])
                except Exception as e:
                    raise ValueError(e)
        else:
            error = "Tags modification without id in conditions not implemented"
            logging.error(error)
            raise ValueError(error)

    if [val for key, val in conditions.items() if 'tag' in key] != []:
        error = "Modification by tag not implemented"
        logging.error(error)
        raise ValueError(error)

    if modifs != {}:
        # Prepare query
        # Prepare modifs
        try:
            modifs = normalize_modif_to_str(modifs)
        except Exception as e:
            error = "Can't prepare link modification : " + str(e)
            logging.error(error)
            raise ValueError(error)
        # Prepare conditions
        try:
            conditions = normalize_conditions_to_str(conditions)
        except Exception as e:
            error = "Can't prepare link modification's conditions : " + str(e)
            logging.error(error)
            raise ValueError(error)
        # Create the query
        if conditions != {}:
            query = "UPDATE Link SET " + modifs + " WHERE " + conditions
        else:
            query = "UPDATE Link SET " + modifs
        # Get MariaDB cursor
        cur = DB_connection.cursor()
        # Execute SQL request
        try:
            # Edit values in Link table
            cur.execute(query)
            DB_connection.commit()
            logging.info(
                f"Modification ok -- SET {modifs}  WHERE {conditions} -- in the table 'Link'")
        except mariadb.Error as e:
            error = "Modification failed -- SET " + \
                str(modifs) + " WHERE " + str(conditions) + \
                "--  in the table 'Link' : " + str(e)
            logging.error(error)
            raise ValueError(error)


def lhs(DB_connection, modifs, conditions):
    '''
    Edit Link_Hp_Serv table in the internal database

    ARGUMENTS:
        DB_connection : Connection to the internal database
        modifs (dict) : dict of modifications with column:value syntax
        conditions (dict) : dict of conditions with column:value syntax
    '''
    # Normalize modifs
    try:
        modifs = normalize_lhs_infos(modifs)
    except Exception as e:
        error = "Bad lhs modification : " + str(e)
        logging.error(error)
        raise ValueError(error)

    # Normalize conditions
    try:
        conditions = normalize_lhs_infos(conditions)
    except Exception as e:
        error = "Bad lhs modification's conditions : " + str(e)
        logging.error(error)
        raise ValueError(error)

    # Prepare modifs
    try:
        modifs = normalize_modif_to_str(modifs)
    except Exception as e:
        error = "Can't prepare lhs modification : " + str(e)
        logging.error(error)
        raise ValueError(error)
    # Prepare conditions
    try:
        conditions = normalize_conditions_to_str(conditions)
    except Exception as e:
        error = "Can't prepare lhs modif's conditions : " + str(e)
        logging.error(error)
        raise ValueError(error)
    # Create the query
    query = "UPDATE Link_Hp_Serv SET " + modifs + " WHERE " + conditions
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    try:
        # Edit values in Link_Hp_Serv table
        cur.execute(query)
        DB_connection.commit()
        logging.info(
            f"Modification ok -- SET {modifs}  WHERE {conditions} -- in the table 'Link_Hp_Serv'")
    except mariadb.Error as e:
        error = "Modification failed -- SET " + \
            str(modifs) + " WHERE " + str(conditions) + \
            "--  in the table 'Link_Hp_Serv' : " + str(e)
        logging.error(error)
        raise ValueError(error)
