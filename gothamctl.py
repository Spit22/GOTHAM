#!/bin/python3

import argparse
import os
import sys
import requests

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
    ssh_key = args.key
    ssh_port = args.port

    # Define the queried endpoint
    endpoint = "/add/server"

    # Before external configuration
    port = args.gotham_port
    gh = args.gotham_hostname

    # Forge url
    url = gh + ":" + port + endpoint

    # Forge POST data
    data = {
        "ip": ip,
        "name": name,
        "descr": descr,
        "tags": tags,
        "ssh_key": ssh_key,
        "ssh_port": ssh_port,
    }

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
    src = args.src
    port = args.port

    # Define the queried endpoint
    endpoint = "/add/honeypot"

    # Before external configuration
    port = args.gotham_port
    gh = args.gotham_hostname

    # Forge url
    url = gh + ":" + port + endpoint

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
    port = args.gotham_port
    gh = args.gotham_hostname

    # Forge url
    url = gh + ":" + port + endpoint

    # Forge POST data
    data = {
        "tags_serv": tags_serv,
        "tags_hp": tags_hp,
        "port": port,
        "nb_hp": nb_hp,
        "nb_serv": nb_serv,
        "exposed_ports": exposed_ports,
    }

    # Query URL and get json
    data = requests.post(url, json=data)

    # Show result
    print(data.json())

def rm_server(args):
    id = args.id
    gh = args.gotham_hostname
    print(id, gh)

def rm_hp(args):
    id = args.id
    print(id)

def rm_link(args):
    id = args.id
    print(id)

def edit_server(args):
    name = args.name
    descr = args.descr
    tag = args.tag
    ip = args.ip
    print(name, descr, tag, ip)
    
def edit_hp(args):
    name = args.name
    descr = args.descr
    tag = args.tag
    parser = args.parser
    logs = args.logs
    src = args.src
    print(name, descr, tag, parser, logs, src)

def edit_link(args):
    tag_hp = args.tag_hp
    tag_serv = args.tag_serv
    nb_hp = args.nb_hp
    nb_serv = args.nb_serv
    print(tag_hp, tag_serv, nb_hp, nb_serv)

def list_server(args):
    # Query /list/server and format data into a table
    #
    # args (obj) : passed commandline argument
    #
    # Print string formatted table

    # Define the queried endpoint
    endpoint = "/list/server"

    # Before external configuration
    port = args.gotham_port
    gh = args.gotham_hostname

    # Get id of server
    id = args.id

    # If id set, query only for 1 server
    if id:
        # Forge url
        url = gh + ":" + port + endpoint + "?id=" + id
    else:
        # Else query all servers in db
        # Forge url
        url = gh + ":" + port + endpoint

    # Query URL and get json
    data = requests.get(url)

    # Show result
    print(data.json())

def list_hp(args):
    # Query /list/honeypot and format data into a table
    #
    # args (obj) : passed commandline argument
    #
    # Print string formatted table

    # Define the queried endpoint
    endpoint = "/list/honeypot"

    # Before external configuration
    port = args.gotham_port
    gh = args.gotham_hostname

    # Get id of honeypot
    id = args.id

    # If id set, query only for 1 honeypot
    if id:
        # Forge url
        url = gh + ":" + port + endpoint + "?id=" + id
    else:
        # Else query all honeypots in db
        # Forge url
        url = gh + ":" + port + endpoint

    # Query URL and get json
    data = requests.get(url)

    # Show result
    print(data.json())

def list_link(args):
    # Query /list/link and format data into a table
    #
    # args (obj) : passed commandline argument
    #
    # Print string formatted table

    # Define the queried endpoint
    endpoint = "/list/link"

    # Before external configuration
    port = args.gotham_port
    gh = args.gotham_hostname

    # Get id of link
    id = args.id

    # If id set, query only for 1 link
    if id:
        # Forge url
        url = gh + ":" + port + endpoint + "?id=" + id
    else:
        # Else query all links in db
        # Forge url
        url = gh + ":" + port + endpoint

    # Query URL and get json
    data = requests.get(url)

    # Show result
    print(data.json())

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

    #=====ADD ARGUMENTS=====#
    # Create add_hp arguments
    parser_add_hp.add_argument('-name', help='Name of the honeypot', required=True)
    parser_add_hp.add_argument('-descr', help='Description of the honeypot', required=True)
    parser_add_hp.add_argument('-tag', help='Tags of the honeypot', required=True)
    parser_add_hp.add_argument('-parser', help='Parsing rules for logs of the honeypot', required=True)
    parser_add_hp.add_argument('-logs', help='Path of log files of the honeypot', required=True)
    parser_add_hp.add_argument('-src', help='Sources of the honepot (Dockerfile)', required=True)
    parser_add_hp.add_argument('-port', help='Port where the honeypot service run (Dockerfile)', required=True)
    # Create add_server arguments
    parser_add_server.add_argument('-name', help='Name of the server', required=True)
    parser_add_server.add_argument('-descr', help='Description of the server', required=True)
    parser_add_server.add_argument('-tag', help='Tags of the server', required=True)
    parser_add_server.add_argument('-ip', help='IP address of the server', required=True)
    parser_add_server.add_argument('-key', help='Encoded SSH key to connnect to the server', required=True)
    parser_add_server.add_argument('-port', help='SSH port of the server', required=True)
    # Create add_link arguments
    parser_add_link.add_argument('-tags_hp', help='Tags of the honeypots', required=True)
    parser_add_link.add_argument('-tags_serv', help='Tags of the servers', required=True)
    parser_add_link.add_argument('-ports', help='List of exposed ports', required=True)
    parser_add_link.add_argument('-nb_hp', help='Amount of honeypot', required=True)
    parser_add_link.add_argument('-nb_serv', help='Amount of server', required=True)
    #=====REMOVE ARGUMENTS=====#
    parser_remove_hp.add_argument('-id', help='ID of the honeypot', required=True)
    parser_remove_server.add_argument('-id', help='ID of the server', required=True)
    parser_remove_link.add_argument('-id', help='ID of the link', required=True)
    #=====EDIT ARGUMENTS=====#
    # Create add_hp arguments
    parser_edit_hp.add_argument('-name', help='Name of the honeypot', required=True)
    parser_edit_hp.add_argument('-descr', help='Description of the honeypot', required=True)
    parser_edit_hp.add_argument('-tag', help='Tags of the honeypot', required=True)
    parser_edit_hp.add_argument('-parser', help='Parsing rules for logs of the honeypot', required=True)
    parser_edit_hp.add_argument('-logs', help='Path of log files of the honeypot', required=True)
    parser_edit_hp.add_argument('-src', help='Sources of the honepot (Dockerfile)', required=True)
    # Create add_server arguments
    parser_edit_server.add_argument('-name', help='Name of the server', required=True)
    parser_edit_server.add_argument('-descr', help='Description of the server', required=True)
    parser_edit_server.add_argument('-tag', help='Tags of the server', required=True)
    parser_edit_server.add_argument('-ip', help='IP address of the server', required=True)
    # Create add_link arguments
    parser_edit_link.add_argument('-tags_hp', help='Tags of the honeypots', required=True)
    parser_edit_link.add_argument('-tags_serv', help='Tags of the servers', required=True)
    parser_edit_link.add_argument('-nb_hp', help='Amount of honeypot', required=True)
    parser_edit_link.add_argument('-nb_serv', help='Amount of server', required=True)
    #=====LIST ARGUMENTS=====#
    # There are all optionals here
    parser_list_hp.add_argument('-id', help='ID of the honeypot', required=False)
    parser_list_server.add_argument('-id', help='ID of the server', required=False)
    parser_list_link.add_argument('-id', help='ID of the link', required=False)

    # Execute parse_args()
    args = parser.parse_args()
    args.func(args)

