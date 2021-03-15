from Gotham_link_BDD import get_server_infos, get_honeypot_infos, get_tag_infos, get_link_infos
from Gotham_link_BDD import add_server_DB, add_honeypot_DB, add_link_DB, add_lhs_DB
from Gotham_link_BDD import remove_server_DB, remove_honeypot_DB, remove_link_DB

from Gotham_normalize import normalize_honeypot_infos, normalize_server_infos, normalize_link_infos
from Gotham_check import check_used_port, check_ssh, check_doublon_server
from Gotham_choose import choose_servers

import mariadb
import datetime
import json
import uuid
import base64
import os
import random
from io import StringIO  # a suppr

from termcolor import colored, cprint

import rm_server
import os
import sys
import configparser

##########-SETTINGS-##########
DB_settings = {"username": "gotham", "password": "password",
               "hostname": "localhost", "port": "3306", "database": "gotham"}

lk_port_infos = {"id": "lk-1BFB3AFE3FEE1FEFB1D25E22FC2CA69F", "nb_hp": 4, "nb_serv": 2, "tags_hp": "OpenSSH,SSH,Elasticsearch",
                 "tags_serv": "Europe ,  suisse,  geneve,TagDeTest42,TagDeTest4254,TagDeTest427", "ports": "22, 189  ,  469,6484,88"}
serv_already_exist = [{'serv_id': 'sv-88784AF833CD11EBAEA003EBFB2CA371', 'serv_name': 'vps-8.hebergeur.foo', 'serv_descr': 'Server for test', 'serv_ip': '172.0.0.25', 'serv_ssh_key': 'To_Add', 'serv_ssh_port': 22, 'serv_state': 'To_Add', 'serv_tags': 'Europe||France||Vannes', 'serv_created_at': 'datetime.datetime(2021, 1, 27, 22, 18, 52)', 'serv_updated_at': 'datetime.datetime(2021, 1, 27, 22, 18, 52)', 'link_id': 'lk-4FD58A38340111EBB0E722F1FB2CA371||||||lk-72660A46340111EBBAC118F3FB2CA371', 'link_nb_hp': '3||||||2', 'link_nb_serv': '5||||||5', 'link_ports': '53,5353,1053||||||789,987,879,897', 'link_tags_hp': 'DNS||||||haute-dispo||port_22||SSH', 'link_tags_serv': 'Europe||France||||||Europe',
                       'link_created_at': '2021-01-27 22:18:52||||||2021-01-27 22:18:52', 'link_updated_at': '2021-01-27 22:18:52||||||2021-01-27 22:18:52', 'lhs_port': '5353||||||879', 'hp_id': 'hp-5DED2C8A33C911EBADD59A1EFC2CA371||||||hp-75034A4E33C911EB9D009933FC2CA371', 'hp_name': 'Honeypot_DNS||||||Honeypot_openssh', 'hp_descr': 'Hp for test||||||Hp for test', 'hp_port': None, 'hp_parser': 'To Add||||||To Add', 'hp_logs': 'To add||||||To add', 'hp_source': 'To add||||||To add', 'hp_state': 'ERROR||||||UNUSED', 'hp_port_container': '443||||||987', 'hp_tags': 'DNS||||||haute-dispo||OpenSSH||port_22||SSH', 'hp_created_at': '2021-01-27 22:18:52||||||2021-01-27 22:18:52', 'hp_updated_at': '2021-01-27 22:18:52||||||2021-01-27 22:18:52'}]

lk_infos = {"id": "lk-1BFB3AFE3FEE1FEFB1D25E22FC2CA777", "nb_hp": 4, "nb_serv": 2,
            "tags_hp": "SSH", "tags_serv": "France, Europe", 'ports': '22,186,658'}
server_infos = {'id': 'sv-62323F6F323F38F42d656DF861566689', 'name': 'serveur-test-6', 'descr': 'blabla',
                'tags': 'TestTag697', 'ip': '42.56.99.99', 'ssh_key': 'non', 'ssh_port': '22', 'state': 'ERROR'}
honeypot_infos = {"id": "hp-1F5B3AFE32EE71EFB1D25EFFFC2CA666", 'name': 'hp-test-6', 'tags': 'TestTag22,TesTag666,TagDeTest42',
                  'port': 22, 'parser': 'TO_ADD', 'logs': 'TO_ADD', 'source': "TO_ADD", "port_container": 22, 'state': 'UNUSED'}
##########-SETTINGS-##########


print(colored("########## ########## ADD SECTION ########## ##########", 'blue'))
try:
    print(colored("########## Add Server ##########", 'yellow'))
    print(add_server_DB(DB_settings, server_infos))
except:
    print(colored('[X] add_server_DB failed', 'red'))

try:
    print(colored("########## Add Honeypot ##########", 'yellow'))
    print(add_honeypot_DB(DB_settings, honeypot_infos))
except:
    print(colored('[X] add_honeypot_DB failed', 'red'))

try:
    print(colored("########## Add Link ##########", 'yellow'))
    #print(add_link_DB(DB_settings, lk_infos))
except:
    print(colored('[X] add_link_DB failed', 'red'))

print(colored("########## ########## GET INFOS SECTION ########## ##########", 'blue'))

try:
    print(colored("########## Get Server Infos with tag (false mode) ##########", 'yellow'))
    print(get_server_infos(DB_settings, mode=False, tags=server_infos["tags"]))
except:
    print(colored('[X] get_server_infos failed', 'red'))

try:
    print(colored("########## Get Server Infos with tag (true mode) ##########", 'yellow'))
    print(get_server_infos(DB_settings, mode=True, tags=server_infos["tags"]))
except:
    print(colored('[X] get_server_infos failed', 'red'))

try:
    print(colored("########## Get Server Infos with ip (true mode) ##########", 'yellow'))
    print(get_server_infos(DB_settings, mode=True, ip=server_infos["ip"]))
except:
    print(colored('[X] get_server_infos failed', 'red'))


try:
    print(colored("########## Get Tag Infos with id ##########", 'yellow'))
    print(get_tag_infos(DB_settings, id="1"))
except:
    print(colored('[X] get_tag_infos failed', 'red'))

try:
    print(colored("########## Get Honeypot Infos with tag ##########", 'yellow'))
    print(get_honeypot_infos(DB_settings, tags=honeypot_infos["tags"]))
except:
    print(colored('[X] get_honeypot_infos failed', 'red'))

try:
    print(colored("########## Get Honeypot Infos with port ##########", 'yellow'))
    print(get_honeypot_infos(DB_settings,
                             mode=True, port=honeypot_infos["port"]))
except:
    print(colored('[X] get_honeypot_infos failed', 'red'))

try:
    print(colored("########## Get Link Infos with tag ##########", 'yellow'))
    print(get_link_infos(DB_settings, tags_hp=lk_infos["tags_hp"]))
except:
    print(colored('[X] get_link_infos failed', 'red'))

try:
    print(colored("########## Get Link Infos with id ##########", 'yellow'))
    #print(get_link_infos(DB_settings, id=lk_infos["id"])[0])
    print(get_link_infos(DB_settings,
                         id="lk-67C82EAC340111EB85FE89F2FB2CA371")[0])

except:
    print(colored('[X] get_link_infos failed', 'red'))

print(colored("########## ########## NORMALIZE SECTION ########## ##########", 'blue'))
try:
    print(colored("########## Normalize Honeypot Infos ##########", 'yellow'))
    print(normalize_honeypot_infos(honeypot_infos))
except:
    print(colored('[X] normalize_honeypot_infos failed', 'red'))

try:
    print(colored("########## Normalize Server Infos ##########", 'yellow'))
    print(normalize_server_infos(server_infos))
except:
    print(colored('[X] normalize_server_infos failed', 'red'))

try:
    print(colored("########## Normalize Link Infos ##########", 'yellow'))
    print(normalize_link_infos(lk_infos))
except:
    print(colored('[X] normalize_link_infos failed', 'red'))


print(colored("########## ########## REMOVE SECTION ########## ##########", 'blue'))
try:
    print(colored("########## Remove Server (with id) ##########", 'yellow'))
    print(remove_server_DB(DB_settings, server_infos['id']))
except:
    print(colored('[X] remove_server_DB failed', 'red'))

try:
    print(colored("########## Remove Honeypot (with id) ##########", 'yellow'))
    print(remove_honeypot_DB(DB_settings, honeypot_infos['id']))
except:
    print(colored('[X] remove_honeypot_DB failed', 'red'))

try:
    print(colored("########## Remove Link (with id) ##########", 'yellow'))
    #print(remove_link_DB(DB_settings, lk_infos['id']))
except:
    print(colored('[X] remove_link_DB failed', 'red'))

print(colored("########## Test weight serv ##########", 'yellow'))
# servs_infos = [{'serv_id': 'sv-62323F6F323F38F42d656DF861566696', 'serv_name': 'serveur-test-6', 'serv_descr': 'blabla', 'serv_ip': '42.254.99.99', 'serv_ssh_key': 'non', 'serv_ssh_port': 22, 'serv_state': 'HEALTHY', 'serv_tags': 'Europe||France||SSH||TagDeTest4TesTag666||TestTag', 'serv_created_at': datetime.datetime(2021, 11, 8, 8, 1, 53), 'serv_updated_at': datetime.datetime(2021, 1, 11, 22, 51, 2), 'link_id': 'lk-4FD58A38340111EBB0E722F1FB2CA371||||||lk-67C82EAC340111EB85FE89F2FB2CA371||||||lk-72660A46340111EBBAC118F3FB2CA371', 'link_nb_hp': '', 'link_nb_serv': '', 'link_ports': '', 'link_tags_hp': '', 'link_tags_serv': '', 'link_created_at': '', 'link_updated_at': '', 'lhs_port': '', 'hp_id': '', 'hp_name': '', 'hp_descr': '', 'hp_port': '', 'hp_parser': '', 'hp_logs': '', 'hp_source': '', 'hp_state': '', 'hp_port_container': '', 'hp_tags': '', 'hp_created_at': '', 'hp_updated_at': ''},{'serv_id': 'sv-62323F6F323F38F42d656DF861566696', 'serv_name': 'serveur-test-6', 'serv_descr': 'blabla', 'serv_ip': '42.254.99.99', 'serv_ssh_key': 'non', 'serv_ssh_port': 22, 'serv_state': 'ERROR', 'serv_tags': 'Europe||France||SSH||TagDeTest4TesTag666||TestTag||Truc', 'serv_created_at': datetime.datetime(2021, 1, 11, 22, 51, 2), 'serv_updated_at': datetime.datetime(2021, 2, 6, 17, 2, 53), 'link_id': 'lk-4FD58A38340111EBB0E722F1FB2CA371||||||lk-72660A46340111EBBAC118F3FB2CA371', 'link_nb_hp': '', 'link_nb_serv': '', 'link_ports': '', 'link_tags_hp': '', 'link_tags_serv': '', 'link_created_at': '', 'link_updated_at': '', 'lhs_port': '53||||||42||||4242||||||789', 'hp_id': '', 'hp_name': '', 'hp_descr': '', 'hp_port': '', 'hp_parser': '', 'hp_logs': '', 'hp_source': '', 'hp_state': '', 'hp_port_container': '', 'hp_tags': '', 'hp_created_at': '', 'hp_updated_at': ''},{'serv_id': 'sv-62323F6F323F38F42d656DF861566696', 'serv_name': 'serveur-test-6', 'serv_descr': 'blabla', 'serv_ip': '42.254.99.99', 'serv_ssh_key': 'non', 'serv_ssh_port': 22, 'serv_state': 'UNUSED', 'serv_tags': 'Europe||France||SSH||TagDeTest4TesTag666||TestTag||Truc||Hachis||Parmentier', 'serv_created_at': datetime.datetime(2021, 2, 6, 17, 2, 53), 'serv_updated_at': '', 'link_id': '', 'link_nb_hp': '', 'link_nb_serv': '', 'link_ports': '', 'link_tags_hp': '', 'link_tags_serv': '', 'link_created_at': '', 'link_updated_at': '', 'lhs_port': '1053', 'hp_id': '', 'hp_name': '', 'hp_descr': '', 'hp_port': '', 'hp_parser': '', 'hp_logs': '', 'hp_source': '', 'hp_state': '', 'hp_port_container': '', 'hp_tags': '', 'hp_created_at': '', 'hp_updated_at': ''}]
# tags="Europe,France,SSH,TagDeTest4TesTag666,TestTag"
# print(choose_servers(servs_infos, 3, tags))


GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
# Retrieve settings from config file
config = configparser.ConfigParser()
config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
ports_separator = config['port']['separator']

tags_serv = ""
tags_hp = ""
nb_srv = "1"
nb_hp = "2"
exposed_ports = "8080,8081"

lk_infos_received = {"nb_hp": nb_hp, "nb_serv": nb_srv,
                     "tags_hp": tags_hp, "tags_serv": tags_serv, "ports": exposed_ports}
lk_infos_received = normalize_link_infos(lk_infos_received)
# Get all function's parameters
tags_serv = lk_infos_received["tags_serv"]
tags_hp = lk_infos_received["tags_hp"]
nb_srv = lk_infos_received["nb_serv"]
nb_hp = lk_infos_received["nb_hp"]
exposed_ports = lk_infos_received["ports"]
exposed_ports_list = exposed_ports.split(ports_separator)

print("lk_infos_received :")
print(lk_infos_received)
print("tags_serv :")
print(tags_serv)
print("tags_hp :")
print(tags_hp)
print("nb_srv :")
print(nb_srv)
print("nb_hp :")
print(nb_hp)
print("exposed_ports :")
print(exposed_ports)
print("exposed_ports_list :")
print(exposed_ports_list)


print(colored("########## Test add server ##########", 'yellow'))

data = {"ip": "172.16.2.202", "name": "bastien-secher.fr", "descr": "first test with api",
        "tags": "france,paris", "ssh_key": "[key...]", "ssh_port": "22"}
# Normalize infos
serv_infos_received = {"name": data["name"], "descr": data["descr"],
                       "tags": data["tags"], "ip": data["ip"], "ssh_port": data["ssh_port"]}
serv_infos_received = normalize_server_infos(serv_infos_received)
# Get all function's parameters
name = serv_infos_received["name"]
descr = serv_infos_received["descr"]
tags = serv_infos_received["tags"]
ip = serv_infos_received["ip"]
encoded_ssh_key = data["ssh_key"]
# Decode and format the ssh key
ssh_key = encoded_ssh_key  # ssh_key is byte
ssh_port = serv_infos_received["ssh_port"]

# First check the ip not already exists in database
exists = check_doublon_server(DB_settings, ip)
if exists:
    print("Provided ip already exists in database")
# If all checks are ok, we can generate an id for the new server
id = 'sv-'+str(uuid.uuid4().hex)
# Create serv_infos
serv_infos = {'id': str(id), 'name': str(name), 'descr': str(descr), 'tags': str(
    tags), 'ip': str(ip), 'ssh_key': str(ssh_key), 'ssh_port': ssh_port, 'state': 'UNUSED'}
# Normalize infos
serv_infos = normalize_server_infos(serv_infos)
print(serv_infos)
# Store new server and tags in the internal database
print(add_server_DB(DB_settings, serv_infos))
