from . import server_infos

def get_server_infos(username, password, hostname, port, database, ip="%", id="%", name="%", tag="%", state="%"):
    return server_infos.main(username=username, password=password, hostname=hostname, port=port, database=database, ip=ip, id=id, name=name, tag=tag, state=state)
