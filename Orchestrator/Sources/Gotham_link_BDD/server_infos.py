import mariadb
import sys

def normalize_used_arguments(arg, default_arg):
    if not(arg == default_arg):
        return "%" + arg + "%"
    else:
        return default_arg

def main(username, password, hostname, port, database, ip, id, name, tag, state):
    # Frame used arguments with %
    ip = normalize_used_arguments(ip, "%")
    id = normalize_used_arguments(id, "%")
    name = normalize_used_arguments(name, "%")
    tag = normalize_used_arguments(tag, "%")
    state = normalize_used_arguments(state, "%")
    # Start connection with mariadb server, hosting the internal DB
    try:
        conn = mariadb.connect(
            user=username,
            password=password,
            host=hostname,
            port=int(port),
            database=database
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
    return json_data


    