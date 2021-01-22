# GENERAL LIBS
import flask
import json
import uuid
import base64
import os
from flask import request, jsonify
from io import StringIO # a suppr

# GOTHAM'S LIBS
import add_server  
import Gotham_link_BDD
import Gotham_check
import add_hp

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
        #for mapped_port in dc_ports_list:
        #    if Gotham_check.is_dc_port_available(mapped_port):
        #        available_port = True
        #        break
        #    available_port = False

        # Check if an available port was found
        #if not available_port:
        #    return "Datacenter : no port available for mapping"
        # TEMP
        mapped_port = "2200"
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
        dc_connect = add_hp.deploy_container(dc_ip, dc_ssh_port, dc_ssh_key, dockerfile_path)
        if not dc_connect:
            return "An error occured in the ssh connection"

        # Store new hp and tags in the database
        sql_data = {'id':str(id),'name':str(name),'descr':str(descr),'tag':str(tags),'port':str(port),'parser':str(parser),'logs':str(logs),'source':str(dockerfile_path),'state':'INACTIVE','id_container':'NULL'}
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
        # tag_srv (list) : tag du/des serveurs ciblés
        # tag_hp (list) : tag du/des hp ciblés
        # nb_srv (int) : nombre de serveurs ciblés
        # nb_hp (int) : nombre de hp ciblés

        # Get POST data on JSON format
        data = request.json

        # Make sure all data are in JSON
        data = json.loads(data)

        # Get all function's parameters
        tag_srv = data["tag_srv"]
        tag_hp = data["tag_hp"]
        nb_srv = data["nb_srv"]
        nb_hp = data["nb_hp"]

        return "NOT IMPLEMENTED"

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
