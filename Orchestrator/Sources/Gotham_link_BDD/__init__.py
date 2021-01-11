import mariadb
import sys
from . import server_infos_by_ip

username = "root"
password = ""
hostname = "localhost"
port = "3306"
database = "GOTHAM"

ip = "172.0.0.29"
id = "sv-9D5E49EA33CD11EBAFE55BF9FB2CA371"
tag = "Europe"

def get_server_infos_by_ip():
    return server_infos_by_ip.main(username=username, password=password, hostname=hostname, port=port, database=database, id=id, tag=tag)

