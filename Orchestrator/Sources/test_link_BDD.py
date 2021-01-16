from Gotham_link_BDD import get_server_infos, add_server_DB

# Database settings
DB_settings = {"username":"gotham", "password":"password", "hostname":"192.168.1.172", "port":"3306", "database":"GOTHAM"}

# Server settings
server_infos = {"ip":"172.0.0.1", "id":"sv-cestpourletestdecrituredanslabdd", "name":"", "tag":"Europe", "state":"TO_ADD" }

print(get_server_infos(DB_settings, ip=server_infos["ip"]))
print("#########################################")
#print(add_server_DB(DB_settings, recording_list))
print("#########################################")
#print(get_server_infos(DB_settings, ip=ip))