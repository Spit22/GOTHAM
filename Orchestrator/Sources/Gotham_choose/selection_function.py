# Import libraries
import configparser
import sys
# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
 

def weighting_nb_link(objects_infos):
	'''
    Add a weight corresponding to the number of links associated with each object 

    ARGUMENTS:
        objects_infos (list of dict) : list of potentials objects
    '''



	return

def weighting_nb_port(servs_infos):
	'''
    Add a weight corresponding to the number of port used by each server 

    ARGUMENTS:
        servs_infos (list of dict) : list of potentials server
    '''



	return

def weighting_state(object_type, objects_infos):
	'''
    Add a weight corresponding to the state associated with each object 

    ARGUMENTS:
    	object_type (string) : hp or serv ; define the object type
        objects_infos (list of dict) : list of potentials objects
    '''



	return


def weighting_nb_useless_tags(object_type, objects_infos, tags):
	'''
    Add a weight corresponding to the number of useless tags associated with each object 

    ARGUMENTS:
    	object_type (string) : hp or serv ; define the object type
        objects_infos (list of dict) : list of potentials objects
        tags (string) : list of desired tags
    '''



	return

def weighting_time(object_type, objects_infos):
	'''
    Add a weight corresponding to the created at and updated at associated with each object 

    ARGUMENTS:
        object_type (string) : hp or serv ; define the object type
		objects_infos (list of dict) : list of potentials objects
    '''



	return