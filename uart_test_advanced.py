#!/usr/bin/env python3

import serial
import time
from time import sleep
import json

def read_block(ser):
	buf = ""
	reading = True
	in_block = False
	if ser.in_waiting > 0:
		while reading:
			try:
				tmp = ser.read().decode('ascii')
				if tmp == "":
					return ""
				elif tmp == "<" and not in_block:
					in_block = True
				elif tmp == ">" and in_block:
					reading = False
				elif in_block:
					buf = buf + tmp
			except:
				pass

	return buf

def send_block(ser, block):
	msg = f'<{block}>'.encode('ascii')
	#for c in msg:
	#	ser.write(c)
	#	sleep(0.001)
	ser.write(msg)
	ser.flush()

with serial.Serial("/dev/ttyAML6", 115200, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE, timeout=1) as serial1:
	print('Giving port a moment after opening...')
	sleep(2)
	print('Resetting sensor manager...')
	send_block(serial1, '{"command": "reset"}')
	checkpoint = time.time()
	while True:
		tmp = read_block(serial1)
		if tmp == "Finished Initializing Sensors":
			print('  Sensor manager ready!')
			break
		elif time.time() - checkpoint > 8:
			print(f'  Waiting...')
			send_block(serial1, '{"command": "reset"}')
			serial1.reset_input_buffer()
			checkpoint = time.time()
		sleep(0.1)
	serial1.reset_input_buffer()
	print('Querying Sensors...')
	send_block(serial1, '{"command": "list_sensors"}')
	sensor_list_raw = read_block(serial1)
	#print(f'Received: {sensor_list_raw}')
	sensor_list = json.loads(sensor_list_raw)
	#serial1.reset_input_buffer()
	if sensor_list["report"] == "sensor_list":
		print('  Response:')
		for sensor in sensor_list["sensors"]:
			print(f'    {sensor["name"]}:')
			print(f'      initialized: {sensor["Initialized"]}')
			print(f'      enabled: {sensor["enabled"]}')
			send_block(serial1, '{"command": "list_options", "sensor": "%s"}'%(sensor["name"]))
			opts_raw = read_block(serial1)
			opts = json.loads(opts_raw)
			while not (opts["rep"] == "OPTIONS" and opts["name"] == sensor["name"]):
				opts_raw = read_block(serial1)
				opts = json.loads(opts_raw)
			print(f'      options: {opts["opts"]}')

			if sensor["Initialized"]:
				send_block(serial1, '{"command": "set_parameter", "sensor": "%s", "param": "enabled", "value": "true"}'%(sensor["name"]))
				data_raw = read_block(serial1)
				data = json.loads(data_raw)
				while not (data["rep"] == "DATA" and data["sensor"] == sensor["name"]):
					data_raw = read_block(serial1)
					data = json.loads(data_raw)
				send_block(serial1, '{"command": "set_parameter", "sensor": "%s", "param": "enabled", "value": "false"}'%(sensor["name"]))
				#print(f'  data: {data_raw}')
				#data = json.loads(data_raw)
				print('      data:')
				for key, value in data["data"].items():
					print(f'        {key}: {value}')
			serial1.reset_input_buffer()
	else:
		print(f'Invalid Response: {sensor_list_raw}')

