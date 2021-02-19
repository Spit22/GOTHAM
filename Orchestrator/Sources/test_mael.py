from Gotham_link_BDD import get_server_infos,get_honeypot_infos,get_tag_infos,get_link_infos
from Gotham_link_BDD import add_server_DB,add_honeypot_DB,add_link_DB,add_lhs_DB
from Gotham_link_BDD import remove_server_DB,remove_honeypot_DB,remove_link_DB

from Gotham_normalize import normalize_honeypot_infos,normalize_server_infos,normalize_link_infos,normalize_display_object_infos
from Gotham_check import check_used_port, check_ssh,check_doublon_server
from Gotham_choose import choose_servers

import mariadb
import datetime
import json
import uuid
import base64
import os
import random
from io import StringIO # a suppr

from termcolor import colored, cprint

import rm_server
import os
import sys
import configparser

##########-SETTINGS-##########
DB_settings = {"username":"gotham", "password":"password", "hostname":"localhost", "port":"3306", "database":"GOTHAM"}

lk_port_infos = {"id":"lk-1BFB3AFE3FEE1FEFB1D25E22FC2CA69F", "nb_hp": 4, "nb_serv": 2, "tags_hp":"OpenSSH,SSH,Elasticsearch", "tags_serv":"Europe ,  suisse,  geneve,TagDeTest42,TagDeTest4254,TagDeTest427","ports":"22, 189  ,  469,6484,88"}
serv_already_exist=[{'serv_id': 'sv-88784AF833CD11EBAEA003EBFB2CA371', 'serv_name': 'vps-8.hebergeur.foo', 'serv_descr': 'Server for test', 'serv_ip': '172.0.0.25', 'serv_ssh_key': 'To_Add', 'serv_ssh_port': 22, 'serv_state': 'To_Add', 'serv_tags': 'Europe||France||Vannes', 'serv_created_at': 'datetime.datetime(2021, 1, 27, 22, 18, 52)', 'serv_updated_at': 'datetime.datetime(2021, 1, 27, 22, 18, 52)', 'link_id': 'lk-4FD58A38340111EBB0E722F1FB2CA371||||||lk-72660A46340111EBBAC118F3FB2CA371', 'link_nb_hp': '3||||||2', 'link_nb_serv': '5||||||5', 'link_ports': '53,5353,1053||||||789,987,879,897', 'link_tags_hp': 'DNS||||||haute-dispo||port_22||SSH', 'link_tags_serv': 'Europe||France||||||Europe', 'link_created_at': '2021-01-27 22:18:52||||||2021-01-27 22:18:52', 'link_updated_at': '2021-01-27 22:18:52||||||2021-01-27 22:18:52', 'lhs_port': '5353||||||879', 'hp_id': 'hp-5DED2C8A33C911EBADD59A1EFC2CA371||||||hp-75034A4E33C911EB9D009933FC2CA371', 'hp_name': 'Honeypot_DNS||||||Honeypot_openssh', 'hp_descr': 'Hp for test||||||Hp for test', 'hp_port': None, 'hp_parser': 'To Add||||||To Add', 'hp_logs': 'To add||||||To add', 'hp_source': 'To add||||||To add', 'hp_state': 'ERROR||||||UNUSED', 'hp_port_container': '443||||||987', 'hp_tags': 'DNS||||||haute-dispo||OpenSSH||port_22||SSH', 'hp_created_at': '2021-01-27 22:18:52||||||2021-01-27 22:18:52', 'hp_updated_at': '2021-01-27 22:18:52||||||2021-01-27 22:18:52'}]

lk_infos = {"id":"lk-1BFB3AFE3FEE1FEFB1D25E22FC2CA777", "nb_hp": 4, "nb_serv": 2, "tags_hp":"SSH", "tags_serv":"France, Europe", 'ports':'22,186,658'}
server_infos = {'id':'sv-62323F6F323F38F42d656DF861566689','name':'serveur-test-6','descr':'blabla','tags':'TestTag697','ip':'42.56.99.99','ssh_key':'non','ssh_port':'22','state':'ERROR'}
honeypot_infos = {"id":"hp-1F5B3AFE32EE71EFB1D25EFFFC2CA666", 'name':'hp-test-6','tags':'TestTag22,TesTag666,TagDeTest42', 'port':22,'parser':'TO_ADD','logs':'TO_ADD','source':"TO_ADD", "port_container":22,'state':'UNUSED'}
##########-SETTINGS-##########
#
#print(colored("########## ########## RM LINK SECTION ########## ##########", 'blue'))
'''
try:
    infos = get_server_infos(DB_settings, id = 'sv-7706DF9633CD11EB82B004DDFB2CA371')
except:
    print('ko')
#print(infos[0])
print(normalize_display_object_infos(infos[0], "serv", next_type=''))
'''

from Gotham_link_BDD import add_server_DB, add_honeypot_DB, add_link_DB
#print(colored("########## ########## EDIT IN IDB SECTION ########## ##########", 'blue'))
#edit_lhs_DB(DB_settings, {'id_serv':server_infos['id']}, {'id_link':'lk-67C82EAC340111EB85FE89F2FB2CA371'})
#edit_lhs_DB(DB_settings, {'id_hp':honeypot_infos['id']}, {'id_link':'lk-4AAB119A340111EB84D6D6F0FB2CA371', 'id_serv':'sv-72D25FB833CD11EBAED4A458FC2CA371'})
#edit_lhs_DB(DB_settings, {'id_link':lk_infos['id']}, {'id_hp':'hp-1B5B3A1E32EE11EBB1F25E22FC2CA372', 'id_serv':'sv-447831E032EE11EBB6D20248FC2CA371'})


#remove_lhs(DB_settings,id_link="lk-67C82EAC340111EB85FE89F2FB2CA371")
import rm_server
#import rm_hp
import rm_link

import add_server
import add_hp
import add_link
import add_hp

server_infos = {'id':'sv-66623F6F323F38F42d656DF861566999','name':'serveur-test-edit-idb','descr':'blabla','tags':'TagTag,France,TagParticulier','ip':'42.42.22.22','ssh_key':'non','ssh_port':'22','state':'UNUSED'}

honeypot_infos = {"id":"hp-666B3AFE32EE71EFB1D25EFFFC2CA999", 'name':'hp-test-6','tags':'TesTag666,Tess', 'port':22,'parser':'TO_ADD','logs':'TO_ADD','source':"TO_ADD", "port_container":22,'state':'UNUSED'}


lk_infos1 = {"id":"lk-111B3AFE3FEE1FEFB1D25E22FC2CA999", "nb_hp": 2, "nb_serv": 1, "tags_hp":"SSH", "tags_serv":"TagParticulier", 'ports':'22,186,658'}
lk_infos2 = {"id":"lk-222B3AFE3FEE1FEFB1D25E22FC2CA999", "nb_hp": 2, "nb_serv": 6, "tags_hp":"Apache", "tags_serv":"France", 'ports':'22,186,658'}
lk_infos3 = {"id":"lk-333B3AFE3FEE1FEFB1D25E22FC2CA999", "nb_hp": 2, "nb_serv": 2, "tags_hp":"DNS", "tags_serv":"TagTag", 'ports':'22,186,658'}


print(colored("########## ########## RM SERVER ########## ##########", 'blue'))
#add_server_DB(DB_settings, server_infos)
#add_link_DB(DB_settings, lk_infos1)
#add_link_DB(DB_settings, lk_infos2)
#add_link_DB(DB_settings, lk_infos3)
#rm_server.main(DB_settings, id='sv-66623F6F323F38F42d656DF861566999')
dc_ip = "192.168.1.22"
dc_ssh_port = "22"
dc_ssh_key="idh"
orch_ip = "192.168.1.23"
orch_rsyslog_port = "1514"
local_rulebase_path = "/rsyslog/rulebase"
remote_rulebase_path = "/rsyslog/rulebase"
id_hp = "hp-7846514"
add_hp.deploy_rsyslog_conf(dc_ip, dc_ssh_port, dc_ssh_key, orch_ip, orch_rsyslog_port, local_rulebase_path, remote_rulebase_path, id_hp)