import mariadb
import sys

def main(username, password, hostname, port, database, ip="%", id="%", name="%", tag="%"):
    print(ip, id, name, tag)
    
    #faire ça pour tous les champs avec conditions pour ne modifier que les paramètres utilisés
    tag = "%"+tag+"%"
    
    try:
        conn = mariadb.connect(
            user=username,
            password=password,
            host=hostname,
            port=int(port),
            database=database
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    # Get Cursor
    cur = conn.cursor()

    cur.execute("SELECT * FROM v_serv_full WHERE serv_ip LIKE ? AND serv_id LIKE ? AND serv_name LIKE ? AND serv_tags LIKE ?", (ip,id,name,tag))

    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for result in rv:
       json_data.append(dict(zip(row_headers,result)))
    return json_data


    