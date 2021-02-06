import mariadb
import sys
import configparser
import re
import os

# Set the path of the home directory of GOTHAM
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')

# Retrieve settings from config file
config = configparser.ConfigParser()
config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
_separator = config['tag']['separator']

############################### MISCELLANEOUS ###############################

def normalize_used_arguments(arg, default_arg):
    if not(arg == default_arg):
        return "%" + str(arg) + "%"
    else:
        return default_arg

def normalize_tags_arguments(mode, column, tags):
    if not(re.match(r"^[a-zA-Z0-9_\-]*$", column)):
        sys.exit("Error in column : invalid syntax")
    if(tags!="%"):
        request=""
        tag_list=tags.split(_separator)
        for a_tag in tag_list:
            if not(re.match(r"^[a-zA-Z0-9_\-]*$", a_tag)):
                sys.exit("Error in tags : invalid syntax")
            if (request==""):
                request="("+column+" like '"
            else:
                if mode:
                    request+="' OR "+column+" like '"
                else:
                    request+="' AND "+column+" like '"
            a_tag = normalize_used_arguments(a_tag, "%")
            request+=a_tag
        request+="')"
    else:
        request=column+" like '%'"
    return request

############################### TAG SECTION ###############################

def tag(DB_connection, mode=False, tag='%', id='%'):
    if mode:
        tag = normalize_used_arguments(tag, "%")
        id = normalize_used_arguments(id, "%")
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    cur.execute("SELECT * FROM Tags WHERE tag LIKE ? AND id like ?", (tag,id))
    # Convert answer to JSON
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for result in rv:
       json_data.append(dict(zip(row_headers,result)))
    return json_data

############################### SERVER SECTION ###############################

def server(DB_connection, mode=False, ip="%", id="%", name="%", tags="%", state="%", descr="%", ssh_port="%"):
    # Frame used arguments with %
    if mode:
        ip = normalize_used_arguments(ip, "%")
        id = normalize_used_arguments(id, "%")
        name = normalize_used_arguments(name, "%")
        state = normalize_used_arguments(state, "%")
        descr = normalize_used_arguments(descr, "%")
        ssh_port = normalize_used_arguments(ssh_port, "%")
    tags_request=normalize_tags_arguments(mode,"serv_tags",tags)
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    cur.execute("SELECT * FROM v_serv_full WHERE serv_ip LIKE ? AND serv_id LIKE ? AND serv_name LIKE ? AND " + tags_request + " AND serv_state LIKE ? AND serv_descr LIKE ? AND serv_ssh_port LIKE ?", (ip,id,name,state,descr,ssh_port))
    # Convert answer to JSON
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for result in rv:
       json_data.append(dict(zip(row_headers,result)))
    return json_data

############################### HONEYPOT SECTION ###############################

def honeypot(DB_connection, mode=False, id="%", name="%", tags="%", state="%", descr="%", port="%", parser="%", logs="%", source="%", port_container="%"):
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

    tags_request=normalize_tags_arguments(mode,"hp_tags",tags)
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    cur.execute("SELECT * FROM v_hp_full WHERE hp_id LIKE ? AND hp_name LIKE ? AND "+tags_request+" AND hp_state LIKE ? AND hp_descr LIKE ? AND hp_port LIKE ? AND hp_parser LIKE ? AND hp_logs LIKE ? AND hp_source LIKE ? AND hp_port_container LIKE ?", (id,name,state,descr,port,parser,logs,source,port_container))
    # Convert answer to JSON
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for result in rv:
       json_data.append(dict(zip(row_headers,result)))
    return json_data

############################### LINK SECTION ###############################

def link(DB_connection, mode=False, id="%", nb_hp="%", nb_serv="%", tags_hp="%", tags_serv="%"):
    # Frame used arguments with %
    if mode:
        id = normalize_used_arguments(id, "%")
        nb_hp = normalize_used_arguments(nb_hp, "%")
        nb_serv = normalize_used_arguments(nb_serv, "%")
    
    tags_hp_request=normalize_tags_arguments(mode,"link_tags_hp",tags_hp)
    tags_serv_request=normalize_tags_arguments(mode,"link_tags_serv",tags_serv)
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    cur.execute("SELECT * FROM v_link_full_hp_serv WHERE link_id LIKE ? AND link_nb_hp LIKE ? AND link_nb_serv LIKE ? AND "+tags_hp_request+" AND "+tags_serv_request+" AND link_nb_hp <= link_nb_serv", (id,nb_hp,nb_serv))
    # Convert answer to JSON
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for result in rv:
       json_data.append(dict(zip(row_headers,result)))

    # Get MariaDB cursor
    cur2 = DB_connection.cursor()
    # Execute SQL request
    cur2.execute("SELECT * FROM v_link_full_serv_hp WHERE link_id LIKE ? AND link_nb_hp LIKE ? AND link_nb_serv LIKE ? AND "+tags_hp_request+" AND "+tags_serv_request+" AND link_nb_hp > link_nb_serv", (id,nb_hp,nb_serv))
    # Convert answer to JSON
    row_headers=[x[0] for x in cur2.description]
    rv = cur2.fetchall()
    for result in rv:
       json_data.append(dict(zip(row_headers,result)))
    return json_data
