# -*- coding: utf-8 -*-

#===Import GOTHAM's libs===#
from Gotham_SSH_SCP import send_file_and_execute_commands
#==========================#


def generate_nginxConf(db_settings, link_id, dc_ip, honeypots, exposed_port):
    # Generate the config file to include in nginx config for the redirection
    # 
    # link_id (string): id of the link we are configuring nginx for
    # dc_ip (string): ip of FQDN of the remote datacenter
    # honeypots (list): list of honeypots
    # exposed_port (int): port to listen on the server

    # Initialise the creation of the new nginx config file
    nginxRedirectionPath = "/data/template/" + \
        str(link_id) + "-"+str(exposed_port)+".conf"
    nginxRedirectionFile = open(nginxRedirectionPath, 'w')
    nginxRedirectionFile.write("upstream " + link_id + " {\n")
    nginxRedirectionFile.write("  hash $remote_addr;\n")
    # Adding each honeypot in upstream
    for honeypot in honeypots:
        # Get the corresponding mapped port for this honeypot
        honeypot_port = int(honeypot["hp_port"])
        nginxRedirectionFile.write("  # " + str(honeypot["hp_id"]) + "\n")
        nginxRedirectionFile.write(
            "  server " + str(dc_ip) + ":" + str(honeypot_port) + ";\n")
    # Closing upstream
    nginxRedirectionFile.write("}\n")
    # Configuring the redirection
    nginxRedirectionFile.write("server {\n")
    nginxRedirectionFile.write("  listen " + str(exposed_port) + ";\n")
    nginxRedirectionFile.write("  proxy_pass " + str(link_id) + ";\n")
    nginxRedirectionFile.write("}\n")


def deploy_nginxConf(db_settings, link_id, servers):
    # Deploy the nginx configuration on all servers chosen
    #
    # link_id (string): id of the link we are configuring nginx for
    # servers (dict): list of servers we want to deploy on associated with exposed ports

    # Initialize command and file
    checkAndReloadNginx_command = [
        "/usr/sbin/nginx -t && /usr/sbin/nginx -s reload"]
    linkConf_dest = "/etc/nginx/conf.d/links/"
    # Deploy new configuration on each servers
    for server in servers:
        if "choosed_port" not in server.keys() and "lhs_port" in server.keys():
            server["choosed_port"] = server["lhs_port"]

        linkConf_path = ["/data/template/" +
                         str(link_id)+"-"+str(server["choosed_port"])+".conf"]
        # Deploy configuration on the server and Reload nginx if ok
        send_file_and_execute_commands(server["serv_ip"], server["serv_ssh_port"],
                                       server["serv_ssh_key"], linkConf_path, linkConf_dest, checkAndReloadNginx_command)
