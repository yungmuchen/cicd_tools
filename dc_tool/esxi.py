###
### Power on all VM on ESXi servers
### Power off all VM on ESXi servers and shutdown the ESXi server
### Execution during power maintenance in the data center
###
from sshclient import sshclient
import paramiko
import re
import pdb
import time
import argparse
from multiprocessing import Pool

from random import randrange

import warnings
warnings.filterwarnings(action='ignore',module='.*paramiko.*')

from pprint import pprint, pformat



class ESXiCli():

    def __init__(self, config=None):
        self.tcfg = dict(
            ip_addr='192.168.1.1',
            username='root',
            password='lab4man1',
            port=22,
        )

        self.pause = 0.5
        self.retry = 200
        self.ssh=None
        if config:
            self.touch_tcfg(config)
            self.login_esxi()
        print(self.tcfg)

    def __del__(self):
        try:
            self.ssh.close()
            self.ssh = None
        except:
            pass

    def close(self):
        try:
            self.ssh.close()
            self.ssh = None
        except:
            pass

    def touch_tcfg(self, conf):
        self.tcfg.update(conf)

    def login_esxi(self):
        self.ssh = sshclient(self.tcfg)

    def get_all_vm(self):
        res = self.ssh.cmd("vim-cmd vmsvc/getallvms")
        print(res)
        return res

    def get_all_vm_id(self):
        res = self.ssh.cmd("vim-cmd vmsvc/getallvms")
        print(res)
        pattern = '\d+.*\w+.*\w+'
        gggg = re.findall(pattern, res)
        vm_id_list=[]
        for line in gggg:
            gg1 = str(line.split(' ')[0])
            vm_id_list.append(gg1)
        return vm_id_list

    def shutdown_vm_by_id(self, vm_id):
        res = self.ssh.cmd("vim-cmd vmsvc/power.getstate %s" % vm_id)
        if 'powered on' in res.lower():
            res = self.ssh.cmd("vim-cmd vmsvc/power.shutdown %s" % vm_id)
            print(res)
        return res

    def power_on_vm_by_id(self, vm_id):
        res = self.ssh.cmd("vim-cmd vmsvc/power.getstate %s" % vm_id)
        if 'powered off' in res.lower():
            res = self.ssh.cmd("vim-cmd vmsvc/power.on %s" % vm_id)
            print(res)
        return res

    def power_reset_vm_by_id(self, vm_id):
        res = self.ssh.cmd("vim-cmd vmsvc/power.reset %s" % vm_id)
        print(res)
        return res

    def power_reboot_vm_by_id(self, vm_id):
        res = self.ssh.cmd("vim-cmd vmsvc/power.reboot %s" % vm_id)
        print(res)
        return res

    def power_off_vm_by_id(self, vm_id):
        res = self.ssh.cmd("vim-cmd vmsvc/power.getstate %s" % vm_id)
        if 'powered on' in res.lower():
            res = self.ssh.cmd("vim-cmd vmsvc/power.off %s" % vm_id)
            print(res)
        return res

    def power_getstate_vm_by_id(self, vm_id):
        res = self.ssh.cmd("vim-cmd vmsvc/power.getstate %s" % vm_id)
        print(res)
        return res

    def shutdown_all_vm_on_esxi(self):
        vm_id_list = self.get_all_vm_id()
        for vm_id in vm_id_list:
            self.shutdown_vm_by_id(vm_id)
            print("esxi host %s, shutdown vm_id %s" % (self.tcfg['ip_addr'], vm_id) )

    def power_on_all_vm_on_esxi(self):
        vm_id_list = self.get_all_vm_id()
        for vm_id in vm_id_list:
            self.power_on_vm_by_id(vm_id)
            print("esxi host %s, power on vm_id %s" % (self.tcfg['ip_addr'], vm_id) )
            time.sleep(5)

    def power_reset_all_vm_on_esxi(self):
        vm_id_list = self.get_all_vm_id()
        for vm_id in vm_id_list:
            res = self.power_reset_vm_by_id(vm_id)
            print("esxi host %s, power reset vm_id %s" % (self.tcfg['ip_addr'], vm_id) )
            print(res)

    def power_reboot_all_vm_on_esxi(self):
        vm_id_list = self.get_all_vm_id()
        for vm_id in vm_id_list:
            res = self.power_reboot_vm_by_id(vm_id)
            print("esxi host %s, power reboot vm_id %s" % (self.tcfg['ip_addr'], vm_id) )
            print(res)

    def power_off_all_vm_on_esxi(self):
        vm_id_list = self.get_all_vm_id()
        for vm_id in vm_id_list:
            res = self.power_off_vm_by_id(vm_id)
            print("esxi host %s, power off vm_id %s" % ( self.tcfg['ip_addr'], vm_id) )
            print(res)

    def power_getstate_all_vm_on_esxi(self):
        vm_id_list = self.get_all_vm_id()
        for vm_id in vm_id_list:
            res = self.power_getstate_vm_by_id(vm_id)
            print(res)

    def esxi_host_power_off(self):
        res = self.ssh.cmd("poweroff")
        print("esxi server %s, power off" % self.tcfg['ip_addr'])

    def esxi_host_power_off_force(self):
        res = self.ssh.cmd("poweroff -f")
        print("esxi server %s, force power off " % self.tcfg['ip_addr'])


def test_esxi_connect_server(tcfg={}):
    try:
        myesxi = ESXiCli(config=tcfg)
        res = myesxi.get_all_vm()
#        print(res)
#        res = myesxi.get_all_vm_id()
#        print(res)
        myesxi.close()
    except:
        print("esxi host %s connect failed " % (tcfg['ip_addr']) )


def esxi_shutdown_all_vm_and_esxi_server(tcfg={}):
    myesxi = ESXiCli(config=tcfg)
    myesxi.shutdown_all_vm_on_esxi()
    time.sleep(30)
    myesxi.power_off_all_vm_on_esxi()
    time.sleep(30)
    myesxi.esxi_host_power_off()
    myesxi.close()

def esxi_shutdown_all_vm(tcfg={}):
    myesxi = ESXiCli(config=tcfg)
    myesxi.shutdown_all_vm_on_esxi()

def esxi_power_off_all_vm(tcfg={}):
    myesxi = ESXiCli(config=tcfg)
    myesxi.power_off_all_vm_on_esxi()
    myesxi.close()

def esxi_power_on_all_vm(tcfg={}):
    myesxi = ESXiCli(config=tcfg)
    myesxi.power_on_all_vm_on_esxi()
    myesxi.close()

def esxi_power_getstate_server(tcfg={}):
    myesxi = ESXiCli(config=tcfg)
    myesxi.power_getstate_all_vm_on_esxi()
    myesxi.close()

def esxi_poweroff_esxi_server(tcfg={}):
    myesxi = ESXiCli(config=tcfg)
    myesxi.esxi_host_power_off_force()
    myesxi.close()


def paraller_run_esxi_shutdown(host_list_dict={}):

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
            pool.apply_async( esxi_shutdown_all_vm_and_esxi_server, (tcfg, ) )

    pool.close()
    pool.join()


def paraller_run_esxi_power_on(host_list_dict={}):

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
            pool.apply_async( esxi_power_on_all_vm, (tcfg, ) )

    pool.close()
    pool.join()


def paraller_run_test_esxi_connection(host_list_dict={}):

    if not host_list_dict:
        print("empty host list configuration file")
        return

    _check_list = []
    if type(host_list_dict) != type(_check_list):
        print("The input host list configuration file is wrong")
        return

    conf = dict()

    pool = Pool(processes=10)
    for tcfg in host_list_dict:
        if type( tcfg ) != type( conf):
            print("The input host list configuration file is wrong 2")
        else:
            pool.apply_async( test_esxi_connect_server, (tcfg, ) )

    pool.close()
    pool.join()



def dev_run():

    tcfg = dict()
    tcfg['ip_addr'] = "192.168.1.1"
    tcfg['username'] = "root"
    tcfg['password'] = "!asdfqwer"
    tcfg['port'] = 22

    pdb.set_trace()

    test_esxi_connect_server(tcfg)
#    esxi_power_getstate_server(tcfg)
#    esxi_shutdown_all_vm(tcfg)
#    esxi_shutdown_all_vm_and_esxi_server(tcfg)
#    esxi_power_off_all_vm(tcfg)
#    esxi_power_on_all_vm(tcfg)




if __name__ == "__main__":

    ######################################
#    paramiko.util.log_to_file("debug_paramiko.log")

    parser = argparse.ArgumentParser()
    mutex_group = parser.add_mutually_exclusive_group(required=True)
    mutex_group.add_argument('-s',
                         help='Note: Users have toenable ssh login service on the ESXi server'
                              '1) on: power on all VMs in ESXi. '
                              '2) off: shutdown all VMs and shutdown ESXi server. '
                              '3) check: get all VMs status ')

    args = vars(parser.parse_args())
    vm_status = args["s"].lower()

    host_list_dict = [
#        { 'ip_addr' : 'YOUR_ESXI_SERVER_IP', 'username':'YOUR_ESXI_LOGIN_ACCOUNT', 'password':'YOUR_ESXI_LOGIN_PASSWORD', 'port': 22},   
        { 'ip_addr' : '192.168.1.1', 'username':'root', 'password':'!asdfqwer"', 'port': 22},   # node 1
        { 'ip_addr' : '192.168.1.2', 'username':'root', 'password':'!asdfqwer"', 'port': 22},   # node 2 ...
    ]

    if vm_status == 'off':
        paraller_run_esxi_shutdown(host_list_dict)
    elif vm_status == 'on':
        paraller_run_esxi_power_on(host_list_dict)
    elif vm_status == 'check':
        paraller_run_test_esxi_connection(host_list_dict)

    
