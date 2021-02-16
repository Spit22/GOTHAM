import sys
import configparser
import os
from . import normalization_functions

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')

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

def normalize_lhs_infos(lhs_infos):
  for key, value in lhs_infos.items():
    if (key=="id_hp"):
      normalize_key=getattr(normalization_functions,'normalize_id')
      lhs_infos[key]=normalize_key("hp",value)
    elif (key=="id_serv"):
      normalize_key=getattr(normalization_functions,'normalize_id')
      lhs_infos[key]=normalize_key("sv",value)
    elif (key=="id_link"):
      normalize_key=getattr(normalization_functions,'normalize_id')
      lhs_infos[key]=normalize_key("lk",value)
    else:
      normalize_key=getattr(normalization_functions,'normalize_' + key)
      lhs_infos[key]=normalize_key(value)
  return lhs_infos

########## NORMALIZE WITH DEFAULT VALUES SECTION ##########

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


def normalize_full_lhs_infos(lhs_infos):
    default_lhs_infos = {"id_link":"NOT NULL","id_hp":"NOT NULL","id_serv":"NOT NULL","port":"NOT NULL"}
    lhs_infos=normalize_lhs_infos(lhs_infos)
    for key, value in default_lhs_infos.items():
        if value == 'NOT NULL':
            if not(key in lhs_infos):
                logging.error(f" Missing value of '{key}'")
                sys.exit(1)
            elif(lhs_infos[key] == '' or lhs_infos[key] == 0):
                logging.error(f" Missing value of '{key}'")
                sys.exit(1)
        else:
            if not(key in lhs_infos):
                lhs_infos[key] = value
    return normalize_lhs_infos(lhs_infos)


########## NORMALIZE DISPLAY SECTION ##########
def normalize_display_object_infos(object_infos, obj_type, next_type=''):
  obj_types=["hp","serv","link"]
  if not(obj_type in obj_types and (next_type in obj_types or next_type=='')):
    logging.error(f" Wrong value of '{obj_type}'")
    sys.exit(1)
  if obj_type != "link":
    next_type= "link"
  elif next_type=='':
    if object_infos["link_nb_hp"] <= object_infos["link_nb_serv"]:
      next_type="hp"
    else:
      next_type="serv"
  resultat = normalization_functions.normalize_display(object_infos, obj_type, "||||||", next_type)
  last_type=list(set(obj_types) - set([obj_type, next_type]))[0]
  for i in range(len(resultat[next_type+'s'])):
    resultat[next_type+'s'][i] = normalization_functions.normalize_display(resultat[next_type+'s'][i], next_type, "||||", last_type)
  return resultat

########## NORMALIZE ID SECTION ##########

def normalize_id_server(id):
  return normalization_functions.normalize_id('sv', id)

def normalize_id_honeypot(id):
  return normalization_functions.normalize_id('hp', id)

def normalize_id_link(id):
  return normalization_functions.normalize_id('lk', id)
  

########## NORMALIZE EDIT SECTION ##########

def normalize_modif_to_str(modifs):
    replacement_dict= {"': ":"=","{'":"","}":"","', ":", "}
    result=str(modifs)
    for key, value in replacement_dict.items():
        result=result.replace(key,value)
    return result

def normalize_conditions_to_str(conditions):
    replacement_dict= {"': ":"=","{'":"","}":"",", '":" and "}
    result=str(conditions)
    for key, value in replacement_dict.items():
        result=result.replace(key,value)
    return result
    