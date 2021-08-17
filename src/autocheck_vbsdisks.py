#!/usr/bin/env python3
import os
import time
import subprocess
####  email notification list
to_addr=['wjhankey@utas.edu.au','guifre.moleracalves@utas.edu.au',"gabor.orosz@utas.edu.au"]
subject="flexbuffyg_disk_state"

### put day number in body of email
d=time.gmtime()
day=int(d[7])
body='On day %s ' %day

### list of unmounted disks
miss_disk=[]

disks_mounted = 0
for disk in range(36):
    stat = os.path.ismount('/mnt/disk{}'.format(disk))
    if stat:
        disks_mounted += 1
    else:
        miss_disk.append(str(disk))
       #### send email to list
if miss_disk:
    disks=','.join(miss_disk)
    body += '... failed to detect flexbuffyg mounted disk numbers  %s ' %disks
    for rec in to_addr:
        cmd='echo %s | mail -s %s  %s' %(body,subject,rec)
        send=subprocess.call(cmd,shell=True)
else:
    body += '... all flexbuffyg disks mounted'
    cmd='echo %s | mail -s %s  wjhankey@utas.edu.au' %(body,subject)
    send=subprocess.call(cmd,shell=True)
