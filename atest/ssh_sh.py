import sys
sys.path.append('D:/local_git/robotfrm/robotframework')

import logging
#from framework.libraries.common.Logger import Logger
from framework.libraries.common.ssh_connection import SSHConnection 

#logger = logging.info("hello world")
#logger_inst = Logger()
#logger_inst.info("hello world!!")
#logger.info("hello")
#print(logger)
#logger_inst.info("Successfully SSH to {}".format("host"))


SSH_Connection = SSHConnection(host="10.0.0.60",username="ding",password="w21842",port="22")
SSH_Connection.sendCommand(command="ll")