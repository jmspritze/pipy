#! /usr/bin/python
import os
from gps import *
from time import *
import time
import threading
import mysql.connector as mariadb
import re
import serial
import Queue
import pynmea2
import socket
import sys


queue = Queue.Queue(1000)
dist = 0.0

BUFF = 1024
HOST = '10.0.0.10'
PORT = 10000


def serial_read(s):
    while True:
        line = s.readline()
        queue.put(line)


def handler(clientsock,addr):
    while True:
        data = clientsock.recv(BUFF)
        print 'data:' + repr(data)
        queue.put(data)
        if not data:
            break
       # clientsock.close()
        
        
if __name__ == '__main__':
    
    # Connect to DB
    try:
        mariadb_connection = mariadb.connect(user = 'root', password = 'Wr9144Ht', database = 'CHDS');
        cursor = mariadb_connection.cursor()
        print "GPS connected to db"
    except:
        print "Error connecting to db."
        sys.exit(1)
        
    # Connect to Lidar
    try:
        lidarPort = serial.Serial('/dev/ttyUSB0') # open COM24
        lidarPort.baudrate = 115200 # set Baud rate to 9600
        lidarPort.bytesize = 8    # Number of data bits = 8
        lidarPort.parity   = 'N'  # No parity
        lidarPort.stopbits = 1    # Number of Stop bits = 1
        print "connected to Lidar"
    except:
        print "Error opening lidar serial port."
        sys.exit(1)

    # Connect to GPS
    try:
        gpsPort = serial.Serial("/dev/ttyS0", baudrate=9600)
        if (gpsPort.isOpen() == False):
            gpsPort.open()
            time.sleep(0.1)
            print "connected to GPS"
    except:
        print "Error opening GPS serial port."
        sys.exit(1)
        
    # Config gps 
    #outStr = '$PMTK605*31\r\n'
    #outStr = '$PMTK447*35\r\n'
    #outStr = '$PMTK220,100*2F\r\n'    # 10.0 hz
    #outStr = '$PMTK220,200*2C\r\n'    #  5.0 hz
    outStr = '$PMTK220,1000*1F\r\n'    #  1.0 hz
    #outStr = '$PMTK220,10000*2F\r\n'  #  0,1 hz
    outStr2 = '$PMTK314,0,1,0,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*2C\r\n'
    #outStr = '$PMTK251,38400*27\r\n'

    gpsPort.write(outStr)
    time.sleep(1)
    gpsPort.write(outStr)
    time.sleep(1)
    gpsPort.write(outStr2)
    time.sleep(1)
    print "GPS configured"

# Connect to TCP Port
ADDR = (HOST, PORT)
serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversock.bind(ADDR)
serversock.listen(5)        
clientsock, addr = serversock.accept()
sleep(1)

thread1 = threading.Thread(target=serial_read, args=(lidarPort,),).start()
thread2 = threading.Thread(target=serial_read, args=(gpsPort,),).start()
thread3 = threading.Thread(target=handler, args=(clientsock, addr,),).start()

while True:
    line = queue.get(True,1)
    if "$GPRMC" in line:
        gpsMsg = pynmea2.parse(line)
        cursor.execute("INSERT INTO gpslid(LAT,LON,GPSTIME,DIST) VALUES (%s,%s,%s,%s)",(gpsMsg.latitude,gpsMsg.longitude,gpsMsg.datetime,dist))   
        mariadb_connection.commit()
    elif "$DM" in line:
        inRange = line.split(',')
        dist = inRange[2]
    else:
        print line
           
        
                    
                    
