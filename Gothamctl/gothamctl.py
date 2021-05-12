#!/bin/python3

import argparse
import os
import sys
import requests
import base64
import configparser
import tabulate

#===Logging components===#
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    #A modifier

def add_server(args):
    # Query /add/server to create server
    #
    # args (obj) : passed commandline argument
    #
    # Show id of created server id

    name = args.name
    descr = args.descr
    tags = args.tag
    ip = args.ip
    autotags = args.autotags

    try:
        ssh_key = str(base64.b64encode(args.key.read().encode("ascii")).decode("ascii"))
    except:
        print("Key not seems to be b64 encoded")
        sys.exit(1)
    ssh_port = args.port

    # Define the queried endpoint
    endpoint = "/add/server"

    # Before external configuration
    gp = args.gotham_port
    gh = args.gotham_hostname

    # Forge url
    url = gh + ":" + gp + endpoint

    # Forge POST data
    data = {
        "ip": ip,
        "name": name,
        "descr": descr,
        "tags": tags,
        "ssh_key": ssh_key,
        "ssh_port": ssh_port
    }

    if autotags:
        data["autotags"] = "1"
    else:
        data["autotags"] = "0"

    # Query URL and get json
    data = requests.post(url, json=data)

    # Show result
    print(data.json())


def add_hp(args):
    # Query /add/honeypot to create honeypot
    #
    # args (obj) : passed commandline argument
    #
    # Show id of created honeypot id

    name = args.name
    descr = args.descr
    tags = args.tag
    parser = args.parser
    logs = args.logs
    try:
        src = str(base64.b64encode(args.src.read().encode("ascii")).decode("ascii"))
    except:
        print("Source not seems to be b64 encoded")
        sys.exit(1)
    port = args.port

    # Define the queried endpoint
    endpoint = "/add/honeypot"

    # Before external configuration
    gp = args.gotham_port
    gh = args.gotham_hostname

    # Forge url
    url = gh + ":" + gp + endpoint

    # Forge POST data
    data = {
        "name": name,
        "descr": descr,
        "tags": tags,
        "parser": parser,
        "logs": logs,
        "dockerfile": src,
        "port": port
    }

    # Query URL and get json
    data = requests.post(url, json=data)

    # Show result
    print(data.json())


def add_link(args):
    # Query /add/link to create link
    #
    # args (obj) : passed commandline argument
    #
    # Show id of created link id

    tags_hp = args.tags_hp
    tags_serv = args.tags_serv
    exposed_ports = args.ports
    nb_hp = args.nb_hp
    nb_serv = args.nb_serv

    # Define the queried endpoint
    endpoint = "/add/link"

    # Before external configuration
    gp = args.gotham_port
    gh = args.gotham_hostname

    # Forge url
    url = gh + ":" + gp + endpoint

    # Forge POST data
    data = {
        "tags_serv": tags_serv,
        "tags_hp": tags_hp,
        "nb_hp": nb_hp,
        "nb_serv": nb_serv,
        "exposed_ports": exposed_ports,
    }

    # Query URL and get json
    data = requests.post(url, json=data)

    # Show result
    print(data.json())


def rm_server(args):
    # Query /delete/server to delete server
    #
    # args (obj) : passed commandline argument
    #
    # Show id of deleted server id

    id = args.id

    # Define the queried endpoint
    endpoint = "/delete/server"

    # Before external configuration
    gp = args.gotham_port
    gh = args.gotham_hostname

    # Forge url
    url = gh + ":" + gp + endpoint

    # Forge POST data
    data = {
        "id": id
    }

    # Query URL and get json
    data = requests.post(url, json=data)

    # Show result
    print(data.json())


def rm_hp(args):
    # Query /delete/honeypot to delete honeypot
    #
    # args (obj) : passed commandline argument
    #
    # Show id of deleted honeypot id

    id = args.id

    # Define the queried endpoint
    endpoint = "/delete/honeypot"

    # Before external configuration
    gp = args.gotham_port
    gh = args.gotham_hostname

    # Forge url
    url = gh + ":" + gp + endpoint

    # Forge POST data
    data = {
        "id": id
    }

    # Query URL and get json
    data = requests.post(url, json=data)

    # Show result
    print(data.text)


def rm_link(args):
    # Query /delete/link to delete link
    #
    # args (obj) : passed commandline argument
    #
    # Show id of deleted link id

    id = args.id

    # Define the queried endpoint
    endpoint = "/delete/link"

    # Before external configuration
    gp = args.gotham_port
    gh = args.gotham_hostname

    # Forge url
    url = gh + ":" + gp + endpoint

    # Forge POST data
    data = {
        "id": id
    }

    # Query URL and get json
    data = requests.post(url, json=data)

    # Show result
    print(data.json())


def edit_server(args):
    # Query /edit/server to edit server
    #
    # args (obj) : passed commandline argument
    #
    # Show modified server

    # id of the object we want to edit
    id = args.id

    name = args.name
    descr = args.descr
    tags = args.tag
    ip = args.ip
    if args.key:
        ssh_key = str(base64.b64encode(args.key.read().encode("ascii")).decode("ascii"))
    else:
        ssh_key = False

    ssh_port = args.port

    # Define the queried endpoint
    endpoint = "/edit/server"

    # Before external configuration
    gp = args.gotham_port
    gh = args.gotham_hostname

    # Forge url
    url = gh + ":" + gp + endpoint

    # Forge POST data
    data = {"id": id}
    if ip:
        data["ip"] = ip
    if name:
        data["name"] = name
    if descr:
        data["descr"] = descr
    if tags:
        data["tags"] = tags
    if ssh_key:
        data["ssh_key"] = ssh_key
    if ssh_port:
        data["ssh_port"] = ssh_port

    # Query URL and get json
    data = requests.post(url, json=data)

    # Show result
    print(data.json())


def edit_hp(args):
    # Query /edit/honeypot to edit honeypot
    #
    # args (obj) : passed commandline argument
    #
    # Show modified honeypot

    # id of the object we want to edit
    id = args.id

    name = args.name
    descr = args.descr
    tags = args.tag
    parser = args.parser
    logs = args.logs
    port = args.port

    if args.src:
        src = str(base64.b64encode(args.src.read().encode("ascii")).decode("ascii"))
    else:
        src = False

    # Define the queried endpoint
    endpoint = "/edit/honeypot"

    # Before external configuration
    gp = args.gotham_port
    gh = args.gotham_hostname

    # Forge url
    url = gh + ":" + gp + endpoint

    # Forge POST data
    data = {"id": id}
    if name:
        data["name"] = name
    if descr:
        data["descr"] = descr
    if tags:
        data["tags"] = tags
    if parser:
        data["parser"] = parser
    if logs:
        data["logs"] = logs
    if src:
        data["dockerfile"] = src
        print("hi")
    if port:
        data["port"] = port

    # Query URL and get json
    data = requests.post(url, json=data)

    # Show result
    print(data.json())


def edit_link(args):
    # Query /edit/link to edit link
    #
    # args (obj) : passed commandline argument
    #
    # Show modified link

    # id of the object we want to edit
    id = args.id

    tags_hp = args.tags_hp
    tags_serv = args.tags_serv
    nb_hp = args.nb_hp
    nb_serv = args.nb_serv
    exposed_ports = args.ports

    # Define the queried endpoint
    endpoint = "/edit/link"

    # Before external configuration
    gp = args.gotham_port
    gh = args.gotham_hostname

    # Forge url
    url = gh + ":" + gp + endpoint

    # Forge POST data
    data = {"id": id}
    if tags_serv:
        data["tags_serv"] = tags_serv
    if tags_hp:
        data["tags_hp"] = tags_hp
    if nb_hp:
        data["nb_hp"] = nb_hp
    if nb_serv:
        data["nb_serv"] = nb_serv
    if exposed_ports:
        data["exposed_ports"] = exposed_ports

    # Query URL and get json
    data = requests.post(url, json=data)

    # Show result
    print(data.json())


def list_server(args):
    # Query /list/server and format data into a table
    #
    # args (obj) : passed commandline argument
    #
    # Print string formatted table

    # Retrieve  internaldb settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Gothamctl/Config/config.ini')
    serv_display = {"default": config['serv_display']['default'], "wide": config['serv_display']['wide'],
               "tree": config['serv_display']['tree'], "json": config['serv_display']['json']}

    # Define the queried endpoint
    endpoint = "/list/server"

    # Before external configuration
    gp = args.gotham_port
    gh = args.gotham_hostname

    # Get id of server
    id = args.id

    # Get format of the display
    format = args.o

    # If id set, query only for 1 server
    if id:
        # Forge url
        url = gh + ":" + gp + endpoint + "?id=" + id
    else:
        # Else query all servers in db
        # Forge url
        url = gh + ":" + gp + endpoint

    # Query URL and get json
    data = requests.get(url)

    # Show result
    print(data.json())
    if format not in serv_display.keys():
        print("Error Format") #A modifier
    else:
        serv_keys_display = serv_display[format].split(',')
        if 'error' in data.keys():
            print(data['error'])
        elif 'servers' in data.keys():
            servers = data['servers']
            servers_infos = []
            for server in servers:
                server_infos = {}
                for key in serv_keys_display:
                   server_infos[key] = server['serv_' + key]
                servers_infos.append(server_infos)
            print(tabulate.tabulate(servers_infos, headers = 'keys')
        elif 'exact' in data.keys() and 'others' in data.keys():
            # A faire
        else:
            print("ERROR") # A modifier


def list_hp(args):
    # Query /list/honeypot and format data into a table
    #
    # args (obj) : passed commandline argument
    #
    # Print string formatted table

    # Retrieve  internaldb settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Gothamctl/Config/config.ini')
    hp_display = {"default": config['hp_display']['default'], "wide": config['hp_display']['wide'],
               "tree": config['hp_display']['tree'], "json": config['hp_display']['json']}

    # Define the queried endpoint
    endpoint = "/list/honeypot"

    # Before external configuration
    gp = args.gotham_port
    gh = args.gotham_hostname

    # Get id of honeypot
    id = args.id

    # Get format of the display
    format = args.o

    # If id set, query only for 1 honeypot
    if id:
        # Forge url
        url = gh + ":" + gp + endpoint + "?id=" + id
    else:
        # Else query all honeypots in db
        # Forge url
        url = gh + ":" + gp + endpoint

    # Query URL and get json
    data = requests.get(url)

    # Show result
    print(data.json())

    if format not in hp_display.keys(): #On check si le format est bien présent parmi les keys du dictionnaire hp_display
        print("Error Format") #A modifier #Si le format n'est pas présent alors on retourne "error format"
    else: #s'il n'y a pas d'erreur on passe à la suite
        hp_keys_display = hp_display[format].split(',') #On place le résultat du split du dico hp_display selon un certain format (default, wide, etc) dans une variable hp_keys_display
        if 'error' in data.keys(): #Si l'output est une erreur
            print(data['error']) #on retourne "error"
        elif 'hps' in data.keys(): #Si l'output est un hps
            hps = data['hps'] #alors on récupère dans la variable hps (qui est un dico) les dico contenus derrière hps (l'output)
            hps_infos = [] #et on édite la liste vide hps_infos
            for hp in hps: #pour tous les hp (variable ici) dans le dico hps
                hp_infos = {} #on édite le dico hp_infos
                for key in hp_keys_display: #pour toutes les keys splitées dans la variable hp_keys_display
                   hp_infos[key] = hp['hp_' + key] #on récupère toutes les valeurs avec pour titre hp_key (hp_id, hp_name, etc)
                hps_infos.append(hp_infos) #on insert les valeurs dans le dico hp_infos
            print(tabulate.tabulate(hps_infos, headers = 'keys') #on crée la table avec pour headers toutes les keys qui étaient contenues dans hp_keys_display
        elif 'exact' in data.keys() and 'others' in data.keys(): #On check si l'output est un exact ou un other 
            # A faire
        else:
            print("ERROR") # A modifier


def list_link(args):
    # Query /list/link and format data into a table
    #
    # args (obj) : passed commandline argument
    #
    # Print string formatted table

    # Retrieve  internaldb settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Gothamctl/Config/config.ini')
    link_display = {"default": config['link_display']['default'], "wide": config['link_display']['wide'],
               "tree": config['link_display']['tree'], "json": config['link_display']['json']}
    # Define the queried endpoint
    endpoint = "/list/link"

    # Before external configuration
    gp = args.gotham_port
    gh = args.gotham_hostname

    # Get id of link
    id = args.id

    # Get format of the display
    format = args.o

    # If id set, query only for 1 link
    if id:
        # Forge url
        url = gh + ":" + gp + endpoint + "?id=" + id
    else:
        # Else query all links in db
        # Forge url
        url = gh + ":" + gp + endpoint

    # Query URL and get json
    data = requests.get(url)

    # Show result
    print(data.json())
    if format not in link_display.keys():
        print("Error Format") #A modifier
    else:
        link_keys_display = link_display[format].split(',')
        if 'error' in data.keys():
            print(data['error'])
        elif 'links' in data.keys():
            links = data['links']
            links_infos = []
            for link in linkss:
                link_infos = {}
                for key in link_keys_display:
                   link_infos[key] = link['lk_' + key]
                links_infos.append(link_infos)
            print(tabulate.tabulate(links_infos, headers = 'keys')
        elif 'exact' in data.keys() and 'others' in data.keys():
            # A faire
        else:
            print("ERROR") # A modifier

if __name__ == "__main__":
    # Create the parser
    parser = argparse.ArgumentParser(description='Gothamctl')

    # Configure main parser
    parser._positionals.title = 'ARGUMENTS'
    parser._optionals.title = 'OPTIONS'

    # URL arguments
    parser.add_argument('-host', dest="gotham_hostname", help='hostname of the orchestrator', required=True)
    parser.add_argument('-port', dest="gotham_port", help='administration port of the orchestrator', required=True)

    # Create main subparsers
    subparsers = parser.add_subparsers(help='sub-command help')

    # Create operation parsers
    parser_add = subparsers.add_parser('add', help='operation add')
    parser_remove = subparsers.add_parser('rm', help='operation remove')
    parser_edit = subparsers.add_parser('edit', help='operation edit')
    parser_list = subparsers.add_parser('ls', help='operation list')

    # Create object subparsers
    subparsers_add = parser_add.add_subparsers()
    subparsers_remove = parser_remove.add_subparsers()
    subparsers_edit = parser_edit.add_subparsers()
    subparsers_list = parser_list.add_subparsers()

    # Create add parsers
    parser_add_hp = subparsers_add.add_parser('hp', help='honeypot')
    parser_add_server = subparsers_add.add_parser('server', help='server')
    parser_add_link = subparsers_add.add_parser('link', help='link')
    # Affect functions to parsers
    parser_add_hp.set_defaults(func=add_hp)
    parser_add_server.set_defaults(func=add_server)
    parser_add_link.set_defaults(func=add_link)
    # Create remove parsers
    parser_remove_hp = subparsers_remove.add_parser('hp', help='honeypot')
    parser_remove_server = subparsers_remove.add_parser('server', help='server')
    parser_remove_link = subparsers_remove.add_parser('link', help='link')
    # Affect functions to parsers
    parser_remove_hp.set_defaults(func=rm_hp)
    parser_remove_server.set_defaults(func=rm_server)
    parser_remove_link.set_defaults(func=rm_link)
    # Create edit parsers
    parser_edit_hp = subparsers_edit.add_parser('hp', help='honeypot')
    parser_edit_server = subparsers_edit.add_parser('server', help='server')
    parser_edit_link = subparsers_edit.add_parser('link', help='link')
    # Affect functions to parsers
    parser_edit_hp.set_defaults(func=edit_hp)
    parser_edit_server.set_defaults(func=edit_server)
    parser_edit_link.set_defaults(func=edit_link)
    # Create list parsers
    parser_list_hp = subparsers_list.add_parser('hp', help='honeypot')
    parser_list_server = subparsers_list.add_parser('server', help='server')
    parser_list_link = subparsers_list.add_parser('link', help='link')
    # Affect functions to parsers
    parser_list_hp.set_defaults(func=list_hp)
    parser_list_server.set_defaults(func=list_server)
    parser_list_link.set_defaults(func=list_link)

    # =====ADD ARGUMENTS=====#
    # Create add_hp arguments
    parser_add_hp.add_argument('-name', help='Name of the honeypot', required=True)
    parser_add_hp.add_argument('-descr', help='Description of the honeypot', required=True)
    parser_add_hp.add_argument('-tag', help='Tags of the honeypot', required=True)
    parser_add_hp.add_argument('-parser', help='Parsing rules for logs of the honeypot', required=True)
    parser_add_hp.add_argument('-logs', help='Path of log files of the honeypot', required=True)
    parser_add_hp.add_argument('-src', type=argparse.FileType('r'),
                               help='Base64 encoded source file of the honepot (Dockerfile)', required=True)
    parser_add_hp.add_argument('-port', help='Port where the honeypot service run (Dockerfile)', required=True)
    # Create add_server arguments
    parser_add_server.add_argument('-name', help='Name of the server', required=True)
    parser_add_server.add_argument('-descr', help='Description of the server', required=True)
    parser_add_server.add_argument('-tag', help='Tags of the server', required=True)
    parser_add_server.add_argument('-ip', help='IP address of the server', required=True)
    parser_add_server.add_argument('-key', type=argparse.FileType('r'),
                                   help='Base64 encoded SSH key file to connect to the server', required=True)
    parser_add_server.add_argument('-port', help='SSH port of the server', required=True)
    parser_add_server.add_argument('-autotags', action='store_true',
                                   help='Choose if you want to automatically add tags to server', required=False)
    # Create add_link arguments
    parser_add_link.add_argument('-tags_hp', help='Tags of the honeypots', required=True)
    parser_add_link.add_argument('-tags_serv', help='Tags of the servers', required=True)
    parser_add_link.add_argument('-ports', help='List of exposed ports', required=True)
    parser_add_link.add_argument('-nb_hp', help='Amount of honeypot', required=True)
    parser_add_link.add_argument('-nb_serv', help='Amount of server', required=True)
    # =====REMOVE ARGUMENTS=====#
    parser_remove_hp.add_argument('-id', help='ID of the honeypot', required=True)
    parser_remove_server.add_argument('-id', help='ID of the server', required=True)
    parser_remove_link.add_argument('-id', help='ID of the link', required=True)
    # =====EDIT ARGUMENTS=====#
    # Create edit_hp arguments
    parser_edit_hp.add_argument('-id', help='Id of the honeypot', required=True)
    parser_edit_hp.add_argument('-name', help='Name of the honeypot', required=False)
    parser_edit_hp.add_argument('-descr', help='Description of the honeypot', required=False)
    parser_edit_hp.add_argument('-tag', help='Tags of the honeypot', required=False)
    parser_edit_hp.add_argument('-parser', help='Parsing rules for logs of the honeypot', required=False)
    parser_edit_hp.add_argument('-logs', help='Path of log files of the honeypot', required=False)
    parser_edit_hp.add_argument('-src', help='Base64 Encoded Sourcefile of the honeypot (Dockerfile)', required=False)
    parser_edit_hp.add_argument('-port', help='Port the honeypot service listen on', required=False)
    # Create edit_server arguments
    parser_edit_server.add_argument('-id', help='Id of the server', required=True)
    parser_edit_server.add_argument('-name', help='Name of the server', required=False)
    parser_edit_server.add_argument('-descr', help='Description of the server', required=False)
    parser_edit_server.add_argument('-tag', help='Tags of the server', required=False)
    parser_edit_server.add_argument('-ip', help='IP address of the server', required=False)
    parser_edit_server.add_argument('-key', help='Base64 encoded ssh key file of the server', required=False)
    parser_edit_server.add_argument('-port', help='SSH port of the server', required=False)
    # Create edit_link arguments
    parser_edit_link.add_argument('-id', help='Id of the link', required=True)
    parser_edit_link.add_argument('-tags_hp', help='Tags of the honeypots', required=False)
    parser_edit_link.add_argument('-tags_serv', help='Tags of the servers', required=False)
    parser_edit_link.add_argument('-nb_hp', help='Amount of honeypot', required=False)
    parser_edit_link.add_argument('-nb_serv', help='Amount of server', required=False)
    parser_edit_link.add_argument('-ports', help='Ports to expose with link', required=False)
    # =====LIST ARGUMENTS=====#
    # There are all optionals here
    parser_list_hp.add_argument('-id', help='ID of the honeypot', required=False)
    parser_list_server.add_argument('-id', help='ID of the server', required=False)
    parser_list_link.add_argument('-id', help='ID of the link', required=False)
    parser_list_server.add_argument('-o', help='Specify output format to display',default='default', required=False)
    parser_list_hp.add_argument('-o', help='Specify output format to display',default='default', required=False)
    parser_list_link.add_argument('-o', help='Specify output format to display',default='default', required=False)

    # Execute parse_args()
    args = parser.parse_args()
    args.func(args)

