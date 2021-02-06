from Gotham_link_BDD import get_server_infos,get_honeypot_infos,get_tag_infos,get_link_infos
from Gotham_link_BDD import add_server_DB,add_honeypot_DB,add_link_DB,add_lhs_DB
from Gotham_link_BDD import remove_server_DB,remove_honeypot_DB,remove_link_DB

from Gotham_normalize import normalize_honeypot_infos,normalize_server_infos,normalize_link_infos
from Gotham_check import check_used_port, check_ssh
import mariadb

from termcolor import colored, cprint

import rm_server

##########-SETTINGS-##########
DB_settings = {"username":"gotham", "password":"password", "hostname":"localhost", "port":"3306", "database":"GOTHAM"}

lk_port_infos = {"id":"lk-1BFB3AFE3FEE1FEFB1D25E22FC2CA69F", "nb_hp": 4, "nb_serv": 2, "tags_hp":"OpenSSH,SSH,Elasticsearch", "tags_serv":"Europe ,  suisse,  geneve,TagDeTest42,TagDeTest4254,TagDeTest427","ports":"22, 189  ,  469,6484,88"}
serv_already_exist=[{'serv_id': 'sv-88784AF833CD11EBAEA003EBFB2CA371', 'serv_name': 'vps-8.hebergeur.foo', 'serv_descr': 'Server for test', 'serv_ip': '172.0.0.25', 'serv_ssh_key': 'To_Add', 'serv_ssh_port': 22, 'serv_state': 'To_Add', 'serv_tags': 'Europe||France||Vannes', 'serv_created_at': 'datetime.datetime(2021, 1, 27, 22, 18, 52)', 'serv_updated_at': 'datetime.datetime(2021, 1, 27, 22, 18, 52)', 'link_id': 'lk-4FD58A38340111EBB0E722F1FB2CA371||||||lk-72660A46340111EBBAC118F3FB2CA371', 'link_nb_hp': '3||||||2', 'link_nb_serv': '5||||||5', 'link_ports': '53,5353,1053||||||789,987,879,897', 'link_tags_hp': 'DNS||||||haute-dispo||port_22||SSH', 'link_tags_serv': 'Europe||France||||||Europe', 'link_created_at': '2021-01-27 22:18:52||||||2021-01-27 22:18:52', 'link_updated_at': '2021-01-27 22:18:52||||||2021-01-27 22:18:52', 'lhs_port': '5353||||||879', 'hp_id': 'hp-5DED2C8A33C911EBADD59A1EFC2CA371||||||hp-75034A4E33C911EB9D009933FC2CA371', 'hp_name': 'Honeypot_DNS||||||Honeypot_openssh', 'hp_descr': 'Hp for test||||||Hp for test', 'hp_port': None, 'hp_parser': 'To Add||||||To Add', 'hp_logs': 'To add||||||To add', 'hp_source': 'To add||||||To add', 'hp_state': 'ERROR||||||UNUSED', 'hp_port_container': '443||||||987', 'hp_tags': 'DNS||||||haute-dispo||OpenSSH||port_22||SSH', 'hp_created_at': '2021-01-27 22:18:52||||||2021-01-27 22:18:52', 'hp_updated_at': '2021-01-27 22:18:52||||||2021-01-27 22:18:52'}]

lk_infos = {"id":"lk-1BFB3AFE3FEE1FEFB1D25E22FC2CA777", "nb_hp": 4, "nb_serv": 2, "tags_hp":"SSH", "tags_serv":"France, Europe", 'ports':'22,186,658'}
server_infos = {'id':'sv-62323F6F323F38F42d656DF861566666','name':'serveur-test-6','descr':'blabla','tags':'Europe,France,SSH,TestTag,TagDeTest4TesTag666','ip':'42.56.99.99','ssh_key':'non','ssh_port':'22','state':'ERROR'}
honeypot_infos = {"id":"hp-1F5B3AFE32EE71EFB1D25EFFFC2CA666", 'name':'hp-test-6','tags':'TestTag22,TesTag666,TagDeTest42', 'port':22,'parser':'TO_ADD','logs':'TO_ADD','source':"TO_ADD", "port_container":22,'state':'UNUSED'}
##########-SETTINGS-##########


print(colored("########## ########## ADD SECTION ########## ##########", 'blue'))
try:
    print(colored("########## Add Server ##########", 'yellow'))
    #print(add_server_DB(DB_settings, server_infos))
except:
    print(colored('[X] add_server_DB failed', 'red'))


try:
    print(colored("########## Add Honeypot ##########", 'yellow'))
    #print(add_honeypot_DB(DB_settings, honeypot_infos))
except:
    print(colored('[X] add_honeypot_DB failed', 'red'))

try:
    print(colored("########## Add Link ##########", 'yellow'))
    print(add_link_DB(DB_settings, lk_infos))
except:
    print(colored('[X] add_link_DB failed', 'red'))

print(colored("########## ########## GET INFOS SECTION ########## ##########", 'blue'))

try:
    print(colored("########## Get Server Infos with tag (false mode) ##########", 'yellow'))
    #print(get_server_infos(DB_settings, mode=False, tags=server_infos["tags"]))
except:
    print(colored('[X] get_server_infos failed', 'red'))

try:
    print(colored("########## Get Server Infos with tag (true mode) ##########", 'yellow'))
    #print(get_server_infos(DB_settings, mode=True, tags=server_infos["tags"]))
except:
    print(colored('[X] get_server_infos failed', 'red'))

try:
    print(colored("########## Get Server Infos with ip (true mode) ##########", 'yellow'))
    #print(get_server_infos(DB_settings, mode=True, ip=server_infos["ip"]))
except:
    print(colored('[X] get_server_infos failed', 'red'))


try:
    print(colored("########## Get Tag Infos with id ##########", 'yellow'))
    #print(get_tag_infos(DB_settings, id="1"))
except:
    print(colored('[X] get_tag_infos failed', 'red'))

try:
    print(colored("########## Get Honeypot Infos with tag ##########", 'yellow'))
    #print(get_honeypot_infos(DB_settings, tags=honeypot_infos["tags"]))
except:
    print(colored('[X] get_honeypot_infos failed', 'red'))

try:
    print(colored("########## Get Honeypot Infos with port ##########", 'yellow'))
    #print(get_honeypot_infos(DB_settings, mode=True, port=honeypot_infos["port"]))
except:
    print(colored('[X] get_honeypot_infos failed', 'red'))

try:
    print(colored("########## Get Link Infos with tag ##########", 'yellow'))
    #print(get_link_infos(DB_settings, tags_hp=lk_infos["tags_hp"]))
except:
    print(colored('[X] get_link_infos failed', 'red'))

try:
    print(colored("########## Get Link Infos with id ##########", 'yellow'))
    print(get_link_infos(DB_settings, id=lk_infos["id"])[0])
except:
    print(colored('[X] get_link_infos failed', 'red'))

print(colored("########## ########## NORMALIZE SECTION ########## ##########", 'blue'))
try:
    print(colored("########## Normalize Honeypot Infos ##########", 'yellow'))
    #print(normalize_honeypot_infos(honeypot_infos))
except:
    print(colored('[X] normalize_honeypot_infos failed', 'red'))

try:
    print(colored("########## Normalize Server Infos ##########", 'yellow'))
    #print(normalize_server_infos(server_infos))
except:
    print(colored('[X] normalize_server_infos failed', 'red'))

try:
    print(colored("########## Normalize Link Infos ##########", 'yellow'))
    #print(normalize_link_infos(lk_infos))
except:
    print(colored('[X] normalize_link_infos failed', 'red'))


print(colored("########## ########## REMOVE SECTION ########## ##########", 'blue'))
try:
    print(colored("########## Remove Server (with id) ##########", 'yellow'))
    #print(remove_server_DB(DB_settings, server_infos['id']))
except:
    print(colored('[X] remove_server_DB failed', 'red'))

try:
    print(colored("########## Remove Honeypot (with id) ##########", 'yellow'))
    #print(remove_honeypot_DB(DB_settings, honeypot_infos['id']))
except:
    print(colored('[X] remove_honeypot_DB failed', 'red'))

try:
    print(colored("########## Remove Link (with id) ##########", 'yellow'))
    print(remove_link_DB(DB_settings, lk_infos['id']))
except:
    print(colored('[X] remove_link_DB failed', 'red'))
