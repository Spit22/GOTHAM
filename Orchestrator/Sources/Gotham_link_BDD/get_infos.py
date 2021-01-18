import mariadb
import sys

def normalize_used_arguments(arg, default_arg):
    if not(arg == default_arg):
        return "%" + arg + "%"
    else:
        return default_arg

def server(DB_connection, mode=False, ip="%", id="%", name="%", tag="%", state="%"):
    # Frame used arguments with %
    if mode:
        ip = normalize_used_arguments(ip, "%")
        id = normalize_used_arguments(id, "%")
        name = normalize_used_arguments(name, "%")
        tag = normalize_used_arguments(tag, "%")
        state = normalize_used_arguments(state, "%")
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    cur.execute("SELECT * FROM v_serv_full WHERE serv_ip LIKE ? AND serv_id LIKE ? AND serv_name LIKE ? AND serv_tags LIKE ? AND serv_state LIKE ?", (ip,id,name,tag,state))
    # Convert answer to JSON
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for result in rv:
       json_data.append(dict(zip(row_headers,result)))
    # Before the return, close the connection
    return json_data


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
