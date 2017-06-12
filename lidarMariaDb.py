import serial
import time
import datetime
import os
import sys
import mysql.connector as mariadb

# NOTES
#
  
class Lidar():
    rangeVal = 0.0
    def __init__(self):
        print 'Lidar started'
        try:
            self.lidarPort = serial.Serial('/dev/ttyUSB0') # open COM24
            self.lidarPort.baudrate = 115200 # set Baud rate to 9600
            self.lidarPort.bytesize = 8    # Number of data bits = 8
            self.lidarPort.parity   = 'N'  # No parity
            self.lidarPort.stopbits = 1    # Number of Stop bits = 1
            print "connected to Lidar"
        except:
            print "Error opening lidar serial port."
            sys.exit(1)

        self.lidarPort.flushInput()
        self.lidarPort.flushOutput()    
        try:
            self.lidarPort.write("$st")
            print (self.lidarPort.readline())
            time.sleep(1)

            self.lidarPort.write("$ST\r\n")
            print (self.lidarPort.readline())
            time.sleep(1)

            self.lidarPort.write("$IS\r\n")
            print (self.lidarPort.readline())
            time.sleep(1)

            self.lidarPort.write("$GO,1,1\r\n") #1 hz 
            print (self.lidarPort.readline())
            time.sleep(1)
            
        except:
            print "Error configuring lidar."
            sys.exit(1)


        try:
            mariadb_connection = mariadb.connect(user = 'root', password = 'Wr9144Ht', database = 'CDHS');
            cursor = mariadb_connection.cursor()
            print "lidar connected to db"
        except:
            print "Error connecting to db."
            sys.exit(1)

        #self.lidarPort.write("$TG,1\r\n") #GPSTrigger 
        #print (self.lidarPort.readline())
            
        #self.lidarPort.write("$GO,0\r\n") #10 hz = 0.1
            
      
        while self.lidarPort.isOpen():
            try:
                inStr = self.lidarPort.readline()
                inRange = inStr.split(",")
                rang = inRange[2]
    
                cursor.execute("INSERT INTO lidar(DISTANCE) VALUES (%s)",(rang,))
                mariadb_connection.commit()
                time.sleep(1)
            except:
                print sys.exc_info()[0]
                self.lidarPort.close()
       
      
def Main():
    print "starting app"
    Lidar()
        

if __name__ =='__main__':
    Main()
