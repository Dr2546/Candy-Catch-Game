import time 
import serial

ser = serial.Serial('COM7', 115200, timeout=0.050)
count = 0

while 1:
    s = input("input: ")
    ser.write(s.encode())
    time.sleep(1)