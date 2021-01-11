import flask
import json
from flask import request, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"] = True

version = "0.0"

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
def add_server():
        # Creates a server object
        # 
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
        name = data["name"]
        descr = data["descr"]
        tags = data["tags"]
        ip = data["ip"]
        ssh_key = data["ssh_key"]
        ssh_port = data["ssh_port"]

        return "NOT IMPLEMENTED"

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
