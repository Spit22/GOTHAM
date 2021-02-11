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
    if (id == '' or id == None):
        logging.warning(f"id is undefined or empty")
        sys.exit(1)
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
    if (port == '' or port == None or port==0):
        logging.warning(f"port is undefined or empty")
        sys.exit(1)
    try:
        int(port)
    except:
        logging.warning(f"port has a invalid type : {port} : port must be an interger !")
    port = int(port)
    if (port < 1) or (port > 65536):
        logging.warning(f"port has a invalid value : {port} : port must be between 1 and 65536 !")
    return port

def normalize_parser(parser):
    return parser

def normalize_logs(logs):
    if len(logs) > 255:
        logging.warning(f"log path has a invalid length : {logs} : log path length must be under 255 !")
    if not(re.match(r"^[a-zA-Z0-9_/:\"\-\s]*$", logs)):
        logging.warning(f"log path has a invalid syntax : {logs}")
    return logs
    
def normalize_source(source):
    if len(source) > 255:
        logging.warning(f"source path has a invalid length : {source} : source length must be under 255 !")
    if not(re.match(r"^[a-zA-Z0-9_/:\"\-\s]*$", source)):
        logging.warning(f"source has a invalid syntax : {source}")
    return source

def normalize_state(obj_type, state):
    if (obj_type != "hp" and obj_type != "sv"):
        logging.error(f"'{obj_type}' is uncorrect")
        sys.exit(1)
    state = state.upper()
    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    available_state_list = config['state'][obj_type+'_state'].split(',')
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

    tags_list = [ normalize_tag(a_tag) for a_tag in tags_list]
    tags_list = [ a_tag for n, a_tag in enumerate(tags_list) if a_tag.lower() not in separator.join(tags_list[:n]).lower().split(separator)]
    return separator.join(tags_list)

def normalize_ports(ports):
    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    separator = config['port']['separator']
    ports_list = ports.split(separator)
    ports_list = [ str(normalize_port(a_port.strip())) for a_port in ports_list]
    ports_list = [ a_port for n, a_port in enumerate(ports_list) if a_port not in ports_list[:n]]
    return separator.join(ports_list)

def normalize_tag(tag):
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    if (tag=='' or tag==None):
        tag = config['tag']['default_value']
    tag = tag.strip()
    tag = tag[0].upper() + tag[1:]
    if not(re.match(r"^[a-zA-Z0-9_\-]*$", tag)):
        logging.warning(f"tag has a invalid syntax : {tag}")
    return tag

def normalize_display(object_infos, obj_type, separator, next_type):
    next_obj={key:(value.split(separator) if (separator in str(value)) else value) for (key,value) in object_infos.items() if key[:len(obj_type+"_")]!=obj_type+"_"}
    resultat={**{key:value for (key,value) in object_infos.items() if key[:len(obj_type+"_")]==obj_type+"_"},**{next_type+"s": ([{key:value[i] for (key,value) in next_obj.items()} for i in range(len(next_obj[next_type+"_id"]))] if isinstance(next_obj[next_type+"_id"],list) else [next_obj])}} 
    return resultat



# lk_infos={"id":"lk-1BFB3AFE3FEE1FEFB1D25E22FC2CA69F", "nb_hp": 4, "nb_serv": 2, "tags_hp":"OpenSSH,SSH,Elasticsearch", "tags_serv":"Europe ,  suisse,  geneve,TagDeTest42,TagDeTest4254,TagDeTest427","ports":"22, 189  ,  469,6484,88"}

# for key, value in lk_infos.items():
#   if (key=="id" or key=="state"):
#     lk_infos[key]=globals()['normalize_' + key]("lk",value)
#   elif (key=="tags_hp" or key=="tags_serv"):
#     lk_infos[key]=globals()['normalize_tags'](value)
#   else:
#     lk_infos[key]=globals()['normalize_' + key](value)
# print(lk_infos)

### TEST SECTION ###
if __name__ == '__main__':
    ports="8978, 22   ,18  ,    8978,22,18  ,22,6851,22"
    tags="  Europe ,  France    ,  SSH     ,TagDeTest4TesTag666  ,   TestTag,Europe ,  FrAnce   ,  SSH   ,TagDeTest4TesTag666 ,  TestTag"
    
    print(normalize_tags(tags))
    