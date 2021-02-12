import sys
import configparser
import re
# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')

def check_server_ports(serv_infos, ports):
	GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
	# Retrieve settings from config file
	config = configparser.ConfigParser()
	config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
	separator = config['port']['separator']
	ports_list = ports.split(separator)
	serv_used_port=(list(filter(None,dict.fromkeys(serv_infos["lhs_port"].split("||")))))
	serv_used_port.append(str(serv_infos["serv_ssh_port"]))
	free_port=''
	for port in ports_list:
		if not(port in serv_used_port):
			if free_port=='':
				free_port+=port
			else:
				free_port+=separator+port
	return free_port



### TEST SECTION ###
if __name__ == '__main__':
        object_type = "serv"
        object_infos = {'serv_id': 'sv-62323F6F323F38F42d656DF861566696', 'serv_name': 'serveur-test-6', 'serv_descr': 'blabla', 'serv_ip': '42.254.99.99', 'serv_ssh_key': 'non', 'serv_ssh_port': 22, 'serv_state': 'HEALTHY', 'serv_tags': 'Europe||France||SSH||TagDeTest4TesTag666||TestTag', 'serv_created_at': 'datetime.datetime(2021, 11, 8, 8, 1, 53)', 'serv_updated_at': 'datetime.datetime(2021, 1, 11, 22, 51, 2)', 'link_id': 'lk-4FD58A38340111EBB0E722F1FB2CA371||||||lk-67C82EAC340111EB85FE89F2FB2CA371||||||lk-72660A46340111EBBAC118F3FB2CA371', 'link_nb_hp': '', 'link_nb_serv': '', 'link_ports': '', 'link_tags_hp': '', 'link_tags_serv': '', 'link_created_at': '', 'link_updated_at': '', 'lhs_port': "NULL", 'hp_id': '', 'hp_name': '', 'hp_descr': '', 'hp_port': '', 'hp_parser': '', 'hp_logs': '', 'hp_source': '', 'hp_state': '', 'hp_port_container': '', 'hp_tags': '', 'hp_created_at': '', 'hp_updated_at': ''}
        ports="22,44,66,88"
        print(check_server_ports(object_infos, ports))