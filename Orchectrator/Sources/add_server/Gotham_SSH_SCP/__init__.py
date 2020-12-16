from . import SSH_SCP_classes

def main(hostname, port, username, password, file_path, remote_file_path, commands):
    """Initialize remote server and execute some actions"""
    # Init remote_server object
    remote_server = SSH_SCP_classes.GothamServer(hostname, port, username, password, file_path, remote_file_path, commands)
    # Upload the file
    remote_server.upload_file()
    # Execute the commands
    remote_server.execute_commands()
    # Close the connection
    remote_server.disconnect()
    