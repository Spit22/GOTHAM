# GENERAL LIBS
import flask
import json
import uuid
import base64
from flask import request, jsonify
from io import StringIO # a suppr

# GOTHAM'S LIBS
import add_server  
import Gotham_link_BDD
import Gotham_check


app = flask.Flask(__name__)

# Cette section remplace temporairement le fichier de configuration /etc/gotham/orchestrator.conf #
app.config["DEBUG"] = True
version = "0.0"
db_settings = {"username":"root", "password":"password", "hostname":"localhost", "port":"3306", "database":"GOTHAM"}
###################################################################################################

@app.route('/', methods=['GET'])
def index():
        return 'You\'re on the GOTHAM\'s API'

@app.route('/add/honeypot', methods=['POST'])
def add_hp():
        # Creates a honeypot object
        # 
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
        name = data["name"]
        descr = data["descr"]
        tags = data["tags"]
        logs = data["parser"]

        return "NOT IMPLEMENTED"

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

	# If all checks are ok, we can generate a an id for the new server
        id = 'sv-'+str(uuid.uuid4().hex)

	# Deploy the reverse-proxy service on the new server
        try:
            add_server.deploy(ip, ssh_port, deploy_ssh_key)
        except Exception as e:
            return "Something went wrong while deploying Reverse-Proxy"

	# Store new server and tags on the internal database
        try:
            sql_data = {'id':str(id),'name':str(name),'descr':str(descr),'tag':str(tags),'ip':str(ip),'ssh_key':str(ssh_key),'ssh_port':str(ssh_port),'state':'INACTIVE'}
            Gotham_link_BDD.add_server_DB(db_settings, sql_data)
        except Exception as e:
            return "Internal database error"

        # If all operations succeed
        return "OK : "+str(id)

@app.route('/add/link', methods=['POST'])
def add_link():
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
