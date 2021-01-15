from . import server_infos
from . import add_server_in_BDD

def get_server_infos(DB_username, DB_password, DB_hostname, DB_port, DB_database, ip="%", id="%", name="%", tag="%", state="%"):
    return server_infos.main(DB_username=DB_username, DB_password=DB_password, DB_hostname=DB_hostname, DB_port=DB_port, DB_database=DB_database, ip=ip, id=id, name=name, tag=tag, state=state)

def add_server(DB_username, DB_password, DB_hostname, DB_port, DB_database, recording_list):
    return add_server_in_BDD.main(DB_username, DB_password, DB_hostname, DB_port, DB_database, recording_list)