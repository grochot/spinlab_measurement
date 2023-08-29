from pymeasure.instruments import Instrument
from time import sleep, time
from pymeasure.instruments.validators import truncated_range, strict_discrete_set
import serial
import numpy as np
import re


import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class FieldSensorDummy(Instrument):

    def __init__(self, resourceName):
        self.resource = resourceName
     
    
    def read_field(self): 
        return 0,0,0

    def read_field_init(self):
        pass

# test = FieldSensor('COM8')

# test.read_field_init()

# test.read_field()
# test.read_field()
# test.read_field()
# test.read_field()
# test.read_field()
