from . import SSH_SCP_classes

def send_file(hostname, port, username, password, file_path, remote_file_path):
    # Init remote_server object
    remote_server = SSH_SCP_classes.GothamServer(hostname, port, username, password)
    # Upload the file
    remote_server.upload_file(file_path, remote_file_path)
    # Close the connection
    remote_server.disconnect()

def execute_commands(hostname, port, username, password, commands):
    """Initialize remote server and execute some actions"""
    # Init remote_server object
    remote_server = SSH_SCP_classes.GothamServer(hostname, port, username, password)
    # Execute the commands
    remote_server.commands_execution(commands)
    # Close the connection
    remote_server.disconnect()

def send_file_and_execute_commands(hostname, port, username, password, file_path, remote_file_path, commands):
    # Init remote_server object
    remote_server = SSH_SCP_classes.GothamServer(hostname, port, username, password)
    # Upload the file
    remote_server.upload_file(file_path, remote_file_path)
    # Execute the commands
    remote_server.commands_execution(commands)
    # Close the connection
    remote_server.disconnect()