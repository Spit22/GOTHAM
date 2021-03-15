import sys


def get_used_port(DB_connection):
    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    cur.execute("SELECT DISTINCT port FROM Honeypot")
    # Convert answer to JSON
    res = [item[0] for item in cur.fetchall()]
    return res
