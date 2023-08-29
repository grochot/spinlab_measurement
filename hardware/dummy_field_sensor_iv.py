from pymeasure.instruments import Instrument
from time import sleep, time
from pymeasure.instruments.validators import truncated_range, strict_discrete_set
import serial
import numpy as np



import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class DummyFieldSensor(Instrument):

    def __init__(self):
        pass
     
    
    def read_field(self):
        x = 0
        y = 0
        z = 0
        #field = np.sqrt(x**2+y**2+z**2)
       
        return x,y,z

