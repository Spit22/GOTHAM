# GENERAL LIBS
import flask
import json
import uuid
import base64
import os
import random
import configparser
from flask import request, jsonify
from io import StringIO

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
#import edit_link

# GOTHAM'S LIB
import Gotham_link_BDD
import Gotham_check
import Gotham_choose
import Gotham_normalize

# Logging components
import os
import logging

app = flask.Flask(__name__)


# GHOTHAM_HOME env definition 
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')

# Logging Configuration
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


##### Chargement des variables globales #######
app.config["DEBUG"] = True
version = "0.0"

# Retrieve  internaldb settings from config file
config = configparser.ConfigParser()
config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
DB_settings = {"username":config['internaldb']['username'], "password":config['internaldb']['password'], "hostname":config['internaldb']['hostname'], "port":config['internaldb']['port'], "database": config['internaldb']['database']}
dc_ports_list = range(int(config['datacenter']['min_port']), int(config['datacenter']['max_port']))

# Retrieve datacenter settings from config file
dc_ip = config['datacenter']['ip']
dc_ssh_port = int(config['datacenter']['ssh_port'])

# Retreive separators
ports_separator = config['port']['separator']
tags_separator = config['tag']['separator']


# Path to store object's data
store_path = "/data"
dockerfile_storage = "/data/"


@app.route('/', methods=['GET'])
def index():
        return """
               _,    _   _    ,_
  .o888P     Y8o8Y     Y888o.
 d88888      88888      88888b
d888888b_  _d88888b_  _d888888b
8888888888888888888888888888888
8888888888888888888888888888888
YJGS8P"Y888P"Y888P"Y888P"Y8888P
 Y888   '8'   Y8P   '8'   888Y
  '8o          V          o8'\n
                                GOTHAM's project\n
"""

@app.route('/add/honeypot', methods=['POST'])
def add_honeypot(hp_infos_received={}):
        # Creates a honeypot object
        # 
        # name (string) : nom du honeypot
        # descr (string) : description du honeypot
        # tags (list) : liste des tags du honeypot
        # logs (string) : path des logs à monitorer
        # parser (string) : règle de parsing des logs monitorés
        # dockerfile (string) : dockerfile to generate the honeypot on datacenter, base64 encoded
        # service_port (int) : port on which the honeypot will lcoally listen


        if hp_infos_received=={}:
            # Get POST data on JSON format
            data = request.get_json()
            received=True
        else:
            data=hp_infos_received
            received=False

        try:
            # Normalize infos
            hp_infos_received = {"name": data["name"],"descr": data["descr"],"tags": data["tags"],"logs": data["logs"],"parser": data["parser"],"port": data["port"]}
            hp_infos_received = Gotham_normalize.normalize_honeypot_infos(hp_infos_received)

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
            return "Invalid data sent "+str(e)

        # Retrieve datacenter's SSH key from config file
        try:
            dc_ssh_key = config['datacenter']['ssh_key']
            dc_ssh_key = base64.b64decode(dc_ssh_key) # ssh_key is byte
            dc_ssh_key = dc_ssh_key.decode('ascii') # ssh_key is ascii string
            dc_ssh_key = StringIO(dc_ssh_key) # ssh_key is a file-like object

        except Exception as e:
            print("Error loading datacenter's SSH key")

        # First find an available port to map on datacenter
        used_ports = Gotham_check.check_used_port(DB_settings)
        available_ports=[port for port in dc_ports_list if not(port in used_ports)]
        
        if available_ports==[]:
            return "Datacenter : no port available for mapping"
        
        else:
            mapped_port=random.choice(available_ports)

        # Generate honeypot's id
        id = 'hp-'+str(uuid.uuid4().hex)

        # Write the dockerfile in the local storage
        dockerfile_path = str(dockerfile_storage)+str(id)+"/"
        
        if not os.path.isdir(dockerfile_path):
            os.mkdir(dockerfile_path)
            dockerfile_file = open(str(dockerfile_path)+"Dockerfile", 'a')
            dockerfile_file.write(dockerfile)
            dockerfile_file.close()
        
        else:
            return "Can't store the dockerfile locally : path already exists"

        # Generate docker-compose.yml from information
        add_hp.generate_dockercompose(id, dockerfile_path, logs, port, mapped_port)
        
        # Deploy the hp's container on datacenter
        try:
            add_hp.deploy_container(dc_ip, dc_ssh_port, dc_ssh_key, dockerfile_path, id)
        
        except Exception as e:
            return "An error occured in the ssh connection"
        
        # Create and deploy rsyslog configuration on the datacenter and the orchestrator
        try:
            add_hp.deploy_rsyslog_conf(dc_ip, dc_ssh_port, dc_ssh_key, orch_ip, orch_rsyslog_port, local_rulebase_path, remote_rulebase_path, id_hp)
        except:
            return "Rsyslog configuration failed"

        # Create hp_infos
        hp_infos = {'id':str(id),'name':str(name),'descr':str(descr),'tags':str(tags),'port_container':port,'parser':str(parser),'logs':str(logs),'source':str(dockerfile_path),'state':'UNUSED','port':mapped_port}
        
        # Normalize infos
        hp_infos = Gotham_normalize.normalize_honeypot_infos(hp_infos)
        
        # Store new hp and tags in the database
        Gotham_link_BDD.add_honeypot_DB(DB_settings, hp_infos)

        # If all operations succeed
        if received==True:
            return "OK : "+str(id)
        
        else:
            return str(id)

@app.route('/add/server', methods=['POST'])
def add_srv():
        # Creates a server object
        # 
        # name (string) : nom du serveur
        # descr (string) : description du serveur
        # tags (list) : liste des tags du serveur
        # ip (string) : adresse IP publique du serveur
        # ssh_key (string) : clé SSH à utiliser pour la connexion
        # ssh_port (int) : port d'écoute du service SSH 

        # Get POST data on JSON format
        data = request.get_json()

        # Get all function's parameters
        try:
            # Normalize infos
            serv_infos_received = {"name": data["name"],"descr": data["descr"],"tags": data["tags"],"ip": data["ip"],"ssh_port": data["ssh_port"]}
            serv_infos_received = Gotham_normalize.normalize_server_infos(serv_infos_received)
            # Get all function's parameters
            name = serv_infos_received["name"]
            descr = serv_infos_received["descr"]
            tags = serv_infos_received["tags"]
            ip = serv_infos_received["ip"]
            encoded_ssh_key = data["ssh_key"]
            # Decode and format the ssh key
            ssh_key = base64.b64decode(encoded_ssh_key) # ssh_key is byte
            ssh_key = ssh_key.decode('ascii') # ssh_key is ascii string
            check_ssh_key = StringIO(ssh_key) # ssh_key for the check is a file-like object
            deploy_ssh_key = StringIO(ssh_key) # ssh_key for the deployment is a file-like object
            ssh_port = serv_infos_received["ssh_port"]
        
        except Exception as e:
            return "Invalid data sent "+str(e)

        # First check the ip not already exists in database
        exists = Gotham_check.check_doublon_server(DB_settings, ip)
        
        if exists:
            return "Provided ip already exists in database"

        # Check given auth information are ok
        connected = Gotham_check.check_ssh(ip, ssh_port, check_ssh_key) 
        
        if not connected:
            return "Provided ssh_key or ssh_port is wrong"

        # If all checks are ok, we can generate an id for the new server
        id = 'sv-'+str(uuid.uuid4().hex)

        # Deploy the reverse-proxy service on the new server
        try:
            add_server.deploy(ip, ssh_port, deploy_ssh_key)
        
        except Exception as e:
            return "Something went wrong while deploying Reverse-Proxy"

        # Create serv_infos
        serv_infos = {'id':str(id),'name':str(name),'descr':str(descr),'tags':str(tags),'ip':str(ip),'ssh_key':str(ssh_key),'ssh_port':ssh_port,'state':'UNUSED'}
        
        # Normalize infos
        serv_infos = Gotham_normalize.normalize_server_infos(serv_infos)
        
        # Store new server and tags in the internal database        
        Gotham_link_BDD.add_server_DB(DB_settings, serv_infos)   

        # If all operations succeed
        return "OK : "+str(id)

@app.route('/add/link', methods=['POST'])
def add_lk():
        # Creates a link object
        # 
        # tags_serv (list) : tag du/des serveurs ciblés
        # tags_hp (list) : tag du/des hp ciblés
        # nb_srv (int) : nombre de serveurs ciblés
        # nb_hp (int) : nombre de hp ciblés
        # exposed_port (list): list des ports à utiliser

        # Retrieve datacenter's SSH key from config file
        try:
            dc_ssh_key = config['datacenter']['ssh_key']
            dc_ssh_key = base64.b64decode(dc_ssh_key) # ssh_key is byte
            dc_ssh_key = dc_ssh_key.decode('ascii') # ssh_key is ascii string
            dc_ssh_key = StringIO(dc_ssh_key) # ssh_key is a file-like object

        except Exception as e:
            print("Error loading datacenter's SSH key")

        # Get POST data on JSON format
        data = request.get_json()

        # Get all function's parameters
        try:
            # Normalize infos
            lk_infos_received = {"tags_hp":data["tags_hp"], "tags_serv":data["tags_serv"], "ports":data["exposed_ports"]}
            
            if str(data["nb_hp"]).lower() != "all":
                lk_infos_received["nb_hp"]=data["nb_hp"]
            
            if str(data["nb_srv"]).lower() != "all":
                lk_infos_received["nb_serv"]=data["nb_srv"]
                           
            lk_infos_received = Gotham_normalize.normalize_link_infos(lk_infos_received)
            
            # Get all function's parameters
            tags_serv = lk_infos_received["tags_serv"]
            tags_hp = lk_infos_received["tags_hp"]
            nb_srv = lk_infos_received["nb_serv"] if "nb_serv" in lk_infos_received.keys() else data["nb_srv"]
            nb_hp = lk_infos_received["nb_hp"] if "nb_hp" in lk_infos_received.keys() else data["nb_hp"]
            exposed_ports = lk_infos_received["ports"]
            exposed_ports_list = exposed_ports.split(ports_separator)
        
        except Exception as e:
            return "Invalid data sent "+str(e)
       
        # We check that no link exists with same tags, otherwise return error
        existingLinks = Gotham_check.check_tags("link", Gotham_link_BDD.get_link_infos(DB_settings, tags_hp=tags_hp, tags_serv=tags_serv), tags_hp=tags_hp, tags_serv=tags_serv, mode=True)
        
        if existingLinks != []:
            return "A link is already configured for this tags"

        # We check all provided server tags exists, otherwise return error
        try:
            Gotham_check.check_doublon_tags(DB_settings, tags_serv)
        
        except:
            return "Error with tags: some server tags do not exists"

        # We check all provided hp tags exists, otherwise return error
        try:
            Gotham_check.check_doublon_tags(DB_settings, tags_hp)
        
        except:
            return "Error with tags: some honeypot tags do not exists"

        # Get all honeypots corresponding to tags
        honeypots = Gotham_link_BDD.get_honeypot_infos(DB_settings, tags=tags_hp)

        if tags_hp.lower()!="all":
            honeypots = Gotham_check.check_tags("hp", honeypots, tags_hp=tags_hp)

        # Get all servers corresponding to tags
        servers = Gotham_link_BDD.get_server_infos(DB_settings, tags=tags_serv)
        
        if tags_serv.lower()!="all":
            servers = Gotham_check.check_tags("serv",servers, tags_serv=tags_serv)

        # Filter servers in those who have one of ports open
        servers = Gotham_check.check_servers_ports_matching(servers, exposed_ports)
        
        # Filter servers in error
        servers = [server for server in servers if server["serv_state"]!='ERROR']
        
        # Filter honeypots in error
        honeypots = [honeypot for honeypot in honeypots if honeypot["hp_state"]!='ERROR']

        if str(nb_srv).lower()=="all":
            nb_srv=len(servers)
        
        if str(nb_hp).lower()=="all":
            nb_hp=len(honeypots)

        # Checking we have enough servers for the nb_srv directive, otherwise return error
        if len(servers) < nb_srv:
            return "Can't deploy link on "+str(nb_srv)+" servers while there is only "+str(len(servers))+" servers available"
        
        # If we don't have any honeypots corresponding, just return error,
        if len(honeypots) < 1:
            return "Can't configure link if there is no at least one hp corresponding to request"
        
        # Choose best honeypots (the lower scored)
        honeypots = Gotham_choose.choose_honeypots(honeypots, nb_hp, tags_hp)

        # Checking we have enough honeypots for the nb_hp directive
        if len(honeypots) < nb_hp:
            added_hp=[]
            
            for i in range(nb_hp-len(honeypots)):
                
                with open(honeypots[i%len(honeypots)]["hp_source"]+"/Dockerfile", 'r') as file:
                    encoded_dockerfile = base64.b64encode(file.read().encode("ascii"))
                
                name = (honeypots[i%len(honeypots)]["hp_name"]+"_Duplicat" if len(honeypots[i%len(honeypots)]["hp_name"]+"_Duplicat")<=128 else honeypots[i%len(honeypots)]["hp_name"][:(128-len("_Duplicat"))]+"_Duplicat")
                descr = "Duplication of "+honeypots[i%len(honeypots)]["hp_descr"]
                duplicate_hp_infos={"name": name,"descr": descr,"tags": honeypots[i%len(honeypots)]["hp_tags"].replace("||",tags_separator),"logs": honeypots[i%len(honeypots)]["hp_logs"],"parser": honeypots[i%len(honeypots)]["hp_parser"],"port": honeypots[i%len(honeypots)]["hp_port_container"], "dockerfile": encoded_dockerfile}
                
                try:
                    added_hp.append(add_honeypot(duplicate_hp_infos))
                
                except:
                    return "Error with hp duplication"
            
            for id in added_hp:
                honeypots.append(Gotham_link_BDD.get_honeypot_infos(DB_settings, id=id))

        # Choose best servers (the lower scored)
        servers = Gotham_choose.choose_servers(servers, nb_srv, tags_serv)
        
        count_exposed_ports={str(port):0 for port in exposed_ports_list}
        
        # Associate servers and an port of exposition
        for i in range(len(servers)):
            serv_i_free_ports=servers[i]["free_ports"].split(ports_separator)
            servs_free_ports=(ports_separator.join([serv["free_ports"] for serv in servers if serv["serv_id"]!=servers[i]["serv_id"]])).split(ports_separator)
            port_available_only_for_this_server=list(set(serv_i_free_ports).difference(servs_free_ports))

            if len(servers[i]["free_ports"].split(ports_separator))==1 :
                servers[i]["choosed_port"]=int(servers[i]["free_ports"])
                count_exposed_ports[str(servers[i]["choosed_port"])]+=1
            
            elif port_available_only_for_this_server!=[]:
                servers[i]["choosed_port"]=int(port_available_only_for_this_server[0])
                count_exposed_ports[str(servers[i]["choosed_port"])]+=1
        
        for i in range(len(servers)):
            if not("choosed_port" in servers[i].keys()):
                free_ports_for_serv_with_weight={port:count_exposed_ports[port] for port in servers[i]["free_ports"].split(ports_separator)}
                servers[i]["choosed_port"]=int(min(free_ports_for_serv_with_weight, key=free_ports_for_serv_with_weight.get))
                count_exposed_ports[str(servers[i]["choosed_port"])]+=1

        final_exposed_ports=list(filter(None,dict.fromkeys([server["choosed_port"] for server in servers])))

        # Create link id
        id = 'lk-'+str(uuid.uuid4().hex)

        # Generate NGINX configurations for each redirection on a specific exposed_port
        for exposed_port in final_exposed_ports:
            add_link.generate_nginxConf(DB_settings, id, dc_ip, honeypots, exposed_port)

        # Deploy new reverse-proxies's configurations on servers
        add_link.deploy_nginxConf(DB_settings, id, servers)

        # Check redirection is effective on all servers
        for server in servers:
            connected = Gotham_check.check_server_redirects(server["serv_ip"], server["choosed_port"])
            
            if not connected:
                return "Error : link is not effective on server "+str(server["serv_ip"])

        # Create lk_infos
        lk_infos = {"id":id, "nb_hp": nb_hp, "nb_serv": nb_srv, "tags_hp":tags_hp, "tags_serv":tags_serv, "ports":exposed_ports}
        
        # Normalize infos
        lk_infos = Gotham_normalize.normalize_link_infos(lk_infos)
        
        # Store new link and tags in the internal database        
        Gotham_link_BDD.add_link_DB(DB_settings, lk_infos)
        
        # Insert data in Link_Hp_Serv
        for server in servers:
            for honeypot in honeypots:
                # Create lhs_infos
                lhs_infos = {"id_link":lk_infos["id"], "id_hp": honeypot["hp_id"], "id_serv": server["serv_id"], "port":server["choosed_port"]}
                # Normalize infos
                lhs_infos = Gotham_normalize.normalize_lhs_infos(lhs_infos)
                # Store new link and tags in the internal database        
                Gotham_link_BDD.add_lhs_DB(DB_settings, lhs_infos)

        return "OK : "+str(id)

@app.route('/edit/honeypot', methods=['POST'])
def edit_honeypot():
        # Edits a honeypot object
        # 
        # id (string) : id du honeypot à modifier
        # name (string) : nom du honeypot
        # descr (string) : description du honeypot
        # tags (list) : liste des tags du honeypot
        # logs (string) : path des logs à monitorer
        # parser (string) : règle de parsing des logs monitorés
        # service_port (int) : port on which the honeypot will lcoally listen


        # Get POST data on JSON format
        data = request.json

        # Make sure all data are in JSON
        data = json.loads(data)

        hp_infos_received={}
        
        # Get all function's parameters
        if "id" in data.keys():
            hp_infos_received["id"] = data["id"]
        
        else:
            return "Need to specify an honeypot id"
        
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

        try:
            # Normalize infos
            hp_infos_received = Gotham_normalize.normalize_honeypot_infos(hp_infos_received)            
        
        except Exception as e:
            return "Invalid data sent "+str(e)

        # Check if the honyepot exists in the IDB
        honeypots = Gotham_link_BDD.get_honeypot_infos(DB_settings, id=hp_infos_received["id"])
        
        if honeypots == []:
            logging.error(f"You tried to edit a honeypot that doesn't exists with the id = {id}")
            return "Unknown id "+hp_infos_received["id"]+" for Honeypot"
        
        honeypot= honeypots[0]
        modifs={}
        conditions={"id":honeypot["hp_id"]}
        
        if "name" in hp_infos_received.keys():
            if hp_infos_received["name"] != honeypot["hp_name"]:
                modifs["name"]=hp_infos_received["name"]
        
        if "descr" in hp_infos_received.keys():
            if hp_infos_received["descr"] != honeypot["hp_descr"]:
                modifs["descr"] = hp_infos_received["descr"]
        
        if "tags" in hp_infos_received.keys():
            if set(hp_infos_received["tags"].split(tags_separator)) != set(honeypot["hp_tags"].split("||")):
                succes = True
                if honeypot['link_id'] != None and honeypot['link_id'] !="NULL":
                    succes = False
                    try:
                        edit_hp.edit_tags(DB_settings, honeypot, hp_infos_received["tags"])
                        succes = True
                    
                    except:
                        succes = False
                if succes:
                    modifs["tags"] = hp_infos_received["tags"]
                
                else:
                    return "Error in tag edition"
        
        if "logs" in hp_infos_received.keys():
            if hp_infos_received["logs"] != honeypot["hp_logs"]:
                return "Edit logs not IMPLEMENTED"
                modifs["logs"] = hp_infos_received["logs"]
        
        if "parser" in hp_infos_received.keys():
            if hp_infos_received["parser"] != honeypot["hp_parser"]:
                return "Edit parser not IMPLEMENTED"
                modifs["parser"]=hp_infos_received["parser"]
        
        if "port" in hp_infos_received.keys():
            if hp_infos_received["port"]!= honeypot["hp_port"]:
                return "Edit port not IMPLEMENTED"
                modifs["port"]=hp_infos_received["port"]
        
        if modifs != {}:
            Gotham_link_BDD.edit_honeypot_DB(DB_settings, modifs, conditions)

            honeypots = Gotham_link_BDD.get_honeypot_infos(DB_settings, id=hp_infos_received["id"])
            honeypot=Gotham_normalize.normalize_display_object_infos(honeypots[0],"hp")

            return honeypot
        
        return "Nothing to change"

@app.route('/edit/server', methods=['POST'])
def edit_srv():
        # Edits a server object
        # 
        # id (string) : id du serveur à modifier
        # name (string) : nom du serveur
        # descr (string) : description du serveur
        # tags (list) : liste des tags du serveur
        # ip (string) : adresse IP publique du serveur
        # ssh_key (string) : clé SSH à utiliser pour la connexion
        # ssh_port (int) : port d'écoute du service SSH 

        # Get POST data on JSON format
        data = request.json

        # Make sure all data are in JSON
        data = json.loads(data)

        serv_infos_received={}
        
        # Get all function's parameters
        if "id" in data.keys():
            serv_infos_received["id"] = data["id"]
        
        else:
            return "Need to specify a server id"
        
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

        try:
            # Normalize infos
            serv_infos_received = Gotham_normalize.normalize_server_infos(serv_infos_received)            
        
        except Exception as e:
            return "Invalid data sent "+str(e)

        # Check if the honyepot exists in the IDB
        servers = Gotham_link_BDD.get_server_infos(DB_settings, id=serv_infos_received["id"])
        
        if servers == []:
            logging.error(f"You tried to edit a server that doesn't exists with the id = {id}")
            return "Unknown id "+serv_infos_received["id"]+" for server"
        
        server= servers[0]
        modifs={}
        conditions={"id":server["serv_id"]}
        
        if "name" in serv_infos_received.keys():
            if serv_infos_received["name"]!= server["serv_name"]:
                modifs["name"]=serv_infos_received["name"]
        
        if "descr" in serv_infos_received.keys():
            if serv_infos_received["descr"]!= server["serv_descr"]:
                modifs["descr"]=serv_infos_received["descr"]
        
        if "tags" in serv_infos_received.keys():
            if set(serv_infos_received["tags"].split(tags_separator))!= set(server["serv_tags"].split("||")):
                succes=True
                if server['link_id'] != None and server['link_id'] !="NULL":
                    succes=False
                    succes=edit_server.edit_tags(DB_settings, server, serv_infos_received["tags"])
                if succes==True :
                    modifs["tags"]=serv_infos_received["tags"]
                
                else:
                    return "Error in tag edition"
        
        if "ip" in serv_infos_received.keys() or "ssh_key" in serv_infos_received.keys() or "ssh_port" in serv_infos_received.keys():
            ip=server["serv_ip"]
            ssh_port=server["serv_ssh_port"]
            ssh_key=server["serv_ssh_key"]
            
            if "ip" in serv_infos_received.keys():
                if serv_infos_received["ip"]!= server["serv_ip"]:
                    modifs["ip"]=serv_infos_received["ip"]
                    ip=serv_infos_received["ip"]
            
            if "ssh_key" in serv_infos_received.keys():
                if serv_infos_received["ssh_key"]!= server["serv_ssh_key"]:
                    modifs["ssh_key"]=serv_infos_received["ssh_key"]
                    ssh_key=serv_infos_received["ssh_key"]
            
            if "ssh_port" in serv_infos_received.keys():
                if serv_infos_received["ssh_port"]!= server["serv_ssh_port"]:
                    modifs["ssh_port"]=serv_infos_received["ssh_port"]
                    ssh_port=serv_infos_received["ssh_port"]
            try:
                edit_server.edit_connection(DB_settings, server, ip, ssh_port, ssh_key)
            
            except:
                return "Error in connection edition"

        if modifs != {}:
            Gotham_link_BDD.edit_server_DB(DB_settings, modifs, conditions)
            servers = Gotham_link_BDD.get_server_infos(DB_settings, id=serv_infos_received["id"])
            server = Gotham_normalize.normalize_display_object_infos(servers[0],"serv")
            return server
        
        return "Nothing to change"

@app.route('/edit/link', methods=['POST'])
def edit_lk():
        # Edits a link object
        #
        # id (string) : id du lien à modifier
        # tag_srv (list) : tag du/des serveurs ciblés
        # tag_hp (list) : tag du/des hp ciblés
        # nb_srv (int) : nombre de serveurs ciblés
        # nb_hp (int) : nombre de hp ciblés
        # ports (string) : exposed ports

        # Get POST data on JSON format
        data = request.json

        # Make sure all data are in JSON
        data = json.loads(data)

        link_infos_received={}
        
        # Get all function's parameters
        if "id" in data.keys():
            link_infos_received["id"] = data["id"]
        
        else:
            return "Need to specify a link id"
        
        if "tag_srv" in data.keys():
            link_infos_received["tag_srv"] = data["tag_srv"]
        
        if "tag_hp" in data.keys():
            link_infos_received["tag_hp"] = data["tag_hp"]
        
        if "nb_srv" in data.keys():
            link_infos_received["nb_srv"] = data["nb_srv"]
        
        if "nb_hp" in data.keys():
            link_infos_received["nb_hp"] = data["nb_hp"]
        
        if "ports" in data.keys():
            link_infos_received["ports"] = data["ports"]
        
        try:
            # Normalize infos
            link_infos_received = Gotham_normalize.normalize_link_infos(link_infos_received)            
        
        except Exception as e:
            return "Invalid data sent "+str(e)

        # Check if the link exists in the IDB
        links = Gotham_link_BDD.get_link_infos(DB_settings, id=link_infos_received["id"])
        
        if links == []:
            logging.error(f"You tried to edit a link that doesn't exists with the id = {id}")
            return "Unknown id "+link_infos_received["id"]+" for link"
        
        link= links[0]
        modifs={}
        conditions={"id":link["link_id"]}
        
        if "tag_srv" in link_infos_received.keys():
            if set(link_infos_received["tag_srv"].split(tags_separator))!= set(link["link_tag_srv"].split("||")):
                return "Edit tag_srv not IMPLEMENTED"
                modifs["tag_srv"]=link_infos_received["tag_srv"]
        
        if "tag_hp" in link_infos_received.keys():
            if set(link_infos_received["tag_hp"].split(tags_separator))!= set(link["link_tag_hp"].split("||")):
                return "Edit tag_hp not IMPLEMENTED"
                modifs["tag_hp"]=link_infos_received["tag_hp"]
        
        if "nb_srv" in link_infos_received.keys():
            if link_infos_received["nb_srv"]!= link["link_nb_serv"]:
                return "Edit nb_srv not IMPLEMENTED"
                modifs["nb_serv"]=link_infos_received["nb_srv"]
        
        if "nb_hp" in link_infos_received.keys():
            if link_infos_received["nb_hp"]!= link["link_nb_hp"]:
                return "Edit nb_hp not IMPLEMENTED"
                modifs["nb_hp"]=link_infos_received["nb_hp"]
        
        if "ports" in link_infos_received.keys():
            if link_infos_received["ports"]!= link["link_ports"]:
                return "Edit ports not IMPLEMENTED"
                modifs["ports"]=link_infos_received["ports"]
        
        if modifs != {}:
            Gotham_link_BDD.edit_link_DB(DB_settings, modifs, conditions)
            links = Gotham_link_BDD.get_link_infos(DB_settings, id=link_infos_received["id"])
            link = Gotham_normalize.normalize_display_object_infos(links[0],"link")
            return link

        return "Nothing to change"

@app.route('/delete/honeypot', methods=['POST'])
def rm_honeypot():
        # Removes a honeypot object
        # 
        # id (string) : id du honeypot à supprimer

        # Get POST data on JSON format
        data = request.get_json()

        # Get all function's parameters
        id = data["id"]
        
        # Retrieve datacenter's SSH key from config file
        try:
            dc_ssh_key = config['datacenter']['ssh_key']
            dc_ssh_key = base64.b64decode(dc_ssh_key) # ssh_key is byte
            dc_ssh_key = dc_ssh_key.decode('ascii') # ssh_key is ascii string
            dc_ssh_key = StringIO(dc_ssh_key) # ssh_key is a file-like object

        except Exception as e:
            print("Error loading datacenter's SSH key")

        datacenter_settings = {"hostname": dc_ip, "ssh_key": dc_ssh_key, "ssh_port": dc_ssh_port}
        
        try:
            rm_hp.main(DB_settings, datacenter_settings, id)
        
        except Exception as e:
            return "An error occured during the deletion of the honeypot : "+str(e)
        
        return "Deletion completed : " + str(id)

@app.route('/delete/server', methods=['POST'])
def rm_srv():
        # Removes a server object
        # 
        # id (string) : id du serveur à supprimer

        # Get POST data on JSON format
        data = request.get_json()

        # Get all function's parameters
        id = data["id"]

        ##### TODO : ADD ABILITY TO DELETE WITH IP ######
        try:
            rm_server.main(DB_settings, id=id)
        
        except Exception as e:
            return "An error occured during the deletion of the server : "+str(e)
        
        return "Deletion completed : " + str(id)

@app.route('/delete/link', methods=['POST'])
def rm_lk():
        # Removes a link object
        #
        # id (string) : id du lien à supprimer

        # Get POST data on JSON format
        data = request.get_json()

        # Get all function's parameters
        id = data["id"]

        try:
            rm_link.main(DB_settings, id=id)
        
        except Exception as e:
            return "An error occured during the deletion of the link : "+str(e)
        
        return "Deletion completed : " + str(id)

@app.route('/list/honeypot', methods=['GET'])
def ls_honeypot():
        # Gives information on honeypot object
        # 
        # id (string) : id du honeypot à afficher

        hp_infos_received={}

        id = request.args.get('id')
        tags = request.args.get('tags')
        name = request.args.get('name')
        descr = request.args.get('descr')
        port = request.args.get('port')
        state = request.args.get('state')


        if (id) or (tags) or (name) or (descr) or (port) or (state):
            
            if (id):
                hp_infos_received["id"] = id
            else:
                hp_infos_received["id"] = "%"
            
            if (tags):
                hp_infos_received["tags"] = tags
            else:
                hp_infos_received["tags"] = "%"
            
            if (name):
                hp_infos_received["name"] = name
            else:
                hp_infos_received["name"] = "%"
            
            if (descr):
                hp_infos_received["descr"] = descr
            else:
                hp_infos_received["descr"] = "%"
            
            if (port):
                hp_infos_received["port"] = port
            else:
                hp_infos_received["port"] = "%"
            
            if (state):
                hp_infos_received["state"] = state
            else:
                hp_infos_received["state"] = "%"
            

            honeypots_exact = Gotham_link_BDD.get_honeypot_infos(DB_settings, mode=False, id=hp_infos_received["id"], name=hp_infos_received["name"], tags=hp_infos_received["tags"], state=hp_infos_received["state"], descr=hp_infos_received["descr"], port=hp_infos_received["port"])
            honeypots_others = Gotham_link_BDD.get_honeypot_infos(DB_settings, mode=True, id=hp_infos_received["id"], name=hp_infos_received["name"], tags=hp_infos_received["tags"], state=hp_infos_received["state"], descr=hp_infos_received["descr"], port=hp_infos_received["port"])
            
            if honeypots_exact!=[] or honeypots_others != []:
                set_exact={ frozenset(row.items()) for row in honeypots_exact}
                set_others={ frozenset(row.items()) for row in honeypots_others}
                honeypots_others=[dict(i) for i in set_others - set_exact]
                honeypots_exact = [Gotham_normalize.normalize_display_object_infos(honeypot,"hp") for honeypot in honeypots_exact]
                honeypots_others = [Gotham_normalize.normalize_display_object_infos(honeypot,"hp") for honeypot in honeypots_others]
                return {"exact":honeypots_exact,"others":honeypots_others}
            
            else:
                logging.error(f"No honeypot found with given arguments : {hp_infos_received}")
                return "No honeypot found with given arguments"
        
        else:
            honeypots = Gotham_link_BDD.get_honeypot_infos(DB_settings)
            
            if honeypots!=[]:
                honeypots=[Gotham_normalize.normalize_display_object_infos(honeypot,"hp") for honeypot in honeypots]
                return {"honeypots":honeypots}
            else:
                logging.error(f"You tried to list honeypots but no one exists")
                return "No honeypot in database"

@app.route('/list/server', methods=['GET'])
def ls_srv():
        # Gives information on server object
        # 
        # id (string) : id du serveur à afficher

        serv_infos_received = {}

        id = request.args.get("id")
        ip = request.args.get("ip")
        name = request.args.get("name")
        tags = request.args.get("tags")
        state = request.args.get("state")
        descr = request.args.get("descr")
        ssh_port = request.args.get("ssh_port")

        if (id) or (ip) or (name) or (tags) or (state) or (descr) or (ssh_port):
            
            if (id):
                serv_infos_received["id"] = id
            else:
                serv_infos_received["id"] = "%"
            
            if (ip):
                serv_infos_received["ip"] = ip
            else:
                serv_infos_received["ip"] = "%"
            
            if (tags):
                serv_infos_received["tags"] = tags
            else:
                serv_infos_received["tags"] = "%"
            
            if (name):
                serv_infos_received["name"] = name
            else:
                serv_infos_received["name"] = "%"
            
            if (descr):
                serv_infos_received["descr"] = descr
            else:
                serv_infos_received["descr"] = "%"
            
            if (ssh_port):
                serv_infos_received["ssh_port"] = ssh_port
            else:
                serv_infos_received["ssh_port"] = "%"
            
            if (state):
                serv_infos_received["state"] = state
            else:
                serv_infos_received["state"] = "%"
            
            
            servers_exact = Gotham_link_BDD.get_server_infos(DB_settings, mode=False, id=serv_infos_received["id"], ip=serv_infos_received["ip"],  name=serv_infos_received["name"], tags=serv_infos_received["tags"], state=serv_infos_received["state"], descr=serv_infos_received["descr"], ssh_port=serv_infos_received["ssh_port"])
            servers_others = Gotham_link_BDD.get_server_infos(DB_settings, mode=True, id=serv_infos_received["id"], ip=serv_infos_received["ip"],  name=serv_infos_received["name"], tags=serv_infos_received["tags"], state=serv_infos_received["state"], descr=serv_infos_received["descr"], ssh_port=serv_infos_received["ssh_port"])
            
            if servers_exact!=[] or servers_others!=[]:
                set_exact={ frozenset(row.items()) for row in servers_exact}
                set_others={ frozenset(row.items()) for row in servers_others}
                servers_others=[dict(i) for i in set_others - set_exact]
                servers_exact = [Gotham_normalize.normalize_display_object_infos(server,"serv") for server in servers_exact]
                servers_others = [Gotham_normalize.normalize_display_object_infos(server,"serv") for server in servers_others]
                return {"exact":servers_exact,"others":servers_others}
            
            else:
                logging.error(f"No server found with given arguments : {serv_infos_received}")
                return "No server found with given arguments"
        else:
            servers = Gotham_link_BDD.get_server_infos(DB_settings)
            
            if servers!=[]:
                servers=[Gotham_normalize.normalize_display_object_infos(server,"serv") for server in servers]
                return {"servers":servers}
            else:
                logging.error(f"You tried to list servers but no one exists")
                return "No server in database"

@app.route('/list/link', methods=['GET'])
def ls_lk():
        # Gives information on link object
        #
        # id (string) : id du lien à afficher

        link_infos_received = {}

        id = request.args.get("id")
        nb_hp = request.args.get("nb_hp")
        nb_serv = request.args.get("nb_serv")
        tags_hp = request.args.get("tags_hp")
        tags_serv = request.args.get("tags_serv")

        if (id) or (nb_hp) or (nb_serv) or (tags_hp) or (tags_serv):
            
            if (id):
                link_infos_received["id"] = id
            else:
                link_infos_received["id"] = "%"
            
            if (nb_hp):
                link_infos_received["nb_hp"] = nb_hp
            else:
                link_infos_received["nb_hp"] = "%"
            
            if (nb_serv):
                link_infos_received["nb_serv"] = nb_serv
            else:
                link_infos_received["nb_serv"] = "%"
            
            if (tags_hp):
                link_infos_received["tags_hp"] = tags_hp
            else:
                link_infos_received["tags_hp"] = "%"
            
            if (tags_serv):
                link_infos_received["tags_serv"] = tags_serv
            else:
                link_infos_received["tags_serv"] = "%"
        
            links_exact = Gotham_link_BDD.get_link_infos(DB_settings, mode=False, id=link_infos_received["id"], nb_hp=link_infos_received["nb_hp"], nb_serv=link_infos_received["nb_serv"], tags_hp=link_infos_received["tags_hp"], tags_serv=link_infos_received["tags_serv"])
            links_others = Gotham_link_BDD.get_link_infos(DB_settings, mode=True, id=link_infos_received["id"], nb_hp=link_infos_received["nb_hp"], nb_serv=link_infos_received["nb_serv"], tags_hp=link_infos_received["tags_hp"], tags_serv=link_infos_received["tags_serv"])
            
            if links_exact!=[] or links_others!=[]:
                set_exact={ frozenset(row.items()) for row in links_exact}
                set_others={ frozenset(row.items()) for row in links_others}
                links_others=[dict(i) for i in set_others - set_exact]
                links_exact = [Gotham_normalize.normalize_display_object_infos(link,"link") for link in links_exact]
                links_others = [Gotham_normalize.normalize_display_object_infos(link,"link") for link in links_others]
                return {"exact":links_exact,"others":links_others}
            
            else:
                logging.error(f"No link found with given arguments : {link_infos_received}")
                return "No link found with given arguments"

        else:
            links = Gotham_link_BDD.get_link_infos(DB_settings)
            
            if links!=[]:
                links=[Gotham_normalize.normalize_display_object_infos(link,"link") for link in links]
                return {"links":links}
            else:
                logging.error(f"You tried to list links but no one exists")
                return "No link in database"
   

@app.route('/list/all', methods=['GET'])
def ls_all():
        # Gives information on all objects
        
        honeypots = Gotham_link_BDD.get_honeypot_infos(DB_settings)
        
        if honeypots!=[]:
            honeypots=[Gotham_normalize.normalize_display_object_infos(honeypot,"hp") for honeypot in honeypots]
        else:
            honeypots="No honeypot in database"   

        servers = Gotham_link_BDD.get_server_infos(DB_settings)
        
        if servers!=[]:
            servers=[Gotham_normalize.normalize_display_object_infos(server,"serv") for server in servers]
        else:
            servers="No server in database"

        links = Gotham_link_BDD.get_link_infos(DB_settings)
        
        if links!=[]:
            links=[Gotham_normalize.normalize_display_object_infos(link,"link") for link in links]
        else:
            links="No link in database"
        
        return {"honeypots":honeypots,"servers":servers,"links":links}
        


@app.route('/version', methods=['GET'])
def get_version():
        # Return the orchestrator's version
        #

        return "GOTHAM's version : "+version+"\n"

app.run()
