import os
import paramiko
import scp

class GothamServer:
    ''' Represent a server used by the project '''

    def __init__(self, hostname, port, username, password, file_path, remote_file_path, commands):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.file_path = file_path
        self.remote_file_path = remote_file_path
        self.commands = commands
        self.ssh_session = None
        self.scp_session = None
        self.is_connected = False
    
    def connect(self):
        ''' Open SSH and SCP session to the remote server '''
        if self.is_connected is False:
            # Init an SSH session
            self.ssh_session = paramiko.SSHClient()
            self.ssh_session.load_system_host_keys()
            self.ssh_session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_session.connect(
                hostname = self.hostname,
                port = 22,
                username = self.username,
                password = self.password
            )
                #Init an SCP session using the SSH session just created
            self.scp_session = scp.SCPClient(self.ssh_session.get_transport())
        return self.ssh_session

    def disconnect(self):
        """Close SSH & SCP connection."""
        if self.ssh_session:
            self.ssh_session.close()
            print("[+] SSH Session closed")
        if self.scp_session:
            self.scp_session.close()
            print("[+] SCP Session closed")
        
    def upload_file(self):
        """Upload a single file to a remote directory."""
        file = self.file_path
        self.is_connected = self.connect()
        self.scp_session.put(
            file,
            recursive=True,
            remote_path="/home/rev"
        )
        print("[+] File Uploaded !")
        

    def execute_commands(self):
        """
        Execute multiple commands in succession.
        param commands: List of unix commands as strings.
        :type commands: List[str]
        """
        self.is_connected = self.connect()
        for cmd in self.commands:
            self.ssh_session.exec_command(cmd)
            print("[+] Command executed !")
            #stdin, stdout, stderr = self.ssh_session.exec_command(cmd)
            #stdout.channel.recv_exit_status()
            #response = stdout.readlines()