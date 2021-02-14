from Gotham_SSH_SCP import execute_commands
from Gotham_normalize import normalize_server_infos, normalize_display_object_infos
from Gotham_link_BDD import get_server_infos, remove_server_DB, edit_lhs_DB, edit_link_DB, remove_lhs

import sys

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')

def main(DB_settings, id='sv-00000000000000000000000000000000', ip='255.255.255.255'):
    # Check id format
    try:
        serv_infos = {'id':id, 'ip':ip}
        serv_infos = normalize_server_infos(serv_infos)
    except:
        logging.error(f"Can't remove the server : its infos is invalid")
        sys.exit(1)
    # Check if the server exists in the IDB
    if id != 'sv-00000000000000000000000000000000':
        result = get_server_infos(DB_settings, id=id)
    elif ip != '255.255.255.255':
        result = get_server_infos(DB_settings, ip=ip)
    else:
        logging.error(f"Remove server failed : no arguments")
        sys.exit(1)
    if result == []:
        logging.error(f"You tried to remove a server that doesn't exists with the id = {id}")
        sys.exit(1)
    # Check if the server is running
    if result[0]['link_id'] != None and result[0]['link_id'] !="NULL":
        serv_infos=normalize_display_object_infos(result[0],"serv")
        for i in range(len(serv_infos["links"])):
            # Try to replace
            success=replace_server(DB_settings,serv_infos,i)

            # If we can't replace, just modify link to decrease nb serv
            if not(success):
                if serv_infos["links"][i]["link_nb_serv"]>1:
                    try:
                        remove_lhs(DB_settings,id_link=serv_infos["links"][i]["link_id"], id_serv=serv_infos["serv_id"])
                    except:
                        sys.exit(1)
                    try:
                        modifs={"nb_serv":int(serv_infos["links"][i]["link_nb_serv"])-1}
                        conditions={"id":serv_infos["links"][i]["link_id"]}
                        edit_link_DB(DB_settings, modifs, conditions)
                    except:
                        sys.exit(1)
                else:        
                    # If nb serv=1, error, we can't do nothing
                    logging.error(f"You tried to remove a running server with the id = {id}, and it can't be replaced or deleted")
                    sys.exit(1)
    # Remove Server from the server
    try:
        remove_nginx_on_server(result[0]['serv_ip'],result[0]['serv_ssh_port'],result[0]['serv_ssh_key'])
    except:
        sys.exit(1)
    # Remove Server from the IDB
    try:
        remove_server_DB(DB_settings,result[0]['serv_id'])
    except Exception as e:
        logging.error(f"Remove server failed : {e}")
        sys.exit(1)
    return True

def remove_nginx_on_server(hostname, port, ssh_key):
    commands=["sudo rm -r /etc/nginx","sudo rm -r /usr/sbin/nginx","sudo rm -r /usr/lib/nginx/modules","sudo rm -r /etc/nginx/nginx.conf","sudo rm -r /var/log/nginx/error.log", "sudo rm -r /var/log/nginx/access.log", "sudo rm -r /run/nginx.pid","sudo rm -r /var/lock/nginx.lock"]
    try:
        execute_commands(hostname,port,ssh_key,commands)
    except Exception as e:
        logging.error(f"Remove server failed : {e}")
        sys.exit(1)


def replace_server(DB_settings,serv_infos,num_link):

    GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
    # Retrieve settings from config file
    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    tag_separator = config['tag']['separator']
    port_separator = config['port']['separator']

    link=serv_infos["links"][num_link]
    link_tags_serv=tag_separator.join(link["link_tags_serv"].split("||"))

    # Get all servers corresponding to tags
    servers = Gotham_check.check_tags("serv",Gotham_link_BDD.get_server_infos(db_settings, tags=link_tags_serv), tags_serv=link_tags_serv)

    # Filter servers in those who have one of ports open
    servers = Gotham_check.check_servers_ports_matching(servers, link["link_port"])

    # Filter servers in error
    servers = [server for server in servers if not(server["serv_state"]=='ERROR' or link["link_id"] in server["link_id"] or server["serv_id"]==serv_infos["serv_id"])]
    
    if servers==[]:
        return False

    ports_used_ls=[hp["lhs_port"] for hp in link["hps"]]
    ports_used_ls=list(set(ports_used_ls))

    servers_same_port=[server for server in servers if all(port in server["free_ports"].split(port_separator) for port in ports_used_ls)]

    if servers_same_port!=[]:
        replacement_server=Gotham_choose.choose_servers(servers_same_port, 1, link_tags_serv)

        if (len(ports_used_ls)==1):
            replacement_server["choosed_port"]=int(ports_used_ls[0])
            # Deploy new reverse-proxies's configurations on new server
            print("bypassed")
            #add_link.deploy_nginxConf(db_settings, link["link_id"], replacement_server)

        for hp in link["hps"]:
            modifs={"id_serv":replacement_server["serv_id"]}
            conditions={"id_link":link["link_id"],"id_hp":hp["hp_id"],"id_serv":serv_infos["serv_id"]}
            try:
                edit_lhs_DB(DB_settings,modifs,conditions)
            except:
                sys.exit(1)
        return True

    else:
        print("Not implemented")
        return False

