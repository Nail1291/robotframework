*** Settings ***
Documentation     This suite consists all test cases of E2E Stress test for Viavi Tls
#@Library           framework.libraries.common.SSHClient
Library           atest.ssh_cl

*** Test Cases ***
SSH_TO_SERVER_TO_RUN_COMMANDS
    [Documentation]    SSH to the server and run some commands
    SSH AND RUN Command
