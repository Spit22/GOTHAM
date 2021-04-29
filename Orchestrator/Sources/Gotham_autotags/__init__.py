#===Import GOTHAM's libs===#
import Gotham_SSH_SCP

from . import autotags_functions

# Logging components
import os
import configparser
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')



def honeypot(hp_id):
    # Find tags automatically for honeypot
    #
    #
    # hp_id (string) : id of the honeypot
    #
    # Return tags list (string)

    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    separator = config['tag']['separator']

    try:
        trivy_tags=autotags_functions.autotag_by_trivy(hp_id)
    except ValueError as e:
        error = "Error while trying to execute ssh command for trivy check on hp (id: "+hp_id+") : " + str(e)
        logging.error(error)
        raise ValueError(error)

    try:
        docker_tags = autotags_functions.autotag_by_docker_top(hp_id)
    except ValueError as e:
        except ValueError as e:
        error = "Error while trying to execute ssh command for docker top on hp (id: "+hp_id+") : " + str(e)
        logging.error(error)
        raise ValueError(error)

    tags_list=list(set(trivy_tags+docker_tags))

    tags=separator.join(tags_list)

    return tags




def server(serv_id):
    # Find tags automatically for server
    #
    #
    # serv_id (string) : id of the server
    #
    # Return tags list (string)