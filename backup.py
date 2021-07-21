#!/usr/bin/env python3

import subprocess
import time

try:
    from data import IP_ADDRESS, MAC_ADDRESS, SOURCE, DESTINATION
except ImportError:
    print("Create data.py file with \nIP_ADDRESS, MAC_ADDRESS, SOURCE, DESTINATION string variables.")
    exit(1)

if not IP_ADDRESS or not MAC_ADDRESS or not SOURCE or not DESTINATION:
    print("Missing data in data.py file.")
    exit(1)

def main():
    if not ping(IP_ADDRESS):
        print("Host is down.")
        wake_on_lan(MAC_ADDRESS)
        while not ping(IP_ADDRESS):
            time.sleep(.5)
    print("Host is up.\n")

    backup(IP_ADDRESS, SOURCE, DESTINATION)
    # copy files

    shutdown(IP_ADDRESS)
    while ping(IP_ADDRESS):
        time.sleep(.5)
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
    out = subprocess.call(f'rsync -azP {source} root@{host}:{destination}',
        shell=True,
        stdout=open('/dev/null', 'w'),
        stderr=subprocess.PIPE
    )

    if out != 0:
        print("A backup error has occurred.")
        exit(2)

    print(f"{source} backed up.")


def shutdown(host):
    print(f"Shutting down {host}...")
    subprocess.call(f'ssh root@{host} "shutdown now"',
        shell=True,
        stdout=open('/dev/null', 'w'),
        stderr=subprocess.PIPE
    )


if __name__ == '__main__':
  main()
