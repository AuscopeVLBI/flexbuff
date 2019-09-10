#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 16:37:06 2019

@author: gmolera

Usage: ./oneScan_recorder.py <filename> <scan_time> <number_chans_per_IF>
"""

import socket, time
import argparse
import configparser

## MAIN PROGRAM
# Parse command line
parser = argparse.ArgumentParser(prog='oneScan_recorder.py', description= 'Record one single scan given a output filename length and nr of channels')
parser.add_argument('filename',  help='Output filename')
parser.add_argument('scantime',  help='Length of the scan')
parser.add_argument('nrchannel', help='Number of channels recording per IF', default=1)
parser.add_argument('configFile', nargs='?', help='Set the config file', default='/opt/configStation.ini')
parser.add_argument('-v', '--version', action='version',version='%(prog)s 1.0')

args       = parser.parse_args()
output_fn  = args.filename
length     = int(args.scantime)
chans      = args.nrchannel
iniFile    = args.configFile

# Read inital parameters from the config file
config = configparser.ConfigParser()
config.sections()
config.read(iniFile)
print('Using the initial setup from {}'.format(args.configFile))

# FLEXBUFF CONFIGURATION
station   = config['DBBC3']['Station']
conn_fbff = (config['FLEXBUFF']['FbAddress'],int( config['FLEXBUFF']['FbPort']))

'FLEXBUFF CONFIGURATION'
print('Setting up Flexbuff {}\n'.format(station))
sf = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sf.connect(conn_fbff)
except:
    raise RuntimeError('Failed to connect to {0}'.format(conn_fbff))

'''
Using the old-type of data recording with parallel streams in different ports.
46227:IFA  46228:IFB
46229:IFC  46230:IFD
46231:IFE  46232:IFF
as for ex:
nthreads = {'46227':chans,'46228':chans,'46229':chans,'46230':chans,'46231':chans,'46232':chans}
'''
#nthreads = {'46227':chans}
nthreads = {'46229':chans,'46230':chans,'46231':chans,'46232':chans}

# Send commands and messages via socket communication (encode and decode)
def fb_send(s,command):
    s.send(command.encode())
    print(s.recv(4096).decode())

# Configure basic parameters for the Flexbuff recorder
def configure(s, thread, nthreads):
        data_rate = 32*4*int(nthreads[thread])
        fb_send(s,'runtime=stream{}'.format(thread))
        fb_send(s,'mtu=9000')
        fb_send(s,'net_protocol=udps:128M:128M:1')
        fb_send(s,'mode=vdif_8000-{}-{}-2'.format(str(data_rate),nthreads[thread]))
        fb_send(s,'record=mk6')
        fb_send(s,'record=nthread::{}'.format(nthreads[thread]))
        fb_send(s,'net_port={}'.format(thread))
#        fb_send(s,'set_disks={}'.format(disks[thread]))

# Send the command to start recording and request information
def start_rec(s, thread):
        fb_send(s,'runtime=stream{};record=on:{}_{}'.format(thread,output_fn,thread))
        return (fb_send(s,'tstat?'))

# We make sure that all streams are not recording
command = ''
for thread in nthreads:
    str1 = 'runtime=stream{}; record=off;'.format(thread)
    command = command + str1

fb_send(sf,command)

# We configure the main parameters of the VDIF recording
for thread in nthreads:
    configure(sf, thread, nthreads)

print('Now ready to start recording. Press enter to start...')
time.sleep(0.5)

# Start the recording for each of the threads
for thread in nthreads:
    start_rec(sf,thread)

# Make a While loop to control the recording with sleep(5)
n=0
while n < length:
    print('Step: {}\n'.format(str(n*5)))
    for thread in nthreads:
        print(fb_send(sf,'runtime=stream{};evlbi?;tstat?'.format(thread)))
    n = n + 1
    time.sleep(1)

# Send stop commands to all threads
command = ''
for thread in nthreads:
    fb_send(sf,'runtime=stream{}; record=off;'.format(thread))

sf.close()
