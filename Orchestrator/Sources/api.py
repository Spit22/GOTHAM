# GENERAL LIBS
import flask
import json
import uuid
import base64
import os
from flask import request, jsonify
from io import StringIO # a suppr

# GOTHAM'S Scripts
import add_server  
import add_hp
import add_link

# GOTHAM'S LIB
import Gotham_link_BDD
import Gotham_check


app = flask.Flask(__name__)

# Cette section remplace temporairement le fichier de configuration /etc/gotham/orchestrator.conf #
app.config["DEBUG"] = True
version = "0.0"
db_settings = {"username":"root", "password":"password", "hostname":"localhost", "port":"3306", "database":"GOTHAM"}
dc_ports_list = range(1024,2048)
dockerfile_storage = "/data/"
dc_ip = "172.16.2.250"
dc_ssh_port = "22"
dc_ssh_key = StringIO("""-----BEGIN OPENSSH PRIVATE KEY-----
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
-----END OPENSSH PRIVATE KEY-----""")
# Path to store object's data
store_path = "/data"

###################################################################################################

@app.route('/', methods=['GET'])
def index():
        return 'You\'re on the GOTHAM\'s API'

@app.route('/add/honeypot', methods=['POST'])
def add_honeypot():
        # Creates a honeypot object
        # 
        # name (string) : nom du honeypot
        # descr (string) : description du honeypot
        # tags (list) : liste des tags du honeypot
        # logs (string) : path des logs à monitorer
        # parser (string) : règle de parsing des logs monitorés
        # dockerfile (string) : dockerfile to generate the honeypot on datacenter, base64 encoded
        # service_port (int) : port on which the honeypot will lcoally listen

        # Get POST data on JSON format
        data = request.get_json()

        # Get all function's parameters
        name = data["name"]
        descr = data["descr"]
        tags = data["tags"]
        logs = data["logs"]
        parser = data["parser"]
        dockerfile = data["dockerfile"]
        dockerfile = base64.b64decode(dockerfile)
        dockerfile = dockerfile.decode('ascii')
        dockerfile = str(dockerfile)
        port = data["port"]
        

        # First find an available port to map on datacenter
        used_ports = Gotham_check.check_used_port(db_settings)
        available_port = False

        for mapped_port in dc_ports_list:
            if mapped_port not in used_ports:
                available_port = True
                break

        # Check if an available port was found
        if not available_port:
            return "Datacenter : no port available for mapping"

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

        # Store new hp and tags in the database
        sql_data = {'id':str(id),'name':str(name),'descr':str(descr),'tag':str(tags),'port_container':str(port),'parser':str(parser),'logs':str(logs),'source':str(dockerfile_path),'state':'INACTIVE','port':mapped_port}
        Gotham_link_BDD.add_honeypot_DB(db_settings, sql_data)

        # If all operations succeed
        return "OK : "+str(id)

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
            name = data["name"]
            descr = data["descr"]
            tags = data["tags"]
            ip = data["ip"]
            encoded_ssh_key = data["ssh_key"]
            # Decode and format the ssh key
            ssh_key = base64.b64decode(encoded_ssh_key) # ssh_key is byte
            ssh_key = ssh_key.decode('ascii') # ssh_key is ascii string
            check_ssh_key = StringIO(ssh_key) # ssh_key for the check is a file-like object
            deploy_ssh_key = StringIO(ssh_key) # ssh_key for the deployment is a file-like object
            ssh_port = data["ssh_port"]

        except Exception as e:
            return "Invalid data sent "+str(e)

	# First check the ip not already exists in database
        exists = Gotham_check.check_doublon_server(db_settings, ip)
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

	# Store new server and tags in the internal database
        try:
            sql_data = {'id':str(id),'name':str(name),'descr':str(descr),'tag':str(tags),'ip':str(ip),'ssh_key':str(ssh_key),'ssh_port':str(ssh_port),'state':'INACTIVE'}
            Gotham_link_BDD.add_server_DB(db_settings, sql_data)
        except Exception as e:
            return "Internal database error"

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
        # exposed_port (list): list des ports à utiliser

        # Get POST data on JSON format
        data = request.get_json()


        # Get all function's parameters
        tags_serv = str(data["tags_serv"])
        tags_hp = str(data["tags_hp"])
        nb_srv = int(data["nb_srv"])
        nb_hp = int(data["nb_hp"])
        exposed_ports = str(data["exposed_ports"])
        exposed_ports_list = exposed_ports.split(',')

        print("DEBUG : vars ok")

        # We check that no link exists with same tags, otherwise return error
        existingLinks = Gotham_link_BDD.get_link_infos(db_settings, tags_hp=tags_hp, tags_serv=tags_serv)
        if existingLinks != []:
            return "A link is already configured for this tags"
        print(existingLinks)

        print("DEBUG : links already configured ? ok")

        # We check all provided server tags exists, otherwise return error
        for tag_serv in tags_serv:
            existingServTag = Gotham_link_BDD.get_tag_infos(db_settings, tag=tag_serv)
            if existingServTag == []:
                return "Error with tag "+str(tag_serv)+": tag does not exists"
            print(existingServTag)

        print("DEBUG : tags exists ok")

        # We check all provided hp tags exists, otherwise return error
        for tag_hp in tags_hp:
            existingHpTag = Gotham_link_BDD.get_tag_infos(db_settings, tag_hp)
            if existingHpTag == []:
                return "Error with tag "+str(tag_hp)+": tag does not exists"
            print(existingHpTag)

        print("DEBUG : tags exists 2 ok")

        # Get all honeypots corresponding to tags
        honeypots = Gotham_link_BDD.get_honeypot_infos(db_settings, tags=tags_hp)

        print("Get all hp OK")

        # Get all servers corresponding to tags
        servers = Gotham_link_BDD.get_server_infos(db_settings, tags=tags_serv)

        print("Get all srv ok")

        # Filter servers in those who have one of ports open
        #for server in servers:
        #    if server[""]

        # Checking we have enough servers for the nb_srv directive, otherwise return error
        if len(servers) < nb_srv:
            return "Can't deploy link on "+str(nb_srv)+" servers while there is only "+str(len(servers))+" servers available"
        # Checking we have enough honeypots for the nb_hp directive
        if len(honeypots) < nb_hp:
            # If we don't have any honeypots corresponding, just return error,
            if len(honeypots) < 1:
                return "Can't configure link if there is no at least one hp corresponding to request"
            # If we don't have enough but we have one or more
            # Choose one of available honeypots (the best scored), and obtain informations
            # Duplicate this honeypot
        print("DEBUG : check nb ok")        
        # If having enough honeypots, choose best honeypots (the lower scored)
        #for honeypot in honeypots:
        #    hp_score[honeypot] = 0
        #    # Add 10 pts per servers redirecting to the honeypot
        #    if nb_mapping > 0:
        #        hp_score[honeypot] += 10 * nb_mapping

        # Choose best servers (the lower scored)
        #for server in servers:
        #    srv_score[server] = 0
        #    # Add 10 pts per links already configured on server
        #    if nb_linked > 0:
        #        srv_score[server] += 10 * nb_link
        
        # Generate the dict servers associating ip and exposed_port
        avb_servers = {"172.16.2.201":"8080"}
        # Create link id
        id = 'lk-'+str(uuid.uuid4().hex)

        # Generate NGINX configurations for each redirection on a specific exposed_port
        for exposed_port in exposed_ports_list:
            add_link.generate_nginxConf(db_settings, id, dc_ip, honeypots, exposed_port)
        print("DEBUG : gen config ok")
        # Deploy new reverse-proxies's configurations on servers
        add_link.deploy_nginxConf(db_settings, id, avb_servers)
        print("DEBUG : deploy conf ok")
        # Check redirection is effective on all servers
        for avb_server in avb_servers:
            ip_srv = avb_server
            exposed_port = avb_servers[avb_server]
            connected = Gotham_check.check_server_redirects(ip_srv, exposed_port)
            if not connected:
                return "Error : link is not effective on server "+str(ip_srv)
        print("DEBUG : check link ok")
        # Insert new link object in database
        sql_data = {"id":id, "nb_hp": nb_hp, "nb_serv": nb_srv, "tags_hp":tags_hp, "tags_serv":tags_serv, "ports":exposed_ports}
        Gotham_link_BDD.add_link_DB(db_settings, sql_data)
        print("db write ok")
        return "OK : "+str(id)

@app.route('/edit/honeypot', methods=['POST'])
def edit_hp():
        # Edits a honeypot object
        # 
        # id (string) : id du honeypot à modifier
        # name (string) : nom du honeypot
        # descr (string) : description du honeypot
        # tags (list) : liste des tags du honeypot
        # logs (string) : path des logs à monitorer
        # parser (string) : règle de parsing des logs monitorés

        # Get POST data on JSON format
        data = request.json

        # Make sure all data are in JSON
        data = json.loads(data)

        # Get all function's parameters
        id = data["id"]
        name = data["name"]
        descr = data["descr"]
        tags = data["tags"]
        logs = data["parser"]

        return "NOT IMPLEMENTED"

@app.route('/edit/server', methods=['POST'])
def edit_server():
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

        # Get all function's parameters
        id = data["id"]
        name = data["name"]
        descr = data["descr"]
        tags = data["tags"]
        ip = data["ip"]
        ssh_key = data["ssh_key"]
        ssh_port = data["ssh_port"]

        return "NOT IMPLEMENTED"



@app.route('/edit/link', methods=['POST'])
def edit_link():
        # Edits a link object
        #
        # id (string) : id du lien à modifier
        # tag_srv (list) : tag du/des serveurs ciblés
        # tag_hp (list) : tag du/des hp ciblés
        # nb_srv (int) : nombre de serveurs ciblés
        # nb_hp (int) : nombre de hp ciblés

        # Get POST data on JSON format
        data = request.json

        # Make sure all data are in JSON
        data = json.loads(data)

        # Get all function's parameters
        id = data["id"]
        tag_srv = data["tag_srv"]
        tag_hp = data["tag_hp"]
        nb_srv = data["nb_srv"]
        nb_hp = data["nb_hp"]

        return "NOT IMPLEMENTED"

@app.route('/delete/honeypot', methods=['POST'])
def rm_hp():
        # Removes a honeypot object
        # 
        # id (string) : id du honeypot à supprimer

        # Get POST data on JSON format
        data = request.json

        # Make sure all data are in JSON
        data = json.loads(data)

        # Get all function's parameters
        id = data["id"]

        return "NOT IMPLEMENTED"

@app.route('/delete/server', methods=['POST'])
def rm_server():
        # Removes a server object
        # 
        # id (string) : id du serveur à supprimer

        # Get POST data on JSON format
        data = request.json

        # Make sure all data are in JSON
        data = json.loads(data)

        # Get all function's parameters
        id = data["id"]

        return "NOT IMPLEMENTED"


@app.route('/delete/link', methods=['POST'])
def rm_link():
        # Removes a link object
        #
        # id (string) : id du lien à supprimer

        # Get POST data on JSON format
        data = request.json

        # Make sure all data are in JSON
        data = json.loads(data)

        # Get all function's parameters
        id = data["id"]

        return "NOT IMPLEMENTED"

@app.route('/list/honeypot', methods=['GET'])
def ls_hp():
        # Gives information on honeypot object
        # 
        # id (string) : id du honeypot à afficher

        if (id):
            return "/info like, NOT IMPLEMENTED"

        return "NOT IMPLEMENTED"

@app.route('/list/server', methods=['GET'])
def ls_server():
        # Gives information on server object
        # 
        # id (string) : id du serveur à afficher

        if (id):
            return "/info like, NOT IMPLEMENTED"


        return "NOT IMPLEMENTED"


@app.route('/list/link', methods=['GET'])
def ls_link():
        # Gives information on link object
        #
        # id (string) : id du lien à afficher

        if (id):
            return "/info like, NOT IMPLEMENTED"


        return "NOT IMPLEMENTED"

@app.route('/version', methods=['GET'])
def get_version():
        # Return the orchestrator's version
        #

        return "GOTHAM's version : "+version

app.run()
