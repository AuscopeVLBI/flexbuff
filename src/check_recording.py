#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 16:37:06 2019

@author: gmolera

Usage: ./check_recording.py <filename>

"""
import subprocess, os
import argparse
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser(prog='check_recording.py', description='')
parser.add_argument('filename', help='Full Name of the file recorded')
parser.add_argument('nchannels', help='Number of channels per IF')
parser.add_argument('bandwidth', help='Bandwidth of the channel')
parser.add_argument('channel', help='Select channel to display')

args = parser.parse_args()
inFn = args.filename
nch  = args.nchannels
bw   = args.bandwidth
ch   = args.channel

# Unless we do a very short recording we are probably happy to have 5 second integration
fftpoints = 320e3
inttime   = 5

'Mount the file recording into Flexbuff style disks'
# Check if something is mounted - Not even check umount
subprocess.call(['fusermount','-u','/home/observer/vbs_tmp'])

# Mount the file into vbs_tmp
subprocess.call(['vbs_fs','-n','4','-I','{}'.format(inFn),'/home/observer/vbs_tmp/'])

'Run swspectrometer'
# First create the inifile
p = subprocess.Popen(['cp','/home/observer/AuscopeVLBI/flexbuff/config/inifile.ini','inifile.ini'])

sourceFormat = 'VDIF_8000-{}-{}-2'.format(4*int(bw)*int(nch),nch)

s = open('inifile.ini').read()
s.replace('VDIF_8000-0000-00-00',sourceFormat)
s.replace('SourceChannels    = 0','SourceChannels    = {}'.format(nch))
s.replace('BandwidthHz       = 0','BandwidthHz       = {}'.format(bw))
s.replace('UseFile1Channel   = 0','UseFile1Channel   = {}'.format(ch))

f = open('inifile.tmp.ini','w')
f.write(s)
f.close()

# Then modify the parameters related to the observation
# sourceFormat derived

subprocess.call(['swspectrometer','inifile.tmp.ini','/home/observer/vbs_tmp/{}'.format(inFn)])
spec_filename = 'single_channel.bin'

# visualize the spectra

fsize = os.path.getsize(spec_filename)
Nspec = np.int(np.floor(0.5*fsize/(fftpoints + 1)))
Nfft  = np.int(fftpoints/2+1)
Sps    = np.zeros((Nspec,Nfft))

fd = open(spec_filename,'rb')

for ip in np.arange(Nspec):
    read_data = np.fromfile(file=fd, dtype='float32', count=Nfft)
    Sps[ip]   = read_data

Aspec = np.sum(Sps,axis=0)/Nspec

df = 2*bw/fftpoints
jf = np.arange(Nfft)
ff = df*jf
        
# Make a plot
plt.plot(ff,np.log10(Aspec))
plt.ylabel('Spectrum')
plt.xlabel('Freq [Hz]')
plt.title('Last spectrum read from the file')
plt.show()

# Let's clean our mess
#subprocess.call(['rm','inifile.tmp.ini'])
#subprocess.call(['rm','single_channel*'])
#subprocess.call(['fusermount','-u','~/vbs_tmp'])
