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
               msg = pynmea2.parse(resp)
               lat = msg.latitude
               lon = msg.longitude
               Ftime = msg.timestamp
               Fdate = msg.datestamp
               sql = "insert into gps(lat, lon, Fdate, Ftime) values(%s,%s,'%s','%s')" % (lat, lon, Fdate,Ftime)
               print sql
               cur.execute(sql)
               con.commit()

except:
    print sys.exc_info()[0]

finally:
    if con:
        con.close()
    serial.close()

