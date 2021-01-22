import mariadb
import sys

############################### MISCELLANEOUS ###############################

def normalize_used_arguments(arg, default_arg):
    if not(arg == default_arg):
        return "%" + arg + "%"
    else:
        return default_arg

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

def server(DB_connection, mode=False, ip="%", id="%", name="%", tag="%", state="%", descr="%", ssh_port="%"):
    # Frame used arguments with %
    if mode:
        ip = normalize_used_arguments(ip, "%")
        id = normalize_used_arguments(id, "%")
        name = normalize_used_arguments(name, "%")
        tag = normalize_used_arguments(tag, "%")
        state = normalize_used_arguments(state, "%")
        descr = normalize_used_arguments(descr, "%")
        ssh_port = normalize_used_arguments(ssh_port, "%")
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    cur.execute("SELECT * FROM v_serv_full WHERE serv_ip LIKE ? AND serv_id LIKE ? AND serv_name LIKE ? AND serv_tags LIKE ? AND serv_state LIKE ? AND serv_descr LIKE ? AND serv_ssh_port LIKE ?", (ip,id,name,tag,state,descr,ssh_port))
    # Convert answer to JSON
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for result in rv:
       json_data.append(dict(zip(row_headers,result)))
    # Before the return, close the connection
    return json_data

############################### HONEYPOT SECTION ###############################

def honeypot(DB_connection, mode=False, id="%", name="%", tag="%", state="%", descr="%", port="%", parser="%", logs="%", source="%", id_container="%"):
    # Frame used arguments with %
    if mode:
        id = normalize_used_arguments(id, "%")
        name = normalize_used_arguments(name, "%")
        tag = normalize_used_arguments(tag, "%")
        state = normalize_used_arguments(state, "%")
        descr = normalize_used_arguments(descr, "%")
        port = normalize_used_arguments(port, "%")
        parser = normalize_used_arguments(parser, "%")
        logs = normalize_used_arguments(logs, "%")
        source = normalize_used_arguments(source, "%")
        id_container = normalize_used_arguments(id_container, "%")
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    cur.execute("SELECT * FROM v_hp_full WHERE hp_id LIKE ? AND hp_name LIKE ? AND hp_tags LIKE ? AND hp_state LIKE ? AND hp_descr LIKE ? AND hp_port LIKE ? AND hp_parser LIKE ? AND hp_logs LIKE ? AND hp_source LIKE ? AND hp_id_container LIKE ?", (id,name,tag,state,descr,port,parser,logs,source,id_container))
    # Convert answer to JSON
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for result in rv:
       json_data.append(dict(zip(row_headers,result)))
    # Before the return, close the connection
    return json_data