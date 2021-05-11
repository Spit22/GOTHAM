#===Import GOTHAM's libs===#
from . import syslog_output
#==========================#

import os
import subprocess
import configparser

#===Logging components===#
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
#=======================#

def syslog():
    '''
    Manage syslog outputs
    '''
    # Retrieve syslog output configuration
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    if not(config.has_section('syslog')):
        return False
    
    # List existing syslog outputs
    included_extensions = ['conf']
    included_prefix = ['10-syslog']
    existing_configuration = [f for f in os.listdir("/etc/rsyslog.d/") if any(f.startswith(pref) for pref in included_prefix) and any(f.endswith(ext) for ext in included_extensions)]

    # List required syslog outputs
    configuration_required = []
    for key, value in config.items("syslog"):
        value = value.split(',')
        hostname = value[0]
        syslog_port = value[1]
        protocol = value[2]

        digit_list = hostname.split('.')
        name_of_host = digit_list[0] + "-" + digit_list[1] + "-" + digit_list[2] + "-" + digit_list[3]
        configuration_required.append("10-syslog_" + str(protocol) + "_" + str(name_of_host) + "_" + str(syslog_port) + ".conf")

    # Find new outputs and outputs to delete
    outputs_to_create = list(set(configuration_required) - set(existing_configuration))
    outputs_to_delete = list(set(existing_configuration) - set(configuration_required))
    print(outputs_to_create)
    print(outputs_to_delete)

    # Create required outputs
    for new_syslog_output in outputs_to_create:
        try:
            syslog_output.create(new_syslog_output, hostname, syslog_port, protocol)
            logging.debug(f"Syslog output created with following parameters : {protocol}@{hostname}:{syslog_port}")
        except Exception as e:
            error = "Fail to create syslog output"
            raise ValueError(error)
    
    # Delete obsolete outputs
    for obsolete_syslog_output in outputs_to_delete:
        try:
            syslog_output.delete(obsolete_syslog_output)
            logging.debug(f"Syslog output created with following parameters : {protocol}@{hostname}:{syslog_port}")
        except Exception as e:
            error = "Fail to create syslog output"
            raise ValueError(error)
    # Restart rsyslog
    try:
        subprocess.run(["systemctl", "restart", "rsyslog"])
    except Exception as e:
        error = "Fail to deploy syslog output : " + str(e)
        logging.error(error)
        raise ValueError(error)
    return True
