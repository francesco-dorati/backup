#!/usr/bin/env python3

import subprocess
import time
import os


# if not all([IP_ADDRESS, MAC_ADDRESS, SOURCE, MAIN_DESTINATION]):
#     print("Missing data in data.py file.")
#     exit(1)

class Backup:
    def __init__(self, ip, mac, source, destination, backup_destination):
        # TODO 
        # try to get ip address form mac
        self.ip_address = ip
        self.mac_address = mac
        self.source = source
        self.destination = destination
        self.backup_destination = backup_destination

        # check if all
        if not all([ip, mac, source, destination, backup_destination]):
            raise Exception('Missing arguments.')
    
    def start(self):
        # check root access
        if not os.access('/root', os.R_OK):
            raise Exception("Missing root privileges.")

        # switch on
        if not self.__is_up(self.ip_address):
            print(f'Switching on {self.ip_address}...')
            self.__switch_on(self.mac_address)

            # wait for host to switch on
            count = 0
            while not self.__is_up(self.ip_address):
                if count == 10:
                    print(f'Host took too mutch to switch on.\nExiting...')
                    exit(1)
                count += 1

        print(f'{self.ip_address} is up.\n')

        # backup
        print(f"Backing up {self.source}...")
        self.__backup(
            source=self.source,
            destination=f'root@{self.ip_address}:{self.destination}')
        print(f"{self.source} backed up.\n")

        # repeat backup
        print(f"Backing up {self.destination}.. to {self.backup_destination}.")
        self.__internal_backup(
            ip_address=self.ip_address,
            source=self.destination,
            destination=self.backup_destination)
        print(f"{self.destination} backed up.\n")
        

        # shutdown
        self.__shutdown(self.ip_address)
        while self.__is_up(self.ip_address):
            pass
        print("Host is down.\n")
        print("Backup successful.")

        

        
    def __is_up(self, ip_address):
        out = subprocess.call(f'ping -c 1 -t 1 {ip_address}',
            shell=True,
            stdout=open('/dev/null', 'w'),
            stderr=subprocess.PIPE
        )

        return True if out == 0 else False

    def __switch_on(self, mac_address: str):
        subprocess.call(f'wakeonlan {mac_address}',
            shell=True,
            stdout=open('/dev/null', 'w'),
            stderr=subprocess.PIPE
        )

    def __backup(self, source, destination):
        out = subprocess.call(f'rsync -azv --delete {source} {destination}',
            shell=True,
            # stdout=open('/dev/null', 'w'),
            stderr=subprocess.PIPE
        )

        if out != 0:
            print("A backup error has occurred.")
        
    def __internal_backup(self, ip_address, source, destination):
        out = subprocess.call(f'ssh root@{ip_address} "rsync -azv {source}/ {destination}"',
            shell=True,
            # stdout=open('/dev/null', 'w'),
            stderr=subprocess.PIPE
        )

        if out != 0:
            print("A backup error has occurred.")
        pass

    def __shutdown(self, ip_address):
        print(f"Shutting down {ip_address}...")
        subprocess.call(f'ssh root@{ip_address} "shutdown now"',
            shell=True,
            stdout=open('/dev/null', 'w'),
            stderr=subprocess.PIPE
        )

def main():
    try:
        from data import IP_ADDRESS, MAC_ADDRESS, SOURCE, DESTINATION, BACKUP_DESTINATION
    except ImportError:
        print("Create data.py file with \nIP_ADDRESS, MAC_ADDRESS, SOURCE, DESTINATION string variables.")
        exit(1)

    backup = Backup(IP_ADDRESS, MAC_ADDRESS, SOURCE, DESTINATION, BACKUP_DESTINATION)
    backup.start()

if __name__ == '__main__':
  main()
