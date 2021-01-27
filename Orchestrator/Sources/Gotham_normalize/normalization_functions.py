import sys
import re
import configparser
import os

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


def normalize_id(type, id):
    if not(id[:3] == (type + '-')):
        logging.warning(f"id type doesn't match: {id}")
    try:
        int(id[3:], 16)
    except:
        logging.warning(f"id has a invalid type : {id} : id must be an interger !")
    if len(id) != 35:
        logging.warning(f"id has a invalid length : {id} : the length of the id must be 35 !")
    return id

def normalize_name(name):
    if len(name) > 128:
        logging.warning(f"name has a invalid length : {name} : name length must be under 128 !")
    if not(re.match(r"^[a-zA-Z0-9_\-]*$", name)):
        logging.warning(f"name has a invalid syntax : {name}")
    return name
    
def normalize_descr(descr):
    if not(re.match(r"^[a-zA-Z0-9_\-\s]*$", descr)):
        logging.warning(f"descr has a invalid syntax : {descr}")
    return descr

def normalize_port(port):
    try:
        int(port)
    except:
        logging.warning(f"port has a invalid type : {port} : port must be an interger !")
    port = int(port)
    if (port < 0) or (port > 65536):
        logging.warning(f"id has a invalid value : {id} : port must be between 0 and 65536 !")
    return port

def normalize_parser(parser):
    return parser

def normalize_logs(logs):
    if len(logs) > 255:
        logging.warning(f"log path has a invalid length : {logs} : log path length must be under 255 !")
    if not(re.match(r"^[a-zA-Z0-9_/:\"\-\s]*$", logs)):
        logging.warning(f"log path has a invalid syntax : {logs}")
    
def normalize_source(source):
    if len(source) > 255:
        logging.warning(f"source path has a invalid length : {source} : source length must be under 255 !")
    if not(re.match(r"^[a-zA-Z0-9_/:\"\-\s]*$", source)):
        logging.warning(f"source has a invalid syntax : {source}")

def normalize_state(type, state):
    state = state.upper()
    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    available_state_list = config['state'][type+'_state'].split(',')
    if len(state) > 10:
        logging.warning(f"state has a invalid length : {state} : state length must be under 10 !")
    if not(re.match(r"^[A-Z]*$", state)):
        logging.warning(f"state has a invalid syntax : {state}")
    if not(state in available_state_list):
        logging.warning(f"state is not available : {state} : check the configuration")
    return state

def normalize_port_container(port_container):
    return normalize_port(port_container)

def normalize_ip(ip):
    if not(re.match(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", ip)):
        logging.warning(f"ip has a invalid syntax : {ip}")
    return ip

def normalize_ssh_port(ssh_port):
    return normalize_port(ssh_port)

def normalize_ssh_key(ssh_key):
    return ssh_key

def normalize_nb_hp(nb_hp):
    if len(str(nb_hp)) > 5:
        logging.warning(f"Number of honeypots (nb_hp) has a invalid length : {nb_hp} : nb_hp length must be under 5 !")
    try:
        int(nb_hp)
    except:
        logging.warning(f"Number of honeypots (nb_hp) has a invalid type : {nb_hp} : nb_hp must be an interger !")
    return int(nb_hp)

def normalize_nb_serv(nb_serv):
    if len(str(nb_serv)) > 5:
        logging.warning(f"Number of servers (nb_serv) has a invalid length : {nb_serv} : nb_hp length must be under 5 !")
    try:
        int(nb_serv)
    except:
        logging.warning(f"Number of servers (nb_serv) has a invalid type : {nb_serv} : nb_serv must be an interger !")
    return int(nb_serv)

def normalize_tags(tags):
    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    separator = config['tag']['separator']
    tags_list = tags.split(separator)
    res = ''
    for a_tag in tags_list:
        a_tag=normalize_tag(a_tag)
        if res == '':
            res = res + a_tag
        else:
            res = res + separator + a_tag
    return res

def normalize_ports(ports):
    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    separator = config['tag']['separator']
    ports_list = ports.split(separator)
    res = ''
    for a_port in ports_list:
        a_port=normalize_port(a_port.strip())
        a_port=str(a_port)
        if res == '':
            res = res + a_port
        else:
            res = res + separator + a_port
    return res

def normalize_tag(tag):
    tag = tag.strip()
    tag = tag[0].upper() + tag[1:]
    if not(re.match(r"^[a-zA-Z0-9_\-]*$", tag)):
        logging.warning(f"tag has a invalid syntax : {tag}")
    return tag


# lk_infos={"id":"lk-1BFB3AFE3FEE1FEFB1D25E22FC2CA69F", "nb_hp": 4, "nb_serv": 2, "tags_hp":"OpenSSH,SSH,Elasticsearch", "tags_serv":"Europe ,  suisse,  geneve,TagDeTest42,TagDeTest4254,TagDeTest427","ports":"22, 189  ,  469,6484,88"}

# for key, value in lk_infos.items():
#   if (key=="id" or key=="state"):
#     lk_infos[key]=globals()['normalize_' + key]("lk",value)
#   elif (key=="tags_hp" or key=="tags_serv"):
#     lk_infos[key]=globals()['normalize_tags'](value)
#   else:
#     lk_infos[key]=globals()['normalize_' + key](value)
# print(lk_infos)
