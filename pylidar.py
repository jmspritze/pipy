
import time
import serial           # import the module
ComPort = serial.Serial('/dev/ttyUSB0') # open COM24
ComPort.baudrate = 115200 # set Baud rate to 9600
ComPort.bytesize = 8    # Number of data bits = 8
ComPort.parity   = 'N'  # No parity
ComPort.stopbits = 1    # Number of Stop bits = 1
# Write character 'A' to serial port


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

#No3 = ComPort.write(data) #10 hz = 0.1


#line3 = ComPort.readline(data)
#print line3
#time.sleep(1)

#No4 = ComPort.write("$TG,1\r\n") #GPSTrigger 
#line3 = ComPort.readline()
#print line3

#no3 = ComPort.write("$GO,0\r\n") #10 hz = 0.1


while 1 :
   print ComPort.readline()
   
ComPort.close()     




