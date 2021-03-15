import json
import sys
import os
import pytest

GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
sys.path.insert(1, GOTHAM_HOME + 'Orchestrator/Sources')
print(sys.path)

from Gotham_link_BDD import add_server_DB, add_honeypot_DB, add_link_DB
from Gotham_link_BDD import remove_server_DB, remove_honeypot_DB, remove_link_DB



DB_settings = {"username":"gotham", "password":"password", "hostname":"localhost", "port":"3306", "database":"GOTHAM"}

nb_server = 7
nb_honeypot = 7

server_infos_1 = {'id':'sv-62323F6F323F38F42d656DF861566689','name':'serveur-test-1','descr':'blabla','tags':'Europe,France,OVH','ip':'42.42.42.42','ssh_key':'non','ssh_port':'22','state':'UNUSED'}
server_infos_2 = {'id':'sv-62323F6F323F38F42d656DF861566690','name':'serveur-test-2','descr':'blabla','tags':'Asie,Japon','ip':'42.42.42.43','ssh_key':'non','ssh_port':'22','state':'UNUSED'}
server_infos_3 = {'id':'sv-62323F6F323F38F42d656DF861566691','name':'serveur-test-3','descr':'blabla','tags':'USA','ip':'42.42.42.44','ssh_key':'non','ssh_port':'22','state':'UNUSED'}
server_infos_4 = {'id':'sv-62323F6F323F38F42d656DF861566692','name':'serveur-test-4','descr':'blabla','tags':'Europe,Allemagne','ip':'42.42.42.45','ssh_key':'non','ssh_port':'22','state':'UNUSED'}
server_infos_5 = {'id':'sv-62323F6F323F38F42d656DF861566693','name':'serveur-test-5','descr':'blabla','tags':'Italie,Europe','ip':'42.42.42.46','ssh_key':'non','ssh_port':'22','state':'UNUSED'}
server_infos_6 = {'id':'sv-62323F6F323F38F42d656DF861566694','name':'serveur-test-6','descr':'blabla','tags':'Asie,Corée','ip':'42.42.42.47','ssh_key':'non','ssh_port':'22','state':'UNUSED'}
server_infos_7 = {'id':'sv-62323F6F323F38F42d656DF861566695','name':'serveur-test-7','descr':'blabla','tags':'Europe,Serbie','ip':'42.42.42.48','ssh_key':'non','ssh_port':'22','state':'UNUSED'}

honeypot_infos_1 = {"id":"hp-1F5B3AFE32EE71EFB1D25EFFFC2CA000", 'name':'hp-test-1','tags':'SSH,OpenSSH,Port22', 'port':22,'parser':'my%parsing%list','logs':'TO_ADD','source':"TO_ADD", "port_container":22,'state':'UNUSED'}
honeypot_infos_2 = {"id":"hp-1F5B3AFE32EE71EFB1D25EFFFC2CA001", 'name':'hp-test-2','tags':'DNS,OpenDNS', 'port':53,'parser':'my%parsing%list','logs':'TO_ADD','source':"TO_ADD", "port_container":53,'state':'UNUSED'}
honeypot_infos_3 = {"id":"hp-1F5B3AFE32EE71EFB1D25EFFFC2CA002", 'name':'hp-test-3','tags':'DNS,OpenDNS', 'port':53,'parser':'my%parsing%list','logs':'TO_ADD','source':"TO_ADD", "port_container":53,'state':'UNUSED'}
honeypot_infos_3 = {"id":"hp-1F5B3AFE32EE71EFB1D25EFFFC2CA003", 'name':'hp-test-4','tags':'Elasticsearch', 'port':3003,'parser':'my%parsing%list','logs':'TO_ADD','source':"TO_ADD", "port_container":3003,'state':'UNUSED'}
honeypot_infos_4 = {"id":"hp-1F5B3AFE32EE71EFB1D25EFFFC2CA004", 'name':'hp-test-5','tags':'SSH,OpenSSH,Port22', 'port':22,'parser':'my%parsing%list','logs':'TO_ADD','source':"TO_ADD", "port_container":22,'state':'UNUSED'}
honeypot_infos_5 = {"id":"hp-1F5B3AFE32EE71EFB1D25EFFFC2CA005", 'name':'hp-test-6','tags':'DNS,OpenDNS', 'port':53,'parser':'my%parsing%list','logs':'TO_ADD','source':"TO_ADD", "port_container":53,'state':'UNUSED'}
honeypot_infos_6 = {"id":"hp-1F5B3AFE32EE71EFB1D25EFFFC2CA006", 'name':'hp-test-7','tags':'LDAP', 'port':389,'parser':'my%parsing%list','logs':'TO_ADD','source':"TO_ADD", "port_container":389,'state':'UNUSED'}
honeypot_infos_7 = {"id":"hp-1F5B3AFE32EE71EFB1D25EFFFC2CA007", 'name':'hp-test-8','tags':'Elasticsearch', 'port':3003,'parser':'my%parsing%list','logs':'TO_ADD','source':"TO_ADD", "port_container":3003,'state':'UNUSED'}

lk_infos_1 = {"id": "lk-1BFB3AFE3FEE1FEFB1D25E22FC2CA000", "nb_hp": 4, "nb_serv": 2, "tags_hp": "SSH", "tags_serv": "France, Europe", 'ports': '22,186,658'}




def test_add_server(app, client):
    try:
        add_server_DB(DB_settings, server_infos_1)
    except Exception as e:
        raise pytest.fail(e)
    try:
        add_server_DB(DB_settings, server_infos_2)
    except Exception as e:
        raise pytest.fail(e)
    try:
        add_server_DB(DB_settings, server_infos_3)
    except Exception as e:
        raise pytest.fail(e)

def test_add_honeypot(app, client):
    try:
        add_honeypot_DB(DB_settings, honeypot_infos_1)
    except Exception as e:
        raise pytest.fail(e)
    try:
        add_honeypot_DB(DB_settings, honeypot_infos_2)
    except Exception as e:
        raise pytest.fail(e)
    try:
        add_honeypot_DB(DB_settings, honeypot_infos_3)
    except Exception as e:
        raise pytest.fail(e)

def test_rm_server(app, client):
    try:
        remove_server_DB(DB_settings, server_infos_1)
    except Exception as e:
        raise pytest.fail(e)
    try:
        remove_server_DB(DB_settings, server_infos_2)
    except Exception as e:
        raise pytest.fail(e)
    try:
        remove_server_DB(DB_settings, server_infos_3)
    except Exception as e:
        raise pytest.fail(e)

def test_rm_honeypot(app, client):
    try:
        remove_honeypot_DB(DB_settings, honeypot_infos_1)
    except Exception as e:
        raise pytest.fail(e)
    try:
        remove_honeypot_DB(DB_settings, honeypot_infos_2)
    except Exception as e:
        raise pytest.fail(e)
    try:
        remove_honeypot_DB(DB_settings, honeypot_infos_3)
    except Exception as e:
        raise pytest.fail(e)
