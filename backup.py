#!/usr/bin/env python3

import subprocess
import time



def main():
  if not ping(HOSTNAME):
    print("Host is down.")
    wake_on_lan(MAC_ADDRESS)
    while not ping(HOSTNAME):
      time.sleep(1)

  print("Host is up.")
  backup(HOSTNAME, SOURCE, DESTINATION)
  # copy files
  shutdown(HOSTNAME)


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
    subprocess.call(f'rsync -azP {source} root@{host}:{destination}',
        shell=True,
        stdout=open('/dev/null', 'w'),
        stderr=subprocess.PIPE
    )
    print(f"{source} backed up.")


def shutdown(host):
    print(f"Shutting down {host}...")
    subprocess.call(f'ssh root@{host} "shutdown now"',
        shell=True,
        stdout=open('/dev/null', 'w'),
        stderr=subprocess.PIPE
    )
    print(f"{host} is down.")


if __name__ == '__main__':
  main()
