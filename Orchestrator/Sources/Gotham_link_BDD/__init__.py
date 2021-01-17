from . import get_infos
from . import add_in_IDB

########## READ IN THE INTERNAL DATABASE ##########
def get_server_infos(DB_settings, mode=False, ip="%", id="%", name="%", tag="%", state="%"):
    return get_infos.server(DB_settings, mode, ip, id, name, tag, state)

def get_tag_infos(DB_settings, mode=False, tag="%", id="%"):
    return get_infos.tag(DB_settings, mode, tag, id)

#def get_honeypot_infos(DB_settings, ...):

#def get_link_infos(DB_settings, ...):


########## WRITE IN THE INTERNAL DATABASE ##########
def add_server_DB(DB_settings, server_infos):
    return add_in_IDB.server(DB_settings, server_infos)


#def add_honeypot_DB(DB_settings, ...):

#def add_link_DB(DB_settings, ...):