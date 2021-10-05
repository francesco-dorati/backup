#!/usr/bin/env python3

import subprocess
import time
import os

def log(s: str): 
    with open('log.txt', 'a') as file:
        file.write(f'{s} at {time.strftime("%H:%M:%S %d %B %y")}') 

try:
    from data import IP_ADDRESS, MAC_ADDRESS, SOURCE, DESTINATION, INTERNAL_SOURCE, INTERNAL_DESTINATION
except ImportError:
    print("Create data.py file with \nIP_ADDRESS, MAC_ADDRESS, SOURCE, DESTINATION string variables.")
    exit(1)


if not all([IP_ADDRESS, MAC_ADDRESS, SOURCE, DESTINATION, INTERNAL_SOURCE, INTERNAL_DESTINATION]):
    print("Missing data in data.py file.")
    exit(1)

def main():
    # check root access
    if not os.access('/root', os.R_OK):
        print("Missing root privileges.")
        exit(1)
    
    # switch up
    if not ping(IP_ADDRESS):
        print(f"{IP_ADDRESS} is down.")
        wake_on_lan(MAC_ADDRESS)
        while not ping(IP_ADDRESS):
            pass
    print(f"{IP_ADDRESS} is up.\n")

    backup(IP_ADDRESS, SOURCE, DESTINATION)
    internal_backup(IP_ADDRESS, INTERNAL_SOURCE, INTERNAL_DESTINATION)

    shutdown(IP_ADDRESS)
    while ping(IP_ADDRESS):
        pass
    print("Host is down.\n")
    print("Backup successful.")


def ping(host):
    cmd = f'ping -c 1 -t 1 {host}'
    out = subprocess.call(cmd,
        shell=True,
        stdout=open('/dev/null', 'w'),
        stderr=subprocess.PIPE
    )
    log(cmd)

    return True if out == 0 else False


def wake_on_lan(mac):
    print("Switching it up...")
    cmd = f'wakeonlan {mac}'
    subprocess.call(cmd,
        shell=True,
        stdout=open('/dev/null', 'w'),
        stderr=subprocess.PIPE
    )
    log(cmd)

def backup(host, source, destination):
    print(f"Backing up {source}...")
    cmd = f'rsync -azv --delete {source} root@{host}:{destination}'
    out = subprocess.call(cmd,
        shell=True,
        # stdout=open('/dev/null', 'w'),
        stderr=subprocess.PIPE
    )
    log(cmd)

    if out != 0:
        print("A backup error has occurred.")

    print(f"{source} backed up.\n")

def internal_backup(host, source, destination):
    print(f"Backing up {source}...")
    cmd = f'ssh root@{host} "rsync -azv {source} {destination}"' 
    out = subprocess.call(cmd,
        shell=True,
        # stdout=open('/dev/null', 'w'),
        stderr=subprocess.PIPE
    )
    log(cmd)

    if out != 0:
        print("A backup error has occurred.")

    print(f"{source} backed up.\n")

def shutdown(host):
    print(f"Shutting down {host}...")
    cmd = f'ssh root@{host} "shutdown now"'
    subprocess.call(cmd,
        shell=True,
        stdout=open('/dev/null', 'w'),
        stderr=subprocess.PIPE
    )
    log(cmd)


if __name__ == '__main__':
    log('Starting process')
    main()
    log('Ending process')
