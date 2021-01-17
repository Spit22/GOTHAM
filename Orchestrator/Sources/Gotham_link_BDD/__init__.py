from . import server_infos
from . import add_server_in_IDB

########## READ IN THE INTERNAL DATABASE ##########
def get_server_infos(DB_settings, ip="%", id="%", name="%", tag="%", state="%"):
    return server_infos.main(DB_settings, ip=ip, id=id, name=name, tag=tag, state=state)

#def get_honeypot_infos(DB_settings, ...):

#def get_link_infos(DB_settings, ...):


########## WRITE IN THE INTERNAL DATABASE ##########
def add_server_DB(DB_settings, server_infos):
    return add_server_in_IDB.main(DB_settings, server_infos)


#def add_honeypot_DB(DB_settings, ...):

#def add_link_DB(DB_settings, ...):