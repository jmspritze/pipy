import serial
import time
import datetime
import os
import sys
import MySQLdb as mdb
import pynmea2
import threading
from threading import Thread
from Queue import Queue

# NOTES
#
# PPS driver for gps
#fix/problems
## LIDAR config method needed
#
## Start MFAM parser
#
## Clean header needed/documentation of classes

q = Queue(maxsize=2)

class Gps(threading.Thread):
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
        except:
            print sys.exc_info()[0]
        
        
class Db(threading.Thread):
    
    def __init__(self, GpsObj, LidarObj, MfamObj):
        
        self.DbLat = GpsObj.Lat
        self.DbLon = GpsObj.Lon
        self.DbDate = GpsObj.Date
        self.DbTime = GpsObj.Time
        self.DbrangeVal = LidarObj.rangeVal
        self.DbmagOne = MfamObj.magOne
##        self.DbmagTwo = MfamObj.magTwo
##        self.DbmagX = MfamObj.magX
##        self.DbmagY = MfamObj.magY
##        self.DbmagZ = MfamObj.magZ
        try:
            self.con = mdb.connect('localhost', 'root', 'raspberry', 'CDHS');
            self.cur = self.con.cursor()
          #  print "connected to db"
        except:
            print "Error connecting to db."
            sys.exit(1)

    def dbCommit(self):
        #dbSql = "insert into missionData(lat,lon,Fdate,Ftime,rangeVal,magOne,magTwo,magX,magY,magZ) values(%s,%s,'%s','%s',%s,%s,%s,%s,%s,%s)" % (self.DbLat,self.DbLon,self.DbDate,self.DbTime,self.DbrangeVal,self.magOne,self.magTwo,self.magX,self.magY,self.magZ)
        dbSql = "insert into missionData(lat,lon,Fdate,Ftime,rangeVal,magOne) values(%s,%s,'%s','%s',%s,%s)" % (self.DbLat,self.DbLon,self.DbDate,self.DbTime,self.DbrangeVal,self.DbmagOne)
       
        print dbSql
        self.cur.execute(dbSql)
        self.con.commit()
   

class Lidar(threading.Thread):
    rangeVal = 0.0
    def __init__(self):
        print 'Lidar started'
##        try:
##            LidarPort = serial.Serial('/dev/ttyUSB0') # open COM24
##            LidarPort.baudrate = 115200 # set Baud rate to 9600
##            LidarPort.bytesize = 8    # Number of data bits = 8
##            LidarPort.parity   = 'N'  # No parity
##            LidarPort.stopbits = 1    # Number of Stop bits = 1
##            print "connected to Lidar"
##        except:
##            print "Error opening lidar serial port."
##            sys.exit(1)
            
    def LidarData(self):
        self.rangeVal = 999.0
        return
        
    def LidarInit(self):
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
       
        LidarPort.close()
        
        
class Mfam(threading.Thread):
    magOne = 0.0
    magTwo = 0.0
    magX = 0.0
    magY = 0.0
    magZ = 0.0
    
    def __init__(self):
        print "Starting mfam"

    def mfamData(self):
        self.magOne = 12345.1234
        self.magTwo = 54321.4321
        self.magX = 30.0
        self.magY = 40.0
        self.magZ = 50.0
        return
 
def Main():
    print "starting app"
    gpsObj = Gps()
    lidarObj = Lidar()
    mfamObj = Mfam()
    
    while True:
        gpsObj.GpsData()
        q.put(gpsObj)
        lidarObj.LidarData()
        q.put(lidarObj)
        mfamObj.mfamData()
       # q.put(mfamObj)
        dbObj = Db(q.get(0),q.get(1),mfamObj)
        dbObj.dbCommit()
           
        



if __name__ =='__main__':
    Main()
