import os
import paramiko
import scp

class GothamServer:
    '''
    This class represents a server being part of the project
    '''

    def __init__(self, hostname, port, username, password, file_path, remote_file_path, commands):
        '''
        Initialize a GhotamServer object
        '''
        # SSH credentials (username@hostname)
        self.hostname = hostname
        self.username = username
        # Remote SSH port
        self.port = port
        # User's password
        self.password = password
        # Local path of the file to send 
        self.file_path = file_path
        # Remote path of the file sent
        self.remote_file_path = remote_file_path
        # Commands to execute on the remote server
        self.commands = commands
        # Some variable for class's methods
        self.ssh_session = None
        self.scp_session = None
        self.is_connected = False
    
    def connect(self):
        '''
        Open SSH and SCP session to the remote server
        '''
        if self.is_connected is False:
            # Init an SSH session
            self.ssh_session = paramiko.SSHClient()
            # Check in known_host file
            self.ssh_session.load_system_host_keys()
            self.ssh_session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # Start the SSH session
            self.ssh_session.connect(
                hostname = self.hostname,
                port = self.port,
                username = self.username,
                password = self.password
            )
            # Init an SCP session using the SSH session just created
            self.scp_session = scp.SCPClient(self.ssh_session.get_transport())
        return self.ssh_session

    def disconnect(self):
        '''
        Close SSH & SCP connections
        '''
        if self.ssh_session:
            self.ssh_session.close()
            print("[+] SSH Session closed")
        if self.scp_session:
            self.scp_session.close()
            print("[+] SCP Session closed")
        
    def upload_file(self):
        '''
        Upload a single file to a remote directory
        '''
        # Start an SCP connection
        self.is_connected = self.connect()
        # Send the file
        self.scp_session.put(
            self.file_path,
            recursive = True,
            remote_path = self.remote_file_path
        )
        print("[+] File Uploaded !")
        
    def execute_commands(self):
        '''
        Execute multiple commands
        '''
        # Start an SSH connection
        self.is_connected = self.connect()
        # Execute all of the commands
        for cmd in self.commands:
            self.ssh_session.exec_command(cmd)
            print("[+] Command executed !")