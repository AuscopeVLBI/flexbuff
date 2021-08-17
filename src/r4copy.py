#!/usr/bin/env python

###  Author: Warren Hankey 2021
### this version modified to copy r4 weekly (cron)

import subprocess
import os
import time
import sys, getopt
import re
import psycopg2
station='yg'
####  email notification list
to_addr=['wjhankey@utas.edu.au','moblas@midwest.com.au']
#to_addr=['wjhankey@utas.edu.au',]
subject="r4_auto_copy"

try:
    #print("try connect db")
    conn = psycopg2.connect("dbname='experiments' user='observer' host='131.217.63.180' port ='5432'")

except  Exception, e:
    #print("can't connect to postgresql server\n %s" %e)
    pass
else:
    #print("connected to  postgresql db")
    cur=conn.cursor()
    ### get name of r4 just done (started day before)
    sql="""select name from catalog_experiment where name LIKE 'R4%' AND schedate=current_date-INTERVAL '1 DAY';"""
    cur.execute(sql)
    query=cur.fetchone()
    print query
    exp=query[0].lower()
    print exp
    #### has usb been mounted?
    usb=subprocess.call('ls /mnt | grep usb1', shell=True)
    #rusb=usb.wait()
    if usb !=0:
        print("no mnt/usb1")
    else:
        print("usb1 mounted"
    ##### has directory been created?
    dir_cmd='ls /mnt/usb1 | grep %s' %exp
    dir=subprocess.call(dir_cmd, shell=True)
    if dir == 0:
        dogs_body='ready to copy %s mk5 to flexbuffyg'%exp
        pass
    else:
        mk_cmd="mkdir /mnt/usb1/%ske" %exp
        mkdir=subprocess.call(mk_cmd, shell=True)
        if mkdir != 0:
            dogs_body='failed to make directory %ske  on /mnt/usb1' %exp
    ### tell database and warren transfer is 'c', (copying)
        else:
            dogs_body='ready to copy %s mk5 to flexbuffyg'%exp
    cmd='echo %s | mail -s %s  wjhankey@utas.edu.au' %(dogs_body,subject)
    send=subprocess.call(cmd, shell=True)
    sql="""UPDATE catalog_experimentinstance SET extract='c' WHERE experiment_id LIKE %s and station LIKE %s;"""
    ### make exper name alphabet upper case, it also needs to be a tuple for cursor.execute() (even if only one element!)
    Exper=exp.upper()
    try:
        cur.execute(sql,(Exper,station,))
    except Exception, e:
        print("update failed")
    else:
        cur.execute("""COMMIT;""")
        #print("updated %s %s " %(exp,station))
    cur.close()                                
    conn.close()
    ### admin done, time to copy
    with open('%s.copy' %exp, 'a') as log:
        mk5_path="mk5://131.217.61.75/%s_yg*" %exp
        usb_path="file://131.217.61.85/mnt/usb1/%syg/" %exp
        m5copy=subprocess.Popen(["m5copy",  "%s" %mk5_path,  "%s" %usb_path, "--resume"], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        #m5copy=subprocess.Popen(["echo", "%s" %mk5_path,  "%s" %usb_path, "--resume"], stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
        return_code=m5copy.wait()
	if return_code != 0:
	   log.write('%s copy fail' %exp)
        else:
            log.write('%s copy complete\n' %exp)
            #print('success!')
            try:
            #print("try connect db")
                conn = psycopg2.connect("dbname='experiments' user='observer' host='131.217.63.180' port ='5432'")
            except  Exception, e:
    #print("can't connect to postgresql server\n %s" %e)
                pass
            else:
            #print("connected to  postgresql db")
                cur=conn.cursor()
            #### tell db extraction copy is done        
                sql="""UPDATE catalog_experimentinstance SET extract='u' WHERE experiment_id LIKE %s and station LIKE %s;"""
                
                try:
                    cur.execute(sql,(Exper,station,))
                except Exception, e:
                    print("update failed")
                else:
                    cur.execute("""COMMIT;""")
                    #print("updated %s %s " %(exp,station))
                cur.close()                                
                conn.close()
            d=time.gmtime()
            day=int(d[7])
            body='On day %s copy of %s mk5 to to flexbuff completed' %(day, exp)
            for rec in to_addr:
                cmd='echo %s | mail -s %s  %s' %(body,subject,rec)
                send=subprocess.call(cmd, shell=True)
            #cmd='echo %s | mail -s %s  wjhankey@utas.edu.au' %(body,subject)
            log.close()
