from pymeasure.instruments import Instrument
from time import sleep, time
from pymeasure.instruments.validators import truncated_range, strict_discrete_set
import serial
import numpy as np



import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class FieldSensor(Instrument):

    def __init__(self, resourceName):
        self.resource = resourceName
     
    
    def read_field(self): 
        self.address = self.resource
        ser = serial.Serial(self.address[4:16], 115200, timeout=1)
        ser.write("d".encode())
        ser.readline()
        sleep(0.3)
        ser.write("d".encode())
        ser.readline()
        sleep(0.3)
        ser.write("d".encode())
        ser.readline()
        sleep(0.3)
        try:
            ser.write("d".encode())
            out = ''

            
            out += str(ser.readline().decode())

            if out:
                print(out)
        except:
            pass

        x, y, z = out.split(',')
        x = float(x)
        y = float(y)
        z = float(z)
        #field = np.sqrt(x**2+y**2+z**2)
       
        return x,y,z

