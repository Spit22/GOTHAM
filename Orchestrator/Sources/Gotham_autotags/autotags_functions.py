# GOTHAM'S LIB
import Gotham_SSH_SCP
import json
import requests

# Logging components
import configparser
import os
import base64
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


def autotag_by_trivy(hp_id):
    # Find tags automatically for honeypot by trivy analysing
    #
    #
    # hp_id (string) : id of the honeypot
    #
    # Return tags list

    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')

    version=config['trivy']['version']
    template=config['trivy']['template']
    options=config['trivy']['options']
    separator=config['trivy']['separator']

    # Retrieve datacenter settings from config file
    dc_ip = config['datacenter']['ip']
    dc_ssh_port = int(config['datacenter']['ssh_port'])
    try:
        dc_ssh_key = config['datacenter']['ssh_key']
        dc_ssh_key = base64.b64decode(dc_ssh_key)  # ssh_key is byte
        dc_ssh_key = dc_ssh_key.decode('ascii')  # ssh_key is ascii string
        dc_ssh_key_rsyslog = dc_ssh_key  #  ssh_key for rsyslog
    except Exception as e:
        error = "Error loading datacenter's SSH key: "+str(e)
        logging.error(error)
        raise Exception(error)

    # Put datacenter settings in a dictionary
    datacenter_settings = {"hostname": dc_ip, "ssh_key": dc_ssh_key,
                       "rsyslog_ssh_key": dc_ssh_key_rsyslog, "ssh_port": dc_ssh_port}


    command = 'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v /root/Library/Caches:/root/.cache/ aquasec/trivy:'+version+" "+options+'  --format template --template "'+template+'" -o /root/.cache/result.txt '+hp_id+'_honeypot:latest'
    try:
        Gotham_SSH_SCP.execute_command_with_return(dc_ip, dc_ssh_port, dc_ssh_key, command)
    except ValueError as e:
        error = "Error while trying to execute ssh command for trivy check on hp (id: "+hp_id+") : " + str(e)
        logging.error(error)
        raise ValueError(error)
    command= 'cat /root/Library/Caches/result.txt'
    try:
        tags=Gotham_SSH_SCP.execute_command_with_return(dc_ip, dc_ssh_port, dc_ssh_key, command)
        if tags != []:
            tags= tags[0].split(separator)
    except ValueError as e:
        error = "Error while trying to execute ssh command for trivy check on hp (id: "+hp_id+") : " + str(e)
        logging.error(error)
        raise ValueError(error)
    
    return list(set(tags))
  

def autotag_by_docker_top(hp_id):
    # Find tags automatically for honeypot by docker top command
    #
    #
    # hp_id (string) : id of the honeypot
    #
    # Return tags list

    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')

    # Retrieve datacenter settings from config file
    dc_ip = config['datacenter']['ip']
    dc_ssh_port = int(config['datacenter']['ssh_port'])
    try:
        dc_ssh_key = config['datacenter']['ssh_key']
        dc_ssh_key = base64.b64decode(dc_ssh_key)  # ssh_key is byte
        dc_ssh_key = dc_ssh_key.decode('ascii')  # ssh_key is ascii string
        dc_ssh_key_rsyslog = dc_ssh_key  #  ssh_key for rsyslog
    except Exception as e:
        error = "Error loading datacenter's SSH key: "+str(e)
        logging.error(error)
        raise Exception(error)

    # Put datacenter settings in a dictionary
    datacenter_settings = {"hostname": dc_ip, "ssh_key": dc_ssh_key,
                       "rsyslog_ssh_key": dc_ssh_key_rsyslog, "ssh_port": dc_ssh_port}

    command = "docker top "+hp_id+" -eo comm,pid | awk 'NR>1{print $1}'"
    
    try:
        tags=Gotham_SSH_SCP.execute_command_with_return(dc_ip, dc_ssh_port, dc_ssh_key, command)
    except ValueError as e:
        error = "Error while trying to execute ssh command for docker top on hp (id: "+hp_id+") : " + str(e)
        logging.error(error)
        raise ValueError(error)
    
    return list(set(tags))
    

def autotag_by_ipstack(serv_ip):
    # Find tags automatically for server by ipstack command
    #
    #
    # serv_ip (string) : ip of the server
    #
    # Return tags list

    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')

    access_key = config['ipstack']['access_key']
    parser = config['ipstack']['parser']

    tags=[]

    try:
        url = "http://api.ipstack.com/"+serv_ip
        params={"access_key": access_key}
        r = requests.get(url, params=params)
        jsonresponse = r.json()
    except Exception as e:
        error = "Error while trying to get ipstack information on the ip " + \
            str(serv_ip)+" : "+str(e)
        logging.error(error)
        raise ValueError(error)

    for item in parser.split(","):
        key_list=item.split(":")
        value=jsonresponse
        for key in key_list:
            value=value[key]
        tags.append(str(value))




    return list(set(tags))