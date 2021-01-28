import paramiko
import scp
import sys

# Logging components
import os
import logging
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename = GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',level=logging.DEBUG ,format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')


class GothamServer:
    '''
    This class represents a server being part of the project
    '''

    def __init__(self, hostname, port, ssh_key):
        '''
        Initialize a GhotamServer object
        '''
        # SSH credentials (username@hostname)
        self.hostname = hostname
        self.username = "gotham"
        # Remote SSH port
        self.port = port
        # User's password
        self.ssh_key = paramiko.RSAKey.from_private_key(ssh_key)
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
                pkey = self.ssh_key
            )
            # Init an SCP session using the SSH session just created
            self.scp_session = scp.SCPClient(self.ssh_session.get_transport())
        logging.info(f"[+] SSH connection to the remote server {self.hostname} has just started")
        return self.ssh_session

    def disconnect(self):
        '''
        Close SSH & SCP connections
        '''
        if self.ssh_session:
            self.ssh_session.close()
            logging.info(f"[-] SSH connection to the remote server {self.hostname} has just been closed")
        if self.scp_session:
            self.scp_session.close()
        
    def upload_files(self, file_paths, remote_file_path):
        '''
        Upload files to a remote directory
        '''
        # Start an SCP connection
        self.is_connected = self.connect()
        # Send files
        for file_path in file_paths:
            self.scp_session.put(
                file_path,
                recursive = True,
                remote_path = remote_file_path
            )
            logging.info(f"The file {file_paths} has just been uploaded on the server {self.hostname} in the directory {remote_file_path}")
        
    def commands_execution(self, commands):
        '''
        Execute multiple commands
        '''
        # Start an SSH connection
        self.is_connected = self.connect()
        # Execute all of the commands
        for cmd in commands:
            stdin, stdout, stderr = self.ssh_session.exec_command(cmd)

            for line in stdout.read().splitlines():
                print(line)

            logging.info(f"The commands {commands} has just been executed on the server {self.hostname}")

