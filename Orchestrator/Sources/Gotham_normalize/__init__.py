import sys
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


# method_to_call = getattr(foo, 'bar')
# result = method_to_call()