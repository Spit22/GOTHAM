#===Logging components===#
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
#=======================#

def main(hostname, syslog_port):
    # Create a syslog output
    #
    # hostname (string) : hostname of syslog server
    # port (string) : port of syslog server

    # Get POST data on JSON format
    try:
        # Create the configuration file
        rsyslog_conf_file = open("/etc/rsyslog.d/10-syslog-" + str(hostname) + ".conf", "a")
        # Monitor the log file of the honeypot
        rsyslog_conf_file.write('if $msg contains "hp-" then {\n')
        # Apply parsing rules
        rsyslog_conf_file.write('action(Type="omfwd" Target="' + str(hostname) + '" Port="1514" Protocol="' + str(syslog_port) + '" Template="RawFormat")}\n')
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