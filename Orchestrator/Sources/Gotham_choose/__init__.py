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
	
	hps_infos=[dict(hp, **{'weight':100}) for hp in hps_infos]
	object_type="hp"

	hps_infos=selection_function.weighting_nb_link(object_type, hps_infos)
	hps_infos=selection_function.weighting_nb_port(hps_infos)
	hps_infos=selection_function.weighting_state(object_type, hps_infos)
	hps_infos=selection_function.weighting_nb_useless_tags(object_type, hps_infos, tags_hp)
	hps_infos=selection_function.weighting_time(object_type, hps_infos, "created_at")
	hps_infos=selection_function.weighting_time(object_type, hps_infos, "updated_at")

	if len(hps_infos)<nb_hp:
		nb_hp=len(hps_infos)

	return sorted(hps_infos, key=lambda k: k['weight'])[0:nb_hp] 

def choose_servers(servs_infos, nb_serv, tags_serv):
	'''
	Choose the best servers when creating a link according to the need  

	ARGUMENTS:
		servs_infos (list of dict) : list of potentials servers
		nb_serv (int) : number of server wanted
		tags_serv (string) : server tags mentioned in the link
	'''

	servs_infos=[dict(serv, **{'weight':100}) for serv in servs_infos]
	object_type="serv"

	servs_infos=selection_function.weighting_nb_link(object_type, servs_infos)
	servs_infos=selection_function.weighting_nb_port(servs_infos)
	servs_infos=selection_function.weighting_state(object_type, servs_infos)
	servs_infos=selection_function.weighting_nb_useless_tags(object_type, servs_infos, tags_serv)
	servs_infos=selection_function.weighting_nb_free_port(servs_infos)
	servs_infos=selection_function.weighting_time(object_type, servs_infos, "created_at")
	servs_infos=selection_function.weighting_time(object_type, servs_infos, "updated_at")

	return sorted(servs_infos, key=lambda k: k['weight'])[0:nb_serv]

