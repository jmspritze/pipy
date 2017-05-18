import serial
import time
import datetime
import os
import sys
import MySQLdb as mdb
import pynmea2
import threading
from threading import Thread


threadLock = threading.Lock()

    
def GPS_Service():
    threadLock.acquire()

    try:
        ser = serial.Serial("/dev/ttyS0", baudrate=9600)
        time.sleep(1)
        print "connected to GPS"
    except:
        print "Error opening GPS serial port."
        sys.exit(1)


    try:
        con = mdb.connect('localhost', 'root', 'raspberry', 'CDHS');
        cur = con.cursor()
        print "connected to db"

    except:
        print "Error connecting to db."
        sys.exit(1)

        
    resp = ""

    try:
        while (ser.inWaiting() > 0):
            resp = ser.readline()
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
                con.close()
                threadLock.release()
    except:
        print sys.exc_info()[0]



def LIDAR_Service():
    threadLock.acquire()
    
    ComPort = serial.Serial('/dev/ttyUSB0') # open COM24
    ComPort.baudrate = 115200 # set Baud rate to 9600
    ComPort.bytesize = 8    # Number of data bits = 8
    ComPort.parity   = 'N'  # No parity
    ComPort.stopbits = 1    # Number of Stop bits = 1

    No = ComPort.write("$st\r")
    line = ComPort.readline()
    print str(line)
    time.sleep(1)

    No1 = ComPort.write("$ST\n")
    line1 = ComPort.readline()
    print line1
    time.sleep(1)

    No2 = ComPort.write("$IS\r\n")
    line2 = ComPort.readline()
    print line2
    time.sleep(1)

    no3 = ComPort.write("$GO,1\r\n") #10 hz = 0.1
    line2 = ComPort.readline()
    print line2
    time.sleep(1)

    no3 = ComPort.write("$GO,1\r\n") #10 hz = 0.1
    line2 = ComPort.readline()
    print line2
    time.sleep(1)

    #No4 = ComPort.write("$TG,1\r\n") #GPSTrigger 
    #line3 = ComPort.readline()
    #print line3

    #no3 = ComPort.write("$GO,0\r\n") #10 hz = 0.1
    while 1 :
       print ComPort.readline()
       threadLock.release()
   
    ComPort.close()     

def MFAM_Service():
    print "HERE"

def main():
    print "starting app"
    GPS_thread = Thread(target = GPS_Service)
    LIDAR_thread = Thread(target = LIDAR_Service)
    GPS_thread.start()
    GPS_thread.join()
    LIDAR_thread.start()
    LIDAR_thread.join()


if __name__ =='__main__':
    main()
