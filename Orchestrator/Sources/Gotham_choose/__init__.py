from . import selection_function

# Import libraries
import configparser
import mariadb
import sys

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')

def choose_honeypots(hps_infos, nb_hp, tags_hp):
        '''
        Choose the best honeypots when creating a link according to the need  

        ARGUMENTS:
                hps_infos (list of dict) : list of potentials honeypots
                nb_hp (int) : number of honeypot wanted
                tags_hp (string) : Honeypot tags mentioned in the link
        '''
        GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
        # Retrieve settings from config file
        config = configparser.ConfigParser()
        config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
                
        base_weight=int(config['weight_base']["hp"])

        weighted_hps_infos=[]
        for hp_infos in hps_infos:
                if not('weight' in hp_infos.keys()):
                        weighted_hps_infos.append(dict(hp_infos, **{'weight':base_weight}))
                else:
                        weighted_hps_infos.append({**hp_infos, **{"weight":int(hp_infos["weight"])+(base_weight)}})
                

        object_type="hp"

        weighted_hps_infos=selection_function.weighting_nb_link(object_type, weighted_hps_infos)
        weighted_hps_infos=selection_function.weighting_nb_port(weighted_hps_infos)
        weighted_hps_infos=selection_function.weighting_state(object_type, weighted_hps_infos)
        weighted_hps_infos=selection_function.weighting_nb_useless_tags(object_type, weighted_hps_infos, tags_hp)
        weighted_hps_infos=selection_function.weighting_time(object_type, weighted_hps_infos, "created_at")
        weighted_hps_infos=selection_function.weighting_time(object_type, weighted_hps_infos, "updated_at")

        if len(weighted_hps_infos)<nb_hp:
                nb_hp=len(weighted_hps_infos)

        return sorted(weighted_hps_infos, key=lambda k: k['weight'])[0:nb_hp] 

def choose_servers(servs_infos, nb_serv, tags_serv):
        '''
        Choose the best servers when creating a link according to the need  

        ARGUMENTS:
                servs_infos (list of dict) : list of potentials servers
                nb_serv (int) : number of server wanted
                tags_serv (string) : server tags mentioned in the link
        '''
        GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
        # Retrieve settings from config file
        config = configparser.ConfigParser()
        config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
                
        base_weight=int(config['weight_base']["serv"])

        weighted_servs_infos=[]
        for serv_infos in servs_infos:
                if not('weight' in serv_infos.keys()):
                        weighted_servs_infos.append(dict(serv_infos, **{'weight':base_weight}))
                else:
                        weighted_servs_infos.append({**serv_infos, **{"weight":int(serv_infos["weight"])+(base_weight)}})
                
        object_type="serv"

        weighted_servs_infos=selection_function.weighting_nb_link(object_type, weighted_servs_infos)
        weighted_servs_infos=selection_function.weighting_nb_port(weighted_servs_infos)
        weighted_servs_infos=selection_function.weighting_state(object_type, weighted_servs_infos)
        weighted_servs_infos=selection_function.weighting_nb_useless_tags(object_type, weighted_servs_infos, tags_serv)
        weighted_servs_infos=selection_function.weighting_nb_free_port(weighted_servs_infos)
        weighted_servs_infos=selection_function.weighting_time(object_type, weighted_servs_infos, "created_at")
        weighted_servs_infos=selection_function.weighting_time(object_type, weighted_servs_infos, "updated_at")

        return sorted(weighted_servs_infos, key=lambda k: k['weight'])[0:nb_serv]

