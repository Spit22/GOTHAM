# Import external libs
from io import StringIO
import base64
import sys
import configparser

# GOTHAM'S LIB
import Gotham_link_BDD
import Gotham_check
import Gotham_choose
import Gotham_normalize
import Gotham_SSH_SCP
import add_link

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


def edit_tags(DB_settings, server, tags):

    config = configparser.ConfigParser()
    config.read(GOTHAM_HOME + 'Orchestrator/Config/config.ini')
    tags_separator = config['tag']['separator']
    port_separator = config['port']['separator']

    old_tags=server["serv_tags"].split("||")
    new_tags=tags.split(tags_separator)

    deleted_tags=list(set(old_tags)-set(new_tags))

    dsp_server=Gotham_normalize.normalize_display_object_infos(server,"serv")

    for deleted_tag in deleted_tags:
        for link in dsp_server["links"]:
            if deleted_tag in link["link_tags_serv"].split("||"):
                link_tags_serv=tags_separator.join(link["link_tags_serv"].split("||"))

                # Get all servers corresponding to tags
                servers = Gotham_check.check_tags("serv",Gotham_link_BDD.get_server_infos(DB_settings, tags=link_tags_serv), tags_serv=link_tags_serv)

                # Filter servers in those who have one of ports open
                servers = Gotham_check.check_servers_ports_matching(servers, link["link_ports"])

                # Filter servers in error, with same link, and original server by id
                servers = [serv for serv in servers if not(serv["serv_state"]=='ERROR' or link["link_id"] in serv["link_id"] or serv["serv_id"]==server["serv_id"])]
                
                succes=False
                if servers!=[]:
                    ports_used_ls=[hp["lhs_port"] for hp in link["hps"]]
                    ports_used_ls=list(set(ports_used_ls))

                    servers_same_port=[serv for serv in servers if all(port in serv["free_ports"].split(port_separator) for port in ports_used_ls)]

                    if servers_same_port!=[]:
                        replacement_server=Gotham_choose.choose_servers(servers_same_port, 1, link_tags_serv)

                        already_deployed=[]
                        for hp in link["hps"]:
                            if not(int(hp["lhs_port"]) in already_deployed):
                                replacement_server[0]["choosed_port"]=int(hp["lhs_port"])
                                add_link.deploy_nginxConf(DB_settings, link["link_id"], replacement_server)
                                already_deployed.append(int(replacement_server[0]["choosed_port"]))
                            modifs={"id_serv":replacement_server[0]["serv_id"]}
                            conditions={"id_link":link["link_id"],"id_hp":hp["hp_id"],"id_serv":server["serv_id"]}
                            try:
                                Gotham_link_BDD.edit_lhs_DB(DB_settings,modifs,conditions)
                            except:
                                sys.exit(1)
                        succes=True

                    else:
                        print("Not implemented")
                        
                if succes==False:
                    if int(link["link_nb_serv"]) > 1:
                        try:
                            Gotham_link_BDD.remove_lhs(DB_settings,id_link=link["link_id"], id_serv=server["serv_id"])
                        except:
                            sys.exit(1)
                        try:
                            modifs={"nb_serv":int(link["link_nb_serv"])-1}
                            conditions={"id":link["link_id"]}
                            Gotham_link_BDD.edit_link_DB(DB_settings, modifs, conditions)
                            succes=True
                        except:
                            sys.exit(1)
                    else:        
                        # If nb serv=1, error, we can't do nothing
                        logging.warning(f"You tried to remove a running server with the id = {id}, and it can't be replaced or deleted")
                        return False
                if succes==True:
                    try:
                        commands = ["sudo rm /etc/nginx/conf.d/links/" + link["link_id"] +"-*.conf"]
                        Gotham_SSH_SCP.execute_commands(server["serv_ip"], server["serv_ssh_port"], server["serv_ssh_key"], commands)
                        return True
                    except Exception as e:
                        logging.error(f"{link['link_id']} removal on servers failed : {e}")
                        sys.exit(1)

def edit_connection(DB_settings, server, ip, ssh_port, ssh_key):

    # First check the ip not already exists in database
    exists = Gotham_check.check_doublon_server(DB_settings, ip)
    if exists:
        logging.error(f"Provided ip already exists in database")
        sys.exit(1)

    # Check given auth information are ok
    connected = Gotham_check.check_ssh(ip, ssh_port, ssh_key) 
    if not connected:
        logging.error(f"Provided ssh_key or ssh_port is wrong")
        sys.exit(1)

    return