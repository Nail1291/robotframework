import sys
sys.path.append('D:/local_git/robotfrm/robotframework')

import logging
#from framework.libraries.common.Logger import Logger
from framework.libraries.common.SSHClient import SSHClient 


if __name__ == "__main__":
    # Example usage
    hostname = '10.0.0.60'
    port = 22
    username = 'ding'
    password = 'w21842'

    ssh_client = SSHClient(hostname, port, username, password)
    ssh_client.connect()

    commands = ['ls', 'pwd']
    for command in commands:
        ssh_client.run_command(command)

    ssh_client.close()