import subprocess

#===Logging components===#
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
#=======================#

def create(new_syslog_output, hostname, syslog_port, protocol):
    # Create a syslog output
    #
    # hostname (string) : hostname of syslog server
    # port (string) : port of syslog server

    # Get POST data on JSON format
    try:
        # Create the configuration file
        rsyslog_conf_file = open("/etc/rsyslog.d/" + str(new_syslog_output), "a")
        # Monitor the log file of the honeypot
        rsyslog_conf_file.write('if $msg contains "hp-" then {\n')
        # Apply parsing rules
        rsyslog_conf_file.write('action(Type="omfwd" Target="' + str(hostname) + '" Port="' + str(syslog_port) + '" Protocol="' + str(protocol) + '" Template="RawFormat")}\n')
    except Exception as e:
        error = "Fail to generate syslog output configuration file"
        logging.error(error)
        raise ValueError(error)
    try:
        subprocess.run(["systemctl", "restart", "rsyslog"])
    except Exception as e:
        error = "Fail to deploy syslog output configuration : " + str(e)
        logging.error(error)
        raise ValueError(error)

def delete(obsolete_syslog_output):
    # Delete a syslog output
    os.remove("/etc/rsyslog.d/" + str(obsolete_syslog_output))