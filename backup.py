#!/usr/bin/env python3

import subprocess
import time
import os

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
    out = subprocess.call(f'ping -c 1 -t 1 {host}',
        shell=True,
        stdout=open('/dev/null', 'w'),
        stderr=subprocess.PIPE
    )

    return True if out == 0 else False


def wake_on_lan(mac):
    print("Switching it up...")
    subprocess.call(f'wakeonlan {mac}',
        shell=True,
        stdout=open('/dev/null', 'w'),
        stderr=subprocess.PIPE
    )

def backup(host, source, destination):
    print(f"Backing up {source}...")
    out = subprocess.call(f'rsync -azv --delete {source} root@{host}:{destination}',
        shell=True,
        # stdout=open('/dev/null', 'w'),
        stderr=subprocess.PIPE
    )

    if out != 0:
        print("A backup error has occurred.")

    print(f"{source} backed up.\n")

def internal_backup(host, source, destination):
    print(f"Backing up {source}...")
    out = subprocess.call(f'ssh root@{host} "rsync -azv {source} {destination}"',
        shell=True,
        # stdout=open('/dev/null', 'w'),
        stderr=subprocess.PIPE
    )

    if out != 0:
        print("A backup error has occurred.")

    print(f"{source} backed up.\n")

def shutdown(host):
    print(f"Shutting down {host}...")
    subprocess.call(f'ssh root@{host} "shutdown now"',
        shell=True,
        stdout=open('/dev/null', 'w'),
        stderr=subprocess.PIPE
    )


if __name__ == '__main__':
  main()
