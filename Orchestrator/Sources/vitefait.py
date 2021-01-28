from Gotham_link_BDD import get_server_infos,get_honeypot_infos,get_tag_infos,get_link_infos
from Gotham_link_BDD import add_server_DB,add_honeypot_DB,add_link_DB,add_lhs_DB
from Gotham_link_BDD import remove_server_DB,remove_honeypot_DB,remove_link_DB

from Gotham_normalize import normalize_honeypot_infos,normalize_server_infos,normalize_link_infos
from Gotham_check import check_used_port, check_ssh
import mariadb

DB_settings = {"username":"gotham", "password":"password", "hostname":"192.168.1.172", "port":"3306", "database":"GOTHAM"}
lk_infos = {"id":"lk-1BFB3AFE3FEE1FEFB1D25E22FC2CA69F", "nb_hp": 4, "nb_serv": 2, "tags_hp":"OpenSSH,SSH,Elasticsearch", "tags_serv":"Europe,Suisse,Geneve,TagDeTest42,TagDeTest4254,TagDeTest427"}
lk_port_infos = {"id":"lk-1BFB3AFE3FEE1FEFB1D25E22FC2CA69F", "nb_hp": 4, "nb_serv": 2, "tags_hp":"OpenSSH,SSH,Elasticsearch", "tags_serv":"Europe ,  suisse,  geneve,TagDeTest42,TagDeTest4254,TagDeTest427","ports":"22, 189  ,  469,6484,88"}
# Server settings
server_infos = {"ip":"172.0.0.2", "id":"sv-71F6EFA6F2FF11EB830EF9FEFD2CA37F", "tags":"Europe", "state":"TO_ADD" }
recordings = {'id':'sv-62323F6F323F38F42d656DF861566666','name':'serveur-test-6','descr':'blabla','tags':'Europe,France,SSH,TestTag,TagDeTest4TesTag666','ip':'98.254.99.99','ssh_key':'non','ssh_port':'22','state':'ERROR'}
honeypot_infos = {"id":"hp-1F5B3AFE32EE71EFB1D25EFFFC2CA69F", 'name':'hp-test-6','tags':'TestTag22,TesTag666,TagDeTest42', 'port':22,'parser':'TO_ADD','logs':'TO_ADD','source':"TO_ADD", "port_container":22,'state':'UNUSED'}
##########-SETTINGS-##########


##########-TESTS-##########
print("########## ########## TEST LINK BDD########## ##########")
print("########## Add server ##########")
print(add_server_DB(DB_settings, recordings))
print("########## Add Honeypot ##########")
print(add_honeypot_DB(DB_settings, honeypot_infos))
print("########## Add link ##########")
print(add_link_DB(DB_settings, lk_infos))

print("########## Get server infos tag false ##########")
print(get_server_infos(DB_settings, mode=False, tags=recordings["tags"]))
print("########## Get server infos tag true ##########")
print(get_server_infos(DB_settings, mode=True, tags=recordings["tags"]))
print("########## Get server infos ip ##########")
print(get_server_infos(DB_settings, mode=True, ip=server_infos["ip"]))
print("########## Get tag infos id ##########")
print(get_tag_infos(DB_settings, id="1"))
print("########## Get Honeypot infos tag ##########")
print(get_honeypot_infos(DB_settings, tags=honeypot_infos["tags"]))
print("########## Get Honeypot infos port ##########")
print(get_honeypot_infos(DB_settings, mode=True, port=honeypot_infos["port"]))
print("########## Get link infos tag ##########")
print(get_link_infos(DB_settings, tags_hp=lk_infos["tags_hp"]))
print("########## Get link infos id ##########")
print(get_link_infos(DB_settings, mode=True, id=lk_infos["id"]))
print("########## ########## ########## ########## ##########")

print("########## ########## TEST NORMALIZE ########## ##########")
print("########## Normalize Honeypot ##########")
print(normalize_honeypot_infos(honeypot_infos))
print("########## Normalize Server ##########")
print(normalize_server_infos(recordings))
print("########## Normalize Link ##########")
print(normalize_link_infos(lk_port_infos))

print("########## ########## TEST REMOVE ########## ##########")
print("########## Delete Server ##########")
print(remove_server_DB(DB_settings, server_infos['id']))
print("########## Delete Honeypot ##########")
print(remove_honeypot_DB(DB_settings, honeypot_infos['id']))
print("########## Delete Link ##########")
print(remove_link_DB(DB_settings, lk_infos['id']))
