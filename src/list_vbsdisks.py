#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 17 12:37:06 2020

@author: gofrito

Usage: ./list_vbsdisks.py
"""
import os, socket
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-o', dest='save2file', help='write results to disk', action='store_true', default=False)
parser.add_argument('-s', dest='disp_screen', help='write results to screen', action='store_true', default=False)
parser.add_argument('-v', dest='verbose', help='verbose', action='store_true', default=False)

args = parser.parse_args()

start = time.process_time()

# Determine the amount of disks per flexbuff
host: str = socket.gethostname()
num_disks: dict = {'flexbuffhb':34,'flexbuffyg':36,'flexbuffke':36,'flexbuffcd':12,'flexbuflyg':5}

total_disks: int = num_disks[host]
sessions = {}

def progress(percent=0, width=30):
    left = width * percent // 100
    right = width - left
    print('\r[', '#' * left, ' ' * right, ']',
          f' {percent:.0f}%',
          sep='', end='', flush=True)

# We go through all disks and list everything
for disk in range(total_disks):
    disk_directories = os.listdir(f'/mnt/disk{disk}')

    for root, dirs, files in os.walk(f'/mnt/disk{disk}'):
        for name in dirs:
            session = name.split('_')[0]
            if session not in sessions:
                sessions.update( {session:0})

        for name in files:
            session = name.split('_')[0]
            fsize = os.path.getsize(os.path.join(root,name))
            sessions[session] += fsize

    progress(int(101*disk/total_disks))

if args.disp_screen:
    print(f'\nHow many sessions have we found : {len(sessions)}')

    size_trigger: float = 1e9
    if args.verbose:
        size_trigger = 0

    for session in sessions:
        if sessions[session] > size_trigger:
            print(f'Session: {session:9} and total size {sessions[session]/(1024*1024*1024):10.3f} GB')

if args.save2file:
    fn = '/tmp/disk_used.txt'
    f = open(fn, 'w')
    for session in sessions:
        if sessions[session] > 1e9:
            f.write(f'{session},{sessions[session]}\n')
    f.close()
    print(f'\ndata stored in {fn}')

print(f'Total time spent {time.process_time() - start}')
