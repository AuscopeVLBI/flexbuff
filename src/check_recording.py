#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 16:37:06 2019

@author: gofrito

Usage: ./check_recording.py <filename> nchannels bandwidth channel [zoom] min max frequencies

"""
import subprocess, os, time
import argparse
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser(prog='check_recording.py', description='Check recording allows to verify the spectra of the recorded data in a Flexbuff')
parser.add_argument('filename',   help='Full name of the recorded file')
parser.add_argument('nchannels',  help='Number of channels per IF')
parser.add_argument('bandwidth',  help='Bandwidth of the channel')
parser.add_argument('channel',    help='Select channel to display')
parser.add_argument('integration', help='integration time')
parser.add_argument('-zf',dest='zoomfreq',nargs='+',type=float,metavar='N')

args = parser.parse_args()
inFn: str = args.filename
nch: str  = args.nchannels
bw: str   = args.bandwidth
ch: str   = args.channel
dts: str = args.integration

# Unless we do a very short recording we are probably happy to have 5 second integration
fftpoints: int = 3200e3
inttime: int = int(dts)

# frequency resolution
df: float = 2*int(bw)*1e6/fftpoints

if args.zoomfreq:
    fmin: float = args.zoomfreq[0]*1e6
    fmax: float = args.zoomfreq[1]*1e6
    bmin: int = int(fmin/df)
    bmax: int = int(fmax/df)

'Mount the file recording into Flexbuff style disks'
# Check if something is mounted - Not even check umount
subprocess.call(['fusermount','-u','/home/observer/vbs_tmp'])

# Mount the file into vbs_tmp
subprocess.call(['vbs_fs','-n','4','-I','{}'.format(inFn),'/home/observer/vbs_tmp/'])

'Run swspectrometer'
# First create the inifile
p = subprocess.Popen(['cp','/home/observer/AuscopeVLBI/flexbuff/config/inifile.ini','inifile.ini'])

time.sleep(0.5)

# Open inifile and replace those settings that are observation dependent
s = open('inifile.ini').read()

s = s.replace('SourceChannels    = 0',f'SourceChannels = {nch}')
s = s.replace('BandwidthHz       = 0',f'BandwidthHz = {bw}')
s = s.replace('UseFile1Channel   = 0',f'UseFile1Channel = {ch}')
s = s.replace('FFTpoints = 0',f'FFTpoints = {fftpoints}')
print(inttime)
s = s.replace('FFTIntegrationTimeSec = 0',f'FFTIntegrationTimeSec = {inttime}')

f = open('inifile.tmp.ini','w')
f.write(s)

f.close()

# Then modify the parameters related to the observation
# sourceFormat derived

subprocess.call(['swspectrometer','inifile.tmp.ini','/home/observer/vbs_tmp/{}'.format(inFn)])
spec_filename = 'single_channel_swspec.bin'

# visualize the spectra

fsize: float = os.path.getsize(spec_filename)
Nspec: int = np.int(np.floor(0.5*fsize/(fftpoints + 1)))
Nfft: int  = np.int(fftpoints/2+1)
Sps = np.zeros((Nspec,Nfft), dtype=float)

fd = open(spec_filename,'rb')

for ip in np.arange(Nspec):
    read_data = np.fromfile(file=fd, dtype='float32', count=Nfft)
    Sps[ip]   = read_data

#Aspec = np.sum(Sps,axis=0)/Nspec
Aspec = read_data

jf = np.arange(Nfft)
ff = df*jf

# Make a plot
if args.zoomfreq:
    plt.plot(ff[bmin:bmax],np.log10(Aspec[bmin:bmax]))
    plt.ylabel('Spectrum')
    plt.xlabel('Freq [Hz]')
    plt.title('Spectral zoom')
    plt.show()
else:
    plt.plot(ff,np.log10(Aspec))
    plt.ylabel('Spectrum')
    plt.xlabel('Freq [Hz]')
    plt.title('Average spectra')
    plt.show()

# Let's clean our mess
subprocess.call(['rm','./inifile.ini'])
subprocess.call(['rm','./inifile.tmp.ini'])
subprocess.call(['rm','./single_channel_swspec.bin'])
subprocess.call(['rm','./single_channel_runlog.txt'])
subprocess.call(['rm','./single_channel_starttiming.txt'])
subprocess.call(['fusermount','-u','/home/observer/vbs_tmp/'])
