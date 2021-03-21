#===Import external libs===#
import mariadb
import sys
import configparser
import re
import os
#==========================#

# Set the path of the home directory of GOTHAM
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')

#===Retrieve settings from configuration file===#
config = configparser.ConfigParser()
config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
_separator = config['tag']['separator']
#===============================================#

############################### MISCELLANEOUS ###############################


def normalize_used_arguments(arg, default_arg):
    '''
    Normalize arguments which are used

    ARGUMENTS:
        arg (string) : argument to normalize
        default_arg (string) : argument used to compare with the tested argument
    '''
    if not(arg == default_arg):
        return "%" + str(arg) + "%"
    else:
        return default_arg


def normalize_tags_arguments(mode, column, tags):
    if not(re.match(r"^[a-zA-Z0-9_\-]*$", column)):
        sys.exit("Error in column : invalid syntax")
    if(tags != "%"):
        request = ""
        tag_list = tags.split(_separator)
        for a_tag in tag_list:
            if not(re.match(r"^[a-zA-Z0-9_\-]*$", a_tag)):
                sys.exit("Error in tags : invalid syntax")
            if (request == ""):
                request = "("+column+" like '"
            else:
                if mode:
                    request += "' OR "+column+" like '"
                else:
                    request += "' AND "+column+" like '"
            a_tag = normalize_used_arguments(a_tag, "%")
            request += a_tag
        request += "')"
    else:
        request = column+" like '%'"
    return request

############################### TAG SECTION ###############################


def tag(DB_connection, mode=False, tag='%', id='%'):
    '''
    Retrieve tag information from the internal database

    ARGUMENTS:
        DB_connection (<mariadb connection object>) = connection with the internal database
        mode (bool, optional) : False means accurate answer, True means extended answer
        tag (string, optional) : name of the tag whose information we want
        id (string, optional) : id of the tag whose information we want
    '''
    # Normalize arguments according to the mode
    if mode:
        tag = normalize_used_arguments(tag, "%")
        id = normalize_used_arguments(id, "%")
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
    return json_data

def tag_hp(DB_connection, mode=False, tag='%', id='%'):
    '''
    Retrieve honeypot tag information from the internal database

    ARGUMENTS:
        DB_connection (<mariadb connection object>) = connection with the internal database
        mode (bool, optional) : False means accurate answer, True means extended answer
        tag (string, optional) : name of the honeypot tag whose information we want
        id (string, optional) : id of the honeypot tag whose information we want
    '''
    # Normalize arguments according to the mode
    if mode:
        tag = normalize_used_arguments(tag, "%")
        id = normalize_used_arguments(id, "%")
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    cur.execute("SELECT Hp_Tags.id_tag as tag_id, Tags.tag as tag, group_concat(IFNULL(Hp_Tags.id_hp,'NULL') separator '||') AS hp_id FROM Hp_Tags LEFT JOIN Tags on Hp_Tags.id_tag=Tags.id WHERE tag LIKE ? AND Hp_Tags.id_tag like ? group by tag_id", (tag, id))
    # Convert answer to JSON
    row_headers = [x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return json_data

def tag_serv(DB_connection, mode=False, tag='%', id='%'):
    '''
    Retrieve server tag information from the internal database

    ARGUMENTS:
        DB_connection (<mariadb connection object>) = connection with the internal database
        mode (bool, optional) : False means accurate answer, True means extended answer
        tag (string, optional) : name of the server tag whose information we want
        id (string, optional) : id of the server tag whose information we want
    '''
    # Normalize arguments according to the mode
    if mode:
        tag = normalize_used_arguments(tag, "%")
        id = normalize_used_arguments(id, "%")
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    cur.execute("SELECT Serv_Tags.id_tag as tag_id, Tags.tag as tag, group_concat(IFNULL(Serv_Tags.id_serv,'NULL') separator '||') AS serv_id FROM Serv_Tags LEFT JOIN Tags on Serv_Tags.id_tag=Tags.id WHERE tag LIKE ? AND Serv_Tags.id_tag like ? group by tag_id", (tag, id))
    # Convert answer to JSON
    row_headers = [x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return json_data

############################### SERVER SECTION ###############################


def server(DB_connection, mode=False, ip="%", id="%", name="%", tags="%", state="%", descr="%", ssh_port="%"):
    '''
    Retrieve a JSON with all the data of one or several servers from the internal database

    ARGUMENTS:
        DB_connection (<mariadb connection object>) = connection with the internal database
        mode (bool, optional) : False means accurate answer, True means extended answer
        ip (string, optional) : ip address of the server whose information we want
        id (string, optional) : id of the server whose information we want
        name (string, optional) : name of the server whose information we want
        tags (string, optional) : tag(s) of the server whose information we want
        state (string, optional) : state of the server whose information we want
        descr (string, optional) : description of the server whose information we want
        ssh_port (string, optional) : SSH port of the server whose information we want
    '''
    # Frame used arguments with %
    if mode:
        ip = normalize_used_arguments(ip, "%")
        id = normalize_used_arguments(id, "%")
        name = normalize_used_arguments(name, "%")
        state = normalize_used_arguments(state, "%")
        descr = normalize_used_arguments(descr, "%")
        ssh_port = normalize_used_arguments(ssh_port, "%")
    tags_request = normalize_tags_arguments(mode, "serv_tags", tags)
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    cur.execute("SELECT * FROM v_serv_full WHERE serv_ip LIKE ? AND serv_id LIKE ? AND serv_name LIKE ? AND " + tags_request +
                " AND serv_state LIKE ? AND serv_descr LIKE ? AND serv_ssh_port LIKE ?", (ip, id, name, state, descr, ssh_port))
    # Convert answer to JSON
    row_headers = [x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return json_data

############################### HONEYPOT SECTION ###############################


def honeypot(DB_connection, mode=False, id="%", name="%", tags="%", state="%", descr="%", port="%", parser="%", logs="%", source="%", port_container="%"):
    '''
    Retrieve a JSON with all the data of one or several honeypots from the internal database

    ARGUMENTS:
        DB_connection (<mariadb connection object>) = connection with the internal database
        mode (bool, optional) : False means accurate answer, True means extended answer
        id (string, optional) : id of the server whose information we want
        name (string, optional) : name of the honeypot whose information we want
        tags (string, optional) : tag(s) of the honeypot whose information we want
        state (string, optional) : state of the honeypot whose information we want
        descr (string, optional) : description of the honeypot whose information we want
        port (string, optional) : port of the honeypot whose information we want
        parser (string, optional) : parsing rules for the honeypot whose information we want
        logs (string, optional) : path of the log files of the honeypot whose information we want
        source (string, optional) : path of the dockerfile of the honeypot whose information we want
        port_container (string, optional) : container port of the the honeypot whose information we want
    '''
    # Frame used arguments with %
    if mode:
        id = normalize_used_arguments(id, "%")
        name = normalize_used_arguments(name, "%")
        state = normalize_used_arguments(state, "%")
        descr = normalize_used_arguments(descr, "%")
        port = normalize_used_arguments(port, "%")
        parser = normalize_used_arguments(parser, "%")
        logs = normalize_used_arguments(logs, "%")
        source = normalize_used_arguments(source, "%")
        port_container = normalize_used_arguments(port_container, "%")
    tags_request = normalize_tags_arguments(mode, "hp_tags", tags)
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    cur.execute("SELECT * FROM v_hp_full WHERE hp_id LIKE ? AND hp_name LIKE ? AND "+tags_request +
                " AND hp_state LIKE ? AND hp_descr LIKE ? AND hp_port LIKE ? AND hp_parser LIKE ? AND hp_logs LIKE ? AND hp_source LIKE ? AND hp_port_container LIKE ?", (id, name, state, descr, port, parser, logs, source, port_container))
    # Convert answer to JSON
    row_headers = [x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return json_data

############################### LINK SECTION ###############################


def link(DB_connection, mode=False, id="%", nb_hp="%", nb_serv="%", tags_hp="%", tags_serv="%"):
    '''
    Retrieve a JSON with all the data of one or several link from the internal database

    ARGUMENTS:
        DB_connection (<mariadb connection object>) = connection with the internal database
        mode (bool, optional) : False means accurate answer, True means extended answer
        id (string, optional) : id of the link whose information we want
        nb_hp (string, optional) : number of honeypots supported by the link whose information we want
        nb_serv (string, optional) : number of servers supported by the link whose information we want
        tags_hp (string, optional) : tags of the honeypots supported by the link whose information we want
        tags_serv (string, optional) : tags of the servers supported by the link whose information we want
    '''
    # Frame used arguments with %
    if mode:
        id = normalize_used_arguments(id, "%")
        nb_hp = normalize_used_arguments(nb_hp, "%")
        nb_serv = normalize_used_arguments(nb_serv, "%")
    tags_hp_request = normalize_tags_arguments(mode, "link_tags_hp", tags_hp)
    tags_serv_request = normalize_tags_arguments(
        mode, "link_tags_serv", tags_serv)
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    cur.execute("SELECT * FROM v_link_full_hp_serv WHERE link_id LIKE ? AND link_nb_hp LIKE ? AND link_nb_serv LIKE ? AND " +
                tags_hp_request+" AND "+tags_serv_request+" AND link_nb_hp <= link_nb_serv", (id, nb_hp, nb_serv))
    # Convert answer to JSON
    row_headers = [x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    # Get MariaDB cursor
    cur2 = DB_connection.cursor()
    # Execute SQL request
    cur2.execute("SELECT * FROM v_link_full_serv_hp WHERE link_id LIKE ? AND link_nb_hp LIKE ? AND link_nb_serv LIKE ? AND " +
                 tags_hp_request+" AND "+tags_serv_request+" AND link_nb_hp > link_nb_serv", (id, nb_hp, nb_serv))
    # Convert answer to JSON
    row_headers = [x[0] for x in cur2.description]
    rv = cur2.fetchall()
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return json_data


def link_force_hp_serv(DB_connection, mode=False, id="%", nb_hp="%", nb_serv="%", tags_hp="%", tags_serv="%"):
    '''
    Retrieve a JSON with all the data of one or several link from the internal database

    ARGUMENTS:
        DB_connection (<mariadb connection object>) = connection with the internal database
        mode (bool, optional) : False means accurate answer, True means extended answer
        id (string, optional) : id of the link whose information we want
        nb_hp (string, optional) : number of honeypots supported by the link whose information we want
        nb_serv (string, optional) : number of servers supported by the link whose information we want
        tags_hp (string, optional) : tags of the honeypots supported by the link whose information we want
        tags_serv (string, optional) : tags of the servers supported by the link whose information we want
    '''
    # Frame used arguments with %
    if mode:
        id = normalize_used_arguments(id, "%")
        nb_hp = normalize_used_arguments(nb_hp, "%")
        nb_serv = normalize_used_arguments(nb_serv, "%")
    tags_hp_request = normalize_tags_arguments(mode, "link_tags_hp", tags_hp)
    tags_serv_request = normalize_tags_arguments(
        mode, "link_tags_serv", tags_serv)
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    cur.execute("SELECT * FROM v_link_full_hp_serv WHERE link_id LIKE ? AND link_nb_hp LIKE ? AND link_nb_serv LIKE ? AND " +
                tags_hp_request+" AND "+tags_serv_request, (id, nb_hp, nb_serv))
    # Convert answer to JSON
    row_headers = [x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return json_data


def link_force_serv_hp(DB_connection, mode=False, id="%", nb_hp="%", nb_serv="%", tags_hp="%", tags_serv="%"):
    '''
    Retrieve a JSON with all the data of one or several link from the internal database

    ARGUMENTS:
        DB_connection (<mariadb connection object>) = connection with the internal database
        mode (bool, optional) : False means accurate answer, True means extended answer
        id (string, optional) : id of the link whose information we want
        nb_hp (string, optional) : number of honeypots supported by the link whose information we want
        nb_serv (string, optional) : number of servers supported by the link whose information we want
        tags_hp (string, optional) : tags of the honeypots supported by the link whose information we want
        tags_serv (string, optional) : tags of the servers supported by the link whose information we want
    '''
    # Frame used arguments with %
    if mode:
        id = normalize_used_arguments(id, "%")
        nb_hp = normalize_used_arguments(nb_hp, "%")
        nb_serv = normalize_used_arguments(nb_serv, "%")
    tags_hp_request = normalize_tags_arguments(mode, "link_tags_hp", tags_hp)
    tags_serv_request = normalize_tags_arguments(
        mode, "link_tags_serv", tags_serv)
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    cur.execute("SELECT * FROM v_link_full_serv_hp WHERE link_id LIKE ? AND link_nb_hp LIKE ? AND link_nb_serv LIKE ? AND " +
                tags_hp_request+" AND "+tags_serv_request, (id, nb_hp, nb_serv))
    # Convert answer to JSON
    row_headers = [x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return json_data
