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
server_infos_4 = {'id':'sv-62323F6F323F38F42d656DF861566692','name':'serveur-test-4','descr':'blabla','tags':'Europe,Allemagne','ip':'42.42.42.45','ssh_key':'non','ssh_port':'22','state':'UNUSED'}
server_infos_5 = {'id':'sv-62323F6F323F38F42d656DF861566693','name':'serveur-test-5','descr':'blabla','tags':'Italie,Europe','ip':'42.42.42.46','ssh_key':'non','ssh_port':'22','state':'UNUSED'}
server_infos_6 = {'id':'sv-62323F6F323F38F42d656DF861566694','name':'serveur-test-6','descr':'blabla','tags':'Asie,Corée','ip':'42.42.42.47','ssh_key':'non','ssh_port':'22','state':'UNUSED'}
server_infos_7 = {'id':'sv-62323F6F323F38F42d656DF861566695','name':'serveur-test-7','descr':'blabla','tags':'Europe,Serbie','ip':'42.42.42.48','ssh_key':'non','ssh_port':'22','state':'UNUSED'}

def test_add_server():
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

def test_server_integrity():
    result = get_server_infos(DB_settings, id=server_infos_1["id"])[0]
    assert result["serv_id"] == server_infos_1["id"]
    assert result["serv_name"] == server_infos_1["name"]
    assert result["serv_descr"] == server_infos_1["descr"]
    assert result["serv_ip"] == server_infos_1["ip"]
    assert result["serv_ssh_key"] == server_infos_1["ssh_key"]
    assert result["serv_ssh_port"] == server_infos_1["ssh_port"]
    assert result["serv_state"] == server_infos_1["state"]
    # Test tag by tag
    tags_in_IDB = result["serv_tags"].split('||')
    for tag_in_IDB in tags_in_IDB:
        assert tag_in_IDB in server_infos_1["tags"]
    ########################################
    result = get_server_infos(DB_settings, id=server_infos_2["id"])[0]
    assert result["serv_id"] == server_infos_2["id"]
    assert result["serv_name"] == server_infos_2["name"]
    assert result["serv_descr"] == server_infos_2["descr"]
    assert result["serv_ip"] == server_infos_2["ip"]
    assert result["serv_ssh_key"] == server_infos_2["ssh_key"]
    assert result["serv_ssh_port"] == server_infos_2["ssh_port"]
    assert result["serv_state"] == server_infos_2["state"]
    # Test tag by tag
    tags_in_IDB = result["serv_tags"].split('||')
    for tag_in_IDB in tags_in_IDB:
        assert tag_in_IDB in server_infos_2["tags"]
    ########################################
    result = get_server_infos(DB_settings, id=server_infos_3["id"])[0]
    assert result["serv_id"] == server_infos_3["id"]
    assert result["serv_name"] == server_infos_3["name"]
    assert result["serv_descr"] == server_infos_3["descr"]
    assert result["serv_ip"] == server_infos_3["ip"]
    assert result["serv_ssh_key"] == server_infos_3["ssh_key"]
    assert result["serv_ssh_port"] == server_infos_3["ssh_port"]
    assert result["serv_state"] == server_infos_3["state"]
    # Test tag by tag
    tags_in_IDB = result["serv_tags"].split('||')
    for tag_in_IDB in tags_in_IDB:
        assert tag_in_IDB in server_infos_3["tags"]

def test_remove_server():
    try:
        remove_server_DB(DB_settings, server_infos_1["id"])
    except Exception as e:
        raise pytest.fail(e)
    try:
        remove_server_DB(DB_settings, server_infos_2["id"])
    except Exception as e:
        raise pytest.fail(e)
    try:
        remove_server_DB(DB_settings, server_infos_3["id"])
    except Exception as e:
        raise pytest.fail(e)