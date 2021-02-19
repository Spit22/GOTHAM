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
