#!/usr/bin/env python3

import subprocess
import logging
import os

logging.basicConfig(
    filename='process.log', 
    level=10, 
    format='%(asctime)s:%(levelname)s:%(funcName)s:%(message)s')

class Backup:
    def __init__(self, ip, mac, source, destination, backup_destination):
        self.ip_address = ip
        self.mac_address = mac
        self.source = source
        self.destination = destination
        self.backup_destination = backup_destination

        # check if all
        if not all([ip, mac, source, destination, backup_destination]):
            raise Exception('Missing arguments.')
        
        
        logging.info(f'Process Created')
        logging.info(f'{ip=}, {mac=}, {source=}, {destination=}, {backup_destination=}')

    def start(self):
        logging.info(f'Process Started')

        # check root access
        if not os.access('/root', os.R_OK):
            logging.critical('Missing root privileges.')
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

        logging.info('Backup Successful\n')
        print("Backup successful.")

        
    def __is_up(self, ip_address):
        out = subprocess.call(f'ping -c 1 -t 1 {ip_address}',
            shell=True,
            stdout=open('/dev/null', 'w'),
            stderr=subprocess.PIPE
        )

        logging.info(f'Ping {ip_address}: {"True" if out == 0 else "False"}')
        return True if out == 0 else False

    def __switch_on(self, mac_address: str):
        logging.info(f'WakeOnLan {mac_address}')
        subprocess.call(f'wakeonlan {mac_address}',
            shell=True,
            stdout=open('/dev/null', 'w'),
            stderr=subprocess.PIPE
        )

    def __backup(self, source, destination):
        logging.info(f'Remote Backup {source} to {destination}')
        out = subprocess.call(f'rsync -azv --delete {source} {destination}',
            shell=True,
            # stdout=open('/dev/null', 'w'),
            stderr=subprocess.PIPE
        )

        if out != 0:
            logging.error(f'Backup Error - code: {out}')
            print("A backup error has occurred.")
            exit(1)
        
    def __internal_backup(self, ip_address, source, destination):
        logging.info(f'Internal Backup {ip_address}:{source} to {ip_address}:{destination}')
        out = subprocess.call(f'ssh root@{ip_address} "rsync -azv {source}/ {destination}"',
            shell=True,
            # stdout=open('/dev/null', 'w'),
            stderr=subprocess.PIPE
        )

        if out != 0:
            logging.error(f'Backup Error - code: {out}')
            print("A backup error has occurred.")
            exit(1)


    def __shutdown(self, ip_address):
        logging.info(f'Sending shutdown request {ip_address}')
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
