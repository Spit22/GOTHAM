#!/bin/python3

import argparse
import os
import sys
import requests
import base64
import configparser
import tabulate
import json

#===Logging components===#

CONFIG_PATH = "./Config/config.ini"

# Retrieve  GOTHAMCTL settings from config file
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

def add_server(args):
    # Query /add/server to create server
    #
    # args (obj) : passed commandline argument
    #
    # Show id of created server id

    name = normalize_name(args.name)
    descr = normalize_descr(args.descr)
    tags = args.tag
    ip = normalize_ip(args.ip)
    autotags = args.autotags

    try:
        ssh_key = str(base64.b64encode(args.key.read().encode("ascii")).decode("ascii"))
    except:
        print("Key not seems to be b64 encoded")
        sys.exit(1)
    ssh_port = normalize_port(args.port)

    
    # Define the queried endpoint
    endpoint = "/add/server"

    # Before external configuration
    gp = normalize_port(args.gotham_port)
    gh = normalize_ip(args.gotham_hostname)

    if name == False or descr == False or ip == False or ssh_port == False or gp == False or gh == False:
        sys.exit(1) 


    # Forge url
    url = "http://" + gh + ":" + gp + endpoint

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
    response = requests.post(url, json=data)
    status_code = response.status_code

    if status_code == 200:
      data = response.json()
      # Show result
      if "id" in data.keys():
        print(data["id"]+" created")
      else:
        print(str(data))

    else:
      try:
        data = response.json()
        if "error" in data.keys():
          print("Error: "+str(data["error"]))
        else:
          print("Error: Unknown error.")
      except:
        print("Error: api return a " + str(status_code) + " http code.")


def add_hp(args):
    # Query /add/honeypot to create honeypot
    #
    # args (obj) : passed commandline argument
    #
    # Show id of created honeypot id

    name = normalize_name(args.name)
    descr = normalize_descr(args.descr)
    tags = args.tag
    parser = args.parser
    logs = normalize_logs(args.logs)
    autotags = args.autotags

    try:
        src = str(base64.b64encode(args.src.read().encode("ascii")).decode("ascii"))
    except:
        print("Source not seems to be b64 encoded")
        sys.exit(1)
    port = normalize_port(args.port)

    # Define the queried endpoint
    endpoint = "/add/honeypot"

    # Before external configuration
    gp = normalize_port(args.gotham_port)
    gh = normalize_ip(args.gotham_hostname)

    if name == False or descr == False or logs == False or port == False or gp == False or gh == False:
        sys.exit(1) 

    # Forge url
    url = "http://" + gh + ":" + gp + endpoint

    # Forge POST data
    data = {
        "name": name,
        "descr": descr,
        "tags": tags,
        "parser": parser,
        "logs": logs,
        "dockerfile": src,
        "port": port,
    }

    if autotags:
        data["autotags"] = "1"
    else:
        data["autotags"] = "0"

    # Query URL and get json
    response = requests.post(url, json=data)
    status_code = response.status_code

    if status_code == 200:
      data = response.json()
      # Show result
      if "id" in data.keys():
        print(data["id"]+" created")
      else:
        print(str(data))

    else:
      try:
        data = response.json()
        if "error" in data.keys():
          print("Error: "+str(data["error"]))
        else:
          print("Error: Unknown error.")
      except:
        print("Error: api return a " + str(status_code) + " http code.")

def add_link(args):
    # Query /add/link to create link
    #
    # args (obj) : passed commandline argument
    #
    # Show id of created link id

    tags_hp = args.tags_hp
    tags_serv = args.tags_serv
    exposed_ports = args.ports
    nb_hp = normalize_nb_hp(args.nb_hp)
    nb_serv = normalize_nb_serv(args.nb_serv)

    # Define the queried endpoint
    endpoint = "/add/link"

    # Before external configuration
    gp = normalize_port(args.gotham_port)
    gh = normalize_ip(args.gotham_hostname)

    if nb_hp == False or nb_serv == False or gp == False or gh == False:
        sys.exit(1) 

    # Forge url
    url = "http://" + gh + ":" + gp + endpoint

    # Forge POST data
    data = {
        "tags_serv": tags_serv,
        "tags_hp": tags_hp,
        "nb_hp": nb_hp,
        "nb_serv": nb_serv,
        "exposed_ports": exposed_ports,
    }

    # Query URL and get json
    response = requests.post(url, json=data)
    status_code = response.status_code

    if status_code == 200:
      data = response.json()
      # Show result
      if "id" in data.keys():
        print(data["id"]+" created")
      else:
        print(str(data))

    else:
      try:
        data = response.json()
        if "error" in data.keys():
          print("Error: "+str(data["error"]))
        else:
          print("Error: Unknown error.")
      except:
        print("Error: api return a " + str(status_code) + " http code.")


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
    gp = normalize_port(args.gotham_port)
    gh = normalize_ip(args.gotham_hostname)

    if gp == False or gh == False:
        sys.exit(1) 

    # Forge url
    url = "http://" + gh + ":" + gp + endpoint

    # Forge POST data
    data = {
        "id": id
    }

    # Query URL and get json
    response = requests.post(url, json=data)
    status_code = response.status_code

    if status_code == 200:
      data = response.json()
      # Show result
      if "id" in data.keys():
        print(data["id"]+" deleted")
      else:
        print(str(data))

    else:
      try:
        data = response.json()
        if "error" in data.keys():
          print("Error: "+str(data["error"]))
        else:
          print("Error: Unknown error.")
      except:
        print("Error: api return a " + str(status_code) + " http code.")


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
    gp = normalize_port(args.gotham_port)
    gh = normalize_ip(args.gotham_hostname)

    if gp == False or gh == False:
        sys.exit(1) 

    # Forge url
    url = "http://" + gh + ":" + gp + endpoint

    # Forge POST data
    data = {
        "id": id
    }

    # Query URL and get json
    response = requests.post(url, json=data)
    status_code = response.status_code

    if status_code == 200:
      data = response.json()
      # Show result
      if "id" in data.keys():
        print(data["id"]+" deleted")
      else:
        print(str(data))

    else:
      try:
        data = response.json()
        if "error" in data.keys():
          print("Error: "+str(data["error"]))
        else:
          print("Error: Unknown error.")
      except:
        print("Error: api return a " + str(status_code) + " http code.")


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
    gp = normalize_port(args.gotham_port)
    gh = normalize_ip(args.gotham_hostname)

    if gp == False or gh == False:
        sys.exit(1) 

    # Forge url
    url = "http://" + gh + ":" + gp + endpoint

    # Forge POST data
    data = {
        "id": id
    }

    # Query URL and get json
    response = requests.post(url, json=data)
    status_code = response.status_code

    if status_code == 200:
      data = response.json()
      # Show result
      if "id" in data.keys():
        print(data["id"]+" deleted")
      else:
        print(str(data))

    else:
      try:
        data = response.json()
        if "error" in data.keys():
          print("Error: "+str(data["error"]))
        else:
          print("Error: Unknown error.")
      except:
        print("Error: api return a " + str(status_code) + " http code.")


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
    gp = normalize_port(args.gotham_port)
    gh = normalize_ip(args.gotham_hostname)

    if gp == False or gh == False:
        sys.exit(1) 

    # Forge url
    url = "http://" + gh + ":" + gp + endpoint

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
    response = requests.post(url, json=data)
    status_code = response.status_code

    if status_code == 200:
      data = response.json()
      # Show result
      print(data.json())

    else:
      try:
        data = response.json()
        if "error" in data.keys():
          print("Error: "+str(data["error"]))
        else:
          print("Error: Unknown error.")
      except:
        print("Error: api return a " + str(status_code) + " http code.")


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
    gp = normalize_port(args.gotham_port)
    gh = normalize_ip(args.gotham_hostname)

    if gp == False or gh == False:
        sys.exit(1) 

    # Forge url
    url = "http://" + gh + ":" + gp + endpoint

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
    if port:
        data["port"] = port

    # Query URL and get json
    response = requests.post(url, json=data)
    status_code = response.status_code

    if status_code == 200:
      data = response.json()
      print(data.json())

    else:
      try:
        data = response.json()
        if "error" in data.keys():
          print("Error: "+str(data["error"]))
        else:
          print("Error: Unknown error.")
      except:
        print("Error: api return a " + str(status_code) + " http code.")


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
    gp = normalize_port(args.gotham_port)
    gh = normalize_ip(args.gotham_hostname)

    if gp == False or gh == False:
        sys.exit(1) 

    # Forge url
    url = "http://" + gh + ":" + gp + endpoint

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
    response = requests.post(url, json=data)
    status_code = response.status_code

    if status_code == 200:
      data = response.json()
      # Show result
      print(data.json())

    else:
      try:
        data = response.json()
        if "error" in data.keys():
          print("Error: "+str(data["error"]))
        else:
          print("Error: Unknown error.")
      except:
        print("Error: api return a " + str(status_code) + " http code.")


def list_server(args):
    # Query /list/server and format data into a table
    #
    # args (obj) : passed commandline argument
    #
    # Print string formatted table

    hp_display = config['hp_display']
    del hp_display["default"]
    serv_display = config['serv_display']
    del serv_display["default"]
    link_display = config['link_display']
    del link_display["default"]
    
    # Define the queried endpoint
    endpoint = "/list/server"

    # Before external configuration
    gp = normalize_port(args.gotham_port)
    gh = normalize_ip(args.gotham_hostname)

    if gp == False or gh == False:
        sys.exit(1) 

    # Get id of server
    id = args.id
    ip = args.ip
    name = args.name
    tags = args.tags
    state = args.state
    descr = args.descr
    ssh_port = args.ssh_port

    # Get format of the display
    output_format = args.o
    detail_lvl = args.d
    overplus = int(args.p)

    prot="http"
    # Forge url
    url = prot+"://" + gh + ":" + gp + endpoint

    if id :
        if url == prot+"://" + gh + ":" + gp + endpoint:
            url += "?"+"id="+id
        else:
            url += "&"+"id="+id
    if ip :
        if url == prot+"://" + gh + ":" + gp + endpoint:
            url += "?"+"ip="+ip
        else:
            url += "&"+"ip="+ip
    if name :
        if url == prot+"://" + gh + ":" + gp + endpoint:
            url += "?"+"name="+name
        else:
            url += "&"+"name="+name
    if tags :
        if url == prot+"://" + gh + ":" + gp + endpoint:
            url += "?"+"tags="+tags
        else:
            url += "&"+"tags="+tags
    if state :
        if url == prot+"://" + gh + ":" + gp + endpoint:
            url += "?"+"state="+state
        else:
            url += "&"+"state="+state
    if descr :
        if url == prot+"://" + gh + ":" + gp + endpoint:
            url += "?"+"descr="+descr
        else:
            url += "&"+"descr="+descr
    if ssh_port :
        if url == prot+"://" + gh + ":" + gp + endpoint:
            url += "?"+"ssh_port="+ssh_port
        else:
            url += "&"+"ssh_port="+ssh_port

    # Query URL and get json
    response = requests.get(url)
    status_code = response.status_code
    
    if status_code == 200:
        # Show result
        data = response.json()
        servs_infos = [] 
        servs_infos_others = []
        serv_infos = {}

        if detail_lvl not in serv_display.keys(): 
            print("Error Format")
        else:
            if detail_lvl != "full":
                serv_keys_display = [key.strip() for key in serv_display[detail_lvl].split(',')]
            else:
                serv_keys_display = [key.strip() for key in serv_display[serv_display[detail_lvl]].split(',')]
            
            if 'error' in data.keys():
                print(data['error'])
            else:
                if 'servers' in data.keys(): 
                    servs = data['servers'] 
                    
                elif 'exact' in data.keys() and 'others' in data.keys(): 
                    servs = data['exact']
                    servs_other = data['others']
                    for serv in servs_other:
                        serv_infos = {}
                        for key in serv_keys_display: 
                           serv_infos[key] = serv['serv_' + key] 
                        
                        if str(detail_lvl).lower() == "full":
                            serv_infos["links"] = []
                            lk_keys_display = [key.strip() for key in link_display[serv_display[detail_lvl]].split(',')]
                            
                            for link in serv["links"]:
                                lk_infos={}
                                for key in lk_keys_display: 
                                    lk_infos[key] = link['link_' + key]
                                lk_infos["hps"] = []
                                hp_keys_display = [key.strip() for key in hp_display[serv_display[detail_lvl]].split(',')]
                                
                                for hp in link["hps"]:
                                    hp_infos={}
                                    for key in hp_keys_display: 
                                        hp_infos[key] = hp['hp_' + key]
                                    lk_infos["hps"].append(hp_infos)
                                if str(output_format).lower() == "table":
                                    lk_infos["hps"]=tabulate.tabulate(lk_infos["hps"], headers = 'keys')
                                serv_infos["links"].append(lk_infos)
                            if str(output_format).lower() == "table":
                                serv_infos["links"]=tabulate.tabulate(serv_infos["links"], headers = 'keys')
                                
                        servs_infos_others.append(serv_infos)

                else:
                    servs=0
                    print("ERROR") # A modifier
                
                if servs!=0:
                    for serv in servs:
                        serv_infos = {}
                        for key in serv_keys_display: 
                           serv_infos[key] = serv['serv_' + key] 
                        
                        if str(detail_lvl).lower() == "full":
                            serv_infos["links"] = []
                            lk_keys_display = [key.strip() for key in link_display[serv_display[detail_lvl]].split(',')]
                            
                            for link in serv["links"]:
                                lk_infos={}
                                for key in lk_keys_display: 
                                    lk_infos[key] = link['link_' + key]
                                lk_infos["hps"] = []
                                hp_keys_display = [key.strip() for key in hp_display[serv_display[detail_lvl]].split(',')]
                                
                                for hp in link["hps"]:
                                    hp_infos={}
                                    for key in hp_keys_display: 
                                        hp_infos[key] = hp['hp_' + key]
                                    lk_infos["hps"].append(hp_infos)
                                if str(output_format).lower() == "table":
                                    lk_infos["hps"]=tabulate.tabulate(lk_infos["hps"], headers = 'keys')
                                serv_infos["links"].append(lk_infos)
                            if str(output_format).lower() == "table":
                                serv_infos["links"]=tabulate.tabulate(serv_infos["links"], headers = 'keys')
                                
                        servs_infos.append(serv_infos)
                    
                    servs_infos_others = servs_infos_others[0:overplus]
                    if str(output_format).lower() == "json":
                        if servs_infos_others != []:
                            result={"servs":servs_infos,"servs_others":servs_infos_others}
                        else:
                            result={"servs":servs_infos}

                        res = json.dumps(result, indent=4)
                        print(res)
                    elif str(output_format).lower() == "tree":
                        print("Not implemented")
                    elif str(output_format).lower() == "text":
                        print("Servers:")
                        print("==========")
                        
                        for serv in servs_infos:
                            for key in serv.keys():
                                if key != "links":
                                    print("\t- "+key+": "+ str(serv[key]))
                            if "links" in serv.keys(): 
                                if serv["links"] == []:
                                    print("\t- links: Not linked")
                                else:
                                    print("\t- links:")
                                    for link in serv["links"]:
                                        for key in link.keys():
                                            if key != "servs":
                                                print("\t\t- "+key+": "+ str(link[key]))
                                        print("\t\t- hps:")
                                        for hp in link["hps"]:
                                            for key in hp.keys():
                                                print("\t\t\t- "+key+": "+ str(hp[key]))
                                            print("\n")
                                        print("\n")
                            print("\n")
                        if servs_infos_others != []:
                            if servs_infos != []:
                                print("\nOthers:")
                                print("==========")
                            for serv in servs_infos_others:
                                for key in serv.keys():
                                    if key != "links":
                                        print("\t- "+key+": "+ str(serv[key]))
                                if "links" in serv.keys(): 
                                    if serv["links"] == []:
                                        print("\t- links: Not linked")
                                    else:
                                        print("\t- links:")
                                        for link in serv["links"]:
                                            for key in link.keys():
                                                if key != "servs":
                                                    print("\t\t- "+key+": "+ str(link[key]))
                                            print("\t\t- hps:")
                                            for hp in link["hps"]:
                                                for key in hp.keys():
                                                    print("\t\t\t- "+key+": "+ str(hp[key]))
                                                print("\n")
                                            print("\n")
                                print("\n")

                    elif str(output_format).lower() == "table":
                        print("Servers:")
                        print("==========")
                        print(tabulate.tabulate(servs_infos, headers = 'keys'))
                        if servs_infos_others != []:
                            if servs_infos != []:
                                print("\nOthers:")
                                print("==========")
                            print(tabulate.tabulate(servs_infos_others, headers = 'keys')) 
                    else :
                        print("Wrong Format")
    else:
      try:
        data = response.json()
        if "error" in data.keys():
          print("Error: "+str(data["error"]))
        else:
          print("Error: Unknown error.")
      except:
        print("Error: api return a " + str(status_code) + " http code.")


def list_hp(args):
    # Query /list/honeypot and format data into a table
    #
    # args (obj) : passed commandline argument
    #
    # Print string formatted table

    hp_display = config['hp_display']
    del hp_display["default"]
    serv_display = config['serv_display']
    del serv_display["default"]
    link_display = config['link_display']
    del link_display["default"]
    
    # Define the queried endpoint
    endpoint = "/list/honeypot"

    # Before external configuration
    gp = normalize_port(args.gotham_port)
    gh = normalize_ip(args.gotham_hostname)

    if gp == False or gh == False:
        sys.exit(1) 

    # Get infos of honeypot
    id = args.id
    tags = args.tags
    name = args.name
    descr = args.descr
    port = args.port
    state = args.state

    # Get format of the display
    output_format = args.o
    detail_lvl = args.d
    overplus = int(args.p)


    prot="http"
    # Forge url
    url = prot+"://" + gh + ":" + gp + endpoint

    if id :
        if url == prot+"://" + gh + ":" + gp + endpoint:
            url += "?"+"id="+id
        else:
            url += "&"+"id="+id
    if tags :
        if url == prot+"://" + gh + ":" + gp + endpoint:
            url += "?"+"tags="+tags
        else:
            url += "&"+"tags="+tags
    if name :
        if url == prot+"://" + gh + ":" + gp + endpoint:
            url += "?"+"name="+name
        else:
            url += "&"+"name="+name
    if descr :
        if url == prot+"://" + gh + ":" + gp + endpoint:
            url += "?"+"descr="+descr
        else:
            url += "&"+"descr="+descr
    if port :
        if url == prot+"://" + gh + ":" + gp + endpoint:
            url += "?"+"port="+port
        else:
            url += "&"+"port="+port
    if state :
        if url == prot+"://" + gh + ":" + gp + endpoint:
            url += "?"+"state="+state
        else:
            url += "&"+"state="+state

    # Query URL and get json
    response = requests.get(url)
    status_code = response.status_code
        
    if status_code == 200:
        # Show result
        data = response.json()
        hps_infos = [] 
        hps_infos_others = []
        hp_infos = {}

        if detail_lvl not in hp_display.keys(): 
            print("Error Format")
        else:
            if detail_lvl != "full":
                hp_keys_display = [key.strip() for key in hp_display[detail_lvl].split(',')]
            else:
                hp_keys_display = [key.strip() for key in hp_display[hp_display[detail_lvl]].split(',')]
            
            if 'error' in data.keys():
                print(data['error'])
            else: 
                if 'honeypots' in data.keys(): 
                    hps = data['honeypots'] 
                    
                elif 'exact' in data.keys() and 'others' in data.keys(): 
                    hps = data['exact']
                    hps_other = data['others']
                    for hp in hps_other:
                        hp_infos = {}
                        for key in hp_keys_display: 
                           hp_infos[key] = hp['hp_' + key] 
                        
                        if str(detail_lvl).lower() == "full":
                            hp_infos["links"] = []
                            lk_keys_display = [key.strip() for key in link_display[hp_display[detail_lvl]].split(',')]
                            
                            for link in hp["links"]:
                                lk_infos={}
                                for key in lk_keys_display: 
                                    lk_infos[key] = link['link_' + key]
                                lk_infos["servs"] = []
                                serv_keys_display = [key.strip() for key in serv_display[hp_display[detail_lvl]].split(',')]
                                
                                for serv in link["servs"]:
                                    serv_infos={}
                                    for key in serv_keys_display: 
                                        serv_infos[key] = serv['serv_' + key]
                                    lk_infos["servs"].append(serv_infos)
                                if str(output_format).lower() == "table":
                                    lk_infos["servs"]=tabulate.tabulate(lk_infos["servs"], headers = 'keys')
                                    
                                hp_infos["links"].append(lk_infos)
                            if str(output_format).lower() == "table":
                                hp_infos["links"]=tabulate.tabulate(hp_infos["links"], headers = 'keys')
                                
                        hps_infos_others.append(hp_infos)

                else:
                    hps=0
                    print("ERROR") # A modifier
                
                if hps!=0:
                    for hp in hps:
                        hp_infos = {}
                        for key in hp_keys_display: 
                            hp_infos[key] = hp['hp_' + key] 
                        
                        if str(detail_lvl).lower() == "full":
                            hp_infos["links"] = []
                            lk_keys_display = [key.strip() for key in link_display[hp_display[detail_lvl]].split(',')]
                            
                            for link in hp["links"]:
                                lk_infos={}
                                for key in lk_keys_display: 
                                    lk_infos[key] = link['link_' + key]
                                lk_infos["servs"] = []
                                serv_keys_display = [key.strip() for key in serv_display[hp_display[detail_lvl]].split(',')]
                                
                                for serv in link["servs"]:
                                    serv_infos={}
                                    for key in serv_keys_display: 
                                        serv_infos[key] = serv['serv_' + key]
                                    lk_infos["servs"].append(serv_infos)
                                if str(output_format).lower() == "table":
                                    lk_infos["servs"]=tabulate.tabulate(lk_infos["servs"], headers = 'keys')
                                    
                                hp_infos["links"].append(lk_infos)
                            if str(output_format).lower() == "table":
                                hp_infos["links"]=tabulate.tabulate(hp_infos["links"], headers = 'keys')
                                
                        hps_infos.append(hp_infos) 
                    
                    hps_infos_others = hps_infos_others[0:overplus]
                    if str(output_format).lower() == "json":
                        if hps_infos_others != []:
                            result={"hps":hps_infos,"hps_others":hps_infos_others}
                        else:
                            result={"hps":hps_infos}

                        res = json.dumps(result, indent=4)
                        print(res)
                    elif str(output_format).lower() == "tree":
                        print("Not implemented")
                    elif str(output_format).lower() == "text":
                        print("Honeypots:")
                        print("==========")
                        
                        for hp in hps_infos:
                            for key in hp.keys():
                                if key != "links":
                                    print("\t- "+key+": "+ str(hp[key]))
                            if "links" in hp.keys(): 
                                if hp["links"] == []:
                                    print("\t- links: Not linked")
                                else:
                                    print("\t- links:")
                                    for link in hp["links"]:
                                        for key in link.keys():
                                            if key != "servs":
                                                print("\t\t- "+key+": "+ str(link[key]))
                                        print("\t\t- servs:")
                                        for serv in link["servs"]:
                                            for key in serv.keys():
                                                print("\t\t\t- "+key+": "+ str(serv[key]))
                                            print("\n")
                                        print("\n")
                            print("\n")
                        if hps_infos_others != []:
                            if hps_infos != []:
                                print("\nOthers:")
                                print("==========")
                            for hp in hps_infos_others:
                                for key in hp.keys():
                                    if key != "links":
                                        print("\t- "+key+": "+ str(hp[key]))
                                if "links" in hp.keys(): 
                                    if hp["links"] == []:
                                        print("\t- links: Not linked")
                                    else:
                                        print("\t- links:")
                                        for link in hp["links"]:
                                            for key in link.keys():
                                                if key != "servs":
                                                    print("\t\t- "+key+": "+ str(link[key]))
                                            print("\t\t- servs:")
                                            for serv in link["servs"]:
                                                for key in serv.keys():
                                                    print("\t\t\t- "+key+": "+ str(serv[key]))
                                                print("\n")
                                            print("\n")

                                print("\n")

                    elif str(output_format).lower() == "table":
                        print("Honeypots:")
                        print("==========")
                        print(tabulate.tabulate(hps_infos, headers = 'keys'))
                        if hps_infos_others != []:
                            if hps_infos != []:
                                print("\nOthers:")
                                print("==========")
                            print(tabulate.tabulate(hps_infos_others, headers = 'keys')) 
                    else :
                        print("Wrong Format")

    else:
      try:
        data = response.json()
        if "error" in data.keys():
          print("Error: "+str(data["error"]))
        else:
          print("Error: Unknown error.")
      except:
        print("Error: api return a " + str(status_code) + " http code.")


def list_link(args):
    # Query /list/link and format data into a table
    #
    # args (obj) : passed commandline argument
    #
    # Print string formatted table
    
    hp_display = config['hp_display']
    del hp_display["default"]
    serv_display = config['serv_display']
    del serv_display["default"]
    link_display = config['link_display']
    del link_display["default"]
    

    endpoint = "/list/link"

    # Before external configuration
    gp = normalize_port(args.gotham_port)
    gh = normalize_ip(args.gotham_hostname)

    if gp == False or gh == False:
        sys.exit(1) 

    # Get infos of link
    id = args.id
    nb_hp = args.nb_hp
    nb_serv = args.nb_serv
    tags_hp = args.tags_hp
    tags_serv = args.tags_serv
    ports = args.ports

    # Get format of the display
    output_format = args.o
    detail_lvl = args.d
    overplus = int(args.p)

    prot="http"
    # Forge url
    url = prot+"://" + gh + ":" + gp + endpoint

    if id :
        if url == prot+"://" + gh + ":" + gp + endpoint:
            url += "?"+"id="+id
        else:
            url += "&"+"id="+id
    if nb_hp :
        if url == prot+"://" + gh + ":" + gp + endpoint:
            url += "?"+"nb_hp="+nb_hp
        else:
            url += "&"+"nb_hp="+nb_hp
    if nb_serv :
        if url == prot+"://" + gh + ":" + gp + endpoint:
            url += "?"+"nb_serv="+nb_serv
        else:
            url += "&"+"nb_serv="+nb_serv
    if tags_hp :
        if url == prot+"://" + gh + ":" + gp + endpoint:
            url += "?"+"tags_hp="+tags_hp
        else:
            url += "&"+"tags_hp="+tags_hp
    if tags_serv :
        if url == prot+"://" + gh + ":" + gp + endpoint:
            url += "?"+"tags_serv="+tags_serv
        else:
            url += "&"+"tags_serv="+tags_serv
    if ports :
        if url == prot+"://" + gh + ":" + gp + endpoint:
            url += "?"+"ports="+ports
        else:
            url += "&"+"ports="+ports

    # Query URL and get json
    response = requests.get(url)
    status_code = response.status_code
        
    if status_code == 200:
        # Show result
        data = response.json()
        
        links_infos = [] 
        links_infos_others = []
        link_infos = {}

        if detail_lvl not in link_display.keys(): 
            print("Error Format")
        else:
            if detail_lvl != "full":
                link_keys_display = [key.strip() for key in link_display[detail_lvl].split(',')]
            else:
                link_keys_display = [key.strip() for key in link_display[link_display[detail_lvl]].split(',')]
            
            if 'error' in data.keys():
                print(data['error'])
            else:
                if 'links' in data.keys(): 
                    links = data['links'] 
                    
                elif 'exact' in data.keys() and 'others' in data.keys(): 
                    links = data['exact']
                    links_other = data['others']
                    for link in links_other:
                        link_infos = {}
                        for key in link_keys_display: 
                           link_infos[key] = link['link_' + key] 
                        
                        if str(detail_lvl).lower() == "full":
                            if "hps" in link.keys():
                                next_type="hp"
                            elif "servs" in link.keys():
                                next_type="serv"
                            
                            link_infos[next_type+"s"] = []
                            hp_keys_display = [key.strip() for key in hp_display[link_display[detail_lvl]].split(',')]
                            serv_keys_display = [key.strip() for key in serv_display[link_display[detail_lvl]].split(',')]

                            for obj in link[next_type+"s"]:
                                obj_infos={}
                                if next_type=="hp":
                                    for key in hp_keys_display: 
                                        obj_infos[key] = obj[next_type+'_' + key]
                                if next_type=="serv":
                                    for key in serv_keys_display: 
                                        obj_infos[key] = obj[next_type+'_' + key]
                                
                                if next_type=="hp":
                                    last_type="serv"
                                if next_type=="serv":
                                    last_type="hp"
                                obj_infos[last_type+"s"] = []

                                for last_obj in obj[last_type+"s"]:
                                    last_obj_infos={}
                                    if last_type=="hp":
                                        for key in hp_keys_display: 
                                            last_obj_infos[key] = last_obj[last_type+'_' + key]
                                    if last_type=="serv":
                                        for key in serv_keys_display: 
                                            last_obj_infos[key] = last_obj[last_type+'_' + key]
                                    obj_infos[last_type+"s"].append(last_obj_infos)
                                if str(output_format).lower() == "table":
                                    obj_infos[last_type+"s"]=tabulate.tabulate(obj_infos[last_type+"s"], headers = 'keys')
                                    
                                link_infos[next_type+"s"].append(obj_infos)
                            if str(output_format).lower() == "table":
                                link_infos[next_type+"s"]=tabulate.tabulate(link_infos[next_type+"s"], headers = 'keys')
                                
                        links_infos_others.append(link_infos)

                else:
                    links=0
                    print("ERROR") # A modifier
                
                if links!=0:
                    for link in links:
                        link_infos = {}
                        for key in link_keys_display: 
                           link_infos[key] = link['link_' + key] 
                        
                        if str(detail_lvl).lower() == "full":
                            if "hps" in link.keys():
                                next_type="hp"
                            elif "servs" in link.keys():
                                next_type="serv"
                            
                            link_infos[next_type+"s"] = []
                            hp_keys_display = [key.strip() for key in hp_display[link_display[detail_lvl]].split(',')]
                            serv_keys_display = [key.strip() for key in serv_display[link_display[detail_lvl]].split(',')]

                            for obj in link[next_type+"s"]:
                                obj_infos={}
                                if next_type=="hp":
                                    for key in hp_keys_display: 
                                        obj_infos[key] = obj[next_type+'_' + key]
                                if next_type=="serv":
                                    for key in serv_keys_display: 
                                        obj_infos[key] = obj[next_type+'_' + key]
                                
                                if next_type=="hp":
                                    last_type="serv"
                                if next_type=="serv":
                                    last_type="hp"
                                obj_infos[last_type+"s"] = []

                                for last_obj in obj[last_type+"s"]:
                                    last_obj_infos={}
                                    if last_type=="hp":
                                        for key in hp_keys_display: 
                                            last_obj_infos[key] = last_obj[last_type+'_' + key]
                                    if last_type=="serv":
                                        for key in serv_keys_display: 
                                            last_obj_infos[key] = last_obj[last_type+'_' + key]
                                    obj_infos[last_type+"s"].append(last_obj_infos)
                                if str(output_format).lower() == "table":
                                    obj_infos[last_type+"s"]=tabulate.tabulate(obj_infos[last_type+"s"], headers = 'keys')
                                    
                                link_infos[next_type+"s"].append(obj_infos)
                            if str(output_format).lower() == "table":
                                link_infos[next_type+"s"]=tabulate.tabulate(link_infos[next_type+"s"], headers = 'keys')
                                
                        links_infos.append(link_infos) 
                    
                    links_infos_others = links_infos_others[0:overplus]
                    if str(output_format).lower() == "json":
                        if links_infos_others != []:
                            result={"links":links_infos,"links_others":links_infos_others}
                        else:
                            result={"links":links_infos}

                        res = json.dumps(result, indent=4)
                        print(res)
                    elif str(output_format).lower() == "tree":
                        print("Not implemented")
                    elif str(output_format).lower() == "text":
                        print("Links:")
                        print("==========")
                        
                        for link in links_infos:
                            for key in link.keys():
                                if key != "hps" and key != "servs":
                                    print("\t- "+key+": "+ str(link[key]))
                            if "hps" in link.keys():
                                print("\t- hps:")
                                for hp in link["hps"]:
                                    for key in hp.keys():
                                        if key != "servs":
                                            print("\t\t- "+key+": "+ str(hp[key]))
                                    print("\t\t- servs:")
                                    for serv in hp["servs"]:
                                        for key in serv.keys():
                                            print("\t\t\t- "+key+": "+ str(serv[key]))
                                        print("\n")
                                    print("\n")
                            elif "servs" in link.keys():
                                print("\t- servs:")
                                for serv in link["servs"]:
                                    for key in serv.keys():
                                        if key != "hps":
                                            print("\t\t- "+key+": "+ str(serv[key]))
                                    print("\t\t- hps:")
                                    for hp in serv["hps"]:
                                        for key in hp.keys():
                                            print("\t\t\t- "+key+": "+ str(hp[key]))
                                        print("\n")
                                    print("\n")
                            print("\n")
                        if links_infos_others != []:
                            if links_infos != []:
                                print("\nOthers:")
                                print("==========")
                            for link in links_infos_others:
                                for key in link.keys():
                                    if key != "hps" and key != "servs":
                                        print("\t- "+key+": "+ str(hp[key]))
                                if "hps" in link.keys():
                                    print("\t- hps:")
                                    for hp in link["hps"]:
                                        for key in hp.keys():
                                            if key != "servs":
                                                print("\t\t- "+key+": "+ str(hp[key]))
                                        print("\t\t- servs:")
                                        for serv in hp["servs"]:
                                            for key in serv.keys():
                                                print("\t\t\t- "+key+": "+ str(serv[key]))
                                            print("\n")
                                        print("\n")
                                elif "servs" in link.keys():
                                    print("\t- servs:")
                                    for serv in link["servs"]:
                                        for key in serv.keys():
                                            if key != "hps":
                                                print("\t\t- "+key+": "+ str(serv[key]))
                                        print("\t\t- hps:")
                                        for hp in serv["hps"]:
                                            for key in hp.keys():
                                                print("\t\t\t- "+key+": "+ str(hp[key]))
                                            print("\n")
                                        print("\n")
                                print("\n")

                    elif str(output_format).lower() == "table":
                        print("Links:")
                        print("==========")
                        print(tabulate.tabulate(links_infos, headers = 'keys'))
                        if links_infos_others != []:
                            if links_infos != []:
                                print("\nOthers:")
                                print("==========")
                            print(tabulate.tabulate(links_infos_others, headers = 'keys')) 
                    else :
                        print("Wrong Format")

    else:
      try:
        data = response.json()
        if "error" in data.keys():
          print("Error: "+str(data["error"]))
        else:
          print("Error: Unknown error.")
      except:
        print("Error: api return a " + str(status_code) + " http code.")



#===Normalize functions===#
def normalize_name(name):
    if len(name) > 128:
        print("name has a invalid length : "+name+" : name length must be under 128 !")
        return False
    if not(re.match(r"^[a-zA-Z0-9_\-]*$", name)):
        print("name has a invalid syntax : "+name)
        return False
    return name


def normalize_descr(descr):
    if not(re.match(r"^[a-zA-Z0-9_\-\s]*$", descr)):
        print("descr has a invalid syntax : "+descr)
        return False
    return descr


def normalize_port(port):
    if (port == '' or port == None or port == 0):
        pritn("port is undefined or empty")
        return False
    try:
        int(port)
    except:
        print("port has a invalid type : "+port+" : port must be an interger !")
        return False
    port = int(port)
    if (port < 1) or (port > 65536):
        print("port has a invalid value : "+port+" : port must be between 1 and 65536 !")
        return False
    return port

def normalize_logs(logs):
    if len(logs) > 255:
        print("log path has a invalid length: must be under 255 !")
        return False
    if not(re.match(r"^[a-zA-Z0-9_/:\"\-\s]*$", logs)):
        print("log path has a invalid syntax")
        return False
    return logs

def normalize_ip(ip):
    if not(re.match(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", ip)):
        print("ip has a invalid syntax")
        return False
    return ip


def normalize_nb_hp(nb_hp):
    if str(nb_hp).lower() != "all":
        if len(str(nb_hp)) > 5:
            print("Number of honeypots (nb_hp) has a invalid length : "+nb_hp+" : nb_hp length must be under 5 !")
            return False
        try:
            int(nb_hp)
        except:
            print("Number of honeypots (nb_hp) has a invalid type : "+nb_hp+" : nb_hp must be an interger !")
            return False
        if int(nb_hp) < 1:
            print("Number of honeypots (nb_hp) has a invalid value : "+nb_hp+" : nb_hp must be superior to 0 !")
            return False
        return int(nb_hp)
    else:
        return "ALL"


def normalize_nb_serv(nb_serv):
    if str(nb_serv).lower() != "all":
        if len(str(nb_serv)) > 5:
            print("Number of servers (nb_serv) has a invalid length : "+nb_serv+" : nb_hp length must be under 5 !")
            return False
        try:
            int(nb_serv)
        except:
            print("Number of servers (nb_serv) has a invalid type : "+nb_serv+" : nb_serv must be an interger !")
            return False
        if int(nb_serv) < 1:
            print("Number of honeypots (nb_serv) has a invalid value : "+nb_serv+" : nb_serv must be superior to 0 !")
            return False
        return int(nb_serv)
    else:
        return "ALL"



if __name__ == "__main__":

    gh = normalize_ip(config["orchestrator_infos"]["host"])
    if gh == False:
        sys.exit(1)
    gp = normalize_port(config["orchestrator_infos"]["port"])
    if gp == False:
        sys.exit(1)
    default_hp = config["hp_display"]["default"]
    default_serv = config["serv_display"]["default"]
    default_link = config["link_display"]["default"]

    # Create the parser
    parser = argparse.ArgumentParser(description='Gothamctl')

    # Configure main parser
    parser._positionals.title = 'ARGUMENTS'
    parser._optionals.title = 'OPTIONS'

    # URL arguments
    parser.add_argument('-host', dest="gotham_hostname", help='hostname of the orchestrator',default=gh, required=False)
    parser.add_argument('-port', dest="gotham_port", help='administration port of the orchestrator',default=gp, required=False)

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
    parser_add_hp.add_argument('-autotags', action='store_true',
                                   help='Choose if you want to automatically add tags to honeypot', required=False)

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
    # Create list_hp arguments
    parser_list_hp.add_argument('-id', help='ID of the honeypot', required=False)
    parser_list_hp.add_argument('-tags', help='Tags of the honeypot', required=False)
    parser_list_hp.add_argument('-name', help='Name of the honeypot', required=False)
    parser_list_hp.add_argument('-descr', help='Description of the honeypot', required=False)
    parser_list_hp.add_argument('-port', help='Port of the honeypot', required=False)
    parser_list_hp.add_argument('-state', help='State of the honeypot', required=False)
    parser_list_hp.add_argument('-o', help='Specify output format to display',default=default_hp, choices=["json","table","text","tree"], required=False)
    parser_list_hp.add_argument('-d', help='Specify detail level to display',default="normal", required=False)
    parser_list_hp.add_argument('-p', help='Specify number of additional honeypot to display',default="4", required=False)
    # Create list_server arguments
    parser_list_server.add_argument('-id', help='ID of the server', required=False)
    parser_list_server.add_argument('-ip', help='IP of the server', required=False)
    parser_list_server.add_argument('-name', help='Name of the server', required=False)
    parser_list_server.add_argument('-tags', help='Tags of the server', required=False)
    parser_list_server.add_argument('-state', help='State of the server', required=False)
    parser_list_server.add_argument('-descr', help='Description of the server', required=False)
    parser_list_server.add_argument('-ssh_port', help='SSH port of the server', required=False)
    parser_list_server.add_argument('-o', help='Specify output format to display',default=default_serv, choices=["json","table","text","tree"], required=False)
    parser_list_server.add_argument('-d', help='Specify detail level to display',default="normal", required=False)
    parser_list_server.add_argument('-p', help='Specify number of additional server to display',default="4", required=False)
    # Create list_link arguments
    parser_list_link.add_argument('-id', help='ID of the link', required=False)
    parser_list_link.add_argument('-nb_hp', help='Number of honeypots of the link', required=False)
    parser_list_link.add_argument('-nb_serv', help='Number of server of the link', required=False)
    parser_list_link.add_argument('-tags_hp', help='Tag of honeypots of the link', required=False)
    parser_list_link.add_argument('-tags_serv', help='Tag of servers of the link', required=False)
    parser_list_link.add_argument('-ports', help='Ports used for the link', required=False)
    parser_list_link.add_argument('-o', help='Specify output format to display',default=default_link, choices=["json","table","text","tree"], required=False)
    parser_list_link.add_argument('-d', help='Specify detail level to display',default="normal", required=False)
    parser_list_link.add_argument('-p', help='Specify number of additional link to display',default="4", required=False)
    # Execute parse_args()
    args = parser.parse_args()
    args.func(args)
