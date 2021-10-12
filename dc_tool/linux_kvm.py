###
### Power on all kvm server and shutdown linux host.
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


class LinuxCli():

    def __init__(self, config=None):
        self.tcfg = dict(
            ip_addr='192.168.1.1',
            username='root',
            password='!asdfqwer',
            port=22,
        )
        
        self.pause = 0.5
        self.retry = 200 
        self.ssh=None
        if config:
            self.touch_tcfg(config)
            self.login_linux()
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

    def login_linux(self):
        self.ssh = sshclient(self.tcfg)
        
    def get_all_kvm(self):
        res = self.ssh.cmd("virsh list --all")
        print(res)
        return res

    def get_all_kvm_id(self):
        res = self.ssh.cmd("virsh list --all")
        print(res)
        pattern = '\d+.*\w+.*\w+'
        gggg = re.findall(pattern, res)
        vm_id_list=[]
        for line in gggg:
            if 'shut off' in line.lower():
                pass
            else:
                gg1 = str(line.split(' ')[0])
                vm_id_list.append(gg1)
        return vm_id_list

    def get_all_kvm_name(self):
        res = self.ssh.cmd("virsh list --all", return_as_list=True)
        vm_id_list=[]
        for line in res:
            if 'shut off' in line.lower():
                gg1 = line.split('shut off')[0].strip(' ').split(' ')[-1]
                vm_id_list.append(gg1)
        return vm_id_list

    def shutdown_kvm_by_id(self, vm_id):
        res = self.ssh.cmd("virsh shutdown %s" % vm_id )
        return res        

    def start_kvm_by_name(self, vm_name):
        res = self.ssh.cmd("virsh start %s" % vm_name )
        return res        

    def shutdown_all_kvm_by_id(self):
        vm_id_list = self.get_all_kvm_id()
        for vm_id in vm_id_list:
           res = self.shutdown_kvm_by_id(vm_id)
           print("linux kvm host %s, shutdown VM instance: vm_id %s" % (self.tcfg['ip_addr'], vm_id))
           print(res)

    def start_all_kvm_by_name(self):
        vm_name_list = self.get_all_kvm_name()
        for vm_name in vm_name_list:
           res = self.start_kvm_by_name(vm_name)
           print("linux kvm host %s, Power On VM instance: %s" % (self.tcfg['ip_addr'], vm_name))
           print(res)

    def linux_host_force_reboot(self):
        res = self.ssh.cmd("sync;sync;sync;sync;sync;reboot -f")
        print("linux server %s, force reboot "% self.tcfg['ip_addr'])

    def linux_host_shutdown(self):
        res = self.ssh.cmd("sync;sync;sync;sync;sync;shutdown -h now")
        print("linux server %s, shutdown "% self.tcfg['ip_addr'])


def linux_shutdown_all_kvm(tcfg={}):
    try:
        mylinux = LinuxCli(config=tcfg)
        res = mylinux.shutdown_all_kvm_by_id()
        if res:    print(res)
        mylinux.close()
    except:
        print("linux host %s connect failed " % (tcfg['ip_addr']) )


def linux_shutdown_all_kvm_and_host_power_off(tcfg={}):
    try:
        mylinux = LinuxCli(config=tcfg)
        res = mylinux.shutdown_all_kvm_by_id()        
        if res:    print(res)
        res = mylinux.linux_host_shutdown()
        if res:    print(res)
        mylinux.close()
    except:
        print("linux host %s connect failed " % (tcfg['ip_addr']) )


def linux_shutdown_all_kvm_and_host_reboot(tcfg={}):
    try:
        mylinux = LinuxCli(config=tcfg)
        res = mylinux.shutdown_all_kvm_by_id()        
        if res:    print(res)
        res = mylinux.linux_host_force_reboot()
        if res:    print(res)
    except:
        print("linux host %s connect failed " % (tcfg['ip_addr']) )



def linux_host_power_off(tcfg={}):
    try:
        mylinux = LinuxCli(config=tcfg)
        res = mylinux.linux_host_force_reboot()
        res = mylinux.linux_host_shutdown()
        if res:    print(res)
        mylinux.close()
    except:
        print("linux host %s connect failed " % (tcfg['ip_addr']) )


def linux_start_all_kvm(tcfg={}):
    try:
        mylinux = LinuxCli(config=tcfg)
        res = mylinux.start_all_kvm_by_name()
        if res:    print(res)
        mylinux.close()
    except:
        print("linux host %s connect failed " % (tcfg['ip_addr']) )


def test_linux_connect_server(tcfg={}):
    try:
        mylinux = LinuxCli(config=tcfg)
        res = mylinux.get_all_kvm_id()
        if res:    print(res)
        mylinux.close()
    except:
        print("linux host %s connect failed " % (tcfg['ip_addr']) )



def run_kvm_list_vm(host_list_dict={}):

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
            pool.apply_async( test_linux_connect_server, (tcfg, ) )

    pool.close()
    pool.join()


def run_kvm_power_off(host_list_dict={}):

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
            pool.apply_async( linux_shutdown_all_kvm_and_host_power_off, (tcfg, ) )

    pool.close()
    pool.join()




def dev_run():

    tcfg = dict()
    tcfg['ip_addr'] = "192.168.53.82"
    tcfg['username'] = "root"
    tcfg['password'] = "!asdfqwer"
    tcfg['port'] = 22

    pdb.set_trace()

    test_linux_connect_server(tcfg)    
#    linux_shutdown_all_kvm(tcfg)
#    linux_start_all_kvm(tcfg)
#    linux_shutdown_all_kvm_and_host_power_off(tcfg)
#    linux_host_power_off(tcfg)



if __name__ == "__main__":

    ######################################
#    paramiko.util.log_to_file("debug_paramiko.log")

    parser = argparse.ArgumentParser()
    mutex_group = parser.add_mutually_exclusive_group(required=True)
    mutex_group.add_argument('-s',
                         help='Users need to enable ssh root login on the KVM server. '
                              '1) off: power on kvm VM and shutdown Linux server. '
                              '2) check: get kvm VM list. ')

    args = vars(parser.parse_args())
    vm_status = args["s"].lower()
    
    host_list_dict = [
#        { 'ip_addr' : 'YOUR_KVM_LINUX_SERVER_IP', 'username':'root', 'password':'ROOT_PASSWORD', 'port': 22},
        { 'ip_addr' : '192.168.53.84', 'username':'root', 'password':'!asdfqwer', 'port': 22},   # node 1
        { 'ip_addr' : '192.168.53.86', 'username':'root', 'password':'!asdfqwer', 'port': 22},   # node 2
    ]

    if vm_status == 'off':      
        run_kvm_power_off(host_list_dict)
    elif vm_status == 'check':
        run_kvm_list_vm(host_list_dict)
    
    
