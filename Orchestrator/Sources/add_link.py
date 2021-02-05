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
        honeypots (list): list of honeypots id
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
        honeypot_infos = get_honeypot_infos(db_settings, id=honeypot["hp_id"])[0]
        honeypot_port = honeypot_infos["hp_port"] 
        nginxRedirectionFile.write("  # "+ str(honeypot) +"\n")
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
        servers (dict): list of ip of servers we want to deploy on associated with exposed ports
    '''
    # Initialize command and file
    checkAndReloadNginx_command = ["nginx -t; if [ $? -eq 0 ]; then; nginx -s reload; fi"]
    linkConf_dest = "/etc/nginx/conf.d/links/"
    # Deploy new configuration on each servers
    for server in servers:
        print(server)
        exposed_port = servers[server]
        linkConf_path = ["/data/template/"+str(link_id)+"-"+str(exposed_port)+".conf"]
        # Get stored auth info of the server
        server_infos = get_server_infos(db_settings, ip=server)[0]
        srv_ip = server_infos["serv_ip"]
        srv_ssh_port = server_infos["serv_ssh_port"]
        srv_ssh_key = StringIO(server_infos["serv_ssh_key"])
        # Déploy configuration on the server and Reload nginx if ok
        send_file_and_execute_commands(srv_ip, srv_ssh_port, srv_ssh_key, linkConf_path, linkConf_dest, checkAndReloadNginx_command)

### TEST SECTION ###
if __name__ == '__main__':
    db_settings = {"username":"root", "password":"password", "hostname":"localhost", "port":"3306", "database":"GOTHAM"}
    link_id = "lk-123456789"
    dc_ip = "datacenter.local"
    honeypots = ["hp-4332bc41f15f4d9181dd21e175fa3d42","hp-018ad24e2c6942d7ab4ede959035f9d4"]
    exposed_port = "8080"
    generate_nginxConf(db_settings, link_id, dc_ip, honeypots, exposed_port)
    deploy_nginxConf(db_settings, link_id, ["sv-c8d26db7ee934eeb81c5409e67fe1d82%"])
