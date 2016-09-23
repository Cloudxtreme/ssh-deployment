import argparse

from sshexec import SSHExec

DEBUG = False

def main():
    global DEBUG
    parser = argparse.ArgumentParser(description="")
    ## Targets
    parser.add_argument("-t", "--targets", help="Pass in targets on the commandline in the format:... -t 'X.X.X.X, X.X.X.X, X.X.X.X'")
    parser.add_argument("-f", "--targetfile", help="Specify a file to read targets from in the format: X.X.X.X (One per line)")
    ## Commands
    parser.add_argument("-c", "--commands", help="Specify a command to run on the target machines")
    parser.add_argument("-s", "--script", help="Specify a file to read a list of commands from")
    ## Authentication
    parser.add_argument("-k", "--key", help="Specify a private key file to connect with")
    parser.add_argument("-p", "--passwords", help="Specify passwords on the commandline in the format:...-p 'password1,password2'")
    parser.add_argument("-q", "--passwordfile", help="Specify passwords in a file (One per line)'")
    ## Users
    parser.add_argument("-u", "--users", help="Specify users on the commandline in the format:...-u 'user1,user2'")
    parser.add_argument("-x", "--userfile", help="Specify users in a file (One per line)")
    ## Debug
    parser.add_argument("-v", "--debug", action='store_true', help="Enable verbose debugging output")
    args = parser.parse_args()

    target_hosts = []
    target_passes = []
    target_users = []
    target_keyfile = None
    commands = []

    ## Check for debugging
    if args.debug:
        DEBUG = True
    ## Load Targets
    if args.targets:
        target_hosts = args.targets.strip('\n').strip().split(',')
    elif args.targetfile:
        with open(args.targetfile, 'r') as open_file:
            for line in open_file.readlines():
                if not line.strip().startswith('#'):
                    host = line.replace('\n', '')
                    target_hosts.append(host)
                    debug("Adding host: "+str(host))
    else:
        print("Error: Must specify targets.")
        exit(1)

    ## Load Commands
    if args.script:
        with open(args.script, 'r') as open_file:
            for line in open_file.readlines():
                commands.append(line.strip('\n'))
    elif args.commands:
        commands = [args.commands.strip('\n')]
    else:
        print("Error: Must Specify Command(s).")
        exit(2)

    ## Load Credentials
    if args.key:
        target_keyfile = args.key.strip('\n').strip()
    elif args.passwords:
        target_passes = args.passwords.split(',')
    elif args.passwordfile:
        with open(args.passwordfile, 'r') as open_file:
            for line in open_file.readlines():
                if not line.strip().startswith('#'):
                    target_passes.append(line.strip('\n').strip())
    else:
        print("Error: Must specify authentication method.")
        exit(3)

    ## Load Users
    if args.users:
        target_users = args.users.strip('\n').strip().split(',')
    elif args.userfile:
        with open(args.userfile, 'r') as open_file:
            for line in open_file.readlines():
                if not line.strip().startswith('#'):
                    target_users.append(line.strip('\n').strip())
    else:
        print("Error: Must specify user to connect with.")
        exit(4)

    #If the lengths do not match, expand using the last set of credentials
    while(len(target_hosts) > len(target_passes)):
        target_passes.append(target_passes[len(target_passes)-1])
    while(len(target_hosts) > len(target_users)):
        target_users.append(target_users[len(target_users)-1])

    ## Start Execution threads
    debug("Starting ssh execution on "+str(len(target_hosts))+" targets.")
    for i in range(0, len(target_hosts)):
        debug("\tExecuting {} on target {} || {!r}:{!r}@{!r}".format(commands, i, target_users[i], target_passes[i], target_hosts[i]))
        if target_keyfile is not None:
            ssh = SSHExec(host=target_hosts[i], user=target_users[i], passwd="", cmdlines=commands, key=target_keyfile, debug=DEBUG)
        else:
            ssh = SSHExec(host=target_hosts[i], user=target_users[i], passwd=target_passes[i], cmdlines=commands, key=None, debug=DEBUG)
        ssh.start()

    exit(0)

def debug(msg):
    if DEBUG:
        print("{DEBUG} "+str(msg))


if __name__ == "__main__":
    main()
