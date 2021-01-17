import mariadb
import sys

def normalize_used_arguments(arg, default_arg):
    if not(arg == default_arg):
        return "%" + arg + "%"
    else:
        return default_arg

def server(DB_settings, mode, ip, id, name, tag, state):
    # Frame used arguments with %
    if mode:
        ip = normalize_used_arguments(ip, "%")
        id = normalize_used_arguments(id, "%")
        name = normalize_used_arguments(name, "%")
        tag = normalize_used_arguments(tag, "%")
        state = normalize_used_arguments(state, "%")
    # Start connection with mariadb server, hosting the internal DB
    try:
        conn = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB server: {e}")
        sys.exit(1)
    # Get MariaDB cursor
    cur = conn.cursor()
    # Execute SQL request
    cur.execute("SELECT * FROM v_serv_full WHERE serv_ip LIKE ? AND serv_id LIKE ? AND serv_name LIKE ? AND serv_tags LIKE ? AND serv_state LIKE ?", (ip,id,name,tag,state))
    # Convert answer to JSON
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for result in rv:
       json_data.append(dict(zip(row_headers,result)))
    # Before the return, close the connection
    conn.close()
    return json_data


def tag(DB_settings, mode, tag, id):
    if mode:
        tag = normalize_used_arguments(tag, "%")
        id = normalize_used_arguments(id, "%")
    try:
        conn = mariadb.connect(
            user=DB_settings["username"],
            password=DB_settings["password"],
            host=DB_settings["hostname"],
            port=int(DB_settings["port"]),
            database=DB_settings["database"]
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB server: {e}")
        sys.exit(1)
    # Get MariaDB cursor
    cur = conn.cursor()
    # Execute SQL request
    cur.execute("SELECT * FROM Tags WHERE tag LIKE ? AND id like ?", (tag,id))
    # Convert answer to JSON
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for result in rv:
       json_data.append(dict(zip(row_headers,result)))
    conn.close()
    return json_data




    