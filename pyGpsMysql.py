import serial
import time
import datetime
import os
import sys
import MySQLdb as mdb
import pynmea2

try:
    serial = serial.Serial("/dev/ttyS0", baudrate=9600)
    time.sleep(1)
    con = mdb.connect('localhost', 'root', 'raspberry', 'CDHS');
    cur = con.cursor()
    print "connected to db"

except:
    print "Error opening serial port."
    sys.exit(1)

resp = ""

try:
    while True:
       while (serial.inWaiting() > 0):
           resp = serial.readline()
           if "$GPRMC" in resp:
               data = resp.split(',')
               if data[2] == 'A':
                   dom = (data[9][0:2])
                   month = (data[9][2:4])
                   year = int(data[9][4:6]) + 2000
                   hour = data[1][0:2]
                   minute = data[1][2:4]
                   second = data[1][4:6]
                   north = data[3]
                   west = data[5] 
                   northbase = float(north[0:2])
                   northfloat = north[2:9]
                   northdiv = float(northfloat)/60
                   lat = northbase +  northdiv
                   westbase = float(west[0:3])
                   westfloat = west[3:10]
                   westdiv = float(westfloat)/60
                   lon = westbase + westdiv
                   DM = str(year)+str(month)+str(dom)
                   print DM
                   Fdate = time.strptime(DM,"%Y-%m-%d")
                   
                   #sql = "insert into gps(lat, lon, Fdate) values(%s, %s ,%s)" % (lat, lon, Fdate)
                   #print sql
                   #cur.execute(sql)
                   #con.commit()

except:
    print sys.exc_info()[0]

finally:
    if con:
        con.close()
    serial.close()

