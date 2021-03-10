# -*- coding: utf-8 -*-

#===Import GOTHAM's libs===#
from Gotham_SSH_SCP import send_file_and_execute_commands, send_file, execute_commands
#==========================#

#===Logging components===#
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log', level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
#=======================#


def generate_dockercompose(id, dockerfile_path, log_path, honeypot_port, mapped_port):
    '''
    Generates a docker-compose.yml file  from given information

    ARGUMENTS:
        id (string) : id of the honeypot
        dockerfile_path (string) : local path to the dockerfile
        log_path (string) : remote path of logs (in the honeypot)
        mapped_port (int) : available port we can map honeypot to
    '''
    # Create the docker-compose
    dockercompose = open(str(dockerfile_path)+"docker-compose.yml", "a")
    # Write the docker-compose version
    dockercompose.write('version: "3"\n')
    # Add the 'service' tag for honeypot service
    dockercompose.write('services:\n')
    # Add the honeypot service
    dockercompose.write('  honeypot:\n')
    # Configure container name
    dockercompose.write('    container_name: '+str(id)+'\n')
    # Add volumes for logs
    dockercompose.write('    volumes:\n')
    dockercompose.write('      - /data/'+str(id)+'/logs:'+str(log_path)+'\n')
    # Build options
    dockercompose.write('    build:\n')
    dockercompose.write('      context: .\n')
    dockercompose.write('      dockerfile: Dockerfile\n')
    # Map ports
    dockercompose.write('    ports:\n')
    dockercompose.write('      - \"'+str(mapped_port)+':'+str(honeypot_port)+"\"\n")
    # Add a TTY
    dockercompose.write('    tty: true\n')
    # Close file
    dockercompose.close()


def deploy_container(dc_ip, dc_ssh_port, dc_ssh_key, dockerfile_path, id_hp):
    '''
    Install and deploy an Nginx Reverse-Proxy on a given server
    
    ARGUMENTS :
        ip_dc (string): ip of remote server
        dc_ssh_port (int) : port the ssh service listen
        dc_ssh_key (file-like object) : ssh key used to connect to server
        dockerfile_paht (string) : local path of the dockerfile
        id_hp (string) : id of the hp we are deploying
    
    Return True if succeed, False in the other case
    '''
    dockerfile_path = [ dockerfile_path+"/Dockerfile", dockerfile_path+"/docker-compose.yml" ]
    # Declare local vars
    docker_dest = "/data/tmp/"
    command_exec_compose = ["cd "+str(docker_dest),"docker-compose -f "+str(docker_dest)+"/docker-compose.yml  --project-name "+id_hp+" up -d"]
    # Copy docker files on datacenter, and execute docker-compose
    try:
        send_file_and_execute_commands(dc_ip, dc_ssh_port, dc_ssh_key, dockerfile_path, docker_dest, command_exec_compose)
    except Exception as e:
        logging.error(e)
        return False
    # If deployment is OK, return True
    return True


def generate_datacenter_rsyslog_conf(orch_ip, orch_rsyslog_port, rulebase_path, id_hp, rsyslog_conf_datacenter_local_path, remote_hp_log_file_path):
    try:
        # Create the configuration file
        rsyslog_conf_file = open(rsyslog_conf_datacenter_local_path + id_hp + ".conf", "a")
        # Monitor the log file of the honeypot
        rsyslog_conf_file.write('input(Type="imfile" File="' + remote_hp_log_file_path + '" Tag="' + id_hp + '")\n')
        # Apply parsing rules
        rsyslog_conf_file.write('action(Type="mmnormalize" ruleBase="' + str(rulebase_path) + '")\n')
        # Send to orchestrator in JSON format
        rsyslog_conf_file.write('action(Type="omfwd" Target="' + str(orch_ip) + '" Port="' + str(orch_rsyslog_port) + '" Protocol="tcp" Template="JSON_template")\n')
        # Stop dealing with these logs
        rsyslog_conf_file.write('stop\n')
    except Exception as e:
        error = "Fail to create rsyslog configuration for datacenter : " + str(e)
        logging.error(error)
        raise ValueError(error)


def generate_orchestrator_rsyslog_conf(id_hp, rsyslog_conf_orchestrator_local_path, local_hp_log_file_path):
    try:
        # Create the configuration file
        rsyslog_conf_file = open(rsyslog_conf_orchestrator_local_path + id_hp + ".conf", "a")
        # Filter the logs with honeypot tag
        rsyslog_conf_file.write(':msg, contains, "' + id_hp + '"\n')
        # Dump the logs in local log file
        rsyslog_conf_file.write('action(type="omfile" File="' + local_hp_log_file_path + '")\n')
        # Stop dealing with these logs
        rsyslog_conf_file.write('stop\n')
    except Exception as e:
        error = "Fail to create rsyslog configuration for orchestrator : " + str(e)
        logging.error(error)
        raise ValueError(error)

def generate_rulebase(id_hp, rules, rulebase_path):
    try:
        # Create the rulebase
        rulebase = open(rulebase_path + id_hp + ".rb", "a")
        # Specify the liblognorm version
        rulebase.write('version=2\n')
        # Write each rule in the rulebase
        for rule in rules:
            rulebase.write(str(rule) + '\n')
    except Exception as e:
        error = "Fail to create rulebase : " + str(e)
        logging.error(error)
        raise ValueError(error)


def deploy_rsyslog_conf(datacenter_settings, orchestrateur_settings, id_hp, rules):
    # On effectue 2 connexions SSH
    dc_ssh_key_1 = datacenter_settings["ssh_key"]
    dc_ssh_key_2 = datacenter_settings["ssh_key"]
    # PATH ON ORCHESTRATOR
    ### Configuration
    rsyslog_conf_datacenter_local_path = "/data/rsyslog/datacenter-configuration/"
    rsyslog_conf_orchestrator_local_path = "/data/rsyslog/"
    ### Log files
    local_hp_log_file_path = "/data/honeypot-log/"
    # Rulebase
    local_rulebase_path = "/data/rsyslog/rulebase/"

    # PATH ON DATACENTER
    ### Configuration
    #remote_path = "/data/"+str(id_hp)+"/"
    rsyslog_conf_datacenter_remote_path = "/data/rsyslog/"
    ## Log files
    remote_hp_log_file_path = "/data/"+str(id_hp)+"/logs/syslog"
    ## Rulebase
    remote_rulebase_path = "/data/rsyslog/rulebase/" 

    ### SSH SCP ARGUMENTS
    exec_restart_rsyslog = ["service rsyslog restart"]

    # Generate configuration files and rulebase
    try:
        generate_rulebase(id_hp, rules, local_rulebase_path)
        generate_datacenter_rsyslog_conf(orchestrateur_settings["hostname"], orchestrateur_settings["syslog_port"], remote_rulebase_path, id_hp, rsyslog_conf_datacenter_local_path, remote_hp_log_file_path)
        generate_orchestrator_rsyslog_conf(id_hp, rsyslog_conf_orchestrator_local_path, local_hp_log_file_path)
    except Exception as e:
        error = "Fail to generate rsyslog configuration : " + str(e)
        logging.error(error)
        raise ValueError(error)
    # Send datacenter rsyslog configuration to the datacenter
    try:
        # Send the rulebase
        send_file(datacenter_settings["hostname"], datacenter_settings["ssh_port"], dc_ssh_key_1, [ local_rulebase_path + id_hp + ".rb" ], remote_rulebase_path)
        # Send rsyslog configuration
        send_file_and_execute_commands(datacenter_settings["hostname"], datacenter_settings["ssh_port"], dc_ssh_key_2, [ rsyslog_conf_datacenter_local_path + id_hp + ".conf" ], rsyslog_conf_datacenter_remote_path, exec_restart_rsyslog)
    except Exception as e:
        error = "Fail to deploy rsyslog configuration : " + str(e)
        logging.error(error)
        raise ValueError(error)
