from . import server_infos

username = "root"
password = ""
hostname = "localhost"
port = "3306"
database = "GOTHAM"

# Server settings
ip = "172.0.0.29"
id = "sv-9D5E49EA33CD11EBAFE55BF9FB2CA371"
tag = "Europe"
state = "TO_ADD"

def get_server_infos():
    return server_infos.main(username=username, password=password, hostname=hostname, port=port, database=database, state=state)

