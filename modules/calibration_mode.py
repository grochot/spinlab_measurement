from time import sleep
import math
import numpy as np
import logging
from hardware.daq import DAQ

from hardware.lakeshore import Lakeshore


from hardware.dummy_gaussmeter import DummyGaussmeter
from hardware.dummy_field import DummyField
from logic.vector import Vector
from logic.field_calibration import FieldCalibration

log = logging.getLogger(__name__) 
log.addHandler(logging.NullHandler()) 

class FieldCalibrationMode():
    def __init__(self, set_field, set_gaussmeter, address_daq, address_gaussmeter, vector ) -> None: 
        self.set_field = set_field
        self.set_gaussmeter = set_gaussmeter
        self.address_gaussmeter = address_gaussmeter
        self.address_daq = address_daq
        self.vector = vector
       
        ## parameter initialization 
        
        
        
    def generate_points(self):
        pass


    def initializing(self):
        self.calibration = FieldCalibration(self.address_daq, self.address_gaussmeter)

    def operating(self):
        self.start = self.vector[0]
        self.stop = self.vector[2]
        self.points = self.vector[1]

        self.calibration_constant = self.calibration.calibration(self.start, self.stop, self.points)

        data = {
            'Voltage (V)': math.nan,
            'Current (A)': math.nan,
            'Resistance (ohm)': math.nan,
            'Field (Oe)': math.nan,
            'Frequency (Hz)': math.nan,
            'X (V)':  math.nan,
            'Y (V)':  math.nan,
            'Phase': math.nan,
            'Polar angle (deg)': math.nan,
            'Azimuthal angle (deg)': math.nan
            }
        
        return data, self.calibration_constant
        

    def end(self):
        FieldCalibrationMode.idle(self)

    def idle(self):
        self.calibration.set_calibrated_field(0, self.calibration_constant )