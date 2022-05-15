#!/usr/bin/env python3

import serial

from time import sleep

ser = serial.Serial("/dev/ttyS0", 115200)
while True:
	received_data = ser.readline()              #read serial port
	#sleep(1)
	data_left = ser.inWaiting()             #check for remaining byte
	received_data += ser.read(data_left)
	print (received_data.decode())                   #print received data
