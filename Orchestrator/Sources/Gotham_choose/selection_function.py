# Import libraries
import configparser
import sys
import operator

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
 

def weighting_nb_link(object_type, objects_infos):
	'''
    Add a weight corresponding to the number of links associated with each object 

    ARGUMENTS:
        objects_infos (list of dict) : list of potentials objects
    '''

	if (object_type != "hp" and object_type != "serv"):
		logging.error(f"'{object_type}' is uncorrect")
		sys.exit(1)

	GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
	# Retrieve settings from config file
	config = configparser.ConfigParser()
	config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
	if (object_type == "hp"):
		weight=int(config['hp_weight']["nb_link"])
	elif (object_type == "serv"):
		weight=int(config['serv_weight']["nb_link"])

	objects_infos=[{**object_infos, **{"weight":int(object_infos["weight"])+(weight*int(len(object_infos["link_id"].split("||||||"))))}} if (object_infos["link_id"] != '' and object_infos["link_id"] != None and object_infos["link_id"] != 'NULL') else object_infos for object_infos in objects_infos]

	return objects_infos


def weighting_nb_port(servs_infos):
	'''
    Add a weight corresponding to the number of port used by each server 

    ARGUMENTS:
        servs_infos (list of dict) : list of potentials server
    '''

	GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
	# Retrieve settings from config file
	config = configparser.ConfigParser()
	config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')

	weight=int(config['serv_weight']["nb_port_used"])

	servs_infos=[{**serv_infos, **{"weight":int(serv_infos["weight"])+(weight*int(len(serv_infos["lhs_port"].replace("||||||", "||||").split("||||"))))}} if (serv_infos["lhs_port"] != '' and serv_infos["lhs_port"] != None and serv_infos["lhs_port"] != 'NULL') else serv_infos for serv_infos in servs_infos]

	return servs_infos

def weighting_state(object_type, objects_infos):
	'''
    Add a weight corresponding to the state associated with each object 

    ARGUMENTS:
    	object_type (string) : hp or serv ; define the object type
        objects_infos (list of dict) : list of potentials objects
    '''

	if (object_type != "hp" and object_type != "serv"):
		logging.error(f"'{object_type}' is uncorrect")
		sys.exit(1)

	GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
	# Retrieve settings from config file
	config = configparser.ConfigParser()
	config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
	if (object_type == "hp"):
		weights=dict(config.items('hp_weight'))
	elif (object_type == "serv"):
		weights=dict(config.items('serv_weight'))

	objects_infos=[{**object_infos, **{"weight":int(object_infos["weight"])+int(weights[object_infos[object_type+"_state"].lower()])}} if object_infos[object_type+"_state"].lower() in weights else {**object_infos, **{"weight":int(object_infos["weight"])+int(max([int(i) for i in weights.values()]))}} for object_infos in objects_infos]

	return objects_infos


def weighting_nb_useless_tags(object_type, objects_infos, tags):
	'''
	Add a weight corresponding to the number of useless tags associated with each object 

	ARGUMENTS:
		object_type (string) : hp or serv ; define the object type
		objects_infos (list of dict) : list of potentials objects
		tags (string) : list of desired tags
	'''

	if (object_type != "hp" and object_type != "serv"):
		logging.error(f"'{object_type}' is uncorrect")
		sys.exit(1)

	GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
	# Retrieve settings from config file
	config = configparser.ConfigParser()
	config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
	if (object_type == "hp"):
		weight=int(config['hp_weight']["nb_useless_tag"])
	elif (object_type == "serv"):
		weight=int(config['serv_weight']["nb_useless_tag"])
	
	separator = config['tag']['separator']
	tags_list=tags.lower().split(separator)

	objects_infos=[{**object_infos, **{"weight":int(object_infos["weight"])+(weight*int(int(len(object_infos[object_type+"_tags"].lower().split('||')))-int(len(set(object_infos[object_type+"_tags"].lower().split('||')).intersection(tags_list)))))}} for object_infos in objects_infos]

	return objects_infos


def weighting_time(object_type, objects_infos):
	'''
	Add a weight corresponding to the created at and updated at associated with each object 

	ARGUMENTS:
		object_type (string) : hp or serv ; define the object type
		objects_infos (list of dict) : list of potentials objects
	'''

	return



### TEST SECTION ###
if __name__ == '__main__':
	object_type = "serv"
	objects_infos = [{'serv_id': 'sv-62323F6F323F38F42d656DF861566696', 'serv_name': 'serveur-test-6', 'serv_descr': 'blabla', 'serv_ip': '42.254.99.99', 'serv_ssh_key': 'non', 'serv_ssh_port': 22, 'serv_state': 'HEALTHY', 'serv_tags': 'Europe||France||SSH||TagDeTest4TesTag666||TestTag', 'serv_created_at': 'datetime.datetime(2021, 2, 6, 17, 2, 53)', 'serv_updated_at': 'datetime.datetime(2021, 2, 6, 17, 2, 53)', 'link_id': 'lk-4FD58A38340111EBB0E722F1FB2CA371||||||lk-67C82EAC340111EB85FE89F2FB2CA371||||||lk-72660A46340111EBBAC118F3FB2CA371', 'link_nb_hp': '', 'link_nb_serv': '', 'link_ports': '', 'link_tags_hp': '', 'link_tags_serv': '', 'link_created_at': '', 'link_updated_at': '', 'lhs_port': '', 'hp_id': '', 'hp_name': '', 'hp_descr': '', 'hp_port': '', 'hp_parser': '', 'hp_logs': '', 'hp_source': '', 'hp_state': '', 'hp_port_container': '', 'hp_tags': '', 'hp_created_at': '', 'hp_updated_at': ''},{'serv_id': 'sv-62323F6F323F38F42d656DF861566696', 'serv_name': 'serveur-test-6', 'serv_descr': 'blabla', 'serv_ip': '42.254.99.99', 'serv_ssh_key': 'non', 'serv_ssh_port': 22, 'serv_state': 'ERROR', 'serv_tags': 'Europe||France||SSH||TagDeTest4TesTag666||TestTag||Truc', 'serv_created_at': 'datetime.datetime(2021, 2, 6, 17, 2, 53)', 'serv_updated_at': 'datetime.datetime(2021, 2, 6, 17, 2, 53)', 'link_id': 'lk-4FD58A38340111EBB0E722F1FB2CA371||||||lk-72660A46340111EBBAC118F3FB2CA371', 'link_nb_hp': '', 'link_nb_serv': '', 'link_ports': '', 'link_tags_hp': '', 'link_tags_serv': '', 'link_created_at': '', 'link_updated_at': '', 'lhs_port': '53||||||42||||4242||||||789', 'hp_id': '', 'hp_name': '', 'hp_descr': '', 'hp_port': '', 'hp_parser': '', 'hp_logs': '', 'hp_source': '', 'hp_state': '', 'hp_port_container': '', 'hp_tags': '', 'hp_created_at': '', 'hp_updated_at': ''},{'serv_id': 'sv-62323F6F323F38F42d656DF861566696', 'serv_name': 'serveur-test-6', 'serv_descr': 'blabla', 'serv_ip': '42.254.99.99', 'serv_ssh_key': 'non', 'serv_ssh_port': 22, 'serv_state': 'UNUSED', 'serv_tags': 'Europe||France||SSH||TagDeTest4TesTag666||TestTag||Truc||Hachis||Parmentier', 'serv_created_at': 'datetime.datetime(2021, 2, 6, 17, 2, 53)', 'serv_updated_at': 'datetime.datetime(2021, 2, 6, 17, 2, 53)', 'link_id': '', 'link_nb_hp': '', 'link_nb_serv': '', 'link_ports': '', 'link_tags_hp': '', 'link_tags_serv': '', 'link_created_at': '', 'link_updated_at': '', 'lhs_port': '1053', 'hp_id': '', 'hp_name': '', 'hp_descr': '', 'hp_port': '', 'hp_parser': '', 'hp_logs': '', 'hp_source': '', 'hp_state': '', 'hp_port_container': '', 'hp_tags': '', 'hp_created_at': '', 'hp_updated_at': ''}]
	objects_infos=[dict(serv, **{'weight':0}) for serv in objects_infos]
	tags="Europe,France,SSH,TagDeTest4TesTag666,TestTag"
	print(weighting_nb_useless_tags(object_type, objects_infos, tags))