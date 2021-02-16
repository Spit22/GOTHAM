# GENERAL LIBS
import flask
import json
import uuid
import base64
import os
import random
import configparser
from flask import request, jsonify
from io import StringIO # a suppr

# GOTHAM'S Add Scripts
import add_server  
import add_hp
import add_link

# GOTHAM's Remove Scripts
import rm_hp
import rm_server
import rm_link

# GOTHAM'S LIB
import Gotham_link_BDD
import Gotham_check
import Gotham_choose
import Gotham_normalize


app = flask.Flask(__name__)

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


# Cette section remplace temporairement le fichier de configuration /etc/gotham/orchestrator.conf #
app.config["DEBUG"] = True
version = "0.0"
DB_settings = {"username":"gotham", "password":"password", "hostname":"localhost", "port":"3306", "database":"GOTHAM"}
dc_ports_list = range(1024,2048)
dockerfile_storage = "/data/"
# Path to store object's data
store_path = "/data"

###################################################################################################

@app.route('/', methods=['GET'])
def index():
        return 'You\'re on the GOTHAM\'s API'

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

        # Retrieve settings from config file
        config = configparser.ConfigParser()
        config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
        dc_ip = config['datacenter']['ip']
        dc_ssh_key = config['datacenter']['ssh_key']
        dc_ssh_key = base64.b64decode(dc_ssh_key) # ssh_key is byte
        dc_ssh_key = dc_ssh_key.decode('ascii') # ssh_key is ascii string
        dc_ssh_key = StringIO(dc_ssh_key) # ssh_key is a file-like object
        dc_ssh_port = config['datacenter']['ssh_port']

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

        # Retrieve settings from config file
        config = configparser.ConfigParser()
        config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
        ports_separator = config['port']['separator']
        tags_separator = config['tag']['separator']
        dc_ip = config['datacenter']['ip']

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
                with open(honeypots[i%len(honeypots)]["hp_source"], 'r') as file:
                    encoded_dockerfile = base64.b64encode(file.read().encode("ascii"))
                name = (honeypots[i%len(honeypots)]["name"]+"_Duplicat" if len(honeypots[i%len(honeypots)]["name"]+"_Duplicat")<=128 else honeypots[i%len(honeypots)]["name"][:(128-len("_Duplicat"))]+"_Duplicat")
                descr = "Duplication of "+honeypots[i%len(honeypots)]["descr"]
                duplicate_hp_infos={"name": name,"descr": descr,"tags": honeypots[i%len(honeypots)]["tags"].remplace("||",tags_separator),"logs": honeypots[i%len(honeypots)]["logs"],"parser": honeypots[i%len(honeypots)]["parser"],"port": honeypots[i%len(honeypots)]["port"], "dockerfile": encoded_dockerfile}
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
        print("bypassed")
        #add_link.deploy_nginxConf(DB_settings, id, servers)

        # Check redirection is effective on all servers
        for server in servers:
            print("bypassed")
            #connected = Gotham_check.check_server_redirects(server["serv_ip"], server["choosed_port"])
            #if not connected:
            #    return "Error : link is not effective on server "+str(ip_srv)

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
        if id in data.keys():
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
            if hp_infos_received["name"]!= honeypot["hp_name"]:
                modifs["name"]=hp_infos_received["name"]
        if "descr" in hp_infos_received.keys():
            if hp_infos_received["descr"]!= honeypot["hp_descr"]:
                modifs["descr"]=hp_infos_received["descr"]
        if "tags" in hp_infos_received.keys():
            if hp_infos_received["tags"]!= honeypot["hp_tags"]:
                return "Edit tags not IMPLEMENTED"
                modifs["tags"]=hp_infos_received["tags"]
        if "logs" in hp_infos_received.keys():
            if hp_infos_received["logs"]!= honeypot["hp_logs"]:
                return "Edit logs not IMPLEMENTED"
                modifs["logs"]=hp_infos_received["logs"]
        if "parser" in hp_infos_received.keys():
            if hp_infos_received["parser"]!= honeypot["hp_parser"]:
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
        if id in data.keys():
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
            if serv_infos_received["tags"]!= server["serv_tags"]:
                return "Edit tags not IMPLEMENTED"
                modifs["tags"]=serv_infos_received["tags"]
        if "ip" in serv_infos_received.keys():
            if serv_infos_received["ip"]!= server["serv_ip"]:
                return "Edit ip not IMPLEMENTED"
                modifs["ip"]=serv_infos_received["ip"]
        if "ssh_key" in serv_infos_received.keys():
            if serv_infos_received["ssh_key"]!= server["serv_ssh_key"]:
                return "Edit ssh_key not IMPLEMENTED"
                modifs["ssh_key"]=serv_infos_received["ssh_key"]
        if "ssh_port" in serv_infos_received.keys():
            if serv_infos_received["ssh_port"]!= server["serv_ssh_port"]:
                return "Edit ssh_port not IMPLEMENTED"
                modifs["ssh_port"]=serv_infos_received["ssh_port"]
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
        if id in data.keys():
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
            if link_infos_received["tag_srv"]!= link["link_tag_srv"]:
                return "Edit tag_srv not IMPLEMENTED"
                modifs["tag_srv"]=link_infos_received["tag_srv"]
        if "tag_hp" in link_infos_received.keys():
            if link_infos_received["tag_hp"]!= link["link_tag_hp"]:
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

        # Make sure all data are in JSON
        data = json.loads(data)

        # Get all function's parameters
        id = data["id"]

        try:
            rm_hp.main(DB_settings, id)
        except:
            return "An error occured during the deletion of the honeypot"
        return "Deletion completed : " + str(id)

@app.route('/delete/server', methods=['POST'])
def rm_srv():
        # Removes a server object
        # 
        # id (string) : id du serveur à supprimer

        # Get POST data on JSON format
        data = request.get_json()

        # Make sure all data are in JSON
        #data = json.loads(data)

        # Get all function's parameters
        id = data["id"]
        ##### ADD ABILITY TO DELETE WITH IP ######
        try:
            rm_server.main(DB_settings, id=id)
        except:
            return "An error occured during the deletion of the server"
        return "Deletion completed : " + str(id)

@app.route('/delete/link', methods=['POST'])
def rm_lk():
        # Removes a link object
        #
        # id (string) : id du lien à supprimer

        # Get POST data on JSON format
        
        data = request.get_json()

        # Make sure all data are in JSON
        #data = json.loads(data)

        # Get all function's parameters
        id = data["id"]

        try:
            rm_link.main(DB_settings, id=id)
        except:
            return "An error occured during the deletion of the link"
        return "Deletion completed : " + str(id)

@app.route('/list/honeypot', methods=['GET'])
def ls_honeypot():
        # Gives information on honeypot object
        # 
        # id (string) : id du honeypot à afficher

        hp_infos_received={}

        if (id):
            hp_infos_received["id"] = id
            try:
                # Normalize infos
                hp_infos_received = Gotham_normalize.normalize_honeypot_infos(hp_infos_received)            
            except Exception as e:
                return "Invalid data sent "+str(e)
            honeypots = Gotham_link_BDD.get_honeypot_infos(DB_settings, id=hp_infos_received["id"])
            if honeypots!=[]:
                honeypot = Gotham_normalize.normalize_display_object_infos(honeypots[0],"hp")
                return honeypot
            else:
                logging.error(f"You tried to list a honeypot that doesn't exists with the id = {id}")
                return "Unknown id "+hp_infos_received["id"]+" for Honeypot"
        else:
            honeypots = Gotham_link_BDD.get_honeypot_infos(DB_settings)
            if honeypots!=[]:
                honeypots=[Gotham_normalize.normalize_display_object_infos(honeypot,"hp") for honeypot in honeypots]
                return honeypots
            else:
                logging.error(f"You tried to list honeypots but no one exists")
                return "No honeypot in database"

@app.route('/list/server', methods=['GET'])
def ls_srv():
        # Gives information on server object
        # 
        # id (string) : id du serveur à afficher

        serv_infos_received = {}

        if (id):
            serv_infos_received["id"] = id
            try:
                # Normalize infos
                serv_infos_received = Gotham_normalize.normalize_server_infos(serv_infos_received)            
            except Exception as e:
                return "Invalid data sent "+str(e)
            servers = Gotham_link_BDD.get_server_infos(DB_settings, id=serv_infos_received["id"])
            if servers!=[]:
                server = Gotham_normalize.normalize_display_object_infos(servers[0],"serv")
                return server
            else:
                logging.error(f"You tried to list a server that doesn't exists with the id = {id}")
                return "Unknown id "+serv_infos_received["id"]+" for server"
        else:
            servers = Gotham_link_BDD.get_server_infos(DB_settings)
            if servers!=[]:
                servers=[Gotham_normalize.normalize_display_object_infos(server,"serv") for server in servers]
                return servers
            else:
                logging.error(f"You tried to list servers but no one exists")
                return "No server in database"

@app.route('/list/link', methods=['GET'])
def ls_lk():
        # Gives information on link object
        #
        # id (string) : id du lien à afficher

        link_infos_received = {}

        if (id):
            link_infos_received["id"] = id
            try:
                # Normalize infos
                link_infos_received = Gotham_normalize.normalize_link_infos(link_infos_received)            
            except Exception as e:
                return "Invalid data sent "+str(e)
            links = Gotham_link_BDD.get_link_infos(DB_settings, id=link_infos_received["id"])
            if links!=[]:
                link = Gotham_normalize.normalize_display_object_infos(links[0],"link")
                return link
            else:
                logging.error(f"You tried to list a link that doesn't exists with the id = {id}")
                return "Unknown id "+link_infos_received["id"]+" for link"
        else:
            links = Gotham_link_BDD.get_link_infos(DB_settings)
            if links!=[]:
                links=[Gotham_normalize.normalize_display_object_infos(link,"link") for link in links]
                return links
            else:
                logging.error(f"You tried to list links but no one exists")
                return "No link in database"
        

@app.route('/version', methods=['GET'])
def get_version():
        # Return the orchestrator's version
        #

        return "GOTHAM's version : "+version

app.run()
