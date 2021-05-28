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
    try:
        remote_server.upload_files(file_path, remote_file_path)
    except Exception as e:
        raise ValueError(e)
    # Close the connection
    try:
        remote_server.disconnect()
    except Exception as e:
        raise ValueError(e)


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
    try:
        remote_server.commands_execution(commands)
    except Exception as e:
        raise ValueError(e)
    # Close the connection
    try:
        remote_server.disconnect()
    except Exception as e:
        raise ValueError(e)


def execute_command_with_return(hostname, port, ssh_key, command):
    '''
    Execute command on a remote server
    
    ARGUMENTS:
        hostname (string) : hostname of the remote host
        port (string) : SSH port of the remote host
        ssh_key (string) : SSH key that allow the orchestrator to connect to the remote host
        command (string) : the command we want to execute on the remote server
    '''
    # Init remote_server object
    remote_server = SSH_SCP_classes.GothamServer(hostname, port, ssh_key)
    # Execute the commands
    try:
        answer=remote_server.command_execution_with_return(command)
    except Exception as e:
        raise ValueError(e)
    # Close the connection
    try:
        remote_server.disconnect()
    except Exception as e:
        raise ValueError(e)
    return answer


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
    try:
        remote_server.upload_files(file_path, remote_file_path)
    except Exception as e:
        raise ValueError(e)
    # Execute the commands
    try:
        remote_server.commands_execution(commands)
    except Exception as e:
        raise ValueError(e)
    # Close the connection
    try:
        remote_server.disconnect()
    except Exception as e:
        raise ValueError(e)
