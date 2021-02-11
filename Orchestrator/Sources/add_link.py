# -*- coding: utf-8 -*-
# Import Gotham's libs
from Gotham_SSH_SCP import send_file_and_execute_commands
from Gotham_link_BDD import get_server_infos, get_honeypot_infos

# Import external libs
from io import StringIO

def generate_nginxConf(db_settings, link_id, dc_ip, honeypots, exposed_port):
    '''
    Generate the config file to include in nginx config for the redirection
    
    ARGUMENTS:
        link_id (string): id of the link we are configuring nginx for
        dc_ip (string): ip of FQDN of the remote datacenter
        honeypots (list): list of honeypots
        exposed_port (int): port to listen on the server
    '''
    # Initialise the creation of the new nginx config file
    nginxRedirectionPath = "/data/template/"+ str(link_id) +"-"+str(exposed_port)+".conf"
    nginxRedirectionFile = open(nginxRedirectionPath, 'w')
    nginxRedirectionFile.write("upstream "+ link_id +" {\n")
    nginxRedirectionFile.write("  hash $remote_addr;\n")
    # Adding each honeypot in upstream
    for honeypot in honeypots:
        # Get the corresponding mapped port for this honeypot
        honeypot_port = honeypot["hp_port"] 
        nginxRedirectionFile.write("  # "+ str(honeypot["hp_id"]) +"\n")
        nginxRedirectionFile.write("  server "+ str(dc_ip) +":"+ str(honeypot_port) +";\n")
    # Closing upstream
    nginxRedirectionFile.write("}\n")
    # Configuring the redirection 
    nginxRedirectionFile.write("server {\n")
    nginxRedirectionFile.write("  listen "+ exposed_port +";\n")
    nginxRedirectionFile.write("  proxy_pass "+ link_id +";\n")
    nginxRedirectionFile.write("}\n")

def deploy_nginxConf(db_settings, link_id, servers):
    '''
    Deploy the nginx configuration on all servers chosen
    
    ARGUMENTS:
        link_id (string): id of the link we are configuring nginx for
        servers (dict): list of servers we want to deploy on associated with exposed ports
    '''
    # Initialize command and file
    checkAndReloadNginx_command = ["nginx -t; if [ $? -eq 0 ]; then; nginx -s reload; fi"]
    linkConf_dest = "/etc/nginx/conf.d/links/"
    # Deploy new configuration on each servers
    for server in servers:
        linkConf_path = ["/data/template/"+str(link_id)+"-"+str(server["choosed_port"])+".conf"]
        # Déploy configuration on the server and Reload nginx if ok
        send_file_and_execute_commands(server["serv_ip"], server["serv_ssh_port"], StringIO(server["serv_ssh_key"]), linkConf_path, linkConf_dest, checkAndReloadNginx_command)

### TEST SECTION ###
if __name__ == '__main__':
    db_settings = {"username":"root", "password":"password", "hostname":"localhost", "port":"3306", "database":"GOTHAM"}
    link_id = "lk-123456789"
    dc_ip = "datacenter.local"
    honeypots = ["hp-4332bc41f15f4d9181dd21e175fa3d42","hp-018ad24e2c6942d7ab4ede959035f9d4"]
    exposed_port = "8080"
    generate_nginxConf(db_settings, link_id, dc_ip, honeypots, exposed_port)
    deploy_nginxConf(db_settings, link_id, ["sv-c8d26db7ee934eeb81c5409e67fe1d82%"])
