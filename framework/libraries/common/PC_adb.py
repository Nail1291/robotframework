import paramiko
import subprocess
import logging
import sys
from robot.api import logger

class LaptopMTPManager:
    def __init__(self, hostname, port, username, password, adb_path="adb"):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.client = None
        self.ssh = None
        self.adb_path = adb_path  # Path to adb command
        self.mtp_device = None

        # Configure logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        # Add a stream handler to output to the console
        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setLevel(logging.INFO)  # Adjust log level if needed
        self.console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        self.logger.addHandler(self.console_handler)


    def connect_rdp(self):
        """Establish an RDP connection to the laptop."""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.hostname, port=self.port, username=self.username, password=self.password)
            self.ssh = self.client.invoke_shell()
            self.logger.info(f"Connected to {self.hostname} via RDP")
        except paramiko.AuthenticationException:
            self.logger.error("Authentication failed")
        except paramiko.SSHException as e:
            self.logger.error(f"Unable to establish RDP connection: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")

    def run_adb_on_laptop(self, command):
        """Run a command on the connected laptop."""
        if not self.ssh:
            self.logger.error("Not connected to laptop")
            return None
        else:
            self.logger.info("laptop connected")
            logger.console(f"Connecting to {self.hostname} via RDP") #Calling the function from robot.api.logger for Robot console logging


        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()

            if output:
                self.logger.info(f"Output of '{command}':\n{output}")
                logger.console(f"Console Output of '{command}':\n{output}")
            if error:
                self.logger.error(f"Error executing '{command}':\n{error}")

            return output, error
        except Exception as e:
            self.logger.error(f"Error running command on laptop: {e}")
            return None, str(e)

    def connect_adb(self):
        """Connect to the Qualcomm MTP device via ADB."""
        try:
            result = subprocess.run([self.adb_path, "devices"], stdout=subprocess.PIPE)
            device_list = result.stdout.decode().splitlines()
            self.mtp_device = [line.split()[0] for line in device_list if "device" in line]

            if self.mtp_device:
                self.logger.info(f"Connected to MTP device: {self.mtp_device[0]}")
            else:
                self.logger.error("No MTP device found")
        except Exception as e:
            self.logger.error(f"Error connecting to MTP device: {e}")

    def run_adb_command(self, command):
        """Run an ADB command on the Qualcomm MTP device."""
        if not self.mtp_device:
            self.logger.error("No MTP device connected")
            return None

        try:
            full_command = [self.adb_path, "-s", self.mtp_device[0], "shell"] + command.split()
            result = subprocess.run(full_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout.decode()
            error = result.stderr.decode()

            if output:
                self.logger.info(f"Output of ADB command '{command}':\n{output}")
            if error:
                self.logger.error(f"Error executing ADB command '{command}':\n{error}")

            return output, error
        except Exception as e:
            self.logger.error(f"Error running ADB command '{command}': {e}")
            return None, str(e)

    def adb_start(self):
        """Start the MTP device using adb."""
        return self.run_adb_command("start")

    def ue_attach(self):
        """Attach the UE (Mobile Device) to the network."""
        return self.run_adb_command("service call phone 1")  # Example attach command

    def ue_detach(self):
        """Detach the UE (Mobile Device) from the network."""
        return self.run_adb_command("service call phone 2")  # Example detach command

    def run_iperf3(self, server_ip, port=5201, duration=10):
        """Run iperf3 on the MTP device to test network performance."""
        iperf_command = f"iperf3 -c {server_ip} -p {port} -t {duration}"
        return self.run_adb_command(iperf_command)

    def close_connections(self):
        """Close both SSH and ADB connections."""
        if self.client:
            self.client.close()
            self.logger.info("RDP connection closed")
        # No need to explicitly close ADB as subprocess will handle it

