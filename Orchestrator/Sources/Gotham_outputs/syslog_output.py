import subprocess
import hashlib

#===Logging components===#
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
#=======================#

def create(new_syslog_output, hostname, syslog_port, protocol):
    '''
    Create a syslog output
    
    ARGUMENTS:
        new_syslog_output (string) : name of the new configuration file
        hostname (string) : hostname of the syslog server
        syslog_port (string) : port of the syslog server
        protocol (string) : protocol to use with the syslog server
    '''
    # Generate rsyslog configuration
    try:
        # Create the configuration file with the right name
        rsyslog_conf_file = open(f"/etc/rsyslog.d/{str(new_syslog_output)}", "a")
        # Monitor the log file of the honeypot
        rsyslog_conf_file.write('if $msg contains "hp-" then {\n')
        # Apply parsing rules
        rsyslog_conf_file.write(f'    action(Type="omfwd" Target="{str(hostname)}" Port="{str(syslog_port)}" Protocol="{str(protocol)}" Template="RawFormat")\n')
        # Close the if condition
        rsyslog_conf_file.write('}\n')
    except Exception as e:
        error = "Fail to generate syslog output configuration file"
        logging.error(error)
        raise ValueError(error)
    try:
        subprocess.run(["systemctl", "restart", "rsyslog"])
    except Exception as e:
        error = f"Fail to deploy syslog output configuration : {str(e)}"
        logging.error(error)
        raise ValueError(error)

def delete(obsolete_syslog_output):
    '''
    Delete obsolete syslog output
    An output is considered as obsolete if it exists but it is not required in the configuration anymore

    ARGUMENT:
        obsolete_syslog_output (string) : name of the configuration file of the obsolete syslog output
    '''
    os.remove(f"/etc/rsyslog.d/{str(obsolete_syslog_output)}")


def naming(name, hostname, port, protocol):
    '''
    Generate the name of syslog configuration files, based on its parameters

    ARGUMENTS:
        name (string) : name of the required configuration
        hostname (string) : hostname of the syslog server
        syslog_port (string) : port of the syslog server
        protocol (string) : protocol to use with the syslog server
    '''
    # Hash the parameters
    hash_obj = hashlib.sha1()
    hash_obj.update(str(name).encode() + str(hostname).encode() + str(port).encode() + str(protocol).encode())
    hash_name = hash_obj.hexdigest()
    # return the name containing the hash of parameters
    return(f"10-syslog_{str(hash_name)}.conf")