# -*- coding: utf-8 -*-
# Import Gotham's libs
from Gotham_SSH_SCP import send_file_and_execute_commands

def generate_nginxConf(link_id, dc_ip, honeypots, exposed_port):
    # Generate the config file to include in nginx config for the redirection
    #
    # link_id (string): id of the link we are configuring nginx for
    # dc_ip (string): ip of FQDN of the remote datacenter
    # honeypots (dict): dict of honeypots id associated to ports where to redirect the trafic
    # exposed_port (int): port to listen on the server
    
    nginxRedirectionPath = "/data/template/"+ str(link_id) +".conf"
    nginxRedirectionFile = open(nginxRedirectionPath, 'a')

    nginxRedirectionFile.write("upstream "+ link_id +" {\n")
    nginxRedirectionFile.write("  hash $remote_addr;\n")

    # Adding each honeypot in upstream
    for honeypot in honeypots:
        nginxRedirectionFile.write("  # "+ honeypot +"\n")
        nginxRedirectionFile.write("  server "+ dc_ip +":"+ honeypots[honeypot] +";\n")
    
    # Closing upstream
    nginxRedirectionFile.write("}\n")

    # Configuring the redirection 
    nginxRedirectionFile.write("server {\n")
    nginxRedirectionFile.write("  listen "+ exposed_port +";\n")
    nginxRedirectionFile.write("  proxy_pass "+ link_id +";\n")
    nginxRedirectionFile.write("}\n")

def deploy_nginxConf(link_id, servers):
    # Deploy the nginx configuration on all servers chosen
    #
    # link_id (string): id of the link we are configuring nginx for
    # servers (list): list of ip of servers we want to deploy on
    checkAndReloadNginx_command = ["nginx -t; if [ $? -eq 0 ]; then; nginx -s reload; fi"]
    linkConf_path = ["/data/template/"+str(link_id)+".conf"]
    linkConf_dest = "/etc/nginx/conf.d/links/"

    for server in servers:
        # Get stored auth info of the server

        # Déploy configuration on the server and Reload nginx if ok
        send_file_and_execute_commands(srv_ip, srv_ssh_port, srv_ssh_key, linkConf_path, linkConf_dest, checkAndReloadNginx_command)

if __name__ == '__main__':
    link_id = "hp-123456789"
    dc_ip = "datacenter.local"
    honeypots = {"hp-123456":"1037","hp-test":"1035"}
    exposed_port = "8080"
    generate_nginxConf(link_id, dc_ip, honeypots, exposed_port)
