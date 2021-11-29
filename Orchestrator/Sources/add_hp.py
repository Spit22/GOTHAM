# -*- coding: utf-8 -*-
import subprocess

from Gotham_SSH_SCP import send_file_and_execute_commands, send_file
from Gotham_SSH_SCP import execute_command_with_return, execute_commands


# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logger = logging.getLogger('general-logger')


def generate_dockercompose(id, dockerfile_path, honeypot_port, mapped_port):
    '''
    Generates a docker-compose.yml file  from given information

    ARGUMENTS:
        id (string) : id of the honeypot
        dockerfile_path (string) : local path to the dockerfile
        log_path (string) : remote path of logs (in the honeypot)
        mapped_port (int) : available port we can map honeypot to
    '''

    # Create the docker-compose
    dockercompose = open(str(dockerfile_path) + "docker-compose.yml", "a")
    # Write the docker-compose version
    dockercompose.write('version: "3"\n')
    # Add the 'service' tag for honeypot service
    dockercompose.write('services:\n')
    # Add the honeypot service
    dockercompose.write('  honeypot:\n')
    # Configure container name
    dockercompose.write('    container_name: ' + str(id) + '\n')
    # Build options
    dockercompose.write('    build:\n')
    dockercompose.write('      context: .\n')
    dockercompose.write('      dockerfile: Dockerfile\n')
    # Map ports
    dockercompose.write('    ports:\n')
    dockercompose.write('      - \"' + str(mapped_port) +
                        ':' + str(honeypot_port) + "\"\n")
    # Change logging facility
    dockercompose.write('    logging:\n')
    dockercompose.write('      driver: syslog\n')
    dockercompose.write('      options:\n')
    dockercompose.write('        tag: ' + str(id) + '\n')
    # Close file
    dockercompose.close()
    logger.debug("[add_hp] Dockerfile successfully generated")


def deploy_container(dc_ip, dc_ssh_port, dc_ssh_key,
                     dockerfile_path, id_hp, logs):
    '''
    Install and deploy an Nginx Reverse-Proxy on a given server

    ARGUMENTS:
        ip_dc (string): ip of remote server
        dc_ssh_port (int) : port the ssh service listen
        dc_ssh_key (file-like object) : ssh key used to connect to server
        dockerfile_paht (string) : local path of the dockerfile
        id_hp (string) : id of the hp we are deploying

    Return True if succeed, False in the other case
    '''

    dockerfile_path = [dockerfile_path + "/Dockerfile",
                       dockerfile_path + "/docker-compose.yml"]
    # Declare local vars
    docker_dest = "/data/tmp/"
    command_exec_compose = ["cd " + str(docker_dest),
                            "docker-compose -f " + str(docker_dest) +
                            "/docker-compose.yml  --project-name " +
                            id_hp + " up -d"]
    # Copy docker files on datacenter, and execute docker-compose
    try:
        send_file_and_execute_commands(
            dc_ip, dc_ssh_port, dc_ssh_key, dockerfile_path,
            docker_dest, command_exec_compose)
    except Exception as e:
        error = "Container deployement failed : " + str(e)
        logger.error(error)
        raise ValueError(error)
    # Create symlinks between log files and /dev/stdout
    try:
        log_path_list = logs.split(",")
        commands = []
        for path in log_path_list:
            commands.append(
                f'docker exec {str(id_hp)} ln -sf /dev/stdout {str(path)}\n')
        execute_commands(dc_ip, dc_ssh_port, dc_ssh_key, commands)
    except Exception as e:
        error = "Symlinks creation failed : " + str(e)
        logger.error(error)
        raise ValueError(error)


def generate_datacenter_rsyslog_conf(
        orch_ip, orch_rsyslog_port, rulebase_path, id_hp,
        rsyslog_conf_datacenter_local_path):
    '''
    Generates Rsyslog configuration for datacenter-side

    ARGUMENTS:
        orch_ip (string) : Orchestrator's IP
        orch_rsyslog_port (int) : Port where rsyslog is listening
        rulebase_path (string) : intern path of the rulebase
        id_hp (string) : id of the honeypot we are configuring logging
        rsyslog_conf_datacenter_local_path (string) : intern path of rsyslog
            datacenter configuration
    '''

    try:
        # Create the configuration file
        rsyslog_conf_file = open(
            rsyslog_conf_datacenter_local_path + id_hp + ".conf", "a")
        # Monitor the log file of the honeypot
        rsyslog_conf_file.write(
            'if $programname == "' +
            str(id_hp) +
            '" then {\n')
        # Apply parsing rules
        rsyslog_conf_file.write(
            '  action(Type="mmnormalize" ruleBase="' +
            str(rulebase_path) +
            str(id_hp) +
            '.rb")\n')
        # If parsing operations succeeded
        rsyslog_conf_file.write('  if $parsesuccess == "OK" then {\n')
        # Send to orchestrator in parsed JSON format
        rsyslog_conf_file.write(
            '    action(Type="omfwd" Target="' +
            str(orch_ip) +
            '" Port="' +
            str(orch_rsyslog_port) +
            '" Protocol="tcp" Template="all-json-template")\n')
        # If parsing operations failed
        rsyslog_conf_file.write('  } else {\n')
        # Send to orchestrator in default JSON format
        rsyslog_conf_file.write(
            '    action(Type="omfwd" Target="' +
            str(orch_ip) +
            '" Port="' +
            str(orch_rsyslog_port) +
            '" Protocol="tcp" Template="default-template")\n')
        rsyslog_conf_file.write('  }\n')
        # Stop dealing with these logs
        rsyslog_conf_file.write('  stop\n')
        rsyslog_conf_file.write('}\n')
    except Exception as e:
        error = "Fail to create rsyslog configuration for datacenter : " + \
            str(e)
        logger.error(error)
        raise ValueError(error)


def generate_orchestrator_rsyslog_conf(
        id_hp, rsyslog_conf_orchestrator_local_path, local_hp_log_file_path):
    '''
    Generates Rsyslog configuration for orchestrator-side

    ARGUMENTS:
        id_hp (string) : id of the honyepot we are configuring logging
        rsyslog_conf_orchestrator_local_path (string) : Rsyslog
            configuration path
        local_hp_log_file_path (string) : Hp logs files path
    '''

    try:
        # Create the configuration file
        rsyslog_conf_file = open(
            rsyslog_conf_orchestrator_local_path + id_hp + ".conf", "a")
        # Filter the logs with honeypot tag
        rsyslog_conf_file.write(
            'if $msg contains "' +
            str(id_hp) +
            '" then {\n')
        # Dump the logs in local log file
        rsyslog_conf_file.write(
            'action(type="omfile" File="' +
            str(local_hp_log_file_path) +
            str(id_hp) +
            '.log" Template="RawFormat")\n')
        # Stop dealing with these logs
        rsyslog_conf_file.write('stop}\n')
    except Exception as e:
        error = "Fail to create rsyslog configuration for orchestrator : " + \
            str(e)
        logger.error(error)
        raise ValueError(error)


def generate_rulebase(id_hp, rules, rulebase_path):
    '''
    Generates the specific rulebase for honeypot

    ARGUMENTS:
        id_hp (string) : Id of the honeypot we are configuring
        rules (string) : Honeypot rsyslog rules
        rulebase_path (string) : Intern path to honeypot rulebase
    '''

    try:
        # Create the rulebase
        rulebase = open(rulebase_path + id_hp + ".rb", "a")
        # Specify the liblognorm version
        rulebase.write('version=2\n')
        # Write each rule in the rulebase
        for rule in rules.split(","):
            rulebase.write("rule=:" + str(rule) + '\n')
    except Exception as e:
        error = "Fail to create rulebase : " + str(e)
        logger.error(error)
        raise ValueError(error)


def deploy_rsyslog_conf(datacenter_settings,
                        orchestrateur_settings, id_hp, rules):
    '''
    Deploy remotely the rsyslog configuration

    ARGUMENTS:
        datacenter_settings (dict) : all authentication information to
            connect to datacenter
        orchestrateur_settinfs (dict) : all authentication information to
            connect to orchestrator
        id_hp (string) : Id of the honeypot we are configuring
        rules (string) : rsyslog rules
    '''

    # On effectue 2 connexions SSH
    dc_ssh_key_1 = datacenter_settings["ssh_key"]
    dc_ssh_key_2 = datacenter_settings["ssh_key"]

    # PATH ON ORCHESTRATOR
    # Configuration
    rsyslog_conf_datacenter_local_path = "/data/rsyslog/datacenter-configuration/"
    rsyslog_conf_orchestrator_local_path = "/etc/rsyslog.d/"
    # Log files
    local_hp_log_file_path = "/data/honeypot-log/"
    # Rulebase
    local_rulebase_path = "/data/rsyslog/rulebase/"

    # PATH ON DATACENTER
    # Configuration
    # remote_path = "/data/"+str(id_hp)+"/"
    rsyslog_conf_datacenter_remote_path = "/etc/rsyslog.d/"
    # Rulebase
    remote_rulebase_path = "/data/rsyslog/rulebase/"

    # SSH SCP ARGUMENTS
    exec_restart_rsyslog = ["service rsyslog restart"]

    # Check if required directories on orchestrator exists
    rsyslog_conf_datacenter_local_path_exists = os.path.exists(
        rsyslog_conf_datacenter_local_path)
    rsyslog_conf_orchestrator_local_path_exists = os.path.exists(
        rsyslog_conf_orchestrator_local_path)
    local_hp_log_file_path_exists = os.path.exists(local_hp_log_file_path)
    local_rulebase_path_exists = os.path.exists(remote_rulebase_path)
    if not(rsyslog_conf_datacenter_local_path_exists
           and rsyslog_conf_orchestrator_local_path_exists
           and local_hp_log_file_path_exists and local_rulebase_path_exists):
        error = "At least one directory on orchestrator is missing"
        logger.error(error)
        raise ValueError(error)

    # Check if required directories on datacenter exists
    rsyslog_conf_datacenter_remote_path_exists = execute_command_with_return(
        datacenter_settings["hostname"],
        datacenter_settings["ssh_port"],
        datacenter_settings["ssh_key"],
        f"[[ -d {rsyslog_conf_datacenter_remote_path} ]] && echo 'OK'")
    remote_rulebase_path_exists = execute_command_with_return(
        datacenter_settings["hostname"],
        datacenter_settings["ssh_port"],
        datacenter_settings["ssh_key"],
        f"[[ -d {remote_rulebase_path} ]] && echo 'OK'")
    if not(rsyslog_conf_datacenter_remote_path_exists == [
           'OK'] and remote_rulebase_path_exists == ['OK']):
        error = "At least one directory on datacenter is missing"
        logger.error(error)
        raise ValueError(error)

    # Generate configuration files and rulebase
    try:
        generate_rulebase(id_hp, rules, local_rulebase_path)
        generate_datacenter_rsyslog_conf(orchestrateur_settings["hostname"],
                                         orchestrateur_settings["syslog_port"],
                                         remote_rulebase_path, id_hp,
                                         rsyslog_conf_datacenter_local_path)
        generate_orchestrator_rsyslog_conf(
            id_hp, rsyslog_conf_orchestrator_local_path,
            local_hp_log_file_path
        )
    except Exception as e:
        error = "Fail to generate rsyslog configuration : " + str(e)
        logger.error(error)
        raise ValueError(error)
    # Send and apply datacenter rsyslog configuration to the datacenter
    try:
        # Send the rulebase
        send_file(datacenter_settings["hostname"],
                  datacenter_settings["ssh_port"],
                  dc_ssh_key_1,
                  [local_rulebase_path + id_hp + ".rb"],
                  remote_rulebase_path)
        # Send rsyslog configuration
        send_file_and_execute_commands(
            datacenter_settings["hostname"],
            datacenter_settings["ssh_port"], dc_ssh_key_2,
            [rsyslog_conf_datacenter_local_path + id_hp + ".conf"],
            rsyslog_conf_datacenter_remote_path, exec_restart_rsyslog
        )
    except Exception as e:
        error = "Fail to deploy rsyslog configuration : " + str(e)
        logger.error(error)
        raise ValueError(error)

    # Try to apply orchestrator rsyslog configuration
    try:
        subprocess.run(["systemctl", "restart", "rsyslog"])
    except Exception as e:
        error = "Fail to deploy rsyslog configuration : " + str(e)
        logger.error(error)
        raise ValueError(error)
