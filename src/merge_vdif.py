#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 26 21:08:56 2020

Merge 2 VDIF files
the files have missing packets due to the recorder, search those in the other file and merge to a single file
Output the file in the current directory.

./merge_vdif.py file1 file2
@author: gofrito
"""
import numpy as np
import argparse
import os.path

parser = argparse.ArgumentParser()
parser.add_argument('fn1', nargs='?',help='First file',default="check_string_for_empty")
parser.add_argument('fn2', nargs='?',help='Second file',default="check_string_for_empty")

args = parser.parse_args()

input_file1 = args.fn1
input_file2 = args.fn2

# Set the  length of the scan
sec: int = 300

output_file = f'./{os.path.basename(input_file1)[:-4]}.vdif'

try:
    fd1 = open(input_file1,'rb')
    fd2 = open(input_file2,'rb')
    fd3 = open(output_file,'wb')
except:
    raise FileNotFoundError

def read_header(packet):
    hex_seconds: bytes = packet[0:4]
    hex_frame: bytes = packet[4:7]
    hex_epoch: bytes = packet[7:8]
    seconds: int = int.from_bytes(hex_seconds, 'little')
    frame_nr: int = int.from_bytes(hex_frame, 'little')
    epoch: int = int.from_bytes(hex_epoch, 'little')

    sec = '{0:0b}'.format(seconds)
    seconds: int = int(sec[2:],2)
    return (seconds, frame_nr)

total_packets: int = 0
total_sec: int = 0

#read the first packet in each file
packet1 = fd1.read(8032)
packet2 = fd2.read(8032)

time1, frame1 = read_header(packet1)
time2, frame2 = read_header(packet2)

# Check the initial times, and reverse if necessary
if time2 < time1:
    fd4 = fd1
    fd1 = fd2
    fd2 = fd4
    fd3.write(packet2)
    last_time, last_frame = time2, frame2
else:
    fd3.write(packet1)
    last_time, last_frame = time1, frame1

# Go through all the packets
for ip in range(8000*sec):
    packet1 = fd1.read(8032)

    time1,frame1 = read_header(packet1)

    # If frames follow a nice order
    if frame1 == last_frame + 1 and time1 == last_time:
        last_time, last_frame = time1, frame1
        fd3.write(packet1)
        total_packets += 1

    # If we have a second step
    elif time1 == last_time + 1 and frame1 == 0:
        last_time, last_frame = time1, frame1
        fd3.write(packet1)
        print(f'Sec: {total_sec} and total number of packets: {total_packets} from file1')
        total_packets = 1
        total_sec += 1

    # If a packet or second are not in order
    else:
        # Remove the packet read from fd1
        fd1.seek(-8032,1)
        # We should look for that time frame elsewhere
        searching: bool = True
        while searching:
            packet2 = fd2.read(8032)
            time2, frame2 = read_header(packet2)

            # Is the new one we need?
            if time2 == last_time and frame2 == last_frame + 1 :
                #We actually find it
                searching = False
                # update the timestamps
                last_time, last_frame = time2, frame2
                # Write the packet from the 2nd file to the output
                fd3.write(packet2)
                total_packets += 1

            # Check if the break was on the packet of a seccond
            elif time2 == last_time +1 and frame2 == 0:
                # It jump to the new second
                searching = False
                last_time, last_frame = time2, frame2
                fd3.write(packet2)
                print(f'Sec: {total_sec} and total number of packets: {total_packets} from file2')
                total_packets = 1
                total_sec += 1

            # We don't actually have the missing packet
            elif time2 > last_time:
                searching = False
                # So let's write the last packet missing
                if time1 == time2:
                    last_time, last_frame = time1, frame1
                    packet1 = fd1.read(8032)
                    fd3.write(packet1)
                elif time2 > time1:
                    last_time, last_frame = time1, frame1
                    packet1 = fd1.read(8032)
                    fd3.write(packet1)
                else:
                    last_time, last_frame = time2, frame2
                    fd3.write(packet2)
            else:
                searching = True

fd1.close()
fd2.close()
fd3.close()

print(f'Total # of packets : {total_packets}')
print(f'Total # of seconds : {total_sec}')