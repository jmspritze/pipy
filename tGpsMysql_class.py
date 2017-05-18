import serial
import time
import datetime
import os
import sys
import MySQLdb as mdb
import pynmea2
import threading
from threading import Thread

# NOTES
#
# PPS driver for gps
#fix/problems
## LIDAR config method needed
#
## Start MFAM parser
#
## Clean header needed/documentation of classes

threadLock = threading.Lock()

class GpsAsyn(): #threading.Thread
    Lat = 0.0
    Lon = 0.0
    Time = " "
    Date = " "
    inStr = ''

    def __init__(self): #Initialize serial port connection for GPS
        try:
            self.gpsSer = serial.Serial("/dev/ttyS0", baudrate=9600)
            if (self.gpsSer.isOpen() == False):
                self.gpsSer.open()
            time.sleep(0.1)
          #  print "connected to GPS"
        except:
            print "Error opening GPS serial port."
            sys.exit(1)

        self.gpsSer.flushInput()
        self.gpsSer.flushOutput()

        #############################################
        #             GPS INIT COMMANDS             #
        #############################################
        #outStr = '$PMTK605*31\r\n'
        #outStr = '$PMTK447*35\r\n'
        outStr = '$PMTK220,100*2F\r\n'    # 10.0 hz
        #outStr = '$PMTK220,200*2C\r\n'    #  5.0 hz
        #outStr = '$PMTK220,1000*1F\r\n'    #  1.0 hz
        #outStr = '$PMTK220,10000*2F\r\n'  #  0,1 hz
        outStr2 = '$PMTK314,0,1,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*2C\r\n'
        #outStr = '$PMTK251,38400*27\r\n'

        self.gpsSer.write(outStr)
        time.sleep(1)
        self.gpsSer.write(outStr2)
        time.sleep(1)

    def GpsData(self): # Collect Data for GPRMC NMEA Sentences
        dbObj = DbAsyn(self)
        threadLock.acquire()
        try:
            while (self.gpsSer.inWaiting() > 0):
                inStr = self.gpsSer.readline()
                if "$GPRMC" in inStr:
                    gpsMsg = pynmea2.parse(inStr)
                 #   print gpsMsg
                    self.Lat = gpsMsg.latitude
                    self.Lon = gpsMsg.longitude
                    self.Time = gpsMsg.timestamp
                    self.Date = gpsMsg.datestamp            
                    break     
        except:
            print sys.exc_info()[0]
        threadLock.release()
        dbObj.CommitDb()


  
        
class DbAsyn(): #threading.Thread
    
    def __init__(self, GpsObj):
        
        self.DbLat = GpsObj.Lat
        self.DbLon = GpsObj.Lon
        self.DbDate = GpsObj.Date
        self.DbTime = GpsObj.Time
        
        try:
            self.con = mdb.connect('localhost', 'root', 'raspberry', 'CDHS');
            self.cur = self.con.cursor()
          #  print "connected to db"
        except:
            print "Error connecting to db."
            sys.exit(1)

    def CommitDb(self):
        threadLock.acquire()
        GpsSql = "insert into gps(lat, lon, Fdate, Ftime) values(%s,%s,'%s','%s')" % (self.DbLat, self.DbLon, self.DbDate, self.DbTime)
        print GpsSql
        self.cur.execute(GpsSql)
        self.con.commit()
        threadLock.release()
   

class LidarAsyn(threading.Thread):
   
    def __init__(self):
        try:
            LidarPort = serial.Serial('/dev/ttyUSB0') # open COM24
            LidarPort.baudrate = 115200 # set Baud rate to 9600
            LidarPort.bytesize = 8    # Number of data bits = 8
            LidarPort.parity   = 'N'  # No parity
            LidarPort.stopbits = 1    # Number of Stop bits = 1
            print "connected to Lidar"
        except:
            print "Error opening lidar serial port."
            sys.exit(1)
            
        
    def LidarService(self):
        threadLock.acquire()

        No = LidarPort.write("$st\r")
        line = LidarPort.readline()
        print str(line)
        time.sleep(1)

        No1 = LidarPort.write("$ST\n")
        line1 = LidarPort.readline()
        print line1
        time.sleep(1)

        No2 = LidarPort.write("$IS\r\n")
        line2 = LidarPort.readline()
        print line2
        time.sleep(1)

        no3 = LidarPort.write("$GO,1\r\n") #10 hz = 0.1
        line2 = LidarPort.readline()
        print line2
        time.sleep(1)

        no3 = LidarPort.write("$GO,1\r\n") #10 hz = 0.1
        line2 = LidarPort.readline()
        print line2
        time.sleep(1)

        #No4 = LidarPort.write("$TG,1\r\n") #GPSTrigger 
        #line3 = LidarPort.readline()
        #print line3

        #no3 = LidarPort.write("$GO,0\r\n") #10 hz = 0.1
        while 1 :
           print LidarPort.readline()
           threadLock.release()
       
        LidarPort.close()
        
        
class MfamAsyn(threading.Thread):
    def __init__(self):
        print "HERE"

    def MfamService():
        print "HERE"
 
def Main():
    print "starting app"
    gpsObj = GpsAsyn()  
    while True:
        gpsObj.GpsData()

if __name__ =='__main__':
    Main()
