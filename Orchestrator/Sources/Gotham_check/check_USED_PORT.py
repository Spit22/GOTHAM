
def get_used_port(DB_connection):
	# Determine used ports on datacenter side
	#
	# DB_connection (dict) : all information to connect to db
	#
	# Return a list of ports used on the datacenter

    # Get MariaDB cursor
    cur = DB_connection.cursor()
    # Execute SQL request
    cur.execute("SELECT DISTINCT port FROM Honeypot")
    # Convert answer to JSON
    res = [item[0] for item in cur.fetchall()]
    return res
