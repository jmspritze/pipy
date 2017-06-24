#! /usr/bin/python
import os
from gps import *
from time import *
import time
import threading
import mysql.connector as mariadb
import re

 
gpsd = None #seting the global variable
lidar = None
 
os.system('clear') #clear the terminal (optional)


class LidarAsyn(threading.Thread): 
    def __init__(self):
        threading.Thread.__init__(self)
        global lidar
        self.distance = 999
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
    
    def run(self):
       global lidar
       try:
           #inStr = self.LidarPort.readline()
           #inRange = inStr.split(',')
           self.distance = 111 #inRange[2]
           #print inRange
       except:
           print sys.exc_info()[0]
           #self.lidarPort.close()

 
class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd #bring it in scope
    gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
    self.current_value = None
    self.running = True #setting the thread running to true
 
  def run(self):
    global gpsd
    while gpsp.running:
      gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer

      
 
if __name__ == '__main__':
  try:
    mariadb_connection = mariadb.connect(user = 'root', password = 'Wr9144Ht', database = 'CHDS');
    cursor = mariadb_connection.cursor()
    print "GPS connected to db"
  except:
    print "Error connecting to db."
    sys.exit(1)
    
  gpsp = GpsPoller() # create the thread
  lidar = LidarAsyn()
  
  try:
    gpsp.start() # start it up
    lidar.start() 
    while True:
      print lidar.distance
      os.system('clear')
      cursor.execute("INSERT INTO gps(LAT,LON,GPSTIME) VALUES (%s,%s,%s)",(gpsd.fix.latitude,gpsd.fix.longitude,gpsd.utc))
      mariadb_connection.commit()

##      print 'time utc    ' , gpsd.utc,' + ', gpsd.fix.time 
  except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print "\nKilling Thread..."
    gpsp.running = False
    gpsp.join() # wait for the thread to finish what it's doing
  print "Done.\nExiting."
