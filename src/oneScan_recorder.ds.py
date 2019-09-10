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

vdif_frame_ch = ('0','0','1','1','0','0')
ip_orig       = ('15','16','17','18','19','20')
ifboards      = ('a','b','c','d','e','f')

## MAIN PROGRAM
# Parse command line
parser = argparse.ArgumentParser(prog='oneScan_recorder.ds.py', description= 'Record one single scan given a output filename length and nr of channels width datastreams')
parser.add_argument('filename',  help='Output filename')
parser.add_argument('scantime',  help='Length of the scan')
parser.add_argument('nrchannel', help='Number of channels recording per IF', default=1)
parser.add_argument('configFile', nargs='?', help='Set the config file', default='/opt/configStation.ini')
parser.add_argument('recordingMode', help='Specify recording mode 0=old 1=new', default=0)
parser.add_argument('-v', '--version', action='version',version='%(prog)s 1.0')

args       = parser.parse_args()
outputFn   = args.filename
length     = int(args.scantime)
chans      = args.nrchannel
iniFile    = args.configFile
mode       = args.recordingMode

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
Using the new style of data recording. 
In this case all the streams are sent via the same network port.
'''

# Send commands and messages via socket communication (encode and decode)
def fbComms(s,command):
    s.send(command.encode())
    print(s.recv(4096).decode())

# Configure basic parameters for the Flexbuff recorder

def configure(s, thread, nthreads):
        data_rate = 128*int(nthreads[thread])
        fbComms(s,'datastream=reset')
        fbComms(s,'mtu=9000')
        fbComms(s,'net_protocol=udpsnor:128M:128M:1')
        fbComms(s,'mode=vdif_8000-{}-{}-2'.format(str(data_rate),nthreads[thread]))
        fbComms(s,'record=nthread::{}'.format(nthreads[thread]))
        fbComms(s,'net_port=46227')


'1. Having the vdif_frame_ch, we can determine which datastreams should be active '
for board in range(6):
    if vdif_frame_ch[board] == '1':
        fbComms(sf,'datastream = add : {}.vdif : 192.168.1.{}/{}.*'.format(ifboards[board],ip_orig[board],station))

'''2. We concatenate everything into the same file as they all use same port and different thread IDs
I don't like to create a file with termination abcd that depend on the ifs, but it's one way.
aggregate = ''
for board in range(nboards):
    if vdif_frame_ch == '1':
        aggregate = aggregate + ifboards[boards]
fbComms(sf,'datastream = add : {} : */{}.*'.format(aggregate, station))
THIS PART NEEDS TBT
'''

fbComms(sf,'datastream?')
fbComms(sf,'record?')
fbComms(sf,'evlbi?')
fbComms(sf,'record=on: {}_{}'.format(outputFn,station))

# Make a While loop to control the recording with sleep(5)
n=0
while n < length:
    print('Step: {}\n'.format(str(n*5)))
    print(fbComms(sf,'evlbi?;tstat?'))
    n = n + 1
    time.sleep(1)
 
fbComms(sf,'record=off')
 
'We do some clean up before shutting the door'
# Clean the datastreams
sf.send('datastream?'.encode())
elem_ds = sf.recv(1024).decode().split(':')


for ds in range(int(elem_ds[1])):
   if ds+1 ==  elem_ds[1]:
       # If it is the last datastream then
       fbComms(sf,'datastream = remove :{}'.format(elem_ds[ds+2][0:-2]))
   else:
       # If there are more than one datastream 
       fbComms(sf,'datastream = remove :{}'.format(elem_ds[ds+2]))

sf.close()
