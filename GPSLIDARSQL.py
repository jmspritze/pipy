import serial
import time
import datetime
import os
import sys
import MySQLdb as mdb
import pynmea2


def configGPS():
    pass

def configLIDAR(LIDAR):
    Wo = LIDAR.write("$st\r")
    In = LIDAR.readline()
    print str(In)
    time.sleep(1)

    Wo = LIDAR.write("$ST\n")
    In = LIDAR.readline()
    print In
    time.sleep(1)

    Wo = LIDAR.write("$IS\r\n")
    In = LIDAR.readline()
    print In
    time.sleep(1)
    
def startLIDAR(LIDAR):
    Wo = LIDAR.write("$GO,1\r\n") #10 hz = 0.1
    #Wo = LIDAR.write("$TG,1\r\n") #GPSTrigger

def connectLidar(LIDAR):
    #connect Lidar
    try:
        LIDAR.baudrate = 115200 # set Baud rate to 9600
        LIDAR.bytesize = 8    # Number of data bits = 8
        LIDAR.parity   = 'N'  # No parity
        LIDAR.stopbits = 1    # Number of Stop bits = 1
    except IOError:
        print "LIDAR port error"
        
def getData(GPS,LIDAR):
    resp = ""
   # SQLcur = SQL.cursor()
    resp = GPS.readline()
    if "$GPRMC" in resp:
        msg = pynmea2.parse(resp)
        lat = msg.latitude
        lon = msg.longitude
        Ftime = msg.timestamp
        Fdate = msg.datestamp

        print msg
        #sql = "insert into gps(lat, lon, Fdate, Ftime) values(%s,%s,'%s','%s')" % (lat, lon, Fdate,Ftime)
        #print sql
        #SQLcur.execute(sql)
        #SQL.commit()



#SQL = mdb.connect('localhost', 'root', 'raspberry', 'CDHS');

GPS = serial.Serial("/dev/ttyS0", baudrate=9600)

LIDAR = serial.Serial('/dev/ttyUSB0') 
connectLidar(LIDAR)
configLIDAR(LIDAR)
startLIDAR(LIDAR)

while True:
    getData(GPS,LIDAR)

##finally:
##    if SQLcon:
##        SQLcon.close()
##    GPS.close()
##    LIDAR.close()

