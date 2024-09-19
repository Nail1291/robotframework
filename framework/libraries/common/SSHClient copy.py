import paramiko
import logging

class SSHClient:
    def __init__(self, hostname, port, username, password):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.client = None
        self.ssh = None

        # Configure logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def connect(self):
        """Establish an SSH connection."""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.hostname, port=self.port, username=self.username, password=self.password)
            self.ssh = self.client.invoke_shell()
            self.logger.info(f"Connected to {self.hostname}")
        except paramiko.AuthenticationException:
            self.logger.error("Authentication failed")
        except paramiko.SSHException as e:
            self.logger.error(f"Unable to establish SSH connection: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")

    def run_command(self, command):
        """Execute a command on the remote server and return the output."""
        if not self.client:
            self.logger.error("SSH client is not connected")
            return None
        else: 
            self.logger.info(f"{self.hostname} Connected")            
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            
            if output:
                self.logger.info(f"Output of '{command}':\n{output}")
            if error:
                self.logger.error(f"Error executing '{command}':\n{error}")
            
            return output, error
        except Exception as e:
            self.logger.error(f"Error running command '{command}': {e}")
            return None, str(e)

    def close(self):
        """Close the SSH connection."""
        if self.client:
            self.client.close()
            self.logger.info("SSH connection closed")
