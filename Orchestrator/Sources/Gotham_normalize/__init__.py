import sys
from . import normalization_functions



# THE DATA
'''
#Honeypot
  `id` varchar(35) NOT NULL,
  `name` varchar(128) NOT NULL,
  `descr` text DEFAULT NULL,
  `port` int(5) DEFAULT NULL,
  `parser` text NOT NULL,
  `logs` varchar(255) NOT NULL,
  `source` varchar(255) NOT NULL,
  `id_container` char(12) DEFAULT NULL,
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