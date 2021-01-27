'''
#Honeypot
  `id` varchar(35) NOT NULL,
  `name` varchar(128) NOT NULL,
  `descr` text DEFAULT NULL,
  `port` int(5) DEFAULT NULL,
  `parser` text NOT NULL,
  `logs` varchar(255) NOT NULL,
  `source` varchar(255) NOT NULL,
  `port_container` char(12) DEFAULT NULL,
  `state` varchar(10) DEFAULT NULL,

# Link
  `id` varchar(35) NOT NULL,
  `nb_hp` int(5) NOT NULL,
  `nb_serv` int(5) NOT NULL,

# Server
  `id` varchar(35) NOT NULL,
  `name` varchar(128) NOT NULL,
  `descr` text DEFAULT NULL,
  `ip` varchar(15) NOT NULL,
  `ssh_port` int(5) NOT NULL DEFAULT 22,
  `state` varchar(10) DEFAULT NULL,

# Tags
  `tag` varchar(22) NOT NULL,
'''
import sys
import re
import configparser
import os


def normalize_id(type, id):
    if not(id[:3] == (type + '-')):
        sys.exit("Error in id header")
    try:
        int(id[3:], 16)
    except:
        sys.exit("Error in id content: not hexadecimal")
    if len(id) != 35:
        sys.exit("Error in id : invalid length")
    return id

def normalize_name(name):
    if len(name) > 128:
        sys.exit("Error in name : too long")
    if not(re.match(r"^[a-zA-Z0-9_\-]*$", name)):
        sys.exit("Error in name : invalid syntax")
    return name
    
def normalize_descr(descr):
    if not(re.match(r"^[a-zA-Z0-9_\-\s]*$", descr)):
        sys.exit("Error in name : invalid syntax")
    return descr

def normalize_port(port):
    try:
        int(port)
    except:
        sys.exit("Error in port : not an interger")
    port = int(port)
    if (port < 0) or (port > 65536):
        sys.exit("Error in port : invalid")
    return port

def normalize_parser(parser):
    return parser

def normalize_logs(logs):
    if len(logs) > 255:
        sys.exit("Error in logs : too long")
    if not(re.match(r"^[a-zA-Z0-9_/:\"\-\s]*$", logs)):
        sys.exit("Error in logs : not a path")
    
def normalize_source(source):
    if len(source) > 255:
        sys.exit("Error in source : too long")
    if not(re.match(r"^[a-zA-Z0-9_/:\"\-\s]*$", source)):
        sys.exit("Error in source : not a path")

def normalize_state(type, state):
    state = state.upper()
    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    available_state_list = config['state'][type+'_state'].split(',')
    if len(state) > 10:
        sys.exit("Error in state : too long")
    if not(re.match(r"^[A-Z]*$", state)):
        sys.exit("Error in state : invalid syntax")
    if not(state in available_state_list):
        sys.exit("Error in state : state not available")
    return state

def normalize_port_container(port_container):
    return normalize_port(port_container)

def normalize_ip(ip):
    if not(re.match(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", ip)):
        sys.exit("Error in ip : invalid syntax")
    return ip

def normalize_ssh_port(ssh_port):
    return normalize_port(ssh_port)

def normalize_ssh_key(ssh_key):
    return ssh_key

def normalize_nb_hp(nb_hp):
    if len(str(nb_hp)) > 5:
        sys.exit("Error in nb_hp : bad length")
    try:
        int(nb_hp)
    except:
        sys.exit("Error in nb_hp : not an integer")
    return int(nb_hp)

def normalize_nb_serv(nb_serv):
    if len(str(nb_serv)) > 5:
        sys.exit("Error in nb_serv : bad length")
    try:
        int(nb_serv)
    except:
        sys.exit("Error in nb_serv : not an integer")
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
        sys.exit("Error in tags : invalid syntax")
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
