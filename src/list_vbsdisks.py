#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 17 12:37:06 2020

@author: gofrito

Usage: ./list_vbsdisks.py
"""
import os
import time

start = time.process_time()

total_disks: int = 36
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

print(f'\nHow many sessions have we found : {len(sessions)}')

size_trigger = 1e9
for session in sessions:
    if sessions[session] > size_trigger:
        print(f'Session: {session:9} and total size {sessions[session]/(1024*1024*1024):10.3f} TB')


print(f'Total time spent {time.process_time() - start}')
