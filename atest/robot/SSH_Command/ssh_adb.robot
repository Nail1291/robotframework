*** Settings ***
Documentation     This suite consists all test cases of E2E Tls
#@Library           framework.libraries.common.SSHClient
Library           atest.ssh_adb

*** Test Cases ***
SSH_TO_SERVER_TO_RUN_ADB
    [Documentation]    SSH to the server and run adb command
    SSH AND RUN ADB
    Log To Console      End of TEST CASE: SSH_TO_SERVER_TO_RUN_ADB !!