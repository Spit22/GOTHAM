# -*- coding: utf-8 -*-

from Gotham_SSH_SCP import send_file_and_execute_commands, send_file
from Gotham_SSH_SCP import execute_command_with_return

# Logging components
import os
import subprocess
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logger = logging.getLogger('general-logger')


def generate_nginxConf(db_settings, link_id, dc_ip, honeypots, exposed_port):
    '''
    Generate the config file to include in nginx config for the redirection

    ARGUMENTS:
        link_id (string): id of the link we are configuring nginx for
        dc_ip (string): ip of FQDN of the remote datacenter
        honeypots (list): list of honeypots
        exposed_port (int): port to listen on the server
    '''

    # Initialise the creation of the new nginx config file
    nginxRedirectionPath = "/data/template/" + \
        str(link_id) + "-" + str(exposed_port) + ".conf"
    nginxRedirectionFile = open(nginxRedirectionPath, 'w')
    nginxRedirectionFile.write("upstream " + link_id + " {\n")
    nginxRedirectionFile.write("  hash $remote_addr;\n")
    # Adding each honeypot in upstream
    for honeypot in honeypots:
        # Get the corresponding mapped port for this honeypot
        honeypot_port = int(honeypot["hp_port"])
        nginxRedirectionFile.write("  # " + str(honeypot["hp_id"]) + "\n")
        nginxRedirectionFile.write(
            "  server " + str(dc_ip) + ":" + str(honeypot_port) + ";\n")
    # Closing upstream
    nginxRedirectionFile.write("}\n")
    # Configuring the redirection
    nginxRedirectionFile.write("server {\n")
    nginxRedirectionFile.write("  listen " + str(exposed_port) + ";\n")
    nginxRedirectionFile.write("  proxy_pass " + str(link_id) + ";\n")
    nginxRedirectionFile.write(
        "  access_log /var/log/nginx/" +
        str(link_id) +
        ".log combined;\n")
    nginxRedirectionFile.write("}\n")


def deploy_nginxConf(db_settings, link_id, servers):
    '''
    Deploy the nginx configuration on all servers chosen

    ARGUMENTS:
        link_id (string): id of the link we are configuring nginx for
        servers (dict): list of servers we want to deploy on associated
            with exposed ports
    '''

    # Initialize command and file
    checkAndReloadNginx_command = [
        "/usr/sbin/nginx -t && /usr/sbin/nginx -s reload"]
    linkConf_dest = "/etc/nginx/conf.d/links/"
    # Deploy new configuration on each servers
    for server in servers:
        if "choosed_port" not in server.keys() and "lhs_port" in server.keys():
            server["choosed_port"] = server["lhs_port"]

        linkConf_path = ["/data/template/" +
                         str(link_id) + "-" +
                         str(server["choosed_port"]) + ".conf"]
        # Deploy configuration on the server and Reload nginx if ok
        send_file_and_execute_commands(
            server["serv_ip"],
            server["serv_ssh_port"],
            server["serv_ssh_key"],
            linkConf_path,
            linkConf_dest,
            checkAndReloadNginx_command
        )


def generate_server_rsyslog_conf(
        orch_ip, orch_rsyslog_port, rulebase_path, id_lk,
        rsyslog_conf_server_local_path):
    '''
    Generates Rsyslog configuration for server-side

    ARGUMENTS:
        orch_ip (string) : Orchestrator's IP
        orch_rsyslog_port (int) : Port where rsyslog is listening
        rulebase_path (string) : intern path of the rulebase
        id_lk (string) : id of the link we are configuring logging
        rsyslog_conf_server_local_path (string) : intern path of rsyslog
            server configuration
    '''

    try:
        # Create the configuration file
        rsyslog_conf_file = open(
            rsyslog_conf_server_local_path + id_lk + ".conf", "a")
        # Monitor the log file of the link
        rsyslog_conf_file.write('input(Type="imfile" File="/var/log/nginx/' +
                                str(id_lk) + '.log" Tag="' +
                                str(id_lk) + '")\n')
        rsyslog_conf_file.write(
            'if $syslogtag contains "' +
            str(id_lk) +
            '" then {\n')
        # Send to orchestrator in parsed JSON format
        rsyslog_conf_file.write(
            '  action(Type="omfwd" Target="' +
            str(orch_ip) +
            '" Port="' +
            str(orch_rsyslog_port) +
            '" Protocol="tcp" Template="LongTagForwardFormat")\n')
        # Stop dealing with these logs
        rsyslog_conf_file.write('  stop\n')
        rsyslog_conf_file.write('}\n')
    except Exception as e:
        error = "Fail to create rsyslog configuration for link : " + \
            str(e)
        raise ValueError(error)


def generate_orchestrator_rsyslog_conf(
        id_lk, rsyslog_conf_orchestrator_local_path, local_lk_log_file_path):
    '''
    Generates Rsyslog configuration for orchestrator-side

    ARGUMENTS:
        id_lk (string) : id of the link we are configuring logging
        rsyslog_conf_orchestrator_local_path (string) : Rsyslog configuration
            path
        local_lk_log_file_path (string) : link logs files path
    '''

    try:
        # Create the configuration file
        rsyslog_conf_file = open(
            rsyslog_conf_orchestrator_local_path + id_lk + ".conf", "a")
        # Filter the logs with link tag
        rsyslog_conf_file.write(
            'if $syslogtag contains "' +
            str(id_lk) +
            '" then {\n'
        )
        # Dump the logs in local log file
        rsyslog_conf_file.write(
            'action(type="omfile" File="' +
            str(local_lk_log_file_path) +
            str(id_lk) +
            '.log" Template="RawFormat")\n'
        )
        # Stop dealing with these logs
        rsyslog_conf_file.write('stop}\n')
    except Exception as e:
        error = "Fail to create rsyslog configuration for orchestrator : " + \
            str(e)
        raise ValueError(error)


def deploy_rsyslog_conf(servers, orchestrateur_settings, id_lk):
    '''
    Deploy remotely the rsyslog configuration

    ARGUMENTS:
        servers (dict) : all authentication information to connect to servers
        orchestrateur_settings (dict) : all authentication information
            to connect to orchestrator
        id_lk (string) : Id of the link we are configuring
        rules (string) : rsyslog rules
    '''

    # PATH ON ORCHESTRATOR
    # Configuration
    rsyslog_conf_server_local_path = "/data/rsyslog/servers-configuration/"
    rsyslog_conf_orchestrator_local_path = "/etc/rsyslog.d/"
    # Log files
    local_lk_log_file_path = "/data/link-log/"

    # PATH ON SERVERS
    # Configuration
    # remote_path = "/data/"+str(id_hp)+"/"
    rsyslog_conf_server_remote_path = "/etc/rsyslog.d/"
    # Rulebase
    remote_rulebase_path = "/data/rsyslog/rulebase/"

    # SSH SCP ARGUMENTS
    exec_restart_rsyslog = ["service rsyslog restart"]

    # For each server on the link
    for server in servers:

        # Check if required directories on server exists
        rsyslog_conf_server_local_path_exists = os.path.exists(
            rsyslog_conf_server_local_path)
        rsyslog_conf_orchestrator_local_path_exists = os.path.exists(
            rsyslog_conf_orchestrator_local_path)
        local_lk_log_file_path_exists = os.path.exists(local_lk_log_file_path)
        if not (rsyslog_conf_server_local_path_exists and
                rsyslog_conf_orchestrator_local_path_exists and
                local_lk_log_file_path_exists):
            error = "At least one directory on orchestrator is missing"
            logger.error('[add_link] ' + error)
            raise ValueError(error)

        # Check if required directories on server exists
        rsyslog_conf_server_remote_path_exists = execute_command_with_return(
            server["serv_ip"],
            server["serv_ssh_port"],
            server["serv_ssh_key"],
            f"[[ -d {rsyslog_conf_server_remote_path} ]] && echo 'OK'")
        remote_rulebase_path_exists = execute_command_with_return(
            server["serv_ip"],
            server["serv_ssh_port"],
            server["serv_ssh_key"],
            f"[[ -d {remote_rulebase_path} ]] && echo 'OK'")
        if not (rsyslog_conf_server_remote_path_exists == [
                'OK'] and remote_rulebase_path_exists == ['OK']):
            error = "At least one directory on server is missing"
            logger.error('[add_link] ' + error)
            raise ValueError(error)

        # Generate configuration files and rulebase
        try:
            generate_server_rsyslog_conf(orchestrateur_settings["hostname"],
                                         orchestrateur_settings["syslog_port"],
                                         remote_rulebase_path, id_lk,
                                         rsyslog_conf_server_local_path)
            generate_orchestrator_rsyslog_conf(
                id_lk,
                rsyslog_conf_orchestrator_local_path,
                local_lk_log_file_path
            )
        except Exception as e:
            error = "Fail to generate rsyslog configuration : " + str(e)
            logger.error('[add_link] ' + error)
            raise ValueError(error)
        # Send and apply server rsyslog configuration to the server
        try:
            # Send rsyslog configuration
            send_file_and_execute_commands(
                server["serv_ip"],
                server["serv_ssh_port"],
                server["serv_ssh_key"],
                [rsyslog_conf_server_local_path + id_lk + ".conf"],
                rsyslog_conf_server_remote_path,
                exec_restart_rsyslog
            )
        except Exception as e:
            error = "Fail to deploy rsyslog configuration : " + str(e)
            logger.error('[add_link] ' + error)
            raise ValueError(error)

    # Try to apply orchestrator rsyslog configuration
    try:
        subprocess.run(["systemctl", "restart", "rsyslog"])
    except Exception as e:
        error = "Fail to deploy rsyslog configuration : " + str(e)
        logger.error('[add_link] ' + error)
        raise ValueError(error)
