import serial
import time
from datetime import datetime
import os
import sys
#import MySQLdb as mdb
import pynmea2
import mysql.connector as mariadb
import re
# NOTES
'''
'''


class Gps():

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
        #outStr = '$PMTK220,100*2F\r\n'    # 10.0 hz
        #outStr = '$PMTK220,200*2C\r\n'    #  5.0 hz
        outStr = '$PMTK220,1000*1F\r\n'    #  1.0 hz
        #outStr = '$PMTK220,10000*2F\r\n'  #  0,1 hz
        outStr2 = '$PMTK314,0,1,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*2C\r\n'
        #outStr = '$PMTK251,38400*27\r\n'

        self.gpsSer.write(outStr)
        time.sleep(1)
        self.gpsSer.write(outStr)
        time.sleep(1)
        self.gpsSer.write(outStr2)
        time.sleep(1)
        print "GPS configured"

        try:
            mariadb_connection = mariadb.connect(user = 'root', password = 'Wr9144Ht', database = 'CDHS');
            cursor = mariadb_connection.cursor()
            print "GPS connected to db"
        except:
            print "Error connecting to db."
            sys.exit(1)
   
        while self.gpsSer.isOpen():
            try:
                inStr = self.gpsSer.readline()
                if "$GPRMC" in inStr:
                    gpsMsg = pynmea2.parse(inStr)
                    #print gpsMsg
                    #dt = datetime.now()
                    #print gpsMsg.datetime
                    #cursor.execute("INSERT INTO gps(uDATETIME,LAT,LON,GPSTIME) VALUES (%s,%s,%s,%s)",(datetime.now(),gpsMsg.latitude,gpsMsg.longitude,gpsMsg.datetime))
                    cursor.execute("INSERT INTO gps(LAT,LON,GPSTIME) VALUES (%s,%s,%s)",(gpsMsg.latitude,gpsMsg.longitude,gpsMsg.datetime))
                    mariadb_connection.commit()
                    instr = ""
                else:
                     pass
            except:
                print sys.exc_info()[0]
        




def Main():
    print "starting app"
    Gps()
    

                   

if __name__ =='__main__':
    Main()
