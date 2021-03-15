import sys
import configparser
import re
# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


def check_tags(object_type, objects_infos, tags_hp='', tags_serv='', mode=False):
    if (object_type != "hp" and object_type != "serv" and object_type != "link"):
        error = str(object_type) + " is uncorrect"
        logging.error(error)
        raise ValueError(error)

    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    separator = config['tag']['separator']
    if object_type == "hp" or object_type == "serv":
        if object_type == "hp":
            tags_list = tags_hp.lower().split(separator)
        elif object_type == "serv":
            tags_list = tags_serv.lower().split(separator)
        if mode == False:
            result = [object_infos for object_infos in objects_infos if (len(set(
                object_infos[object_type+"_tags"].lower().split('||')).intersection(tags_list)) == len(tags_list))]
        elif mode == True:
            result = [object_infos for object_infos in objects_infos if (len(set(object_infos[object_type+"_tags"].lower().split(
                '||')).intersection(tags_list)) == len(tags_list) == len(object_infos[object_type+"_tags"].lower().split('||')))]
    elif object_type == "link":
        tags_hp_list = tags_hp.lower().split(separator)
        tags_serv_list = tags_serv.lower().split(separator)
        if mode == False:
            result = [object_infos for object_infos in objects_infos if (len(set(object_infos[object_type+"_tags_hp"].lower().split('||')).intersection(tags_hp_list)) == len(
                tags_hp_list) and len(set(object_infos[object_type+"_tags_serv"].lower().split('||')).intersection(tags_serv_list)) == len(tags_serv_list))]
        elif mode == True:
            result = [object_infos for object_infos in objects_infos if (len(set(object_infos[object_type+"_tags_hp"].lower().split('||')).intersection(tags_hp_list)) == len(tags_hp_list) == len(object_infos[object_type+"_tags_hp"].lower(
            ).split('||')) and len(set(object_infos[object_type+"_tags_serv"].lower().split('||')).intersection(tags_serv_list)) == len(tags_serv_list) == len(object_infos[object_type+"_tags_serv"].lower().split('||')))]
    return result


def check_tag_still_used(DB_connection, tag="%", id="%"):
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    cur.execute("SELECT * FROM Tags WHERE tag LIKE ? AND id like ?", (tag, id))
    # Convert answer to JSON
    row_headers = [x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))

    if json_data == []:
        error = "Tag can't be found"
        logging.error(error)
        raise ValueError(error)

    id_tag = json_data[0]["id"]
    # Get MariaDB cursor
    cur_sec = DB_connection.cursor()
    # Execute SQL request
    cur_sec.execute("SELECT * FROM Serv_Tags WHERE id_tag = ", (id_tag,))
    # Convert answer to JSON
    row_headers = [x[0] for x in cur_sec.description]
    rv = cur_sec.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))

    # Get MariaDB cursor
    cur_ter = DB_connection.cursor()
    # Execute SQL request
    cur_ter.execute("SELECT * FROM Hp_Tags WHERE id_tag = ", (id_tag,))
    # Convert answer to JSON
    row_headers = [x[0] for x in cur_ter.description]
    rv = cur_ter.fetchall()
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))

    return json_data
