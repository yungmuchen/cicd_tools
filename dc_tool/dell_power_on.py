###
### porting from GetSetPowerStateREDFISH.py
###

import re
import pdb
import time, os
import argparse
import json
import requests
import sys
from multiprocessing import Pool

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

from pprint import pprint, pformat


def test_idrac_creds(tcfg={}):

    response = requests.get('https://%s/redfish/v1/Managers/iDRAC.Embedded.1' % (tcfg['idrac_ip']), auth=( tcfg['idrac_username'],  tcfg['idrac_password'] ), verify=False)
    if response.status_code == 401:
        print("\n- WARNING, status code 401 detected, check iDRAC username / password credentials")
        sys.exit(1)
    else:
        pass


def get_current_power_state(tcfg={}):
    if not tcfg:  return

    response = requests.get('https://%s/redfish/v1/Systems/System.Embedded.1/' % (tcfg['idrac_ip']), verify=False,
                            auth=( tcfg['idrac_username'], tcfg['idrac_password']) )
    data = response.json()
    print("\n- INFO, %s Current server power state is: %s\n" % ( tcfg['idrac_ip'], data['PowerState'] ))
'''
    print("- Supported values for server power control are:\n")
    for i in data['Actions']['#ComputerSystem.Reset']['ResetType@Redfish.AllowableValues']:
        print(i)
'''
'''
On
ForceOff
ForceRestart
GracefulShutdown
PushPowerButton
Nmi
'''
def set_power_state_On(tcfg={}):
    if not tcfg:  return

    requests.get('https://%s/redfish/v1/Systems/System.Embedded.1/' % ( tcfg['idrac_ip'] ), verify=False,
                 auth=(tcfg['idrac_username'], tcfg['idrac_password']))
    print("\n- INFO, %s setting new server power state to: On" % ( tcfg['idrac_ip'] ) )

    url = 'https://%s/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset' % ( tcfg['idrac_ip'] )
    payload = {'ResetType': "On"}
    headers = {'content-type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False,
                             auth=( tcfg['idrac_username'], tcfg['idrac_password'] ) )

    status_code = response.status_code
    if status_code == 204:
        print("\n- PASS, status code %s returned, %s server power state successfully set to On" % (
            status_code , tcfg['idrac_ip'] ))
    else:
        print("\n- FAIL, %s Command failed, status code %s returned\n" % ( tcfg['idrac_ip'], status_code ) )
        print(response.json())
        sys.exit(1)


def set_power_state_GracefulShutdown(tcfg={}):
    if not tcfg:  return

    requests.get('https://%s/redfish/v1/Systems/System.Embedded.1/' % ( tcfg['idrac_ip'] ), verify=False,
                 auth=( tcfg['idrac_username'], tcfg['idrac_password'] ) )
    print("\n- INFO, %s setting new server power state to: GracefulShutdown" % ( tcfg['idrac_ip'] ) )

    url = 'https://%s/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset' % ( tcfg['idrac_ip'] )
    payload = {'ResetType': "GracefulShutdown"}
    headers = {'content-type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False,
                             auth=( tcfg['idrac_username'], tcfg['idrac_password'] ) )

    status_code = response.status_code
    if status_code == 204:
        print("\n- PASS, status code %s returned, %s server power state successfully set to GracefulShutdown" % (
            status_code, tcfg['idrac_ip'] ) )
    else:
        print("\n- FAIL, %s Command failed, status code %s returned\n" % ( tcfg['idrac_ip'], status_code ) )
        print(response.json())
        sys.exit(1)


def set_power_state_ForceOff(tcfg={}):
    if not tcfg:  return

    requests.get('https://%s/redfish/v1/Systems/System.Embedded.1/' % ( tcfg['idrac_ip'] ) , verify=False,
                 auth=(tcfg['idrac_username'], tcfg['idrac_password']))
    print("\n- INFO, %s setting new server power state to: ForceOff" % ( tcfg['idrac_ip'] ) )

    url = 'https://%s/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset' % ( tcfg['idrac_ip'] )
    payload = {'ResetType': "ForceOff"}
    headers = {'content-type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False,
                             auth=( tcfg['idrac_username'], tcfg['idrac_password'] ) )

    status_code = response.status_code
    if status_code == 204:
        print("\n- PASS, status code %s returned, %s server power state successfully set to ForceOff" % (
            status_code, tcfg['idrac_ip'] ))
    else:
        print("\n- FAIL, %s Command failed, status code %s returned\n" % ( tcfg['idrac_ip'], status_code ) )
        print(response.json())
        sys.exit(1)


def set_power_state_ForceRestart(tcfg={}):
    if not tcfg:  return

    requests.get('https://%s/redfish/v1/Systems/System.Embedded.1/' % ( tcfg['idrac_ip'] ), verify=False,
                 auth=( tcfg['idrac_username'], tcfg['idrac_password'] ) )
    print("\n- INFO, %s setting new server power state to: ForceRestart" % ( tcfg['idrac_ip'] ) )

    url = 'https://%s/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset' % ( tcfg['idrac_ip'] )
    payload = {'ResetType': "ForceRestart"}
    headers = {'content-type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False,
                             auth=( tcfg['idrac_username'], tcfg['idrac_password'] ))

    status_code = response.status_code
    if status_code == 204:
        print("\n- PASS, status code %s returned, %s server power state successfully set to ForceRestart" % (
            status_code, tcfg['idrac_ip']))
    else:
        print("\n- FAIL, %s Command failed, status code %s returned\n" % ( tcfg['idrac_ip'], status_code ))
        print(response.json())
        sys.exit(1)


def run_dell_set_power_on(host_list_dict={}):

    if not host_list_dict:
        print("empty host list configuration file")
        return

    _check_list = []
    if type(host_list_dict) != type(_check_list):
        print("The input host list configuration file is wrong")
        return

    conf = dict()

    for tcfg in host_list_dict:
        if type( tcfg ) != type( conf):
            print("The input host list configuration file is wrong 2")
        else:
            set_power_state_On(tcfg)
            time.sleep(30)


def run_dell_get_power_status(host_list_dict={}):

    if not host_list_dict:
        print("empty host list configuration file")
        return

    _check_list = []
    if type(host_list_dict) != type(_check_list):
        print("The input host list configuration file is wrong")
        return

    conf = dict()

    pool = Pool(processes=20)
    for tcfg in host_list_dict:
        if type( tcfg ) != type( conf):
            print("The input host list configuration file is wrong 2")
        else:
            pool.apply_async( get_current_power_state, (tcfg, ) )
#            pool.apply_async( test_idrac_creds, (tcfg, ) )

    pool.close()
    pool.join()


def dev_run():

    tcfg = dict()
    tcfg['idrac_ip'] = "192.168.1.1"
    tcfg['idrac_username'] = "root"
    tcfg['idrac_password'] = "calvin"
    tcfg['port'] = 22

    pdb.set_trace()

#    get_current_power_state(tcfg)
#    set_power_state_On(tcfg)
#    set_power_state_GracefulShutdown(tcfg)


if __name__ == "__main__":

    ######################################

#    paramiko.util.log_to_file("debug_paramiko.log")

    parser = argparse.ArgumentParser()
    mutex_group = parser.add_mutually_exclusive_group(required=True)
    mutex_group.add_argument('-s',
                         help='1) on: power on dell server via idrac. '
                              '2) check: get dell server power status. ')

    args = vars(parser.parse_args())
    vm_status = args["s"].lower()


    host_list_dict = [
#       Dell Server Idrac default user "root and password "calvin".
#        { 'idrac_ip' : 'YOUR_DELL_IDRAC_IP', 'idrac_username':'root', 'idrac_password':'calvin', 'port': 22},
        { 'idrac_ip' : '192.168.1.1', 'idrac_username':'root', 'idrac_password':'calvin', 'port': 22},
    ]

    if vm_status == 'on':
        run_dell_set_power_on(host_list_dict)
    elif vm_status == 'check':
        run_dell_get_power_status(host_list_dict)


