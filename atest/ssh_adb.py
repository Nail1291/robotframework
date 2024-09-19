import sys
sys.path.append('D:/local_git/robotfrm/robotframework')

import logging
#from framework.libraries.common.Logger import Logger
from framework.libraries.common.PC_adb import LaptopMTPManager
#import framework.libraries.common.PC_adb


class ssh_adb:

    def __init__(self):

        hostname = '10.0.0.60'
        port = 2222
        username = 'njding'
        password = 'w21842@r00T'

        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.client = None
        self.ssh = None

        self.ssh_client = LaptopMTPManager(hostname, port, username, password)
        #self.ssh_client = framework.libraries.common.SSHClient.SSHClient(hostname, port, username, password)
        #self.ssh_client = SSHClient()
        self.ssh_client.connect_rdp()


    def ssh_and_run_adb(self):
        command = "adb shell ip -br addr"
        self.ssh_client.run_adb_on_laptop(command)

        self.ssh_client.close_connections()