import configparser

# Logging components
import os
import logging

GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


def check_server_ports(serv_infos, ports):
    # Determine available ports on a server from a specified list
    #
    # serv_infos (dict) : all informations of the server
    # ports (string) : ports we want to check for
    #
    # Return the list of available ports presents in the list of given ports

    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    separator = config['port']['separator']
    ports_list = ports.split(separator)
    serv_used_port = (
        list(filter(None, dict.fromkeys(serv_infos["lhs_port"].split("||")))))
    serv_used_port.append(str(serv_infos["serv_ssh_port"]))
    free_port = ''
    for port in ports_list:
        if not(port in serv_used_port):
            if free_port == '':
                free_port += port
            else:
                free_port += separator+port
    return free_port
