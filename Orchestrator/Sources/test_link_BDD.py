##########-IMPORT SECTION-##########
from Gotham_link_BDD import get_server_infos, add_server_DB, get_tag_infos
##########-IMPORT SECTION-##########

##########-SETTINGS-##########
# Database settings
DB_settings = {"username":"gotham", "password":"password", "hostname":"192.168.1.172", "port":"3306", "database":"GOTHAM"}
# Server settings
server_infos = {"ip":"172.0.0.1", "id":"sv-7126ECA632EC11EB830EA9EEFB2CA371", "name":"", "tag":"Europe", "state":"TO_ADD" }
##########-SETTINGS-##########

##########-TESTS-##########
print("####################")
#print(get_server_infos(DB_settings, mode=True, tag=server_infos["tag"]))
print("####################")
#print(get_tag_infos(DB_settings, id="1"))
print("####################")
#print(add_server_DB(DB_settings, recording_list))
print("####################")
#print(get_server_infos(DB_settings, ip=ip))
##########-TESTS-##########