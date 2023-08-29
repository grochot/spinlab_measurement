import time
import serial

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

if ser.isOpen():
    ser.close()
ser.open()

while(True):

    try:
        print("dd")
        ser.write(input().encode())
        out = ''

        while ser.inWaiting() > 0:
            out += str(ser.readline().decode())

        if out:
            print(">>" + out)

    
    except KeyboardInterrupt:
        ser.close()
        print("Finished")
        exit(0)
        
ser.close()
