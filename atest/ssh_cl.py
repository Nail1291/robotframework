import sys
sys.path.append('D:/local_git/robotfrm/robotframework')

import logging
#from framework.libraries.common.Logger import Logger
from framework.libraries.common.PC_adb import SSHClient
import framework.libraries.common.PC_adb


class ssh_cl:

    def __init__(self):

        hostname = '10.0.0.90'
        port = 22
        username = 'ding'
        password = 'w21842'

        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.client = None
        self.ssh = None

        self.ssh_client = SSHClient(hostname, port, username, password)
        #self.ssh_client = framework.libraries.common.SSHClient.SSHClient(hostname, port, username, password)
        #self.ssh_client = SSHClient()
        self.ssh_client.connect()


    def ssh_and_run_command(self):
        commands = ['ls', 'pwd']
        for command in commands:
            self.ssh_client.run_command(command)

        self.ssh_client.close()