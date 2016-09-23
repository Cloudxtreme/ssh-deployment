import paramiko
from threading import Thread
from datetime import datetime

class SSHExec(Thread):
    def __init__(self, host, user, passwd, cmdlines, key=None, debug=False):
        Thread.__init__(self)
        self.host = host
        self.user = user
        self.passwd = passwd
        self.cmdlines = cmdlines
        self.keyfile = key
        self.debug = debug
        self.ssh = None

    def run(self):
        self.ssh = self.ssh_connect()
        if self.ssh is not None:
            self.ssh_run()
            self.ssh.close()

    def ssh_connect(self):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if self.keyfile is not None:
                key = paramiko.RSAKey.from_private_key_file(self.keyfile)
                ssh.connect(self.host, username=self.user, pkey=key)
                if self.debug:
                    print("---\tConnected to {}@{} using keyfile {}".format(self.host, self.user, key))
            else:
                ssh.connect(self.host, username=self.user, password=self.passwd)
                if self.debug:
                    print("---\tConnected to {}@{} using password".format(self.host, self.user))
            return ssh
        except Exception as e:
            if self.debug:
                print("Error: Could not establish a connection")
                print(e)

    def ssh_run(self):
        try:
            for cmd in self.cmdlines:
                timestamp = datetime.now().strftime('%m/%d/%Y %H:%M:%S.%f')
                stdin, stdout, stderr = self.ssh.exec_command(cmd + '\n', get_pty=True)
                retout = stdout.read().splitlines()
                reterr = stderr.read().splitlines()

                #if self.debug:
                for line in retout:
                    print("[{}] {}@{}\t>>> {}".format(timestamp, self.user, self.host, line))

                for line in reterr:
                    print("!!! [{}] {}@{} >>> {}".format(timestamp, self.user, self.host, line))

                if "sudo" in cmd and "password" in retout:
                    stdin.write(self.passwd + '\n')
                    stdin.flush()
                stdin.close()
        except Exception as e:
            print("Encountered error running command:")
            print(e)
