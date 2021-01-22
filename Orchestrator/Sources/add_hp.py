# -*- coding: utf-8 -*-
# Import Gotham's libs
from Gotham_SSH_SCP import send_file_and_execute_commands

def generate_compose(id, dockerfile_path, log_path, honeypot_port, mapped_port):
    # Generates a docker-compose.yml file  from given information
    #
    # id (string) : id of the honeypot
    # dockerfile_path (string) : local path to the dockerfile
    # log_path (string) : remote path of logs (in the honeypot)
    # mapped_port (int) : available port we can map honeypot to

    dockercompose = open(str(dockerfile_path)+"docker-compose.yml", "a")
    
    # Write the docker-compose version
    dockercompose.write('version: "3"\n')
    # Add the 'service' tag for honeypot service
    dockercompose.write('services:\n')
    # Add the honeypot service
    dockercompose.write('  honeypot:\n')
    # Configure container name
    dockercompose.write('    container_name: '+str(id)+'\n')
    # Add volumes for logs
    dockercompose.write('    volumes:\n')
    dockercompose.write('      - /data/'+str(id)+'/logs:'+str(log_path)+'\n')
    # Build options
    dockercompose.write('    build:\n')
    dockercompose.write('      context: .\n')
    dockercompose.write('      dockerfile: Dockerfile\n')
    # Map ports
    dockercompose.write('    ports:\n')
    dockercompose.write('      - '+str(mapped_port)+':'+str(honeypot_port))
    # Close file
    dockercompose.close()

def deploy_container(dc_ip, dc_ssh_port, dc_ssh_key, dockerfile_path):
    # Install and deploy an Nginx Reverse-Proxy on a given server
    #
    # ip (string): ip of remote server
    # ssh_port (int) : port the ssh service listen
    # used_ssh_key (file-like object) : ssh key used to connect to server
    #
    # Return True if succeed, False in the other case

    # Declare local vars
    docker_dest = "/tmp/tmpdocker/"
    command_exec_compose = ["cd "+str(docker_dest),"docker-compose up -d", "rm -rf /tmp/tmpdocker"]
    
    # Copy docker files on datacenter, and execute docker-compose
    try:
        send_file_and_execute_commands(dc_ip, dc_ssh_port, dc_ssh_key, dockerfile_path, docker_dest, command_exec_compose)
    except Exception as e:
        return False
    # If deployment is OK, return True
    return True

if __name__ == '__main__':
    id = "sv-test"
    dockerfile_path = "/data/sv-test/docker/"
    log_path = "/var/log/syslog"
    honeypot_port = "22"
    mapped_port = "2200"
    generate_compose(id, dockerfile_path, log_path, honeypot_port, mapped_port)
