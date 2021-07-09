from . import syslog_output

import subprocess
import configparser

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


def list_existing_outputs(type):
    '''
    List existing outputs based on created configuration files in /etc/rsyslog.d/

    ARGUMENTS:
        type(string): type of output
            - syslog
    '''
    included_extensions = ['conf']
    included_prefix = [f'10-{type}']
    existing_configuration = [
        f for f in os.listdir("/etc/rsyslog.d/") if any(
            f.startswith(pref) for pref in included_prefix) and any(
            f.endswith(ext) for ext in included_extensions)
        ]
    return existing_configuration


def syslog():
    '''
    Manage syslog outputs, based on orchestrator rsyslog configuration
    '''
    # List existing syslog outputs
    existing_configuration = list_existing_outputs('syslog')

    # Retrieve syslog output configuration from main config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    # If there is no configuration, delete all existing configuration
    if not(config.has_section('syslog')):
        for obsolete_syslog_output in existing_configuration:
            try:
                syslog_output.delete(obsolete_syslog_output)
                logging.debug(
                    f"Syslog output deleted : {obsolete_syslog_output}")
            except Exception:
                error = "Fail to create syslog output"
                raise ValueError(error)
        return True

    # List required syslog outputs
    configuration_required = []
    if not(config.items("syslog")):
        error = "Syslog outputs configuration is empty"
        logging.error(error)
        raise ValueError(error)
    for key, value in config.items("syslog"):
        value = value.split(';')
        hostname = value[0]
        syslog_port = value[1]
        protocol = value[2].lower()
        honeypot_list = value[3]
        server_list = value[4]
        configuration_required.append(
            syslog_output.naming(
                key,
                hostname,
                syslog_port,
                protocol,
                honeypot_list,
                server_list
            )
        )

    # Find new outputs and outputs to delete
    outputs_to_create = list(
        set(configuration_required) -
        set(existing_configuration))
    outputs_to_delete = list(
        set(existing_configuration) -
        set(configuration_required))

    # Create required outputs
    for new_syslog_output in outputs_to_create:
        try:
            syslog_output.create(
                new_syslog_output,
                hostname,
                syslog_port,
                protocol,
                honeypot_list,
                server_list
            )
            logging.debug(
                f"Syslog output created with following parameters : {protocol}@{hostname}:{syslog_port}")
        except Exception:
            error = "Fail to create syslog output"
            raise ValueError(error)

    # Delete obsolete outputs
    for obsolete_syslog_output in outputs_to_delete:
        try:
            syslog_output.delete(obsolete_syslog_output)
            logging.debug(
                f"Syslog output deleted : {obsolete_syslog_output}")
        except Exception:
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
