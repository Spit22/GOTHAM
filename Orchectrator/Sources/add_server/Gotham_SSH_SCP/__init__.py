from . import SSH_SCP_classes

def main(hostname, port, username, password, file_path, remote_file_path, commands):
    """Initialize remote host client and execute actions."""
    remote_server = SSH_SCP_classes.GothamServer(hostname, port, username, password, file_path, remote_file_path, commands)
    remote_server.upload_file()
    remote_server.execute_commands()
    remote_server.disconnect()
    