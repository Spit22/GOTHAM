#===Import external libs===#
import paramiko
import scp
from io import StringIO
import os
import logging
#==========================#

#===Logging components===#
GOTHAM_HOME = os.environ.get('GOTHAM_HOME')
logging.basicConfig(filename=GOTHAM_HOME + 'Orchestrator/Logs/gotham.log',
                    level=logging.DEBUG, format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
#=======================#


class GothamServer:
    '''
    This class represents a remote server being part of the project

    METHODS:
        connect() : open a ssh session with the remote server
        disconnect() : close the ssh session with the remote server
        upload_files() : upload file(s) on the remote server
        commands_execution() : execute command(s) on the remote server
    '''

    def __init__(self, hostname, port, ssh_key):
        '''
        Initialize a GhotamServer object

        ARGUMENTS:
            hostname (string) : hostname of the remote server
            port (string) : SSH port of the remote host
            ssh_key (string) : SSH key that allow the orchestrator to connect to the remote host
        '''
        # SSH credentials (username@hostname)
        self.hostname = hostname
        self.username = "root"
        # Remote SSH port
        self.port = port
        # User's key
        self.ssh_key = StringIO(ssh_key)
        self.ssh_key = paramiko.RSAKey.from_private_key(self.ssh_key)
        # Some variable for class's methods
        self.ssh_session = None
        self.scp_session = None
        self.is_connected = False

    def connect(self):
        '''
        Open SSH and SCP session with the remote server
        '''
        if self.is_connected is False:
            # Init an SSH session
            self.ssh_session = paramiko.SSHClient()
            # Check in known_host file
            self.ssh_session.load_system_host_keys()
            self.ssh_session.set_missing_host_key_policy(
                paramiko.AutoAddPolicy())
            # Start the SSH session
            self.ssh_session.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                pkey=self.ssh_key
            )
            # Init an SCP session using the SSH session just created
            self.scp_session = scp.SCPClient(self.ssh_session.get_transport())
        logging.info(f"[+] SSH connection with the remote server {self.hostname} has just started")
        return self.ssh_session

    def disconnect(self):
        '''
        Close SSH & SCP connections
        '''
        if self.ssh_session:
            try:
                self.ssh_session.close()
                logging.info(f"[-] SSH connection with the remote server {self.hostname} has just been closed")
            except Exception as e:
                error = f"SSH disconnection with {self.hostname} failed : {e}"
                logging.error(error)
                raise ValueError(error)
        if self.scp_session:
            try:
                self.scp_session.close()
            except Exception as e:
                error = f"SCP disconnection with {self.hostname} failed : {e}"
                logging.error(error)
                raise ValueError(error)

    def upload_files(self, file_paths, remote_file_path):
        '''
        Upload files to a remote directory

        ARGUMENTS:
            file_path (list) : local path(s) of the file(s) we want to send
            remote_file_path (string) : path on the remote host we want to put the file(s)
        '''
        # Start an SCP connection
        try:
            self.is_connected = self.connect()
        except Exception as e:
            error = f"Connection with {self.hostname} failed : {e}"
            logging.error(error)
            raise ValueError(error)
        # Send files
        for file_path in file_paths:
            self.scp_session.put(
                file_path,
                recursive=True,
                remote_path=remote_file_path
            )
            logging.info(
                f"The file {file_paths} has just been uploaded on the server {self.hostname} in the directory {remote_file_path}")

    def commands_execution(self, commands):
        '''
        Execute multiple commands

        ARGUMENTS:
            commands (list) : list of the commands we want to execute on the remote server
        '''
        # Start an SSH connection
        try:
            self.is_connected = self.connect()
        except Exception as e:
            error = f"Connection with {self.hostname} failed : {e}"
            logging.error(error)
            raise ValueError(error)

        # Execute all of the commands
        for cmd in commands:
            stdin, stdout, stderr = self.ssh_session.exec_command(cmd)
            for line in stdout.read().splitlines():
                print("Command return : "+str(line))

        logging.info(
            f"The commands {commands} has just been executed on the server {self.hostname}")

    def command_execution_with_return(self, command):
        '''
        Execute a command and return the stdout

        ARGUMENTS:
            command (string) : command we want to execute on the remote server
        '''
        # Start an SSH connection
        try:
            self.is_connected = self.connect()
        except Exception as e:
            error = f"Connection with {self.hostname} failed : {e}"
            logging.error(error)
            raise ValueError(error)

        # Execute all of the commands
        stdin, stdout, stderr = self.ssh_session.exec_command(command)
        answer=[]
        for line in stdout.read().splitlines():
            if str(line)[0:2] == "b'" or str(line)[0:2] == 'b"':
                line=str(line)[2:-1]
            answer.append(str(line))

        logging.info(
            f"The command {command} has just been executed on the server {self.hostname}")
        return answer
