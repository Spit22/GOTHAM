import configparser

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


def weighting_nb_link(object_type, objects_infos):
    '''
    Add a weight corresponding to the number of links associated with each object

    ARGUMENTS:
        object_type (string) : type of the object ("hp" or "serv")
        objects_infos (list of dict) : list of potentials objects

    Return list of dict of object with additional weight based on the number of link using the object
    '''

    # Check object_type
    if (object_type != "hp" and object_type != "serv"):
        error = str(object_type) + " is uncorrect"
        logging.error(error)
        raise ValueError(error)

    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    # Retrieve the corresponding weight
    weight = int(config[object_type + '_weight']["nb_link"])

    # Apply weight for each object according to its number of links
    objects_infos = [{
        **object_infos,
        **{"weight": int(object_infos["weight"]) +
           (weight * int(len(object_infos["link_id"].split("||||||"))))
           }
    } if (
        object_infos["link_id"] != '' and not(object_infos["link_id"] is None)
        and object_infos["link_id"] != 'NULL'
    ) else object_infos for object_infos in objects_infos
    ]

    return objects_infos


def weighting_nb_port(servs_infos):
    '''
    Add a weight corresponding to the number of port used by each server

    ARGUMENTS:
        servs_infos (list of dict) : list of potentials server

    Return list of dict of serv with additional weight based on the number
    of port used
    '''

    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    # Retrieve the corresponding weight
    weight = int(config['serv_weight']["nb_port_used"])

    # Apply weight for each object according to its number of port used
    servs_infos = [{
        **serv_infos,
        **{"weight": int(serv_infos["weight"]) +
        (weight * int(len(serv_infos["lhs_port"].replace("||||||", "||||").split("||||"))))}
    } if (
        serv_infos["lhs_port"] != '' and not(serv_infos["lhs_port"] is None)
        and serv_infos["lhs_port"] != 'NULL'
    ) else serv_infos for serv_infos in servs_infos
    ]

    return servs_infos


def weighting_state(object_type, objects_infos):
    '''
    Add a weight corresponding to the state associated with each object

    ARGUMENTS:
        object_type (string) : type of the object ("hp" or "serv")
        objects_infos (list of dict) : list of potentials objects

    Return list of dict of object with additional weight based on the state
    '''

    # Check object_type
    if (object_type != "hp" and object_type != "serv"):
        error = str(object_type) + " is uncorrect"
        logging.error(error)
        raise ValueError(error)

    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    # Retrieve the corresponding weight
    weights = dict(config.items(object_type + '_weight'))

    # Apply weight for each object according to its state
    objects_infos = [{
        **object_infos,
        **{"weight": int(object_infos["weight"]) + int(weights[object_infos[object_type + "_state"].lower()])}
    } if (
        object_infos[object_type + "_state"].lower() in weights
    ) else {
        **object_infos,
        **{"weight": int(object_infos["weight"]) +
        int(max([int(i) for i in weights.values()]))}
    } for object_infos in objects_infos
    ]

    return objects_infos


def weighting_nb_useless_tags(object_type, objects_infos, tags):
    '''
    Add a weight corresponding to the number of useless tags associated
    with each object

    ARGUMENTS:
        object_type (string) : type of the object ("hp" or "serv")
        objects_infos (list of dict) : list of potentials objects
        tags (string) : list of desired tags separate by tag separator

    Return list of dict of object with additional weight based on the
    useless tag number
    '''

    # Check object_type
    if (object_type != "hp" and object_type != "serv"):
        error = str(object_type) + " is uncorrect"
        logging.error(error)
        raise ValueError(error)

    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    # Retrieve the corresponding weight
    weight = int(config[object_type + '_weight']["nb_useless_tag"])
    # Retrieve the port separator
    separator = config['tag']['separator']

    # Create list of tags
    tags_list = tags.lower().split(separator)

    # Apply weight for each object according to its number of useless tags
    objects_infos = [{
        **object_infos,
        **{"weight": int(object_infos["weight"]) +
           (weight * int(int(len(object_infos[object_type +
            "_tags"].lower().split('||'))) -
            int(len(set(object_infos[object_type +
                                     "_tags"
                                     ].lower().split('||')).intersection(tags_list))))
            )
           }
    } for object_infos in objects_infos]

    return objects_infos


def weighting_nb_free_port(servs_infos):
    '''
    Add a weight corresponding to the number of free port associated with 
    each server

    ARGUMENTS:
        servs_infos (list of dict) : list of potentials servs

    Return list of dict of server with additional weight based on the free
    port number
    '''

    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    # Retrieve the corresponding weight
    weight = int(config['serv_weight']["nb_free_port"])
    # Retrieve the port separator
    separator = config['port']['separator']

    # Apply weight for each server according to its number of free port for
    # the link
    servs_infos = [{
        **serv_infos,
        **{"weight": int(serv_infos["weight"]) +
           (weight * int(len(serv_infos["free_ports"].split(separator))))
           }
    } for serv_infos in servs_infos]

    return servs_infos


def weighting_duplicat(hps_infos):
    '''
    Add a weight if the honeypot is a duplicat

    ARGUMENTS:
        hps_infos (list of dict) : list of potentials honeypots

    Return list of dict of honeypot with additional weight if the honeypot
    is a duplicat
    '''

    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    # Retrieve the corresponding weight
    weight = int(config['hp_weight']["duplicat"])

    # Apply weight if the hp is a duplicat
    hps_infos = [{
        **hp_infos,
        **{"weight": (int(hp_infos["weight"]) +
           int(weight) if (
               int(hp_infos["hp_duplicat"]) != 0
               ) else int(hp_infos["weight"]))
           }
    } for hp_infos in hps_infos]

    return hps_infos


def weighting_time(object_type, objects_infos, column):
    '''
    Add a weight corresponding to the creation and modification timestamp
    associated with each object

    ARGUMENTS:
        object_type (string) : type of the object ("hp" or "serv")
        objects_infos (list of dict) : list of potentials objects
        column (string) : type of the timestamp ("created_at" or "updated_at")

    Return list of dict of object with additional weight based on the
    creation and modification timestamp
    '''

    # Check object_type
    if (object_type != "hp" and object_type != "serv"):
        error = str(object_type) + " is uncorrect"
        logging.error(error)
        raise ValueError(error)

    # Check column
    if (column != "created_at" and column != "updated_at"):
        error = str(object_type) + " is uncorrect"
        logging.error(error)
        raise ValueError(error)

    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    # Retrieve the corresponding weight
    weight = int(config[object_type + '_weight'][column])

    # List all timestamp of the objects according to the column
    timestamp_list = [float(
        object_infos[object_type + "_" + column].timestamp()
    ) for object_infos in objects_infos if (
        object_infos[object_type + '_' + column] != ''
        and not(object_infos[object_type + '_' + column] is None)
        and object_infos[object_type + '_' + column] != 'NULL'
        )
    ]
    # Get the max
    max_time = max(timestamp_list)
    # Get the min
    min_time = min(timestamp_list)

    # Apply weight for each object according to its creation or modification
    # timestamp
    if max_time > min_time:
        objects_infos = [{
            **object_infos,
            **{"weight": int(object_infos["weight"]) +
                round(float(weight) * (
                        float(object_infos[object_type + '_' + column].timestamp())
                        - min_time
                       ) / (max_time - min_time)
                      )
               }
        } if (object_infos[object_type + '_' + column] != ''
              and not(object_infos[object_type + '_' + column] is None)
              and object_infos[object_type + '_' + column] != 'NULL'
              ) else {
                  **object_infos,
                  **{"weight": int(object_infos["weight"]) +
                     round(float(weight) / 2)}
                  } for object_infos in objects_infos
        ]

    return objects_infos
