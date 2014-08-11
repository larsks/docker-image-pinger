#!/usr/bin/python

import os
import sys
import argparse
import subprocess
import time
import random
import logging

import etcdclient


def wait_for_address(name):
    logging.info('waiting for address on %s', name)
    p = subprocess.Popen(['ip', 'monitor', 'address'],
                         stdout=subprocess.PIPE)

    for line in iter(p.stdout.readline, ''):
        if not line[0].isdigit():
            continue

        fields = line.strip().split()
        if not fields[1] == name:
            continue

        if not fields[2] == 'inet':
            continue

        return fields[3].split('/')[0]


def get_address_of(name):
    logging.info('looking up address of %s', name)
    try:
        out = subprocess.check_output(['ip', 'addr', 'show', name])
    except subprocess.CalledProcessError:
        return

    for line in out.split('\n'):
        line = line.split()
        if line[0] != 'inet':
            continue

        return line[1].split('/')[0]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--endpoint', '-e',
                   default='http://localhost:4001/v2')
    p.add_argument('--verbose', '-v',
                   action='store_const',
                   const=logging.INFO,
                   dest='loglevel')
    p.add_argument('--debug', '-D',
                   action='store_const',
                   const=logging.DEBUG,
                   dest='loglevel')
    p.set_defaults(loglevel=logging.WARN)
    return p.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(
        level=args.loglevel)

    logging.info('connected to etcd at %s', args.endpoint)
    etcd = etcdclient.Etcd(args.endpoint)

    myaddress = get_address_of('eth1')
    if myaddress is None:
        myaddress = wait_for_address('eth1')

    logging.info('got my address = %s', myaddress)
    etcd.append('addresses', myaddress)

    while True:
        addresses = [ node['value'] for node in etcd.get_all('addresses')
                     if node['value'] != myaddress ]

        if not addresses:
            logging.warn('no other addresses; sleeping')
            time.sleep(1)
            continue

        logging.info('found %d addresses', len(addresses))
        selected = random.choice(addresses)
        logging.info('selected address %s', selected)
        subprocess.call(['ping', '-c10', selected])

if __name__ == '__main__':
    main()


