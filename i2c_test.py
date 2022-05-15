#!/usr/bin/env python3

#import smbus
import board
import busio
#import adafruit_ltr390

#i2c = busio.I2C(board.SCL, board.SDA)
#ltr = adafruit_ltr390.LTR390(i2c)

#bus = smbus.SMBus(0)
#address = 0x53

i2c = busio.I2C(board.SCL, board.SDA)

print("Locking...")
while not i2c.try_lock():
	pass
print("Locked.")

print("Querying...")
i2c.writeto(0x39, bytes([0x11]), stop=False)
result = bytearray(2)
print("Reading...")
i2c.readfrom_into(0x39, result)
print("Read!")
print(result)

print("Unlocking...")
i2c.unlock()
print("Complete!")
