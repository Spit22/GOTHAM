# GENERAL LIBS
import logging
import flask
import json
import uuid
import base64
import os
import random
import requests
import configparser
import sys
from flask import request, jsonify

# GOTHAM'S Add Scripts
import add_server
import add_hp
import add_link

# GOTHAM's Remove Scripts
import rm_hp
import rm_server
import rm_link

# GOTHAM's Edit Scripts
import edit_hp
import edit_server
import edit_link

# GOTHAM'S LIB
import Gotham_link_BDD
import Gotham_check
import Gotham_choose
import Gotham_normalize
import Gotham_replace
import Gotham_state
import Gotham_error
import Gotham_autotags

# Create the flask application
app = flask.Flask(__name__)

#===Logging components===#
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
#=======================#


#===Retrieve settings from configuration file===#
# General settings
app.config["DEBUG"] = True
version = "0.1.0"
debug_mode = True

# Retrieve  internaldb settings from config file
config = configparser.ConfigParser()
config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')

# Bring database settings together
DB_settings = {
    "username": config['internaldb']['username'],
    "password": config['internaldb']['password'],
    "hostname": config['internaldb']['hostname'],
    "port": config['internaldb']['port'],
    "database": config['internaldb']['database']
}

# Bring datacenter port settings together
dc_ports_list = range(
    int(config['datacenter']['min_port']),
    int(config['datacenter']['max_port'])
)

# Retrieve datacenter settings from config file
dc_ip = config['datacenter']['ip']
dc_ssh_port = int(config['datacenter']['ssh_port'])
try:
    dc_ssh_key = config['datacenter']['ssh_key']
    dc_ssh_key = base64.b64decode(dc_ssh_key)  # ssh_key is byte
    dc_ssh_key = dc_ssh_key.decode('ascii')  # ssh_key is ascii string
    dc_ssh_key_rsyslog = dc_ssh_key  #  ssh_key for rsyslog
except Exception:
    print("Error loading datacenter's SSH key")
    sys.exit(1)

# Put datacenter settings in a dictionary
datacenter_settings = {
    "hostname": dc_ip,
    "ssh_key": dc_ssh_key,
    "rsyslog_ssh_key": dc_ssh_key_rsyslog,
    "ssh_port": dc_ssh_port
}

# Retrieve orchestrator settings from config file
orchestrator_ip = config["orchestrator"]["ip"]
orchestrator_rsyslog_port = config["orchestrator"]["syslog_port"]
# Put orchestrator settings in a dictionary
orchestrator_settings = {
    "hostname": orchestrator_ip,
    "syslog_port": orchestrator_rsyslog_port
}

# Retreive separators
ports_separator = config['port']['separator']
tags_separator = config['tag']['separator']

# Path to store object's data
store_path = "/data"
dockerfile_storage = "/data/"


@app.route('/', methods=['GET'])
def index():
    return """
  .o888P     Y8o8Y     Y888o.
 d88888      88888      88888b
d888888b_  _d88888b_  _d888888b
8888888888888888888888888888888
8888888888888888888888888888888
YJGS8P"Y888P"Y888P"Y888P"Y8888P
 Y888   '8'   Y8P   '8'   888Y
  '8o          V          o8'\n
                                GOTHAM's project\n
""", 200


@app.route('/add/honeypot', methods=['POST'])
def add_honeypot():
    '''
    Creates a honeypot object

    ARGUMENTS:
        name (string) : nom du honeypot
        descr (string) : description du honeypot
        tags (list) : liste des tags du honeypot
        logs (string) : path des logs à monitorer
        parser (string) : règle de parsing des logs monitorés
        dockerfile (string) : dockerfile to generate the honeypot
            on datacenter, base64 encoded
        service_port (int) : port on which the honeypot will lcoally listen
    '''

    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    # Retrieve State list
    state_list = config['state']['hp_state'].split(",")
    separator = config['tag']['separator']

    if len(state_list) < 4:
        error = """
        The config file needs 4 differents states for honeypot and server
        """
        logging.error(error)
        return Gotham_error.format_usererror(
            error,
            str(error),
            debug_mode
        ), 400

    # Get POST data on JSON format
    data = request.get_json()

    autotags = True if "autotags" in data and int(
        data["autotags"]) == 1 else False
    duplicat = 1 if "duplicat" in data and int(data["duplicat"]) == 1 else 0

    try:
        # Normalize infos
        hp_infos_received = {
            "name": data["name"],
            "descr": data["descr"],
            "tags": data["tags"],
            "logs": data["logs"],
            "parser": data["parser"],
            "port": data["port"],
            "duplicat": duplicat
        }
        hp_infos_received = Gotham_normalize.normalize_honeypot_infos(
            hp_infos_received
        )

        # Get all function's parameters
        name = hp_infos_received["name"]
        descr = hp_infos_received["descr"]
        tags = hp_infos_received["tags"]
        logs = hp_infos_received["logs"]
        parser = hp_infos_received["parser"]
        dockerfile = data["dockerfile"]
        dockerfile = base64.b64decode(dockerfile)
        dockerfile = dockerfile.decode('ascii')
        dockerfile = str(dockerfile)
        port = hp_infos_received["port"]
    except Exception as e:
        error = "Invalid POST data"
        return Gotham_error.format_usererror(error, str(e), debug_mode), 400

    # First find an available port to map on datacenter
    used_ports = Gotham_check.check_used_port(DB_settings)
    available_ports = [
        port for port in dc_ports_list
        if not(port in used_ports)
    ]

    if available_ports == []:
        error = "No ports available for mapping on datacenter"
        return Gotham_error.format_usererror(error, "", debug_mode), 500

    else:
        mapped_port = random.choice(available_ports)

    # Generate honeypot's id
    id = 'hp-' + str(uuid.uuid4().hex)

    # Write the dockerfile in the local storage
    dockerfile_path = str(dockerfile_storage) + str(id) + "/"

    if not os.path.isdir(dockerfile_path):
        os.mkdir(dockerfile_path)
        dockerfile_file = open(str(dockerfile_path) + "Dockerfile", 'a')
        dockerfile_file.write(dockerfile)
        dockerfile_file.close()

    else:
        error = "A dockerfile with same name already exists under " + \
            str(store_path)
        return Gotham_error.format_usererror(error, "", debug_mode), 500

    # Generate docker-compose.yml from information
    add_hp.generate_dockercompose(id, dockerfile_path, port, mapped_port)

    # Deploy the hp's container on datacenter
    try:
        add_hp.deploy_container(
            dc_ip,
            dc_ssh_port,
            dc_ssh_key,
            dockerfile_path,
            id,
            logs
        )
    except Exception as e:
        error = "SSH connection failed"
        return Gotham_error.format_usererror(error, str(e), debug_mode), 500

    # Create and deploy rsyslog configuration on the datacenter and the
    # orchestrator
    try:
        add_hp.deploy_rsyslog_conf(
            datacenter_settings,
            orchestrator_settings,
            id,
            parser
        )
    except Exception as e:
        error = "Rsyslog configuration failed for hp " + str(id)
        return Gotham_error.format_usererror(error, str(e), debug_mode), 500

    # Create tag automaticaly
    if autotags:
        autotags_list = Gotham_autotags.honeypot(id)
        tags = str(tags) + separator + autotags_list

    # Create hp_infos
    hp_infos = {
        'id': str(id),
        'name': str(name),
        'descr': str(descr),
        'tags': str(tags),
        'port_container': port,
        'parser': str(parser),
        'logs': str(logs),
        'source': str(dockerfile_path),
        'state': str(state_list[0]).upper(),
        'port': mapped_port,
        "duplicat": duplicat
    }

    # Normalize infos
    hp_infos = Gotham_normalize.normalize_honeypot_infos(hp_infos)

    # Store new hp and tags in the database
    Gotham_link_BDD.add_honeypot_DB(DB_settings, hp_infos)

    try:
        # Update state of honeypot
        Gotham_state.adapt_state(DB_settings, hp_infos["id"], "hp")
    except Exception as e:
        logging.error(
            "Error while configuring honeypot state : " + str(e))

    # If all operations succeed, return id of created object
    response = str({"id": str(id)}).replace("\'", "\"") + "\n"
    return response, 200


@app.route('/add/server', methods=['POST'])
def add_serv():
    '''
    Creates a server object

    ARGUMENTS:
        name (string) : nom du serveur
        descr (string) : description du serveur
        tags (list) : liste des tags du serveur
        ip (string) : adresse IP publique du serveur
        ssh_key (string) : clé SSH à utiliser pour la connexion
        ssh_port (int) : port d'écoute du service SSH
    '''

    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    # Retrieve State list
    state_list = config['state']['serv_state'].split(",")
    separator = config['tag']['separator']

    if len(state_list) < 4:
        error = """
        The config file needs 4 differents states for honeypot and server
        """
        logging.error(error)
        return Gotham_error.format_usererror(
            error, str(error), debug_mode), 400

    # Get POST data on JSON format
    data = request.get_json()

    autotags = True if "autotags" in data and int(
        data["autotags"]) == 1 else False

    # Get all function's parameters
    try:
        # Normalize infos
        serv_infos_received = {
            "name": data["name"],
            "descr": data["descr"],
            "tags": data["tags"],
            "ip": data["ip"],
            "ssh_port": data["ssh_port"]
        }
        serv_infos_received = Gotham_normalize.normalize_server_infos(
            serv_infos_received
        )
        # Get all function's parameters
        name = serv_infos_received["name"]
        descr = serv_infos_received["descr"]
        tags = serv_infos_received["tags"]
        ip = serv_infos_received["ip"]
        encoded_ssh_key = data["ssh_key"]
        # Decode and format the ssh key
        ssh_key = base64.b64decode(encoded_ssh_key)  # ssh_key is byte
        ssh_key = ssh_key.decode('ascii')  # ssh_key is ascii string
        check_ssh_key = ssh_key  # ssh_key for the check is a file-like object
        deploy_ssh_key = ssh_key  #  ssh_key for the deployment is a file-like object
        ssh_port = serv_infos_received["ssh_port"]

    except Exception as e:
        error = "Invalid POST data"
        return Gotham_error.format_usererror(error, str(e), debug_mode), 400

    # First check the ip not already exists in database
    exists = Gotham_check.check_doublon_server(DB_settings, ip)

    if exists:
        error = "Provided ip already exists in database"
        return Gotham_error.format_usererror(error, "", debug_mode), 403

    # Check given auth information are ok
    connected = Gotham_check.check_ssh(ip, ssh_port, check_ssh_key)

    if not connected:
        error = "Provided ssh_key of ssh_port is wrong"
        return Gotham_error.format_usererror(error, "", debug_mode), 400

    # If all checks are ok, we can generate an id for the new server
    id = 'sv-' + str(uuid.uuid4().hex)

    # Deploy the reverse-proxy service on the new server
    try:
        print("bypassed")
        # add_server.deploy(ip, ssh_port, deploy_ssh_key)

    except Exception as e:
        error = "Server deployment failed"
        return Gotham_error.format_usererror(error, str(e), debug_mode), 500

    # Create tag automaticaly
    if autotags:
        autotags_list = Gotham_autotags.server(
            DB_settings,
            serv_id=id,
            serv_ip=ip
        )
        tags = str(tags) + separator + autotags_list

    # Create serv_infos
    serv_infos = {
        'id': str(id),
        'name': str(name),
        'descr': str(descr),
        'tags': str(tags),
        'ip': str(ip),
        'ssh_key': str(ssh_key),
        'ssh_port': ssh_port,
        'state': str(state_list[0]).upper()
    }

    # Normalize infos
    serv_infos = Gotham_normalize.normalize_server_infos(serv_infos)

    # Store new server and tags in the internal database
    Gotham_link_BDD.add_server_DB(DB_settings, serv_infos)

    try:
        # Update state of server
        Gotham_state.adapt_state(DB_settings, serv_infos["id"], "serv")
    except Exception as e:
        logging.error(
            "Error while configuring server state : " + str(e))

    # If all operations succeed, return id of created object
    response = str({"id": str(id)}).replace("\'", "\"") + "\n"
    return response, 200


@app.route('/add/link', methods=['POST'])
def add_lk():
    '''
    Creates a link object

    ARGUMENTS:
        tags_serv (list) : tag du/des serveurs ciblés
        tags_hp (list) : tag du/des hp ciblés
        nb_serv (int) : nombre de serveurs ciblés
        nb_hp (int) : nombre de hp ciblés
        exposed_port (list): list des ports à utiliser
    '''

    # Get POST data on JSON format
    data = request.get_json()

    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    # Retrieve State list
    state_list_serv = config['state']['serv_state']
    state_list_hp = config['state']['hp_state']

    if len(state_list_serv) < 4 or len(state_list_hp) < 4:
        error = """
        The config file needs 4 differents states for honeypot and server
        """
        logging.error(error)
        return Gotham_error.format_usererror(
            error, str(error), debug_mode), 400

    # Get all function's parameters
    try:
        # Normalize infos
        lk_infos_received = {
            "tags_hp": data["tags_hp"],
            "tags_serv": data["tags_serv"],
            "ports": data["exposed_ports"]
        }

        if str(data["nb_hp"]).lower() != "all":
            lk_infos_received["nb_hp"] = data["nb_hp"]

        if str(data["nb_serv"]).lower() != "all":
            lk_infos_received["nb_serv"] = data["nb_serv"]

        lk_infos_received = Gotham_normalize.normalize_link_infos(
            lk_infos_received)

        # Get all function's parameters
        tags_serv = lk_infos_received["tags_serv"]
        tags_hp = lk_infos_received["tags_hp"]
        nb_serv = lk_infos_received["nb_serv"] if "nb_serv" in lk_infos_received.keys() else data["nb_serv"]
        nb_hp = lk_infos_received["nb_hp"] if "nb_hp" in lk_infos_received.keys() else data["nb_hp"]
        exposed_ports = lk_infos_received["ports"]
        exposed_ports_list = exposed_ports.split(ports_separator)

    except Exception as e:
        error = "Invalid POST data"
        return Gotham_error.format_usererror(error, str(e), debug_mode), 400

    # We check that no link exists with same tags, otherwise return error
    existingLinks = Gotham_check.check_tags(
        "link",
        Gotham_link_BDD.get_link_infos(
            DB_settings,
            tags_hp=tags_hp,
            tags_serv=tags_serv
        ),
        tags_hp=tags_hp,
        tags_serv=tags_serv,
        mode=True
    )

    if existingLinks != []:
        error = "A link is already configured for this tags"
        return Gotham_error.format_usererror(error, "", debug_mode), 403

    # We check all provided server tags exists, otherwise return error
    if tags_serv.lower() != "all":
        try:
            Gotham_check.check_doublon_tags(
                DB_settings, tags_serv, table="serv")
        except Exception as e:
            error = "Some server tags does not exist"
            return Gotham_error.format_usererror(
                error, str(e), debug_mode), 400

    # We check all provided hp tags exists, otherwise return error
    if tags_hp.lower() != "all":
        try:
            Gotham_check.check_doublon_tags(DB_settings, tags_hp, table="hp")

        except Exception as e:
            error = "Some honeypot tags does not exist"
            return Gotham_error.format_usererror(
                error, str(e), debug_mode), 400

    # Get all honeypots corresponding to tags
    honeypots = Gotham_link_BDD.get_honeypot_infos(DB_settings, tags=tags_hp)

    if tags_hp.lower() != "all":
        # update state
        try:
            honeypots = [Gotham_state.adapt_state(
                DB_settings,
                honeypot["hp_id"],
                "hp"
            ) for honeypot in honeypots]
        except Exception as e:
            logging.error(
                "Error while configuring honeypot state : " + str(e))
        honeypots = Gotham_check.check_tags(
            "hp",
            honeypots,
            tags_hp=tags_hp
        )

    # Get all servers corresponding to tags
    servers = Gotham_link_BDD.get_server_infos(DB_settings, tags=tags_serv)

    if tags_serv.lower() != "all":
        # update state
        try:
            servers = [Gotham_state.adapt_state(
                DB_settings,
                server["serv_id"],
                "serv"
            ) for server in servers]
        except Exception as e:
            logging.error(
                "Error while configuring server state : " + str(e))
        servers = Gotham_check.check_tags(
            "serv",
            servers,
            tags_serv=tags_serv
        )

    # Filter servers in those who have one of ports open
    servers = Gotham_check.check_servers_ports_matching(servers, exposed_ports)

    # Filter servers in error or down
    servers = [
        server for server in servers if (
            server["serv_state"] != str(
                state_list_serv[2]).upper() and server["serv_state"] != str(
                state_list_serv[3]).upper()
        )
    ]

    # Filter honeypots in error or down
    honeypots = [
        honeypot for honeypot in honeypots
        if (honeypot["hp_state"] != str(state_list_hp[2]).upper()
            and honeypot["hp_state"] != str(state_list_hp[3]).upper())
    ]

    if str(nb_serv).lower() == "all":
        nb_serv = len(servers)

    if str(nb_hp).lower() == "all":
        nb_hp = len(honeypots)

    #  Checking we have enough servers for the nb_serv directive, otherwise
    # return error
    if len(servers) < nb_serv:
        error = "Can't deploy link on " + \
            str(nb_serv) + " servers while there is only " + \
            str(len(servers)) + " servers available"
        return Gotham_error.format_usererror(error, "", debug_mode), 400

    # If we don't have any honeypots corresponding, just return error,
    if len(honeypots) < 1:
        error = """
        Can't configure link if there is no at least one hp corresponding to request
        """
        return Gotham_error.format_usererror(error, "", debug_mode), 400

    # Choose best honeypots (the lower scored)
    honeypots = Gotham_choose.choose_honeypots(honeypots, nb_hp, tags_hp)

    # Checking we have enough honeypots for the nb_hp directive
    if len(honeypots) < nb_hp:
        added_hp = []

        for i in range(nb_hp - len(honeypots)):

            with open(honeypots[i % len(honeypots)]["hp_source"] + "/Dockerfile", 'r') as file:
                encoded_dockerfile = base64.b64encode(
                    file.read().encode("ascii"))

            name = (honeypots[i % len(honeypots)]["hp_name"] +
                    "_Duplicat" if len(honeypots[i % len(honeypots)]["hp_name"] + "_Duplicat")
                    <= 128 else honeypots[i % len(honeypots)]["hp_name"][:(128 - len("_Duplicat"))] + "_Duplicat")
            descr = "Duplication of " + \
                honeypots[i % len(honeypots)]["hp_descr"]

            duplicate_hp_infos = {
                "name": str(name),
                "descr": str(descr),
                "tags": str(honeypots[i % len(honeypots)]["hp_tags"].replace("||", tags_separator)),
                "logs": str(honeypots[i % len(honeypots)]["hp_logs"]),
                "parser": str(honeypots[i % len(honeypots)]["hp_parser"]),
                "port": int(honeypots[i % len(honeypots)]["hp_port_container"]),
                "dockerfile": str(encoded_dockerfile.decode("utf-8")),
                "duplicat": 1
            }
            try:
                jsondata = json.dumps(duplicate_hp_infos)
                url = "http://localhost:5000/add/honeypot"
                headers = {'Content-type': 'application/json'}
                r = requests.post(url, data=jsondata, headers=headers)
                jsonresponse = r.json()
                id_hp = jsonresponse["id"]
                added_hp.append(id_hp)
            except Exception as e:
                error = "Hp duplication failed"
                return Gotham_error.format_usererror(
                    error, str(e), debug_mode), 500

        for id in added_hp:
            honeypots.append(
                Gotham_link_BDD.get_honeypot_infos(DB_settings, id=id)[0])

    # Choose best servers (the lower scored)
    servers = Gotham_choose.choose_servers(servers, nb_serv, tags_serv)

    count_exposed_ports = {str(port): 0 for port in exposed_ports_list}

    # Associate servers and an port of exposition
    for i in range(len(servers)):
        serv_i_free_ports = servers[i]["free_ports"].split(ports_separator)
        servs_free_ports = (ports_separator.join(
            [serv["free_ports"] for serv in servers if serv["serv_id"] != servers[i]["serv_id"]])).split(ports_separator)
        port_available_only_for_this_server = list(
            set(serv_i_free_ports).difference(servs_free_ports))

        if len(servers[i]["free_ports"].split(ports_separator)) == 1:
            servers[i]["choosed_port"] = int(servers[i]["free_ports"])
            count_exposed_ports[str(servers[i]["choosed_port"])] += 1

        elif port_available_only_for_this_server != []:
            free_ports_available_only_for_this_server_with_weight = {
                key: value for key, value in count_exposed_ports.items() if key in port_available_only_for_this_server}
            servers[i]["choosed_port"] = int(min(
                free_ports_available_only_for_this_server_with_weight, key=free_ports_available_only_for_this_server_with_weight.get))
            count_exposed_ports[str(servers[i]["choosed_port"])] += 1

    for i in range(len(servers)):
        if not("choosed_port" in servers[i].keys()):
            free_ports_for_serv_with_weight = {
                port: count_exposed_ports[port] for port in servers[i]["free_ports"].split(ports_separator)}
            servers[i]["choosed_port"] = int(
                min(free_ports_for_serv_with_weight, key=free_ports_for_serv_with_weight.get))
            count_exposed_ports[str(servers[i]["choosed_port"])] += 1

    final_exposed_ports = list(filter(None, dict.fromkeys(
        [server["choosed_port"] for server in servers])))

    # Create link id
    id = 'lk-' + str(uuid.uuid4().hex)

    # Generate NGINX configurations for each redirection on a specific
    # exposed_port
    for exposed_port in exposed_ports_list:
        add_link.generate_nginxConf(
            DB_settings,
            id,
            dc_ip,
            honeypots,
            exposed_port
        )

    # Deploy new reverse-proxies's configurations on servers
    add_link.deploy_nginxConf(
        DB_settings,
        id,
        servers
    )

    # Create and deploy rsyslog configuration on servers and the orchestrator
    try:
        # print("bypassed")
        add_link.deploy_rsyslog_conf(
            servers, orchestrator_settings, id)
    except Exception as e:
        error = "Rsyslog configuration failed for link " + str(id)
        return Gotham_error.format_usererror(error, str(e), debug_mode), 500

    # Check redirection is effective on all servers
    for server in servers:
        connected = Gotham_check.check_server_redirects(
            server["serv_ip"], server["choosed_port"])

        if not connected:
            error = "Link seems to not beeing effective on server " + \
                str(server["serv_ip"])
            return Gotham_error.format_usererror(error, "", debug_mode), 500

    # Create lk_infos
    lk_infos = {
        "id": id,
        "nb_hp": nb_hp,
        "nb_serv": nb_serv,
        "tags_hp": tags_hp,
        "tags_serv": tags_serv,
        "ports": exposed_ports
    }

    # Normalize infos
    lk_infos = Gotham_normalize.normalize_link_infos(lk_infos)

    # Store new link and tags in the internal database
    Gotham_link_BDD.add_link_DB(DB_settings, lk_infos)

    # Insert data in Link_Hp_Serv
    for server in servers:
        for honeypot in honeypots:
            # Create lhs_infos
            lhs_infos = {
                "id_link": lk_infos["id"],
                "id_hp": honeypot["hp_id"],
                "id_serv": server["serv_id"],
                "port": server["choosed_port"]
            }
            # Normalize infos
            lhs_infos = Gotham_normalize.normalize_lhs_infos(lhs_infos)
            # Store new link and tags in the internal database
            Gotham_link_BDD.add_lhs_DB(DB_settings, lhs_infos)

            try:
                # Update state of honeypot
                Gotham_state.adapt_state(
                    DB_settings,
                    honeypot["hp_id"],
                    "hp"
                )
            except Exception as e:
                logging.error(
                    "Error while configuring honeypot state : " + str(e))

        try:
            # Update state of server
            Gotham_state.adapt_state(DB_settings, server["serv_id"], "serv")
        except Exception as e:
            logging.error(
                "Error while configuring server state : " + str(e))

    # If all operations succeed, return id of created object
    response = str({"id": str(id)}).replace("\'", "\"") + "\n"
    return response, 200


@app.route('/edit/honeypot', methods=['POST'])
def edit_honeypot():
    '''
    Edits a honeypot object

    ARGUMENTS:
        id (string) : id du honeypot à modifier
        name (string) : nom du honeypot
        descr (string) : description du honeypot
        tags (list) : liste des tags du honeypot
        logs (string) : path des logs à monitorer
        parser (string) : règle de parsing des logs monitorés
        service_port (int) : port on which the honeypot will lcoally listen
    '''

    # Get POST data on JSON format
    data = request.get_json()

    hp_infos_received = {}
    try:
        # Get all function's parameters
        if "id" in data.keys():
            hp_infos_received["id"] = data["id"]

        else:
            error = "Honeypot id missing"
            return Gotham_error.format_usererror(error, "", debug_mode), 400

        if "name" in data.keys():
            hp_infos_received["name"] = data["name"]

        if "descr" in data.keys():
            hp_infos_received["descr"] = data["descr"]

        if "tags" in data.keys():
            hp_infos_received["tags"] = data["tags"]

        if "logs" in data.keys():
            hp_infos_received["logs"] = data["logs"]

        if "parser" in data.keys():
            hp_infos_received["parser"] = data["parser"]

        if "port" in data.keys():
            hp_infos_received["port"] = data["port"]

        # Normalize infos
        hp_infos_received = Gotham_normalize.normalize_honeypot_infos(
            hp_infos_received)

    except Exception as e:
        error = "Invalid POST data"
        return Gotham_error.format_usererror(error, str(e), debug_mode), 400

    # Check if the honyepot exists in the IDB
    honeypots = Gotham_link_BDD.get_honeypot_infos(
        DB_settings, id=hp_infos_received["id"])

    if honeypots == []:
        logging.error(
            f"You tried to edit a honeypot that doesn't exists with the id = {hp_infos_received['id']}")
        error = "Unknown hp id" + hp_infos_received["id"]
        return Gotham_error.format_usererror(error, "", debug_mode), 400

    honeypot = honeypots[0]
    modifs = {}
    conditions = {"id": honeypot["hp_id"]}

    if "name" in hp_infos_received.keys():
        if hp_infos_received["name"] != honeypot["hp_name"]:
            modifs["name"] = hp_infos_received["name"]

    if "descr" in hp_infos_received.keys():
        if hp_infos_received["descr"] != honeypot["hp_descr"]:
            modifs["descr"] = hp_infos_received["descr"]

    if "tags" in hp_infos_received.keys():
        if set(hp_infos_received["tags"].split(tags_separator)) != set(
                honeypot["hp_tags"].split("||")):
            succes = True
            if honeypot['link_id'] is not None and honeypot['link_id'] != "NULL":
                succes = False
                try:
                    succes = edit_hp.edit_tags(
                        DB_settings,
                        datacenter_settings,
                        honeypot,
                        hp_infos_received["tags"]
                    )

                except Exception as e:
                    succes = False
                    debug_information = e
            if succes:
                modifs["tags"] = hp_infos_received["tags"]

            else:
                error = "Tag edition failed"
                return Gotham_error.format_usererror(
                    error,
                    str(debug_information),
                    debug_mode
                ), 500

    if "logs" in hp_infos_received.keys():
        if hp_infos_received["logs"] != honeypot["hp_logs"]:
            error = "Log parameters edition not implemented"
            return Gotham_error.format_usererror(error, "", debug_mode), 501
            modifs["logs"] = hp_infos_received["logs"]

    if "parser" in hp_infos_received.keys():
        if hp_infos_received["parser"] != honeypot["hp_parser"]:
            error = "Parser parameters edition not implemented"
            return Gotham_error.format_usererror(error, "", debug_mode), 501
            modifs["parser"] = hp_infos_received["parser"]

    if "port" in hp_infos_received.keys():
        if hp_infos_received["port"] != honeypot["hp_port"]:
            error = "Port parameters edition not implemented"
            return Gotham_error.format_usererror(error, "", debug_mode), 501
            modifs["port"] = hp_infos_received["port"]

    if modifs != {}:
        Gotham_link_BDD.edit_honeypot_DB(DB_settings, modifs, conditions)

        try:
            # Update state of honeypot
            honeypot = Gotham_state.adapt_state(
                DB_settings, hp_infos_received["id"], "hp")
        except Exception as e:
            logging.error(
                "Error while configuring honeypot state : " + str(e))
            honeypot = Gotham_link_BDD.get_honeypot_infos(
                DB_settings, id=hp_infos_received["id"])[0]

        honeypot = Gotham_normalize.normalize_display_object_infos_with_tags(Gotham_normalize.normalize_display_object_infos(
            honeypot, "hp"), "hp")

        return honeypot, 200

    return "{\"message\": \"Nothing to change\"}\n", 200


@app.route('/edit/server', methods=['POST'])
def edit_serv():
    '''
    Edits a server object

    ARGUMENTS:
        id (string) : id du serveur à modifier
        name (string) : nom du serveur
        descr (string) : description du serveur
        tags (list) : liste des tags du serveur
        ip (string) : adresse IP publique du serveur
        ssh_key (string) : clé SSH à utiliser pour la connexion
        ssh_port (int) : port d'écoute du service SSH
    '''

    # Get POST data on JSON format
    data = request.get_json()

    serv_infos_received = {}

    try:
        # Get all function's parameters
        if "id" in data.keys():
            serv_infos_received["id"] = data["id"]

        else:
            error = "Server id not specified"
            return Gotham_error.format_usererror(error, "", debug_mode), 400

        if "name" in data.keys():
            serv_infos_received["name"] = data["name"]

        if "descr" in data.keys():
            serv_infos_received["descr"] = data["descr"]

        if "tags" in data.keys():
            serv_infos_received["tags"] = data["tags"]

        if "ip" in data.keys():
            serv_infos_received["ip"] = data["ip"]

        if "ssh_key" in data.keys():
            serv_infos_received["ssh_key"] = data["ssh_key"]

        if "ssh_port" in data.keys():
            serv_infos_received["ssh_port"] = data["ssh_port"]

        # Normalize infos
        serv_infos_received = Gotham_normalize.normalize_server_infos(
            serv_infos_received)

    except Exception as e:
        error = "Invalid POST data"
        return Gotham_error.format_usererror(error, str(e), debug_mode), 400

    # Check if the server exists in the IDB
    servers = Gotham_link_BDD.get_server_infos(
        DB_settings, id=serv_infos_received["id"])

    if servers == []:
        logging.error(
            f"You tried to edit a server that doesn't exists with the id = {serv_infos_received['id']}")
        error = "Unknown id " + serv_infos_received["id"]
        return Gotham_error.format_usererror(error, "", debug_mode), 400

    server = servers[0]
    modifs = {}
    conditions = {"id": server["serv_id"]}

    if "name" in serv_infos_received.keys():
        if serv_infos_received["name"] != server["serv_name"]:
            modifs["name"] = serv_infos_received["name"]

    if "descr" in serv_infos_received.keys():
        if serv_infos_received["descr"] != server["serv_descr"]:
            modifs["descr"] = serv_infos_received["descr"]

    if "tags" in serv_infos_received.keys():
        if set(serv_infos_received["tags"].split(tags_separator)) != set(
                server["serv_tags"].split("||")):
            succes = True
            if server['link_id'] is not None and server['link_id'] != "NULL":
                try:
                    succes = edit_server.edit_tags(
                        DB_settings, datacenter_settings, server, serv_infos_received["tags"])
                except Exception as e:
                    succes = False
                    debug_information = e
            if succes:
                modifs["tags"] = serv_infos_received["tags"]

            else:
                error = "Tag edition failed"
                return Gotham_error.format_usererror(
                    error, str(debug_information), debug_mode), 500

    if "ip" in serv_infos_received.keys() or "ssh_key" in serv_infos_received.keys(
    ) or "ssh_port" in serv_infos_received.keys():
        ip = server["serv_ip"]
        ssh_port = server["serv_ssh_port"]
        ssh_key = server["serv_ssh_key"]
        # Decode and format the ssh key
        # ssh_key = base64.b64decode(ssh_key) # ssh_key is byte
        # ssh_key = ssh_key.decode('ascii') # ssh_key is ascii string

        if "ip" in serv_infos_received.keys():
            if serv_infos_received["ip"] != server["serv_ip"]:
                modifs["ip"] = serv_infos_received["ip"]
                ip = serv_infos_received["ip"]

        if "ssh_key" in serv_infos_received.keys():
            if serv_infos_received["ssh_key"] != server["serv_ssh_key"]:
                modifs["ssh_key"] = serv_infos_received["ssh_key"]
                ssh_key = serv_infos_received["ssh_key"]
                # Decode and format the ssh key
                ssh_key = base64.b64decode(ssh_key)  # ssh_key is byte
                ssh_key = ssh_key.decode('ascii')  # ssh_key is ascii string

        if "ssh_port" in serv_infos_received.keys():
            if serv_infos_received["ssh_port"] != server["serv_ssh_port"]:
                modifs["ssh_port"] = serv_infos_received["ssh_port"]
                ssh_port = serv_infos_received["ssh_port"]
        try:
            edit_server.check_edited_connection(
                DB_settings, server, ip, ssh_port, ssh_key)

        except Exception as e:
            error = "Connexion edition failed"
            return Gotham_error.format_usererror(
                error, str(e), debug_mode), 500

    if modifs != {}:
        Gotham_link_BDD.edit_server_DB(DB_settings, modifs, conditions)

        try:
            # Update state of server
            server = Gotham_state.adapt_state(
                DB_settings, serv_infos_received["id"], "serv")
        except Exception as e:
            logging.error(
                "Error while configuring server state : " + str(e))
            server = Gotham_link_BDD.get_server_infos(
                DB_settings, id=serv_infos_received["id"])[0]

        server = Gotham_normalize.normalize_display_object_infos_with_tags(
            Gotham_normalize.normalize_display_object_infos(
                server,
                "serv"
            ),
            "serv"
        )
        return server, 200

    return "{\"message\": \"Nothing to change\"}\n", 200


@app.route('/edit/link', methods=['POST'])
def edit_lk():
    '''
    Edits a link object

    ARGUMENTS:
        id (string) : id du lien à modifier
        tags_serv (list) : tag du/des serveurs ciblés
        tags_hp (list) : tag du/des hp ciblés
        nb_serv (int) : nombre de serveurs ciblés
        nb_hp (int) : nombre de hp ciblés
        ports (string) : exposed ports
    '''

    # Get POST data on JSON format
    data = request.get_json()

    link_infos_received = {}
    all_error = ""

    try:
        # Get all function's parameters
        if "id" in data.keys():
            link_infos_received["id"] = data["id"]

        else:
            error = "Link id not specified"
            return Gotham_error.format_usererror(error, "", debug_mode), 400

        if "tags_serv" in data.keys():
            link_infos_received["tags_serv"] = data["tags_serv"]

        if "tags_hp" in data.keys():
            link_infos_received["tags_hp"] = data["tags_hp"]

        if "nb_serv" in data.keys():
            link_infos_received["nb_serv"] = data["nb_serv"]

        if "nb_hp" in data.keys():
            link_infos_received["nb_hp"] = data["nb_hp"]

        if "ports" in data.keys():
            link_infos_received["ports"] = data["ports"]

        # Normalize infos
        link_infos_received = Gotham_normalize.normalize_link_infos(
            link_infos_received)

    except Exception as e:
        error = "Invalid POST data"
        return Gotham_error.format_usererror(error, str(e), debug_mode), 400

    # Check if the link exists in the IDB
    links = Gotham_link_BDD.get_link_infos(
        DB_settings, id=link_infos_received["id"])

    if links == []:
        logging.error(
            f"You tried to edit a link that doesn't exists with the id = {id}")
        error = "Unknown id " + link_infos_received["id"]
        return Gotham_error.format_usererror(error, "", debug_mode), 400

    link = links[0]

    links = Gotham_link_BDD.get_link_hp_serv_infos(
        DB_settings, id=link_infos_received["id"])
    link_hp_serv = links[0]

    links = Gotham_link_BDD.get_link_serv_hp_infos(
        DB_settings, id=link_infos_received["id"])
    link_serv_hp = links[0]

    modifications = False
    modifs = {}
    conditions = {"id": link["link_id"]}

    if "tags_serv" in link_infos_received.keys():
        if set(link_infos_received["tags_serv"].split(tags_separator)) != set(
                link["link_tags_serv"].split("||")):

            if link_infos_received["tags_serv"].lower() != "all":
                #  We check all provided server tags exists, otherwise return
                # error
                try:
                    Gotham_check.check_doublon_tags(
                        DB_settings, link_infos_received["tags_serv"], table="serv")
                except Exception as e:
                    error = "Some server tags does not exist"
                    return Gotham_error.format_usererror(
                        error, str(e), debug_mode), 400
                try:
                    result = edit_link.edit_tags(
                        DB_settings,
                        datacenter_settings,
                        link_serv_hp,
                        link_infos_received["tags_serv"],
                        "serv"
                    )
                except Exception as e:
                    error = "Tag server edition failed"
                    return Gotham_error.format_usererror(
                        error, str(e), debug_mode), 500
            if result:
                modifs["tags_serv"] = link_infos_received["tags_serv"]
            else:
                error = "Tag server edition failed, some links cannot be decremented"
                return Gotham_error.format_usererror(
                    error, str(""), debug_mode), 500

    # Update database in memory
    if modifs != {}:
        Gotham_link_BDD.edit_link_DB(DB_settings, modifs, conditions)
        links = Gotham_link_BDD.get_link_infos(
            DB_settings, id=link_infos_received["id"])
        link = Gotham_normalize.normalize_display_object_infos(
            links[0], "link")
        # Triage of links
        link_hp_serv = Gotham_link_BDD.get_link_hp_serv_infos(
            DB_settings, id=link_infos_received["id"])[0]
        link_serv_hp = Gotham_link_BDD.get_link_serv_hp_infos(
            DB_settings, id=link_infos_received["id"])[0]

        modifications = True

    # Clean modifs dict before editing nb_hp
    modifs = {}

    if "tags_hp" in link_infos_received.keys():
        if set(link_infos_received["tags_hp"].split(tags_separator)) != set(
                link["link_tags_hp"].split("||")):

            if link_infos_received["tags_hp"].lower() != "all":
                # We check all provided hp tags exists, otherwise return error
                try:
                    Gotham_check.check_doublon_tags(
                        DB_settings, link_infos_received["tags_hp"], table="hp")
                except Exception as e:
                    error = "Some honeypot tags does not exist"
                    return Gotham_error.format_usererror(
                        error, str(e), debug_mode), 400
                try:
                    result = edit_link.edit_tags(
                        DB_settings,
                        datacenter_settings,
                        link_hp_serv,
                        link_infos_received["tags_hp"],
                        "hp"
                    )
                except Exception as e:
                    error = "Tag honeypot edition failed"
                    return Gotham_error.format_usererror(
                        error, str(e), debug_mode), 500
            if result:
                modifs["tags_hp"] = link_infos_received["tags_hp"]
            else:
                error = "Tag honeypot edition failed, some links cannot be decremented"
                return Gotham_error.format_usererror(
                    error, str(""), debug_mode), 500

    # Update database
    if modifs != {}:
        Gotham_link_BDD.edit_link_DB(DB_settings, modifs, conditions)
        links = Gotham_link_BDD.get_link_infos(
            DB_settings, id=link_infos_received["id"])
        link = Gotham_normalize.normalize_display_object_infos(
            links[0], "link")
        # Triage of links
        link_hp_serv = Gotham_link_BDD.get_link_hp_serv_infos(
            DB_settings, id=link_infos_received["id"])[0]
        link_serv_hp = Gotham_link_BDD.get_link_serv_hp_infos(
            DB_settings, id=link_infos_received["id"])[0]

        modifications = True

    # Clean modifs dict before editing nb_hp
    modifs = {}

    if "ports" in link_infos_received.keys():
        if link_infos_received["ports"] != link["link_ports"]:
            try:
                edit_link.edit_ports(
                    DB_settings,
                    datacenter_settings,
                    link_serv_hp,
                    link_infos_received["ports"]
                )
            except Exception as e:
                error = "Port edition failed"
                return Gotham_error.format_usererror(
                    error, str(e), debug_mode), 500
            modifs["ports"] = link_infos_received["ports"]

            # Update link before edit nb_serv and nb_hp (Edit tags can decrease
            # nb_serv and nb_hp)
            if modifs != {}:
                Gotham_link_BDD.edit_link_DB(DB_settings, modifs, conditions)
                links = Gotham_link_BDD.get_link_infos(
                    DB_settings, id=link_infos_received["id"])
                link = Gotham_normalize.normalize_display_object_infos(
                    links[0], "link")
                modifications = True

            modifs = {}

            # Just redistrib ports
            try:
                Gotham_replace.distrib_servers_on_link_ports(DB_settings, link)
            except Exception as e:
                error = "Port redistribution failed"
                return Gotham_error.format_usererror(
                    error, str(e), debug_mode), 500

    # Update link before edit nb_serv and nb_hp (Edit tags can decrease
    # nb_serv and nb_hp)
    links = Gotham_link_BDD.get_link_infos(
        DB_settings, id=link_infos_received["id"])
    link = Gotham_normalize.normalize_display_object_infos(links[0], "link")

    # Triage of links
    link_hp_serv = Gotham_link_BDD.get_link_hp_serv_infos(
        DB_settings, id=link_infos_received["id"])[0]
    link_serv_hp = Gotham_link_BDD.get_link_serv_hp_infos(
        DB_settings, id=link_infos_received["id"])[0]

    modifs = {}

    if "nb_serv" in link_infos_received.keys():
        if link_infos_received["nb_serv"] != link["link_nb_serv"]:
            try:
                nb_serv = edit_link.edit_nb(
                    DB_settings,
                    datacenter_settings,
                    link_serv_hp,
                    link_infos_received["nb_serv"],
                    "serv"
                )
            except Exception as e:
                error = "Server number edition failed"
                return Gotham_error.format_usererror(
                    error, str(e), debug_mode), 500
            modifs["nb_serv"] = nb_serv

    # Update database
    if modifs != {}:
        Gotham_link_BDD.edit_link_DB(DB_settings, modifs, conditions)
        links = Gotham_link_BDD.get_link_infos(
            DB_settings, id=link_infos_received["id"])
        link = Gotham_normalize.normalize_display_object_infos(
            links[0], "link")
        # Triage of links
        link_hp_serv = Gotham_link_BDD.get_link_hp_serv_infos(
            DB_settings, id=link_infos_received["id"])[0]
        link_serv_hp = Gotham_link_BDD.get_link_serv_hp_infos(
            DB_settings, id=link_infos_received["id"])[0]

        modifications = True

    # Clean modifs dict before editing nb_hp
    modifs = {}

    if "nb_hp" in link_infos_received.keys():
        if link_infos_received["nb_hp"] != link["link_nb_hp"]:
            try:
                nb_hp = edit_link.edit_nb(
                    DB_settings,
                    datacenter_settings,
                    link_hp_serv,
                    link_infos_received["nb_hp"],
                    "hp"
                )
            except Exception as e:
                error = "Honeypot number edition failed"
                return Gotham_error.format_usererror(
                    error, str(e), debug_mode), 500
            modifs["nb_hp"] = nb_hp

    # Update database
    if modifs != {}:
        Gotham_link_BDD.edit_link_DB(DB_settings, modifs, conditions)
        links = Gotham_link_BDD.get_link_infos(
            DB_settings, id=link_infos_received["id"])
        link = Gotham_normalize.normalize_display_object_infos(
            links[0], "link")
        modifications = True

    if modifications:
        return Gotham_normalize.normalize_display_object_infos_with_tags(
            link, "link"), 200
    else:
        return "{\"message\": \"Nothing to change\"}\n", 200


@app.route('/delete/honeypot', methods=['POST'])
def rm_honeypot():
    # Removes a honeypot object
    #
    # id (string) : id du honeypot à supprimer

    # Get POST data on JSON format
    data = request.get_json()

    if "confirm" in data and int(data["confirm"]) == 1:
        confirm = True
        del data["confirm"]
    elif "confirm" in data:
        confirm = False
        del data["confirm"]
    else:
        confirm = False

    # Get all hp possibilities
    try:
        jsondata = json.dumps(data)
        url = "http://localhost:5000/list/honeypot"
        r = requests.get(url, params=jsondata)
        jsonresponse = r.json()
    except Exception as e:
        error = "Hp finding failed"
        return Gotham_error.format_usererror(error, str(e), debug_mode), 500

    response = ""
    error = ""
    if "error" in jsonresponse:
        return jsonresponse, 500
    elif "exact" in jsonresponse:
        if jsonresponse["exact"] != []:
            if not(confirm):
                return {
                    "message": "Are you sure you want to remove these honeypots ? (Y/n)", "hps": jsonresponse["exact"]}
            else:
                for hp in jsonresponse["exact"]:
                    try:
                        succes = rm_hp.main(
                            DB_settings,
                            datacenter_settings,
                            hp["hp_id"]
                        )

                    except Exception:
                        error += "Honeypot deletion failed for id: " + \
                            hp["hp_id"] + "\n"
                    if succes:
                        try:
                            rm_hp.remove_rsyslog_configuration(
                                datacenter_settings,
                                hp["hp_id"]
                            )
                        except Exception:
                            error += "Honeypot rsyslog deletion failed for id: " + \
                                hp["hp_id"] + "\n"

                        # If all operations succeed, return id of deleted object
                        response += str({"id": str(hp["hp_id"])}
                                        ).replace("\'", "\"") + "\n"

                    else:
                        error += "Honeypot deletion failed for id: " + \
                            hp["hp_id"] + "\n"
                if error == "":
                    return response, 200
                else:
                    return response + error, 500

    elif "others" in jsonresponse:
        if jsonresponse["others"] != []:
            if not(confirm):
                return {
                    "message": "Are you sure you want to remove these honeypots ? (Y/n)", "hps": jsonresponse["others"]}
            else:
                for hp in jsonresponse["others"]:
                    try:
                        succes = rm_hp.main(
                            DB_settings,
                            datacenter_settings,
                            hp["hp_id"]
                        )

                    except Exception:
                        error += "Honeypot deletion failed for id: " + \
                            hp["hp_id"] + "\n"
                    if succes:
                        try:
                            rm_hp.remove_rsyslog_configuration(
                                datacenter_settings,
                                hp["hp_id"]
                            )
                        except Exception:
                            error += "Honeypot rsyslog deletion failed for id: " + \
                                hp["hp_id"] + "\n"

                        # If all operations succeed, return id of deleted object
                        response += str({"id": str(hp["hp_id"])}
                                        ).replace("\'", "\"") + "\n"
                    else:
                        error += "Honeypot deletion failed for id: " + \
                            hp["hp_id"] + "\n"

                if error == "":
                    return response, 200
                else:
                    return response + error, 500


@app.route('/delete/server', methods=['POST'])
def rm_serv():
    '''
    Removes a server object

    ARGUMENTS:
        id (string) : id of the server
    '''

    # Get POST data on JSON format
    data = request.get_json()

    if "confirm" in data and int(data["confirm"]) == 1:
        confirm = True
        del data["confirm"]
    elif "confirm" in data:
        confirm = False
        del data["confirm"]
    else:
        confirm = False

    # Get all serv possibilities
    try:
        jsondata = json.dumps(data)
        url = "http://localhost:5000/list/server"
        r = requests.get(url, params=jsondata)
        jsonresponse = r.json()
    except Exception as e:
        error = "Serv finding failed"
        return Gotham_error.format_usererror(error, str(e), debug_mode), 500

    response = ""
    error = ""
    if "error" in jsonresponse:
        return jsonresponse, 500
    elif "exact" in jsonresponse and jsonresponse["exact"] != []:
        if not(confirm):
            return {
                "message": "Are you sure you want to remove these servers ? (Y/n)", "servs": jsonresponse["exact"]}
        else:
            for serv in jsonresponse["exact"]:
                try:
                    succes = rm_server.main(
                        DB_settings, datacenter_settings, serv["serv_id"])

                except Exception:
                    error += "Server deletion failed for id: " + \
                        serv["serv_id"] + "\n"
                if succes:
                    # If all operations succeed, return id of deleted object
                    response += str({"id": str(serv["serv_id"])}
                                    ).replace("\'", "\"") + "\n"

                else:
                    error += "Server deletion failed for id: " + \
                        serv["serv_id"] + "\n"
            if error == "":
                return response, 200
            else:
                return response + error, 500

    elif "others" in jsonresponse and jsonresponse["others"] != []:
        if not(confirm):
            return {
                "message": "Are you sure you want to remove these servers ? (Y/n)", "servs": jsonresponse["others"]}
        else:
            for serv in jsonresponse["others"]:
                try:
                    succes = rm_server.main(
                        DB_settings,
                        datacenter_settings,
                        serv["serv_id"]
                    )

                except Exception:
                    error += "Server deletion failed for id: " + \
                        serv["serv_id"] + "\n"
                if succes:
                    # If all operations succeed, return id of deleted object
                    response += str({"id": str(serv["serv_id"])}
                                    ).replace("\'", "\"") + "\n"
                else:
                    error += "Server deletion failed for id: " + \
                        serv["serv_id"] + "\n"

            if error == "":
                return response, 200
            else:
                return response + error, 500


@app.route('/delete/link', methods=['POST'])
def rm_lk():
    '''
    Removes a link object

    ARGUMENTS:
        id (string) : id of the link
    '''

    # Get POST data on JSON format
    data = request.get_json()

    if "confirm" in data and int(data["confirm"]) == 1:
        confirm = True
        del data["confirm"]
    elif "confirm" in data:
        confirm = False
        del data["confirm"]
    else:
        confirm = False

    # Get all links possibilities
    try:
        jsondata = json.dumps(data)
        url = "http://localhost:5000/list/link"
        r = requests.get(url, params=jsondata)
        jsonresponse = r.json()
    except Exception as e:
        error = "Link finding failed"
        return Gotham_error.format_usererror(error, str(e), debug_mode), 500

    response = ""
    error = ""
    if "error" in jsonresponse:
        return jsonresponse, 500
    elif "exact" in jsonresponse and jsonresponse["exact"] != []:
        if not(confirm):
            return {
                "message": "Are you sure you want to remove these links ? (Y/n)", "links": jsonresponse["exact"]}
        else:
            for link in jsonresponse["exact"]:
                try:
                    rm_link.main(DB_settings, id=link["link_id"])

                except Exception:
                    error += "Link deletion failed for id: " + \
                        link["link_id"] + "\n"

            if error == "":
                return response, 200
            else:
                return response + error, 500

    elif "others" in jsonresponse and jsonresponse["others"] != []:
        if not(confirm):
            return {
                "message": "Are you sure you want to remove these links ? (Y/n)", "links": jsonresponse["others"]}
        else:
            for link in jsonresponse["others"]:
                try:
                    rm_link.main(DB_settings, id=link["link_id"])

                except Exception:
                    error += "Link deletion failed for id: " + \
                        link["link_id"] + "\n"

            if error == "":
                return response, 200
            else:
                return response + error, 500


@app.route('/list/honeypot', methods=['GET'])
def ls_honeypot():
    '''
    Gives information on honeypot object

    ARGUMENTS:
        id (string) : id du honeypot à afficher
    '''

    hp_infos_received = {}

    id = request.args.get('id')
    tags = request.args.get('tags')
    name = request.args.get('name')
    descr = request.args.get('descr')
    port = request.args.get('port')
    state = request.args.get('state')

    find_exact = True

    if (id) or (tags) or (name) or (descr) or (port) or (state):

        if (id):
            hp_infos_received["id"] = id
            if "*" in str(hp_infos_received["id"]):
                hp_infos_received["id"] = str(
                    hp_infos_received["id"]).replace(
                    "*", "%")
                find_exact = False
        else:
            hp_infos_received["id"] = "%"

        if (tags):
            hp_infos_received["tags"] = tags
            if "*" in str(hp_infos_received["tags"]):
                hp_infos_received["tags"] = str(
                    hp_infos_received["tags"]).replace(
                    "*", "%")
                find_exact = False
        else:
            hp_infos_received["tags"] = "%"

        if (name):
            hp_infos_received["name"] = name
            if "*" in str(hp_infos_received["name"]):
                hp_infos_received["name"] = str(
                    hp_infos_received["name"]).replace(
                    "*", "%")
                find_exact = False
        else:
            hp_infos_received["name"] = "%"

        if (descr):
            hp_infos_received["descr"] = descr
            if "*" in str(hp_infos_received["descr"]):
                hp_infos_received["descr"] = str(
                    hp_infos_received["descr"]).replace(
                    "*", "%")
                find_exact = False
        else:
            hp_infos_received["descr"] = "%"

        if (port):
            hp_infos_received["port"] = port
            if "*" in str(hp_infos_received["port"]):
                hp_infos_received["port"] = str(
                    hp_infos_received["port"]).replace(
                    "*", "%")
                find_exact = False
        else:
            hp_infos_received["port"] = "%"

        if (state):
            hp_infos_received["state"] = state
            if "*" in str(hp_infos_received["state"]):
                hp_infos_received["state"] = str(
                    hp_infos_received["state"]).replace(
                    "*", "%")
                find_exact = False
        else:
            hp_infos_received["state"] = "%"

        if find_exact:
            honeypots_exact = Gotham_link_BDD.get_honeypot_infos(
                DB_settings,
                mode=False,
                id=hp_infos_received["id"],
                name=hp_infos_received["name"],
                tags=hp_infos_received["tags"],
                state=hp_infos_received["state"],
                descr=hp_infos_received["descr"],
                port=hp_infos_received["port"]
            )
        else:
            honeypots_exact = []

        honeypots_others = Gotham_link_BDD.get_honeypot_infos(
            DB_settings,
            mode=True,
            id=hp_infos_received["id"],
            name=hp_infos_received["name"],
            tags=hp_infos_received["tags"],
            state=hp_infos_received["state"],
            descr=hp_infos_received["descr"],
            port=hp_infos_received["port"]
        )

        if honeypots_exact != [] or honeypots_others != []:
            set_exact = {frozenset(row.items()) for row in honeypots_exact}
            set_others = {frozenset(row.items()) for row in honeypots_others}
            honeypots_others = [dict(i) for i in set_others - set_exact]

            # update state
            try:
                honeypots_exact = [Gotham_state.adapt_state(
                    DB_settings,
                    honeypot["hp_id"],
                    "hp"
                ) for honeypot in honeypots_exact]
            except Exception as e:
                logging.error(
                    "Error while configuring honeypot state : " + str(e))
            try:
                honeypots_others = [Gotham_state.adapt_state(
                    DB_settings,
                    honeypot["hp_id"],
                    "hp"
                ) for honeypot in honeypots_others]
            except Exception as e:
                logging.error(
                    "Error while configuring honeypot state : " + str(e))

            honeypots_exact = [Gotham_normalize.normalize_display_object_infos_with_tags(
                Gotham_normalize.normalize_display_object_infos(
                    honeypot,
                    "hp"
                ),
                "hp"
            ) for honeypot in honeypots_exact]
            honeypots_others = [Gotham_normalize.normalize_display_object_infos_with_tags(
                Gotham_normalize.normalize_display_object_infos(
                    honeypot,
                    "hp"
                ),
                "hp"
            ) for honeypot in honeypots_others]
            return {"exact": honeypots_exact, "others": honeypots_others}, 200

        else:
            logging.error(
                f"No honeypot found with given arguments : {hp_infos_received}")
            error = "No honeypot found"
            return Gotham_error.format_usererror(error, "", debug_mode), 406

    else:
        honeypots = Gotham_link_BDD.get_honeypot_infos(DB_settings)

        if honeypots != []:
            try:
                honeypots = [Gotham_state.adapt_state(
                    DB_settings,
                    honeypot["hp_id"],
                    "hp"
                ) for honeypot in honeypots]
            except Exception as e:
                logging.error(
                    "Error while configuring honeypot state : " + str(e))
            honeypots = [Gotham_normalize.normalize_display_object_infos_with_tags(
                Gotham_normalize.normalize_display_object_infos(
                    honeypot,
                    "hp"
                ),
                "hp"
            ) for honeypot in honeypots]
            return {"honeypots": honeypots}, 200
        else:
            logging.error(f"You tried to list honeypots but no one exists")
            error = "No honeypot managed in GOTHAM"
            return Gotham_error.format_usererror(error, "", debug_mode), 404


@app.route('/list/server', methods=['GET'])
def ls_serv():
    '''
    Gives information on server object

    ARGUMENTS:
        id (string) : id du serveur à afficher
    '''

    serv_infos_received = {}

    id = request.args.get("id")
    ip = request.args.get("ip")
    name = request.args.get("name")
    tags = request.args.get("tags")
    state = request.args.get("state")
    descr = request.args.get("descr")
    ssh_port = request.args.get("ssh_port")

    find_exact = True

    if (id) or (ip) or (name) or (tags) or (state) or (descr) or (ssh_port):

        if (id):
            serv_infos_received["id"] = id
            if "*" in str(serv_infos_received["id"]):
                serv_infos_received["id"] = str(
                    serv_infos_received["id"]).replace(
                    "*", "%")
                find_exact = False
        else:
            serv_infos_received["id"] = "%"

        if (ip):
            serv_infos_received["ip"] = ip
            if "*" in str(serv_infos_received["ip"]):
                serv_infos_received["ip"] = str(
                    serv_infos_received["ip"]).replace(
                    "*", "%")
                find_exact = False
        else:
            serv_infos_received["ip"] = "%"

        if (tags):
            serv_infos_received["tags"] = tags
            if "*" in str(serv_infos_received["tags"]):
                serv_infos_received["tags"] = str(
                    serv_infos_received["tags"]).replace(
                    "*", "%")
                find_exact = False
        else:
            serv_infos_received["tags"] = "%"

        if (name):
            serv_infos_received["name"] = name
            if "*" in str(serv_infos_received["name"]):
                serv_infos_received["name"] = str(
                    serv_infos_received["name"]).replace(
                    "*", "%")
                find_exact = False
        else:
            serv_infos_received["name"] = "%"

        if (descr):
            serv_infos_received["descr"] = descr
            if "*" in str(serv_infos_received["descr"]):
                serv_infos_received["descr"] = str(
                    serv_infos_received["descr"]).replace(
                    "*", "%")
                find_exact = False
        else:
            serv_infos_received["descr"] = "%"

        if (ssh_port):
            serv_infos_received["ssh_port"] = ssh_port
            if "*" in str(serv_infos_received["ssh_port"]):
                serv_infos_received["ssh_port"] = str(
                    serv_infos_received["ssh_port"]).replace(
                    "*", "%")
                find_exact = False
        else:
            serv_infos_received["ssh_port"] = "%"

        if (state):
            serv_infos_received["state"] = state
            if "*" in str(serv_infos_received["state"]):
                serv_infos_received["state"] = str(
                    serv_infos_received["state"]).replace(
                    "*", "%")
                find_exact = False
        else:
            serv_infos_received["state"] = "%"

        if find_exact == True:
            servers_exact = Gotham_link_BDD.get_server_infos(
                DB_settings,
                mode=False,
                id=serv_infos_received["id"],
                ip=serv_infos_received["ip"],
                name=serv_infos_received["name"],
                tags=serv_infos_received["tags"],
                state=serv_infos_received["state"],
                descr=serv_infos_received["descr"],
                ssh_port=serv_infos_received["ssh_port"]
            )
        else:
            servers_exact = []

        servers_others = Gotham_link_BDD.get_server_infos(
            DB_settings,
            mode=True,
            id=serv_infos_received["id"],
            ip=serv_infos_received["ip"],
            name=serv_infos_received["name"],
            tags=serv_infos_received["tags"],
            state=serv_infos_received["state"],
            descr=serv_infos_received["descr"],
            ssh_port=serv_infos_received["ssh_port"]
        )

        if servers_exact != [] or servers_others != []:
            set_exact = {frozenset(row.items()) for row in servers_exact}
            set_others = {frozenset(row.items()) for row in servers_others}
            servers_others = [dict(i) for i in set_others - set_exact]

            # update state
            try:
                servers_exact = [Gotham_state.adapt_state(
                    DB_settings,
                    server["serv_id"],
                    "serv"
                ) for server in servers_exact]
            except Exception as e:
                logging.error(
                    "Error while configuring server state : " + str(e))
            try:
                servers_others = [Gotham_state.adapt_state(
                    DB_settings,
                    server["serv_id"],
                    "serv"
                ) for server in servers_others]
            except Exception as e:
                logging.error(
                    "Error while configuring server state : " + str(e))

            servers_exact = [Gotham_normalize.normalize_display_object_infos_with_tags(
                Gotham_normalize.normalize_display_object_infos(
                    server,
                    "serv"
                ),
                "serv"
            ) for server in servers_exact]
            servers_others = [Gotham_normalize.normalize_display_object_infos_with_tags(
                Gotham_normalize.normalize_display_object_infos(
                    server,
                    "serv"
                ),
                "serv"
            ) for server in servers_others]
            return {"exact": servers_exact, "others": servers_others}, 200

        else:
            logging.error(
                f"No server found with given arguments : {serv_infos_received}")
            error = "No server found"
            return Gotham_error.format_usererror(error, "", debug_mode), 406
    else:
        servers = Gotham_link_BDD.get_server_infos(DB_settings)

        if servers != []:
            try:
                servers = [Gotham_state.adapt_state(
                    DB_settings,
                    server["serv_id"],
                    "serv"
                ) for server in servers]
            except Exception as e:
                logging.error(
                    "Error while configuring server state : " + str(e))
            servers = [
                Gotham_normalize.normalize_display_object_infos_with_tags(
                    Gotham_normalize.normalize_display_object_infos(
                        server, "serv"), "serv") for server in servers]
            return {"servers": servers}
        else:
            logging.error(f"You tried to list servers but no one exists")
            error = "No server managed in GOTHAM"
            return Gotham_error.format_usererror(error, "", debug_mode), 404


@app.route('/list/link', methods=['GET'])
def ls_lk():
    '''
    Gives information on link object

    ARGUMENTS:
        id (string) : id du lien à afficher
    '''

    link_infos_received = {}

    id = request.args.get("id")
    nb_hp = request.args.get("nb_hp")
    nb_serv = request.args.get("nb_serv")
    tags_hp = request.args.get("tags_hp")
    tags_serv = request.args.get("tags_serv")
    ports = request.args.get("ports")

    find_exact = True

    if (id) or (nb_hp) or (nb_serv) or (tags_hp) or (tags_serv):

        if (id):
            link_infos_received["id"] = id
            if "*" in str(link_infos_received["id"]):
                link_infos_received["id"] = str(
                    link_infos_received["id"]).replace(
                    "*", "%")
                find_exact = False
        else:
            link_infos_received["id"] = "%"

        if (nb_hp):
            link_infos_received["nb_hp"] = nb_hp
            if "*" in str(link_infos_received["nb_hp"]):
                link_infos_received["nb_hp"] = str(
                    link_infos_received["nb_hp"]).replace(
                    "*", "%")
                find_exact = False
        else:
            link_infos_received["nb_hp"] = "%"

        if (nb_serv):
            link_infos_received["nb_serv"] = nb_serv
            if "*" in str(link_infos_received["nb_serv"]):
                link_infos_received["nb_serv"] = str(
                    link_infos_received["nb_serv"]).replace(
                    "*", "%")
                find_exact = False
        else:
            link_infos_received["nb_serv"] = "%"

        if (tags_hp):
            link_infos_received["tags_hp"] = tags_hp
            if "*" in str(link_infos_received["tags_hp"]):
                link_infos_received["tags_hp"] = str(
                    link_infos_received["tags_hp"]).replace(
                    "*", "%")
                find_exact = False
        else:
            link_infos_received["tags_hp"] = "%"

        if (tags_serv):
            link_infos_received["tags_serv"] = tags_serv
            if "*" in str(link_infos_received["tags_serv"]):
                link_infos_received["tags_serv"] = str(
                    link_infos_received["tags_serv"]).replace(
                    "*", "%")
                find_exact = False
        else:
            link_infos_received["tags_serv"] = "%"

        if (ports):
            link_infos_received["ports"] = ports
            if "*" in str(link_infos_received["ports"]):
                link_infos_received["ports"] = str(
                    link_infos_received["ports"]).replace(
                    "*", "%")
                find_exact = False
        else:
            link_infos_received["tags_serv"] = "%"

        if find_exact:
            links_exact = Gotham_link_BDD.get_link_infos(
                DB_settings,
                mode=False,
                id=link_infos_received["id"],
                nb_hp=link_infos_received["nb_hp"],
                nb_serv=link_infos_received["nb_serv"],
                tags_hp=link_infos_received["tags_hp"],
                tags_serv=link_infos_received["tags_serv"]
            )
        else:
            links_exact = []

        links_others = Gotham_link_BDD.get_link_infos(
            DB_settings,
            mode=True,
            id=link_infos_received["id"],
            nb_hp=link_infos_received["nb_hp"],
            nb_serv=link_infos_received["nb_serv"],
            tags_hp=link_infos_received["tags_hp"],
            tags_serv=link_infos_received["tags_serv"]
        )

        if links_exact != [] or links_others != []:
            set_exact = {frozenset(row.items()) for row in links_exact}
            set_others = {frozenset(row.items()) for row in links_others}
            links_others = [dict(i) for i in set_others - set_exact]
            links_exact = [Gotham_normalize.normalize_display_object_infos_with_tags(
                Gotham_normalize.normalize_display_object_infos(
                    link,
                    "link"
                ),
                "link"
            ) for link in links_exact]
            links_others = [Gotham_normalize.normalize_display_object_infos_with_tags(
                Gotham_normalize.normalize_display_object_infos(
                    link,
                    "link"
                ),
                "link"
            ) for link in links_others]
            return {"exact": links_exact, "others": links_others}, 200

        else:
            logging.error(
                f"No link found with given arguments : {link_infos_received}")
            error = "No link found"
            return Gotham_error.format_usererror(error, "", debug_mode), 406

    else:
        links = Gotham_link_BDD.get_link_infos(DB_settings)

        if links != []:
            links = [Gotham_normalize.normalize_display_object_infos_with_tags(
                Gotham_normalize.normalize_display_object_infos(
                    link,
                    "link"
                ),
                "link"
            ) for link in links]
            return {"links": links}, 200
        else:
            logging.error(f"You tried to list links but no one exists")
            error = "No link managed by GOTHAM"
            return Gotham_error.format_usererror(error, "", debug_mode), 404


@app.route('/list/all', methods=['GET'])
def ls_all():
    # Gives information on all objects

    honeypots = Gotham_link_BDD.get_honeypot_infos(DB_settings)

    if honeypots != []:
        honeypots = [Gotham_normalize.normalize_display_object_infos_with_tags(
            Gotham_normalize.normalize_display_object_infos(
                honeypot,
                "hp"
            ),
            "hp"
        ) for honeypot in honeypots]
    else:
        honeypots = "No honeypot in database"

    servers = Gotham_link_BDD.get_server_infos(DB_settings)

    if servers != []:
        servers = [Gotham_normalize.normalize_display_object_infos_with_tags(
            Gotham_normalize.normalize_display_object_infos(
                server,
                "serv"
            ),
            "serv"
        ) for server in servers]
    else:
        servers = "No server in database"

    links = Gotham_link_BDD.get_link_infos(DB_settings)

    if links != []:
        links = [Gotham_normalize.normalize_display_object_infos_with_tags(
            Gotham_normalize.normalize_display_object_infos(
                link,
                "link"
            ),
            "link"
        ) for link in links]
    else:
        links = "No link in database"

    return {"honeypots": honeypots, "servers": servers, "links": links}, 200


@app.route('/version', methods=['GET'])
def get_version():
    # Return the orchestrator's version
    #

    # Return orchestrator version
    response = str({"version": str(version)}).replace("\'", "\"") + "\n"
    return response, 200


if __name__ == "__main__":
    app.run(host='0.0.0.0')
