import sys

def get_used_port(DB_connection):
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    cur.execute("SELECT DISTINCT port FROM Honeypot")
    # Convert answer to JSON
    rv = cur.fetchall()
    res=[]
    for result in rv:
       res.append(result[0])
    # Before the return, close the connection
    return res

