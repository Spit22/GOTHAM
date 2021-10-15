import sys
import os
import pytest

GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
sys.path.insert(1, GOTHAM_HOME + 'Orchestrator/Sources')
print(sys.path)

from Gotham_link_BDD import add_server_DB
from Gotham_link_BDD import remove_server_DB
from Gotham_link_BDD import get_server_infos

DB_settings = {"username":"gotham", "password":"password", "hostname":"172.17.0.2", "port":"3306", "database":"GOTHAM"}

server_infos_1 = {'id':'sv-62323F6F323F38F42d656DF861566689','name':'serveur-test-1','descr':'blabla','tags':'Europe,France,OVH','ip':'42.42.42.42','ssh_key':'non','ssh_port':'22','state':'UNUSED'}
server_infos_2 = {'id':'sv-62323F6F323F38F42d656DF861566690','name':'serveur-test-2','descr':'blabla','tags':'Asie,Japon','ip':'42.42.42.43','ssh_key':'non','ssh_port':'22','state':'UNUSED'}
server_infos_3 = {'id':'sv-62323F6F323F38F42d656DF861566691','name':'serveur-test-3','descr':'blabla','tags':'USA','ip':'42.42.42.44','ssh_key':'non','ssh_port':'22','state':'UNUSED'}

honeypot_infos_1 = {"id":"hp-1F5B3AFE32EE71EFB1D25EFFFC2CA000", 'name':'hp-test-1','tags':'SSH,OpenSSH,Port22', 'port':'22','parser':'my%parsing%list','logs':'TO_ADD','source':"TO_ADD", "port_container":22,'state':'UNUSED'}
honeypot_infos_2 = {"id":"hp-1F5B3AFE32EE71EFB1D25EFFFC2CA001", 'name':'hp-test-2','tags':'DNS,OpenDNS', 'port':'53','parser':'my%parsing%list','logs':'TO_ADD','source':"TO_ADD", "port_container":53,'state':'UNUSED'}
honeypot_infos_3 = {"id":"hp-1F5B3AFE32EE71EFB1D25EFFFC2CA002", 'name':'hp-test-3','tags':'DNS,OpenDNS', 'port':'5353','parser':'my%parsing%list','logs':'TO_ADD','source':"TO_ADD", "port_container":53,'state':'UNUSED'}



