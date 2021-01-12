from Gotham_link_BDD import get_server_infos

# Database settings
username = "root"
password = ""
hostname = "localhost"
port = "3306"
database = "GOTHAM"

# Server settings
ip = "172.0.0.29"
id = "sv-9D5E49EA33CD11EBAFE55BF9FB2CA371"
name=""
tag = "Europe"
state = "TO_ADD"

print(get_server_infos(username, password, hostname, port, database, ip=ip))