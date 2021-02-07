import sys
import configparser
import re
# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


def check_tags(object_type, objects_infos, tags_hp='', tags_serv='', mode=False):
	if (object_type != "hp" and object_type != "serv" and object_type != "link"):
		logging.error(f"'{object_type}' is uncorrect")
		sys.exit(1)

	GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
	# Retrieve settings from config file
	config = configparser.ConfigParser()
	config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
	separator = config['tag']['separator']
	if object_type == "hp" or object_type == "serv":
		if object_type == "hp":
			tags_list=tags_hp.lower().split(separator)
		elif object_type == "serv":
			tags_list=tags_serv.lower().split(separator)
		if mode==False:
			result = [object_infos for object_infos in objects_infos if (len(set(object_infos[object_type+"_tags"].lower().split('||')).intersection(tags_list))==len(tags_list))]
		elif mode==True:
			result = [object_infos for object_infos in objects_infos if (len(set(object_infos[object_type+"_tags"].lower().split('||')).intersection(tags_list))==len(tags_list)==len(object_infos[object_type+"_tags"].lower().split('||')))]
	elif object_type == "link":
		tags_hp_list = tags_hp.lower().split(separator)
		tags_serv_list = tags_serv.lower().split(separator)
		if mode==False:
			result = [object_infos for object_infos in objects_infos if (len(set(object_infos[object_type+"_tags_hp"].lower().split('||')).intersection(tags_hp_list))==len(tags_hp_list) and len(set(object_infos[object_type+"_tags_serv"].lower().split('||')).intersection(tags_serv_list))==len(tags_serv_list))]
		elif mode==True:
			result = [object_infos for object_infos in objects_infos if (len(set(object_infos[object_type+"_tags_hp"].lower().split('||')).intersection(tags_hp_list))==len(tags_hp_list)==len(object_infos[object_type+"_tags_hp"].lower().split('||')) and len(set(object_infos[object_type+"_tags_serv"].lower().split('||')).intersection(tags_serv_list))==len(tags_serv_list)==len(object_infos[object_type+"_tags_serv"].lower().split('||')))]
	return result

### TEST SECTION ###
if __name__ == '__main__':
	object_type = "serv"
	links_infos = [{'link_id': 'lk-6A39971632EE11EB89DC9EECFB2CA371', 'link_nb_hp': 2, 'link_nb_serv': 2, 'link_ports': '22', 'link_tags_hp': 'SSH', 'link_tags_serv': 'Hebergeur.com', 'link_created_at': 'datetime.datetime(2021, 2, 7, 9, 22, 9)', 'link_updated_at': 'datetime.datetime(2021, 2, 7, 9, 22, 9)', 'hp_id': 'hp-1B5B3A1E32EE11EBB1F25E22FC2CA371||||||hp-742F831232ED11EB8FA5D8F7FB2CA371', 'hp_name': 'Honeypot_PythonSSH||||||Honeypot_OpenSSH', 'hp_descr': 'Second Honeypot pour test||||||Premier Honeypot pour test', 'hp_port': '1658||||||1994', 'hp_parser': 'TO_ADD||||||TO_ADD', 'hp_logs': '/var/log/apache2/error.log||||||/var/log/honeypot.log', 'hp_source': '/data/hp-1B5B3A1E32EE11EBB1F25E22FC2CA371/dockerfile||||||/data/hp-742F831232ED11EB8FA5D8F7FB2CA371/dockerfile', 'hp_state': 'UNUSED||||||ERROR', 'hp_port_container': '22||||||181', 'hp_tags': 'SSH||||||Debian||SSH', 'hp_created_at': '2021-02-07 09:22:09||||||2021-02-07 09:22:09', 'hp_updated_at': '2021-02-07 09:22:09||||||2021-02-07 09:22:09', 'lhs_port': '22||||||22', 'serv_id': 'sv-447831E032EE11EBB6D20248FC2CA371||||||sv-7126ECA632EC11EB830EA9EEFB2CA371', 'serv_name': 'vps-2.hebergeur.fr||||||vps-1.hebergeur.fr', 'serv_descr': 'Second serveur de test.||||||Premier serveur de test.', 'serv_ip': '172.0.0.10||||||172.0.0.1', 'serv_ssh_key': 'TO_ADD||||||TO_ADD', 'serv_ssh_port': '22||||||22', 'serv_state': '||||||', 'serv_tags': 'France||Hebergeur.com||Vannes||||||France||Hebergeur.com||Paris', 'serv_created_at': '2021-02-07 09:22:09||||||2021-02-07 09:22:09', 'serv_updated_at': '2021-02-07 09:22:09||||||2021-02-07 09:22:09'}, {'link_id': 'lk-72660A46340111EBBAC118F3FB2CA371', 'link_nb_hp': 2, 'link_nb_serv': 5, 'link_ports': '789,987,879,897', 'link_tags_hp': 'haute-dispo||port_22||SSH', 'link_tags_serv': 'Europe||France||Auxerre', 'link_created_at': 'datetime.datetime(2021, 2, 7, 9, 22, 9)', 'link_updated_at': 'datetime.datetime(2021, 2, 7, 9, 22, 9)', 'hp_id': 'hp-6EAB49BC33C911EBBC754E2EFC2CA371||||||hp-75034A4E33C911EB9D009933FC2CA371', 'hp_name': 'Honeypot_ssh||||||Honeypot_openssh', 'hp_descr': 'Hp for test||||||Hp for test', 'hp_port': '2001', 'hp_parser': 'To Add||||||To Add', 'hp_logs': 'To add||||||To add', 'hp_source': 'To add||||||To add', 'hp_state': 'DOWN||||||UNUSED', 'hp_port_container': '468||||||987', 'hp_tags': 'haute-dispo||port_22||SSH||||||haute-dispo||OpenSSH||port_22||SSH', 'hp_created_at': '2021-02-07 09:22:09||||||2021-02-07 09:22:09', 'hp_updated_at': '2021-02-07 09:22:09||||||2021-02-07 09:22:09', 'lhs_port': '789||||987||||||879||||897||||789', 'serv_id': 'sv-7706DF9633CD11EB82B004DDFB2CA371||||sv-838C81A833CD11EB881DEFE6FB2CA371||||||sv-88784AF833CD11EBAEA003EBFB2CA371||||sv-973CFB8833CD11EBB5BF65F5FB2CA371||||sv-9D5E49EA33CD11EBAFE55BF9FB2CA371', 'serv_name': 'vps-4.hebergeur.foo||||vps-7.hebergeur.foo||||||vps-8.hebergeur.foo||||vps-11.hebergeur.foo||||vps-12.hebergeur.foo', 'serv_descr': 'Server for test||||Server for test||||||Server for test||||Server for test||||Server for test', 'serv_ip': '172.0.0.21||||172.0.0.24||||||172.0.0.25||||172.0.0.28||||172.0.0.29', 'serv_ssh_key': 'To_Add||||To_Add||||||To_Add||||To_Add||||To_Add', 'serv_ssh_port': '22||||22||||||22||||22||||22', 'serv_state': 'To_Add||||To_Add||||||To_Add||||To_Add||||To_Add', 'serv_tags': 'Allemagne||Berlin||Europe||||Auxerre||Europe||France||||||Europe||France||Vannes||||Europe||France||OVH||Paris||||Auxerre||Europe||France||OVH', 'serv_created_at': '2021-02-07 09:22:09||||2021-02-07 09:22:09||||||2021-02-07 09:22:09||||2021-02-07 09:22:09||||2021-02-07 09:22:09', 'serv_updated_at': '2021-02-07 09:22:09||||2021-02-07 09:22:09||||||2021-02-07 09:22:09||||2021-02-07 09:22:09||||2021-02-07 09:22:09'}, {'link_id': 'lk-1BFB3AFE3FEE1FEFB1D25E22FC2CA777', 'link_nb_hp': 4, 'link_nb_serv': 2, 'link_ports': '22,186,658', 'link_tags_hp': 'SSH', 'link_tags_serv': ' Europe||France', 'link_created_at': 'datetime.datetime(2021, 2, 7, 16, 23, 14)', 'link_updated_at': 'datetime.datetime(2021, 2, 7, 16, 23, 14)', 'serv_id': None, 'serv_name': None, 'serv_descr': None, 'serv_ip': None, 'serv_ssh_key': None, 'serv_ssh_port': None, 'serv_state': None, 'serv_tags': None, 'serv_created_at': None, 'serv_updated_at': None, 'lhs_port': None, 'hp_id': None, 'hp_name': None, 'hp_descr': None, 'hp_port': None, 'hp_parser': None, 'hp_logs': None, 'hp_source': None, 'hp_state': None, 'hp_port_container': None, 'hp_tags': None, 'hp_created_at': None, 'hp_updated_at': None}, {'link_id': 'lk-67C82EAC340111EB85FE89F2FB2CA371', 'link_nb_hp': 4, 'link_nb_serv': 2, 'link_ports': '22,2222,42,4242', 'link_tags_hp': 'SSH', 'link_tags_serv': 'Auxerre||Europe||France', 'link_created_at': 'datetime.datetime(2021, 2, 7, 9, 22, 9)', 'link_updated_at': 'datetime.datetime(2021, 2, 7, 9, 22, 9)', 'serv_id': 'sv-838C81A833CD11EB881DEFE6FB2CA371||||||sv-9D5E49EA33CD11EBAFE55BF9FB2CA371', 'serv_name': 'vps-7.hebergeur.foo||||||vps-12.hebergeur.foo', 'serv_descr': 'Server for test||||||Server for test', 'serv_ip': '172.0.0.24||||||172.0.0.29', 'serv_ssh_key': 'To_Add||||||To_Add', 'serv_ssh_port': '22||||||22', 'serv_state': 'To_Add||||||To_Add', 'serv_tags': 'Auxerre||Europe||France||||||Auxerre||Europe||France||OVH', 'serv_created_at': '2021-02-07 09:22:09||||||2021-02-07 09:22:09', 'serv_updated_at': '2021-02-07 09:22:09||||||2021-02-07 09:22:09', 'lhs_port': '22||||2222||||||42||||4242', 'hp_id': 'hp-1B5B3A1E32EE11EBB1F25E22FC2CA371||||hp-6EAB49BC33C911EBBC754E2EFC2CA371||||||hp-742F831232ED11EB8FA5D8F7FB2CA371||||hp-75034A4E33C911EB9D009933FC2CA371', 'hp_name': 'Honeypot_PythonSSH||||Honeypot_ssh||||||Honeypot_OpenSSH||||Honeypot_openssh', 'hp_descr': 'Second Honeypot pour test||||Hp for test||||||Premier Honeypot pour test||||Hp for test', 'hp_port': '1658||||||1994||||2001', 'hp_parser': 'TO_ADD||||To Add||||||TO_ADD||||To Add', 'hp_logs': '/var/log/apache2/error.log||||To add||||||/var/log/honeypot.log||||To add', 'hp_source': '/data/hp-1B5B3A1E32EE11EBB1F25E22FC2CA371/dockerfile||||To add||||||/data/hp-742F831232ED11EB8FA5D8F7FB2CA371/dockerfile||||To add', 'hp_state': 'UNUSED||||DOWN||||||ERROR||||UNUSED', 'hp_port_container': '22||||468||||||181||||987', 'hp_tags': 'SSH||||haute-dispo||port_22||SSH||||||Debian||SSH||||haute-dispo||OpenSSH||port_22||SSH', 'hp_created_at': '2021-02-07 09:22:09||||2021-02-07 09:22:09||||||2021-02-07 09:22:09||||2021-02-07 09:22:09', 'hp_updated_at': '2021-02-07 09:22:09||||2021-02-07 09:22:09||||||2021-02-07 09:22:09||||2021-02-07 09:22:09'}]
	objects_infos = [{'serv_id': 'sv-62323F6F323F38F42d656DF861566696', 'serv_name': 'serveur-test-6', 'serv_descr': 'blabla', 'serv_ip': '42.254.99.99', 'serv_ssh_key': 'non', 'serv_ssh_port': 22, 'serv_state': 'ERROR', 'serv_tags': 'Europe||France||SSH||TagDeTest4TesTag666||TestTag', 'serv_created_at': 'datetime.datetime(2021, 2, 6, 17, 2, 53)', 'serv_updated_at': 'datetime.datetime(2021, 2, 6, 17, 2, 53)', 'link_id': '', 'link_nb_hp': '', 'link_nb_serv': '', 'link_ports': '', 'link_tags_hp': '', 'link_tags_serv': '', 'link_created_at': '', 'link_updated_at': '', 'lhs_port': '', 'hp_id': '', 'hp_name': '', 'hp_descr': '', 'hp_port': '', 'hp_parser': '', 'hp_logs': '', 'hp_source': '', 'hp_state': '', 'hp_port_container': '', 'hp_tags': '', 'hp_created_at': '', 'hp_updated_at': ''},{'serv_id': 'sv-62323F6F323F38F42d656DF861566696', 'serv_name': 'serveur-test-6', 'serv_descr': 'blabla', 'serv_ip': '42.254.99.99', 'serv_ssh_key': 'non', 'serv_ssh_port': 22, 'serv_state': 'ERROR', 'serv_tags': 'Europe||France||SSH||TagDeTest4TesTag666||TestTag||Truc', 'serv_created_at': 'datetime.datetime(2021, 2, 6, 17, 2, 53)', 'serv_updated_at': 'datetime.datetime(2021, 2, 6, 17, 2, 53)', 'link_id': '', 'link_nb_hp': '', 'link_nb_serv': '', 'link_ports': '', 'link_tags_hp': '', 'link_tags_serv': '', 'link_created_at': '', 'link_updated_at': '', 'lhs_port': '', 'hp_id': '', 'hp_name': '', 'hp_descr': '', 'hp_port': '', 'hp_parser': '', 'hp_logs': '', 'hp_source': '', 'hp_state': '', 'hp_port_container': '', 'hp_tags': '', 'hp_created_at': '', 'hp_updated_at': ''},{'serv_id': 'sv-62323F6F323F38F42d656DF861566696', 'serv_name': 'serveur-test-6', 'serv_descr': 'blabla', 'serv_ip': '42.254.99.99', 'serv_ssh_key': 'non', 'serv_ssh_port': 22, 'serv_state': 'ERROR', 'serv_tags': 'Europe||France||SSH||TagDeTest4TesTag666||TestTag||Truc||Hachis||Parmentier', 'serv_created_at': 'datetime.datetime(2021, 2, 6, 17, 2, 53)', 'serv_updated_at': 'datetime.datetime(2021, 2, 6, 17, 2, 53)', 'link_id': '', 'link_nb_hp': '', 'link_nb_serv': '', 'link_ports': '', 'link_tags_hp': '', 'link_tags_serv': '', 'link_created_at': '', 'link_updated_at': '', 'lhs_port': '', 'hp_id': '', 'hp_name': '', 'hp_descr': '', 'hp_port': '', 'hp_parser': '', 'hp_logs': '', 'hp_source': '', 'hp_state': '', 'hp_port_container': '', 'hp_tags': '', 'hp_created_at': '', 'hp_updated_at': ''}]
	print("------------- Doit en avoir 3 -------------")
	tags="Europe,France,SSH,TagDeTest4TesTag666,TestTag"
	print(check_tags(object_type,objects_infos,tags_serv=tags))
	print("------------- Doit en avoir 2 -------------")
	tags="Europe,France,SSH,TagDeTest4TesTag666,TestTag,Truc"
	print(check_tags(object_type,objects_infos,tags_serv=tags))
	print("------------- Doit en avoir 1 -------------")
	tags="Europe,France,SSH,TagDeTest4TesTag666,TestTag,Truc"
	print(check_tags(object_type,objects_infos,tags_serv=tags, mode=True))

	object_type = "link"
	tags_hp="haute-dispo,port_22,SSH"
	tags_serv="Europe,France"

	print("------------- Link avec mode False, doit y en avoir 1-------------")
	print(check_tags(object_type,links_infos,tags_serv=tags_serv, tags_hp=tags_hp))

	print("------------- Link avec mode True, doit y en avoir 0 -------------")
	print(check_tags(object_type,links_infos,tags_serv=tags_serv, tags_hp=tags_hp, mode=True))