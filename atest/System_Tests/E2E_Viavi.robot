*** Settings ***
Documentation     This suite consists all test cases of E2E Stress test for Viavi Tls
Library           framework.keywords.PcapCapture
Library           framework.keywords.TransacAnalysis
Library           framework.keywords.FcapsKeywords
Library           framework.keywords.TmaApi.TmaApi
Library           framework.keywords.SneApi.SneApi
Library           framework.keywords.LogKeywords.LogKeywords
Library           DateTime
Library           Collections
Library           framework.libraries.common.Listener_Agent

Suite Setup       Run Keywords
...     Modify Config File Xpath    CUCP1    DU1    yaml_template_/resources/config/E2E/config_128ue_ueInactivityTimer_min3.yaml    AND
...     Run Keyword And Continue On Failure    Restart Components    AND
...     Run Keyword And Continue On Failure    Load TM4 Campaign File    ${TIL}    ${TMA_CAMPAIGN_NAME}    AND
...     Run Keyword If    '${SKIP_TEST}' == 'True'    Skip    AND
...     Run Keyword And Ignore Error    Configure Pn Counter File    component_id=CUCP1    jobID=0    granularityPeriod=3600    fileReportingPeriods=4    AND
...     Run Keyword And Ignore Error    Configure Pn Counter File    component_id=CUUP1    jobID=0    granularityPeriod=3600    fileReportingPeriods=4

Suite Teardown    Run Keywords
...     Close TMA    AND
...     Log To Console    ${\n}************Starting Test Suite Execution*************${\n}

Test Setup        Run Keywords
...     GNB Health Check    AND
...     Truncate Stats Log    CUCP1    DU    AND
...     Get Current Alarm Time    AND
...     Start Alarm Capture    CUCP    CUUP    DU    AND
...     Get Data Performance From Component Server    duration=90000    interval=60

Test Teardown     Run Keywords
...     Truncate Stats Log    CUCP1    AND
...     Stop Get Data Performance From Component Server    AND
...     Generate Alarm Time Report    AND
...     Generate RAW Test Report    AND
...     Publish RAW Pm Report    CUCP    DU    AND
...     Run If Test Passed    Truncate Stats Log

*** Keywords ***
Get TM500 Version
    [Documentation]    Get Current Version
    ${CURRENT_TMA_VERSION}    C:/Users/aromang/Documents/VIAVI/TM500/5G NR/Test Mobile Application/    N/A    \d+\.\d+\.\d+\.\d+

    Set Suite Variable    ${TMA_VERSION}    ${CURRENT_TMA_VERSION}

Truncate Stats Log
    [Documentation]    Truncate logs in CUCP & DU component before starting next test case
    Execute Command In Folder    CUCP    bin_path=/opt/gnb/du_marvell/bin    file_name=stats.txt
    Execute Command In Folder    CUUP    bin_path=/opt/gnb/cuup/bin    file_name=stats.txt

Get PMCounter Values And Verify
    [Arguments]    ${pm_names}    ${nf_identifier}    ${value}    ${lower_limit}    ${upper_limit}
    ${dict}=    Get Counter Values From Csv File    pn_names=${pn_names}    nf_identifiers=${nf_identifiers}    values=${value}
    FOR    ${key}    IN     @{dict}
        ${value}=    Get From Dictionary    ${dict}     ${key}
        Should Be True    ${lower_limit} <= ${value} <= ${upper_limit}    msg=${key} validation failed

GNB Health Check
    [Documentation]    Check Running Components
    Should Be True    ${health_check}

*** Variables ***
${CONFIGFILE}=                      ./resources/testlines/${TIL}.yaml
${CONFIGNAME}=                      None
${TEST_LOG_DIRECTORY}=              /data/DFW_logs/
${COPY_COMMAND}=                    False
${PCAP_COMPONENTS}=                 CUCP1
${UPLOAD_PATH_TO_FTP_SERVER}=       /e2e-logs/data
${LOGMODE}=                         FTP


*** Test Cases ***
STRESS_MAX_UE_FDX_UDP_SLOW_MOBILITY_BACK_FORTH
    [Documentation]    Verify if gNB remains stable when a maximum number of UEs (attach stagger time 0s) with FDX UDP traffic are moving slowly (walking velocity) simultaneously from center to edge and backwards
    [Tags]    STRESS    MAX_UE    FDX    CUP    SLOW    MOBILITY    CELL
    # Campaign file path
    ${campaign_file_path}=    Set Variable    C:/Users/aromang/Documents/VIAVI/TM500/5G NR/Test Mobile Application/${TMA_VERSION}/MyCampaigns/${STRESS_CAMPAIGN}

    # --------------------- Validate PM counters in PM.xml files ---------------------
    ${component_lists}=    Create List    CUCP1

    Log    Waiting for old PM file to be created & integer 5-min instant    console=True
    ${first_file}=    Check For New PM File Generated    ${component_lists}    0

    # Get current system time
    ${start_time}=    Get Current Date

    # Run individual test cases in a campaign
    ${campaign_name}=    ${campaign_status}=    Start Campaign On Time    ${campaign_file_path}    test_case="STRESS_MAX_UE_FDX_UDP_SLOW_MOBILITY_BACK_FORTH"

    # Waiting for the traffic starting
    Sleep 1m

    Truncate State Log
    Log    Waiting for the 1st PM file to be created & integer 5-min instant    console=True
    ${first_file}=    Check For New PM File Generated    ${component_lists}    0
    Log    Waiting for the 2nd PM file to be created & integer 5-min instant    console=True
    ${second_file}=    Check For New PM File Generated    ${component_lists}    0

    # PM Counters elapsed time
    ${end_time}=    Get Current Date
    ${elapsed_time}=    Subtract Date From Date    ${end_time}    ${start_time}
    Log    The first file name is: ${first_file}, it took: ${elapsed_time}    console=True
    Log    The second file name is: ${second_file}, it took: ${elapsed_time}    console=True

    # --------------------- PM counter validation ---------------------
    # Counter value for UE attach
    Fetch And Validate Pm Counter    component_id=CUCP1    start_file=${first_file}    end_file=${second_file}    counter_name=ConnReconfigAtt    object_dn=${counter_dn}    expected_values=128    validation_type=GREATER_THAN_EQUAL
    Fetch And Validate Pm Counter    component_id=CUCP1    start_file=${first_file}    end_file=${second_file}    counter_name=ConnReconfigSucc    object_dn=${counter_dn}    expected_values=128    validation_type=GREATER_THAN_EQUAL
    Fetch And Validate Pm Counter    component_id=CUCP1    start_file=${first_file}    end_file=${second_file}    counter_name=ConnReconfigSucc    object_dn=${counter_dn2}    expected_values=128    validation_type=GREATER_THAN_EQUAL

    # Counter value for RRC requested
    Fetch And Validate Pm Counter    component_id=CUCP1    start_file=${first_file}    end_file=${second_file}    counter_name=ConnEstabAtt    object_dn=${counter_dn3}    expected_values=128    validation_type=GREATER_THAN_EQUAL
    Fetch And Validate Pm Counter    component_id=CUCP1    start_file=${first_file}    end_file=${second_file}    counter_name=ConnEstabSucc    object_dn=${counter_dn3}    expected_values=128    validation_type=GREATER_THAN_EQUAL
    Fetch And Validate Pm Counter    component_id=CUCP1    start_file=${first_file}    end_file=${second_file}    counter_name=ConnEstabSucc    object_dn=${counter_dn4}    expected_values=128    validation_type=GREATER_THAN_EQUAL

    # Counter value for max number of active UEs in RRC connected mode
    Fetch And Validate Pm Counter    component_id=CUCP1    start_file=${first_file}    end_file=${second_file}    counter_name=ConnMax    object_dn=${counter_dn3}    expected_values=128    validation_type=GREATER_THAN_EQUAL
    Fetch And Validate Pm Counter    component_id=CUCP1    start_file=${first_file}    end_file=${second_file}    counter_name=ConnMax    object_dn=${counter_dn3}    expected_values=128    validation_type=GREATER_THAN_EQUAL

    # Counter value for max number of active UEs in RRC connected mode
    Fetch And Validate Pm Counter    component_id=CUCP1    start_file=${first_file}    end_file=${second_file}    counter_name=ConnMax    object_dn=${counter_dn3}    expected_values=128    validation_type=GREATER_THAN_EQUAL
    Fetch And Validate Pm Counter    component_id=CUCP1    start_file=${first_file}    end_file=${second_file}    counter_name=ConnMax    object_dn=${counter_dn3}    expected_values=128    validation_type=GREATER_THAN_EQUAL

    # --------------------- Get max theoretical throughput from Tpt statistics ---------------------
    Fetch And Validate DU Stat Logs    component_ids=["CUCP1"]    para_name=block-BETW UPPER RX STATISTICS    sorted_by=CELL-ID    width_value=2    return_key=SCH-DL    expected_values=1140    validation_check=GREATER_THAN_EQUAL    slice_start=2    slice_stop=2
    Fetch And Validate DU Stat Logs    component_ids=["CUUP1"]    para_name=block-BETW UPPER RX STATISTICS    sorted_by=CELL-ID    width_value=2    return_key=SCH-DL    expected_values=1140    validation_check=GREATER_THAN_EQUAL    slice_start=2    slice_stop=2
    Fetch And Validate DU Stat Logs    component_ids=["CUCP1"]    para_name=block-BETW UPPER RX STATISTICS    sorted_by=SCH-DL    width_value=2    return_key=TPT_Mbps    expected_values=1.0    validation_check=GREATER_THAN_EQUAL    slice_start=1024    slice_stop=512    stat_file_num=2
    Fetch And Validate DU Stat Logs    component_ids=["CUUP1"]    para_name=block-BETW UPPER RX STATISTICS    sorted_by=SCH-DL    width_value=2    return_key=TPT_Mbps    expected_values=1.0    validation_check=GREATER_THAN_EQUAL    slice_start=1024    slice_stop=512    stat_file_num=2

    [Teardown]    Run Keyword And Ignore Error    Stop Campaign On Time

