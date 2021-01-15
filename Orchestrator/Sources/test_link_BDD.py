from Gotham_link_BDD import get_server_infos, add_server

# Database settings
username = "root"
password = ""
hostname = "localhost"
port = "3306"
database = "GOTHAM"

# Server settings
ip = "8.8.8.4"
id = "sv-cestpourletestdecrituredanslabdd"
name=""
tag = "Europe"
state = "TO_ADD"

recording_list=[['sv-testecriture','vps-42.hebergeur.fr','Second serveur de test.','42.42.42.42','TO_ADD',22,'']]

print(get_server_infos(username, password, hostname, port, database, ip=ip))
print("#########################################")
print(add_server(username, password, hostname, port, database, recording_list))
print("#########################################")
print(get_server_infos(username, password, hostname, port, database, ip=ip))