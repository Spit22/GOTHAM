import sys
import configparser
import os
from . import normalization_functions

def normalize_honeypot_infos(hp_infos):
  for key, value in hp_infos.items():
    normalize_key=getattr(normalization_functions,'normalize_' + key)
    if (key=="id" or key=="state"):
      hp_infos[key]=normalize_key("hp",value)
    else:
      hp_infos[key]=normalize_key(value)
  return hp_infos

def normalize_server_infos(serv_infos):
  for key, value in serv_infos.items():
    normalize_key=getattr(normalization_functions,'normalize_' + key)
    if (key=="id" or key=="state"):
      serv_infos[key]=normalize_key("sv",value)
    else:
      serv_infos[key]=normalize_key(value)
  return serv_infos

def normalize_link_infos(lk_infos):
  for key, value in lk_infos.items():
    if (key=="tags_hp" or key=="tags_serv"):
      normalize_key=getattr(normalization_functions,'normalize_tags')
    else:
      normalize_key=getattr(normalization_functions,'normalize_' + key)
    if (key=="id" or key=="state"):
      lk_infos[key]=normalize_key("lk",value)
    else:
      lk_infos[key]=normalize_key(value)
  return lk_infos

def normalize_full_honeypot_infos(hp_infos):
    # Retrieve settings from config file
    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    default_hp_infos = config['honeypot_infos_default']
    hp_infos=normalize_honeypot_infos(hp_infos)
    for key, value in default_hp_infos.items():
        if value == 'NOT NULL':
            if not(key in hp_infos):
                logging.error(f" Missing value of '{key}'")
                sys.exit(1)
            elif(hp_infos[key] == '' or hp_infos[key] == 0 or hp_infos[key] == None):
                logging.error(f" Missing value of '{key}'")
                sys.exit(1)
        else:
            if not(key in hp_infos):
                hp_infos[key] = value
    return normalize_honeypot_infos(hp_infos)

def normalize_full_server_infos(server_infos):
    # Retrieve settings from config file
    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    default_server_infos = config['server_infos_default']
    server_infos=normalize_server_infos(server_infos)
    for key, value in default_server_infos.items():
        if value == 'NOT NULL':
            if not(key in server_infos):
                logging.error(f" Missing value of '{key}'")
                sys.exit(1)
            elif(server_infos[key] == '' or server_infos[key] == 0 or server_infos[key] == None):
                logging.error(f" Missing value of '{key}'")
                sys.exit(1)
        else:
            if not(key in server_infos):
                server_infos[key] = value
    return normalize_server_infos(server_infos)

def normalize_full_link_infos(lk_infos):
    # Retrieve settings from config file
    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    default_lk_infos = config['link_infos_default']
    lk_infos=normalize_link_infos(lk_infos)
    for key, value in default_lk_infos.items():
        if value == 'NOT NULL':
            if not(key in lk_infos):
                logging.error(f" Missing value of '{key}'")
                sys.exit(1)
            elif(lk_infos[key] == '' or lk_infos[key] == 0 or lk_infos[key] == None):
                logging.error(f" Missing value of '{key}'")
                sys.exit(1)
        else:
            if not(key in lk_infos):
                lk_infos[key] = value
    return normalize_link_infos(lk_infos)


########## NORMALIZE ID SECTION ##########

def normalize_id_server(id):
  return normalization_functions.normalize_id('sv', id)

def normalize_id_honeypot(id):
  return normalization_functions.normalize_id('hp', id)

def normalize_id_link(id):
  return normalization_functions.normalize_id('lk', id)

# method_to_call = getattr(foo, 'bar')
# result = method_to_call()

