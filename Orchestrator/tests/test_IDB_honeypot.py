import sys
import os
import pytest

GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
sys.path.insert(1, GOTHAM_HOME + 'Orchestrator/Sources')
print(sys.path)

from Gotham_link_BDD import add_honeypot_DB
from Gotham_link_BDD import remove_honeypot_DB
from Gotham_link_BDD import get_honeypot_infos

DB_settings = {"username":"gotham", "password":"password", "hostname":"localhost", "port":"3306", "database":"GOTHAM"}

honeypot_infos_1 = {"id":"hp-1F5B3AFE32EE71EFB1D25EFFFC2CA000", 'name':'hp-test-1','tags':'SSH,OpenSSH,Port22', 'port':'22','parser':'my%parsing%list','logs':'TO_ADD','source':"TO_ADD", "port_container":22,'state':'UNUSED'}
honeypot_infos_2 = {"id":"hp-1F5B3AFE32EE71EFB1D25EFFFC2CA001", 'name':'hp-test-2','tags':'DNS,OpenDNS', 'port':'53','parser':'my%parsing%list','logs':'TO_ADD','source':"TO_ADD", "port_container":53,'state':'UNUSED'}
honeypot_infos_3 = {"id":"hp-1F5B3AFE32EE71EFB1D25EFFFC2CA002", 'name':'hp-test-3','tags':'DNS,OpenDNS', 'port':'5353','parser':'my%parsing%list','logs':'TO_ADD','source':"TO_ADD", "port_container":53,'state':'UNUSED'}
honeypot_infos_4 = {"id":"hp-1F5B3AFE32EE71EFB1D25EFFFC2CA004", 'name':'hp-test-5','tags':'SSH,OpenSSH,Port22', 'port':'22','parser':'my%parsing%list','logs':'TO_ADD','source':"TO_ADD", "port_container":22,'state':'UNUSED'}
honeypot_infos_5 = {"id":"hp-1F5B3AFE32EE71EFB1D25EFFFC2CA005", 'name':'hp-test-6','tags':'DNS,OpenDNS', 'port':'53','parser':'my%parsing%list','logs':'TO_ADD','source':"TO_ADD", "port_container":53,'state':'UNUSED'}
honeypot_infos_6 = {"id":"hp-1F5B3AFE32EE71EFB1D25EFFFC2CA006", 'name':'hp-test-7','tags':'LDAP', 'port':'389','parser':'my%parsing%list','logs':'TO_ADD','source':"TO_ADD", "port_container":389,'state':'UNUSED'}
honeypot_infos_7 = {"id":"hp-1F5B3AFE32EE71EFB1D25EFFFC2CA007", 'name':'hp-test-8','tags':'Elasticsearch', 'port':'3003','parser':'my%parsing%list','logs':'TO_ADD','source':"TO_ADD", "port_container":3003,'state':'UNUSED'}

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

def test_honeypot_integrity(app, client):
    result = get_honeypot_infos(DB_settings, id=honeypot_infos_1["id"])[0]
    assert result["hp_id"] == honeypot_infos_1["id"]
    assert result["hp_name"] == honeypot_infos_1["name"]
    assert result["hp_descr"] == honeypot_infos_1["descr"]
    assert result["hp_port"] == honeypot_infos_1["port"]
    assert result["hp_parser"] == honeypot_infos_1["parser"]
    assert result["hp_logs"] == honeypot_infos_1["logs"]
    assert result["hp_source"] == honeypot_infos_1["source"]
    assert result["hp_state"] == honeypot_infos_1["state"]
    assert result["hp_port_container"] == honeypot_infos_1["port_container"]
    # Test tag by tag
    tags_in_IDB = result["hp_tags"].split('||')
    for tag_in_IDB in tags_in_IDB:
        assert tag_in_IDB in honeypot_infos_1["tags"]
    ########################################
    result = get_honeypot_infos(DB_settings, id=honeypot_infos_2["id"])[0]
    assert result["hp_id"] == honeypot_infos_2["id"]
    assert result["hp_name"] == honeypot_infos_2["name"]
    assert result["hp_descr"] == honeypot_infos_2["descr"]
    assert result["hp_port"] == honeypot_infos_2["port"]
    assert result["hp_parser"] == honeypot_infos_2["parser"]
    assert result["hp_logs"] == honeypot_infos_2["logs"]
    assert result["hp_source"] == honeypot_infos_2["source"]
    assert result["hp_state"] == honeypot_infos_2["state"]
    assert result["hp_port_container"] == honeypot_infos_2["port_container"]
    # Test tag by tag
    tags_in_IDB = result["hp_tags"].split('||')
    for tag_in_IDB in tags_in_IDB:
        assert tag_in_IDB in honeypot_infos_2["tags"]
    ########################################
    result = get_honeypot_infos(DB_settings, id=honeypot_infos_3["id"])[0]
    assert result["hp_id"] == honeypot_infos_3["id"]
    assert result["hp_name"] == honeypot_infos_3["name"]
    assert result["hp_descr"] == honeypot_infos_3["descr"]
    assert result["hp_port"] == honeypot_infos_3["port"]
    assert result["hp_parser"] == honeypot_infos_3["parser"]
    assert result["hp_logs"] == honeypot_infos_3["logs"]
    assert result["hp_source"] == honeypot_infos_3["source"]
    assert result["hp_state"] == honeypot_infos_3["state"]
    assert result["hp_port_container"] == honeypot_infos_3["port_container"]
    # Test tag by tag
    tags_in_IDB = result["hp_tags"].split('||')
    for tag_in_IDB in tags_in_IDB:
        assert tag_in_IDB in honeypot_infos_3["tags"]

def test_remove_honeypot(app, client):
    try:
        remove_honeypot_DB(DB_settings, honeypot_infos_1["id"])
    except Exception as e:
        raise pytest.fail(e)
    try:
        remove_honeypot_DB(DB_settings, honeypot_infos_2["id"])
    except Exception as e:
        raise pytest.fail(e)
    try:
        remove_honeypot_DB(DB_settings, honeypot_infos_3["id"])
    except Exception as e:
        raise pytest.fail(e)