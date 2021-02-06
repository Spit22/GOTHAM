import sys
import configparser
import re
# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


def check_tags(object_type, objects_infos, tags):
	if (object_type != "hp" and object_type != "serv"):
		logging.error(f"'{object_type}' is uncorrect")
		sys.exit(1)

	GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
	# Retrieve settings from config file
	config = configparser.ConfigParser()
	config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
	separator = config['tag']['separator']
	tags_list = tags.split(separator)
	result=[]
	for object_infos in objects_infos:
		object_is_ok=True
		obj_tags_list=object_infos[object_type+"_tags"].lower().split('||')
		for a_tag in tags_list:
			if not(a_tag.lower() in obj_tags_list):
				object_is_ok=False
				break
		if object_is_ok:
			result.append(object_infos)
	return result

### TEST SECTION ###
if __name__ == '__main__':
	object_type = "serv"
	objects_infos = [{'serv_id': 'sv-62323F6F323F38F42d656DF861566696', 'serv_name': 'serveur-test-6', 'serv_descr': 'blabla', 'serv_ip': '42.254.99.99', 'serv_ssh_key': 'non', 'serv_ssh_port': 22, 'serv_state': 'ERROR', 'serv_tags': 'Europe||France||SSH||TagDeTest4TesTag666||TestTag', 'serv_created_at': 'datetime.datetime(2021, 2, 6, 17, 2, 53)', 'serv_updated_at': 'datetime.datetime(2021, 2, 6, 17, 2, 53)', 'link_id': '', 'link_nb_hp': '', 'link_nb_serv': '', 'link_ports': '', 'link_tags_hp': '', 'link_tags_serv': '', 'link_created_at': '', 'link_updated_at': '', 'lhs_port': '', 'hp_id': '', 'hp_name': '', 'hp_descr': '', 'hp_port': '', 'hp_parser': '', 'hp_logs': '', 'hp_source': '', 'hp_state': '', 'hp_port_container': '', 'hp_tags': '', 'hp_created_at': '', 'hp_updated_at': ''},{'serv_id': 'sv-62323F6F323F38F42d656DF861566696', 'serv_name': 'serveur-test-6', 'serv_descr': 'blabla', 'serv_ip': '42.254.99.99', 'serv_ssh_key': 'non', 'serv_ssh_port': 22, 'serv_state': 'ERROR', 'serv_tags': 'Europe||France||SSH||TagDeTest4TesTag666||TestTag||Truc', 'serv_created_at': 'datetime.datetime(2021, 2, 6, 17, 2, 53)', 'serv_updated_at': 'datetime.datetime(2021, 2, 6, 17, 2, 53)', 'link_id': '', 'link_nb_hp': '', 'link_nb_serv': '', 'link_ports': '', 'link_tags_hp': '', 'link_tags_serv': '', 'link_created_at': '', 'link_updated_at': '', 'lhs_port': '', 'hp_id': '', 'hp_name': '', 'hp_descr': '', 'hp_port': '', 'hp_parser': '', 'hp_logs': '', 'hp_source': '', 'hp_state': '', 'hp_port_container': '', 'hp_tags': '', 'hp_created_at': '', 'hp_updated_at': ''}]
	tags="Europe,France,SSH,TagDeTest4TesTag666,TestTag"
	print(check_tags(object_type,objects_infos,tags))
	tags="Europe,France,SSH,TagDeTest4TesTag666,TestTag,Truc"
	print(check_tags(object_type,objects_infos,tags))