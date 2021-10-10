#!/usr/bin/env python3

import subprocess
import logging
import time
import sys
import os


logging.basicConfig(
    level=10, 
    format='%(asctime)s:%(levelname)s:%(lineno)d\t\t%(message)s',
    handlers=[
        logging.FileHandler(f'{"/".join(os.path.realpath(__file__).split("/")[:-1])}/process.log'),
        logging.StreamHandler(sys.stdout)
    ]
)


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
        
        
        logging.info(f'PROCESS CREATED')
        logging.info(f'{ip=}')
        logging.info(f'{mac=}')
        logging.info(f'{source=}')
        logging.info(f'{destination=}')
        logging.info(f'{backup_destination=}')

    def start(self):
        logging.info(f'PROCESS STARTED')

        # check root access
        if not os.access('/root', os.R_OK):
            logging.critical('Missing root privileges.\n')
            raise Exception("Missing root privileges.")

        # switch on
        if not self.__is_up(self.ip_address):
            logging.info(f'Switching on {self.mac_address}')
            self.__switch_on(self.mac_address)

            # wait for host to switch on
            count = 0
            while not self.__is_up(self.ip_address):
                if count == 10:
                    logging.critical('Host took too mutch to switch on.\n')
                    exit(1)
                count += 1

        logging.info(f'{self.ip_address} is up.')

        # backup
        source = self.source
        destination = f'root@{self.ip_address}:{self.destination}'

        logging.info(f'Remote Backup {source} to {destination}')
        self.__backup(
            source=source,
            destination=destination
        )
        logging.info(f"{source} backed up.\n")

        # repeat backup
        source = self.destination
        destination = self.backup_destination

        logging.info(f'Internal Backup ({self.ip_address}) {source} to {destination}')
        self.__internal_backup(
            ip_address=self.ip_address,
            source=source,
            destination=destination
        )
        logging.info(f"{source} backed up.\n")
        

        # shutdown
        logging.info(f'Shutting Down {self.ip_address}')
        self.__shutdown(self.ip_address)
        while self.__is_up(self.ip_address):
            time.sleep(5)
        logging.info(f'{self.ip_address} is down.')

        logging.info('Backup Successful\n')

        
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
            stderr=subprocess.PIPE
        )

        if out != 0:
            logging.error(f'Backup Error - code: {out}\n')
            exit(1)
        
    def __internal_backup(self, ip_address, source, destination):
        out = subprocess.call(f'ssh root@{ip_address} "rsync -azv {source}/ {destination}"',
            shell=True,
            stderr=subprocess.PIPE
        )

        if out != 0:
            logging.error(f'Backup Error - code: {out}\n')
            exit(1)


    def __shutdown(self, ip_address):
        subprocess.call(f'ssh root@{ip_address} "shutdown now"',
            shell=True,
            stdout=open('/dev/null', 'w'),
            stderr=subprocess.PIPE
        )

def main():
    try:
        from data import IP_ADDRESS, MAC_ADDRESS, SOURCE, DESTINATION, BACKUP_DESTINATION
    except ImportError:
        print("Create data.py file with \nIP_ADDRESS, MAC_ADDRESS, SOURCE, DESTINATION, BACKUP_DESTINATION string variables.")
        exit(1)
    backup = Backup(IP_ADDRESS, MAC_ADDRESS, SOURCE, DESTINATION, BACKUP_DESTINATION)
    backup.start()

if __name__ == '__main__':
    main()
