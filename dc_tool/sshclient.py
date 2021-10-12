#from cli import LinuxCli
import paramiko
import re
import pdb
import time

#import subprocess
#from Queue import Queue
#from threading import Thread
from multiprocessing import Pool

from random import randrange

import warnings
warnings.filterwarnings(action='ignore',module='.*paramiko.*')

from pprint import pprint as pp

PARAMIKO_VERSIONS_OLD = ['1.7.3', '1.7.4', '1.7.5']

PS_WSGC ="""(ruckus)(|\(([^\)]+)\))(#|>)"""
PS_SHEL1="""(bash)-([^#]+)#"""
PS_SHEL1b="""(bash)-([^\$]+)\$"""
PS_SHEL2="""\[([^@]+)@([^\s]+)\s+([^\]]+)\]\$"""
ALL_PROMPTS = "("+PS_WSGC+")|("+PS_SHEL1+")|("+PS_SHEL2+")"

WSGC_PROMPTS = re.compile(r'\S+(|\(([^\)]+)\))(#|>)', re.I | re.M)
WSGC_SHELL_PROMPTS = re.compile(PS_SHEL1+"|"+PS_SHEL1b+"|"+PS_SHEL2, re.I | re.M)
WSGC_ALL_PROMPTS = re.compile(r'\S+(|\(([^\)]+)\))(#|>)|bash-([^#]+)#', re.I | re.M)
ESXI_SHELL_PROMPTS_1 = re.compile(r'(#|>)', re.I | re.M)

class sshclient:
    def __init__(self, config=None):
        self.sshagent = None
        self.sshchannel = None
        # 0 for user mode; 1 for exec mode; 2 for shell mode
#        self.mode = 0
        self.tcfg = dict(
            ip_addr='10.16.22.10',
            username='root',
            password='lab4man1',
            port=22,
            init=True,
#            privileged_mode=True,
        )
        self.pause = 0.5
        self.retry = 200

        if config:
            self.touch_tcfg(config)
            if self.tcfg['init']:
                self.open()


    def __del__(self):
        try:
            self.sshchannel.close()
            self.sshchannel = None
            self.sshagent.close()
            self.sshagent = None
        except:
            pass


    def touch_tcfg(self, conf):
        self.tcfg.update(conf)

    def __del__(self):
        try:
            self.sshchannel.close()
            self.sshchannel = None
            self.sshagent.close()
            self.sshagent = None
        except:
            pass


    def touch_tcfg(self, conf):
        self.tcfg.update(conf)



    def _try_times(self, times = 3, interval = 2):
        '''
        Simplify the re-trying actions in definite times
        '''
        for t in range(1, times + 1):
            yield t
            time.sleep(interval)


    def _wait_for(self, chan, text, recv_bufsize=1024, retry=200, pause=0.02):
        '''
        quick and dirty excpect substitute for paramiko channel;
        Raise exception if text not found.
        ssh=dict(pause=0.02, retry=200, recv_bufsize=1024, port=22),
        '''
        for x in range(self.retry):
            if self.sshchannel.recv_ready():
                time.sleep(3)
                if text in self.sshchannel.recv(recv_bufsize):
                    return # success
            time.sleep(self.pause) # 100*.02 = approx 2 seconds total
        raise Exception("SSH expect")


    def open(self, retries=3):
        ver = paramiko.__version__
        for i in self._try_times(retries, 5):
            try:
                if not ver[:5] in PARAMIKO_VERSIONS_OLD:
                    self._init_ssh_connect()
                else:
                    self._init_ssh_connect_old()
                self.sshchannel.settimeout(0.5)
                self._read()
#                self._wait_for(self.sshchannel, '>')
#                self.mode = 0
                return
            except:
                if i == retries:
                    print("Unable to login ssh via [%s:%s]" % (self.tcfg['ip_addr'], self.tcfg['port']) )
                    raise

    def close(self):
        try:
            self.sshchannel.close()
            self.sshchannel = None
            self.sshagent.close()
            self.sshagent = None
        except:
            pass


    def _init_ssh_connect(self):
        '''
        This enhancement requires version 1.7.6 or later of paramiko or
        paramiko-on-pypi packages:
         - http://pypi.python.org/pypi/paramiko/1.7.6
         - http://pypi.python.org/pypi/paramiko-on-pypi/1.7.6
        '''
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.client.connect(self.tcfg['ip_addr'], self.tcfg['port'], self.tcfg['username'], self.tcfg['password'])

        except paramiko.BadHostKeyException:
            os.system('ssh-keygen -R ' + ' ' + self.tcfg['ip_addr'])
            self.client.connect(self.tcfg['ip_addr'], self.tcfg['port'], self.tcfg['username'], self.tcfg['password'])

        self.sshchannel = self.client.invoke_shell()
        self.sshagent = self.client.get_transport()


    def _init_ssh_connect_old(self):
        self.sshagent = paramiko.Transport((self.tcfg['ip_addr'], self.tcfg['port']))
        self.sshagent.connect(username = self.tcfg['username'], password = self.tcfg['password'], hostkey = None)
        self.sshchannel = self.sshagent.open_session()
        self.sshchannel.get_pty()
        self.sshchannel.invoke_shell()


    def _read(self, recv_bufsize=1024, timeout = 0, prompt = "",user_input="       "):
        '''
        quick and dirty expect substitute for paramiko channel;
        Raise exception if text not found.
        ssh=dict(pause=0.02, retry=200, recv_bufsize=1024, port=22),
        '''
        res=""
        self.prompt = None
        prompt_list = prompt if type(prompt) is list else [prompt]
        for x in range(self.retry):
            if self.sshchannel.recv_ready() != True:
                time.sleep(self.pause) # 100*.02 = approx 2 seconds total
                continue

            res += self.sshchannel.recv(recv_bufsize)
            moreobj = re.search("--More--", res)
            if moreobj:
                self._send(user_input)
            for prompt in prompt_list:
                mobj = re.search(prompt, res)
                if mobj != None:
                    self.prompt = res[mobj.start():mobj.end()]
                    return res[:mobj.start()] # success
                if self.sshchannel.closed:
                    raise Exception('SSH channel closed')

        raise Exception("SSH expect")


    def _send(self, cmd):
        if self.sshchannel.closed:
            self.open()
        for x in range(self.retry):
            if self.sshchannel.send_ready():
                res = self.sshchannel.send("%s\n" % cmd)
                return res # success; if res > 0
            time.sleep(self.pause) # 100*.02 = approx 2 seconds total
        raise Exception("SSH expect")


    def cmd(self, cmd, return_as_list=False, prompt=""):
        '''
        '''

        self._send(cmd)
        time.sleep(1)
        cur_prompt = ""
        if prompt != "":
            if type(prompt) is str and len(prompt) > 0:
                cur_prompt = [re.compile(prompt, re.I|re.M)]
            elif type(prompt) is list:
                cur_prompt = prompt
            else:
                cur_prompt = [prompt]
        else:
            cur_prompt = [ESXI_SHELL_PROMPTS_1, ALL_PROMPTS]

        res = self._read(prompt = cur_prompt)

        if return_as_list:
            # split at newlines
            rl = res.split("\n")
            # remove any trailing \r
            rl = [x.rstrip('\r') for x in rl]
            # filter empty lines and prompt
            rl = [x for x in rl if x and not x.endswith('#')]
            return rl[1:] # remove cmd_text from output
        else:
            return res


def test_esxi_cli(cfg={}):
    fcfg = dict(ip_addr='10.206.53.81',
                username='root',
                password='lab4man1',
                port=22)

    ssh = sshclient()
    ssh.touch_tcfg(fcfg)
    ssh.open()
    res = ssh.cmd("vim-cmd vmsvc/getallvms", False, "#")
    print(res)

    pattern = '\d+.*\w+.*\w+'
    gggg = re.findall(pattern, res)
    vm_id_list = []
    for line in gggg:
        gg1 = str(line.split(' ')[0])
        vm_id_list.append(gg1)
    
    print(vm_id_list)
    

def test_linux_cli(cfg={}):
    fcfg = dict(ip_addr='10.206.53.82',
                username='root',
                password='lab4man1',
                port=22)

    fcfg.update(cfg)
    
    
    ssh = sshclient()
    ssh.touch_tcfg(fcfg)
    ssh.open()
    res = ssh.cmd("virsh list --all", False)
    print(res)

    pattern = '\d+.*\w+.*\w+'
    gggg = re.findall(pattern, res)
    vm_id_list = []
    for line in gggg:
        gg1 = str(line.split(' ')[0])
        vm_id_list.append(gg1)
    
    print(vm_id_list)
    



if __name__ == "__main__":

    ######################################

    import pdb
    pdb.set_trace()
    test_esxi_cli()