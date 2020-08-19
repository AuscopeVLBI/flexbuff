#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 17 12:37:06 2020

@author: gofrito

Usage: ./check_vbsdisks.py
"""

import os
import time

disks_mounted= 0
total_disks= 36

for disk in range(total_disks):
    stat = os.path.ismount('/mnt/disk{}'.format(disk))
    if stat:
        disks_mounted += 1
    else:
        print('Failed to detect mounted disk {}'.format(disk))

if total_disks == disks_mounted:
    print('All disks are properly mounted')
