import mariadb
import sys

def main(DB_settings, tags, separator=','):
    tag_list = tags.split(separator)
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
    for tag in tag_list:
        tag = tag.strip()
        #Check doublon
        cur.execute("INSERT INTO Tags (tag) VALUES (?)", (tag))
        # Add the tag to the Tags table
        cur.execute("INSERT INTO Tags (tag) VALUES (?)", (tag))
        # Retrieve the ID of the tag just added
        cur.execute("INSERT INTO Tags (tag) VALUES (?)", (tag))
        


