# Copyright.
from typing import List
import datetime
import os
import re
from stat import S_ISDIR
import sys
import time
import traceback
import paramiko
from scp import SCPClient
import socket
from paramiko_expect import SSHClientInteraction
from framework.libraries.common.Logger import Logger as logger
import chardet
from framework.global_variables import Global_Variables

class SSHConnection:
    """
    This class provides the utility to ssh connect and interact with remote server
    """
    
    def __init__(
        self, 
        host: str, 
        username: str, 
        password: str, 
        port: str, 
        match: str = "No match string provided", 
        windows_platform: bool = False,
    ) -> None:
        self.host = host
        self.username = username
        self.password = password
        self.ssh_port = port
        self.match = match
        self.windows_platform = windows_platform

        try:
            # Create a new SSH client object
            self.client = paramiko.SSHClient()
            
            # Set SSH key parameters to auto accept unknown hosts
            self.client.load_system_host_keys()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect to the host
            self.client.connect(
                hostname=self.host,
                username=self.username,
                password=self.password,
                #port=Global_Variables.ssh_port,
                port=self.ssh_port,
                banner_timeout=60,
            )
            self.logg = logger("Just a test")
            self.logg.info("Successfully SSH to {}".format(self.host))
            
            # Open transport channel in case it's needed
            self.transport = self.client.get_transport()
            self.transport.set_keepalive(60)  # send a keepalive packet for every minute
            self.channel = self.transport.open_session()
            self.shell_chan = self.client.invoke_shell(width=160)
            self.ssh_channel_list = []
        
        except Exception as err:
            raise Exception(
                "\nSSH failed to connect {} with error: {}".format(self.host, err)
            )

        # Get user prompt and sudo prompt
        self.user_prompt, self.sudo_prompt = self.get_prompt()

    def check_channel_is_root(self) -> bool:
        """
        Description:
            Check the channel is root or not.
        Parameters:
            None
        Return:
            (bool): True if channel has already root
        """
        channel_id = self.shell_chan.chanid
        if channel_id not in self.root_channel_list:
            command_output = self.send_command_and_extract_output("whoami")
            if command_output[0] == "root":
                logger.info("The session is being run with super user!")
                self.root_channel_list.append(channel_id)
                return True
            else:
                logger.info("The session does not run with super user! Will root")
                return False
        else:
            logger.info("The session is being run with super user!")
            return True

    def reset(self) -> None:
        """
        Description:
            This function will reset the ssh connection, which will close then re-init the connection.
        Parameters:
            None
        Return:
            None
        """
        logger.info(f"Reset the connection to {self.host} for {self.username}")
        self.client.close()
        self.__init__(
            self.host,
            self.username,
            self.password,
            #Global_Variables.ssh_port,
            self.match,
            self.windows_platform,
        )

    def check_ssh_connection(self) -> bool:
        """
        Description:
        This will check if the connection is still available.

        Paramters:
        None

        Return: (bool)
        ...
        """

        if not self.transport.is_active():
            self.shell_chan.transport.close()
            self.channel.close()
            self.transport.close()
            self.client.close()
            return False
        return True
        
    def sendCommand(self, command:str, check_error:bool = True, ignore_err_message:str = "", timeout:int = 60, log_html:bool = True) -> str:
        """
        Description:
        This function will send the comand to remote server, it can be used when send multiple independent commands separately or combined multiple dependent commands and sent once

        Parameters:

        """
        try:
            if "sudo su" == command:
                prompt = self.send_command_and_extract_output("whoami")
                if prompt[0] == "root":
                    logger.debug("The session is being run with super user: {}".format(prompt[0]))
                    return f"{command}\n{self.sudo_prompt}"
            
            if log_html:
                logger.info("Sending Host: {} the command: {}".format(self.host, command))
            
            stdin, stdout, stderr = self.client.exec_command(command=command, timeout=timeout)
            start_time = time.time()
            
            while (
                not stdout.channel.exit_status_ready()
                and not stdout.channel.recv_ready()
            ):
                if time.time() > start_time + (timeout + 2):
                    raise Exception(
                        f"The remote host was not ready for sending command after {timeout + 2}"
                    )
            
            stdout_output = "".join(stdout.readlines())
            if log_html:
                logger.info("stdout of command: {} is: {}".format(command, stdout_output))
            
            # check the stderr
            stderr_output = stderr.readlines()
            if check_error and stderr_output:
                if ignore_err_message and ignore_err_message in "".join(stderr_output):
                    logger.debug(f"Ignore Error: {ignore_err_message}.")
                    logger.debug(f"Command '{command}' got error: {stderr_output}.")
                else:
                    logger.error(f"Command '{command}' hit error: {stderr_output}")
                    raise Exception(f"Command '{command}' hit error: {stderr_output}")
            
            return stdout_output
        except Exception as err:
            logger.error(f"Command '{command}' hit exception: {err}")
            raise Exception(err)

    def send_command_com_port(self, command: str, no_of_lines_to_read: int = 10) -> str:
        """
        Description:
            This function should be used to read a section of continuous output from the serial port.
        Parameters:
            command (str): A command that works through serial port
            no_of_lines_to_read (int): No. of lines to read from continuous serial output; default value is 10
        Return: 
            (str)
            If passed, return stdout_output
            If failed, raise exception
        """
        
        try:
            logger.info("Sending Host: {} the command: {}".format(self.host, command))
            
            stdin, stdout, stderr = self.client.exec_command(command, get_pty=True)
            no_of_lines = 0
            
            for line in iter(lambda: stdout.readline(2048), ""):
                if no_of_lines <= no_of_lines_to_read:
                    line = line.strip("\r\n")
                    logger.info(line)
                    output += line
                    no_of_lines += 1
                else:
                    break
            stdin.clese()
            stdout.close()
            stderr.close()
            return line
        except Exception as err:
            logger.error('command "{}" hit exception: {}'.format(command, err))


    def sendCommand_shell(self, command: str, check_error=False, encoding_standard: str = None, timeout: int = 60, log_html: bool = True) -> str:
        """
        Description:
        Function to send a shell command over SSH, handle different platforms (Windows/Linux), log output,
        and handle success/failure responses from the remote host.

        """
        try:
            self.shell_chan.timeout = timeout
            if not self.transport.is_active():
                raise Exception(
                    f"Command: {command} was sent to an inactive SSH session."
                    "This session may have timed out or failed due to a long-running "
                    "or stuck command or connectivity issues between test runner and component."
                )

            if self.windows_platform:
                end_of_command = "\r\n"
                success_status_command = "echo %ERRORLEVEL%"
            else:
                end_of_command = "\n"
                success_status_command = "echo $?"

            if "sudo su" == command and not self.windows_platform and not self.check_channel_is_root():
                return ""

            if log_html:
                logger.info("sending Host: {} the command: {}".format(self.host, command))

            self.shell_chan.send(command + end_of_command)
            start_time = time.time()
            time_out = timeout if timeout else 60

            while not self.shell_chan.recv_ready():
                if time.time() > start_time + (time_out * 2):
                    raise Exception(
                        f'The remote host was not ready for sending command after {timeout * 2}'
                    )

            # Append the cmd output to str: output until cmd execution is done or cmd asks for password.
            output = ""

            # Check if the cmd is a reboot command and capture the output of the cmd until the server becomes inaccessible via SSH.
            if "reboot" in command:
                start_time = time.time()
                while not (
                    re.search(self.sudo_prompt, output)
                    or re.search(self.user_prompt, output)
                    or re.search("password for .*:", output)
                    or re.search(self.match_output, output)
                    or not self.transport.is_active()
                ):
                    if encoding_standard:
                        output += self.shell_chan.recv(10000).decode(encoding_standard)
                    else:
                        output += self._decode_bytes(self.shell_chan.recv(10000))
                    
                    if timeout and (time.time() > (start_time + timeout * 5)):
                        raise Exception(
                            f"Cannot find any search conditions in the output of command {command} after timeout: {timeout * 5}s"
                        )
                if re.search(command, output):
                    logger.info(
                        f"...INFO, The (soft) reboot command was successfully sent out to the server...",
                        also_console=True,
                    )
                else:
                    raise Exception(
                        "The reboot command was not successfully sent out to the server."
                    )
                return output

            start_time = time.time()
            while not (
                re.search(self.sudo_prompt, output)
                or re.search(self.user_prompt, output)
                or re.search("password for .*:", output)
                or re.search(self.match_output, output)
            ):
                if encoding_standard:
                    output += self.shell_chan.recv(10000).decode(encoding_standard)
                else:
                    output += self._decode_bytes(self.shell_chan.recv(10000))

                if timeout and (time.time() > (start_time + timeout * 5)):
                    raise Exception(
                        f"Cannot find any search conditions in the output of command {command} after timeout: {timeout * 5}s"
                    )

            if check_error:
                self.shell_chan.send(success_status_command + end_of_command)
                start_time = time.time()
                while not self.shell_chan.recv_ready():
                    time.sleep(1)
                    if time.time() > start_time + (time_out * 2):
                        raise Exception(
                            f'The remote host was not ready for sending command after {timeout * 2}'
                        )
                success_status_output = ""
                if encoding_standard:
                    success_status_output += self.shell_chan.recv(4096).decode(encoding_standard)
                else:
                    success_status_output += self.shell_chan.recv(4096).decode()
                success_status_match = re.search(r"\r\n(\d+)\r\n", success_status_output)
                if success_status_match:
                    success_status_number = int(success_status_match.group(1))
                    if success_status_number != 0:
                        raise Exception(
                            f"===Unfortunately the command:{command} failed with error:{output}"
                        )

            if log_html:
                logger.info(
                    "output of command: {} is: {}".format(command, output.replace("\r", ""))
                )

            # Provide the password if it's needed
            if "[sudo] password for " in output:
                self.shell_chan.send(self.password + "\n")
                start_time = time.time()
                while not self.shell_chan.recv_ready():
                    if time.time() > start_time + (time_out * 2):
                        raise Exception(
                            f'The remote host was not ready for sending command after {timeout * 2}'
                        )

            return output

        except socket.timeout as e:
            logger.info(f"Traceback debug: {traceback.print_exc()}")
            # Reset the ssh connection
            self.reset()
            raise Exception(f"Command {command} hits the timeout exception {e}, no response after timeout: {timeout}")

        except Exception as e:
            logger.info(f"Traceback debug: {traceback.print_exc()}")
            raise Exception(f"Command {command} hits the exception: {e}")
        finally:
            #Revert timeout of the ssh connection channel.
            self.shell_chan.timeout = None

    def get_prompt(self):  
        """  
        Description:  
        This function is used to get the user prompt and sudo prompt.  
    
        Parameters:  
        None  
    
        Returns:  
        escaped_user_prompt (str): Regular expression pattern for the user prompt.  
        escaped_sudo_prompt (str): Regular expression pattern for the sudo prompt.  
        """  
        try:  
            user_prompt_found = False  
            get_prompt_timeout = time.time() + 5  
            while time.time() <= get_prompt_timeout:  
                decoded_string = self.decode_bytes(self.shell_chan.recv(1024))
                user_login_text = decoded_string.splitlines()  
                for text in user_login_text:  
                    if self.username.lower() in text.lower():  
                        user_prompt = text  
                        user_prompt_found = True  
                        break  
                if user_prompt_found:  
                    break  
            if not user_prompt_found:  
                raise Exception(
                    "The user prompt was not found successfully. Please check for errors"
                    )  

            if user_prompt[0] == "[":
                escaped_user_prompt = "\\"
                escaped_sudo_prompt = "\\"
                escaped_user_prompt = (
                    escaped_user_prompt + user_prompt.split("~")[0] + r".*\]\$\s+"
                )     
                escaped_sudo_prompt = (
                escaped_sudo_prompt
                + "[root@]"
                + user_prompt.split("@")[1].split("~")[0]
                + r".*\]\#\s+"
            )
    
            else:  
                user_prompt_pattern = re.compile(
                    rf"(?P<user_prompt>{self.username}@\S+)\s+", re.I
                    )  
                hostname_pattern = re.compile(rf"{self.username}@(?P<hostname>\S+)\s+", re.I)
                if (
                    bool(re.search(user_prompt_pattern, user_prompt))
                    and self.windows_platform
                ):
                    escaped_user_prompt = re.compile(
                        re.search(user_prompt_pattern, user_prompt).group("user_prompt")
                        + ".*(>)?$"
                        + re.search(hostname_pattern, user_prompt).group("hostname")
                        + ".*(conhost.exe)?$"
                    )
                    escaped_sudo_prompt = (
                        + ".*(>)?$"
                        + re.search(user_prompt_pattern, user_prompt).group("user_prompt")
                        + ".*(conhost.ext)?$"    
                    )                   
    
                elif not bool(re.search(r"\s", user_prompt.strip())):  
                    escaped_user_prompt = user_prompt.split(":")[0] + ".*"  
                    escaped_sudo_prompt = (
                        "root@" + user_prompt.split('@')[1].split(":")[0] + ".*"
                    )  
                else:  
                    escaped_user_prompt = user_prompt.split()[0] + ".*"  
                    escaped_sudo_prompt = (
                        "root@" + user_prompt.split("@")[1].split()[0] + ".*" 
                    )
    
            logger.debug(f"user prompt of host: {self.host} is: {escaped_user_prompt}")  
            logger.debug(f"sudo prompt of host: {self.host} is: {escaped_sudo_prompt}")  
            return escaped_user_prompt, escaped_sudo_prompt  
    
        except Exception as err:  
            raise Exception(
                f"\nFailed on prompt: {user_prompt} with error: {err}")


