#===Import GOTHAM's libs===#
from . import SSH_SCP_classes
#==========================#


def send_file(hostname, port, ssh_key, file_path, remote_file_path):
    '''
    Send a file to a remote host

    ARGUMENTS:
        hostname (string) : hostname of the remote host
        port (string) : SSH port of the remote host
        ssh_key (string) : SSH key that allow the orchestrator to connect to the remote host
        file_path (list) : list of local path(s) of the file(s) we want to send
        remote_file_path (string) : path on the remote host we want to put the file(s)
    '''
    # Init remote_server object
    remote_server = SSH_SCP_classes.GothamServer(hostname, port, ssh_key)
    # Upload the file
    remote_server.upload_files(file_path, remote_file_path)
    # Close the connection
    remote_server.disconnect()


def execute_commands(hostname, port, ssh_key, commands):
    '''
    Execute commands on a remote server
    
    ARGUMENTS:
        hostname (string) : hostname of the remote host
        port (string) : SSH port of the remote host
        ssh_key (string) : SSH key that allow the orchestrator to connect to the remote host
        commands (list) : list of the commands we want to execute on the remote server
    '''
    # Init remote_server object
    remote_server = SSH_SCP_classes.GothamServer(hostname, port, ssh_key)
    # Execute the commands
    remote_server.commands_execution(commands)
    # Close the connection
    remote_server.disconnect()


def send_file_and_execute_commands(hostname, port, ssh_key, file_path, remote_file_path, commands):
    '''
    Send a file to a remote host then execute commands

    ARGUMENTS:
        hostname (string) : hostname of the remote host
        port (string) : SSH port of the remote host
        ssh_key (string) : SSH key that allow the orchestrator to connect to the remote host
        file_path (list) : local path(s) of the file(s) we want to send
        remote_file_path (string) : path on the remote host we want to put the file(s)
        commands (list) : list of the commands we want to execute on the remote server
    '''
    # Init remote_server object
    remote_server = SSH_SCP_classes.GothamServer(hostname, port, ssh_key)
    # Upload the file
    remote_server.upload_files(file_path, remote_file_path)
    # Execute the commands
    remote_server.commands_execution(commands)
    # Close the connection
    remote_server.disconnect()
