import mariadb
import sys

def main(DB_username, DB_password, DB_hostname, DB_port, DB_database, recording_list):
    try:
        conn = mariadb.connect(
            user=DB_username,
            password=DB_password,
            host=DB_hostname,
            port=int(DB_port),
            database=DB_database
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB server: {e}")
        sys.exit(1)
    # Get MariaDB cursor
    cur = conn.cursor()
    # Execute SQL request(s)
    try:
        for recording in recording_list:
            print(recording)
            cur.execute("INSERT INTO Server (id,name,descr,ip,ssh_key,ssh_port,state) VALUES (?,?,?,?,?,?,?)", (recording[0],recording[1],recording[2],recording[3],recording[4],recording[5],recording[6]))
        conn.commit()
        return True
    except mariadb.Error as e:
        print(e)
        return False