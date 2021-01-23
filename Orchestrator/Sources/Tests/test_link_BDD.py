##########-IMPORT SECTION-##########
from Gotham_link_BDD import get_server_infos, add_server_DB, get_tag_infos
##########-IMPORT SECTION-##########

##########-SETTINGS-##########
# Database settings
DB_settings = {"username":"root", "password":"password", "hostname":"localhost", "port":"3306", "database":"GOTHAM"}
# Server settings
server_infos = {"ip":"172.0.0.1", "id":"sv-7126ECA632EC11EB830EA9EEFB2CA371", "name":"", "tags":"Europe", "state":"TO_ADD" }
recordings = {'id':'sv-62323666323338642d65653864666666','name':'serveur-test-6','descr':'blabla','tags':'Europe,France,SSH,TestTag,TesTag666','ip':'42.42.42.45','ssh_key':'non','ssh_port':'22','state':'to add'}
##########-SETTINGS-##########


##########-TESTS-##########
print("####################")
#print(get_server_infos(DB_settings, mode=True, tag=server_infos["tag"]))
print("####################")
#print(get_tag_infos(DB_settings, id="1"))
print("####################")
print(add_server_DB(DB_settings, recordings))
print("####################")
#print(get_server_infos(DB_settings, ip=ip))
print("####################")
##########-TESTS-##########
