from time import sleep
import math
import numpy as np
import logging
from hardware.daq import DAQ 
from hardware.dummy_field import DummyField
from hardware.lakeshore import Lakeshore 
from hardware.dummy_gaussmeter import DummyGaussmeter
from logic.field_calibration import calibration, set_calibrated_field
from logic.sweep_field_to_zero import sweep_field_to_zero

log = logging.getLogger(__name__) 
log.addHandler(logging.NullHandler()) 

class FieldCalibrationMode():
    def __init__(self, set_field, set_gaussmeter, address_daq, address_gaussmeter, vector, delay ) -> None: 
        self.set_field = set_field
        self.set_gaussmeter = set_gaussmeter
        self.address_gaussmeter = address_gaussmeter
        self.address_daq = address_daq
        self.vector = vector
        self.delay = delay
       
        ## parameter initialization 
        
        
        
    def generate_points(self):
        pass


    def initializing(self):
        self.vector = self.vector.split(",")
        if self.set_field == 'none': 
            self.daq = DummyField(self.address_daq)
        else:
            self.daq = DAQ(self.address_daq)
        if self.set_gaussmeter == 'none': 
            self.gaussmeter = DummyGaussmeter(self.address_gaussmeter)
        else:
            self.gaussmeter = Lakeshore(self.address_gaussmeter)

    def operating(self):
        self.start = float(self.vector[0])
        self.stop = float(self.vector[2])
        self.points = int(self.vector[1])

        self.calibration_constant = calibration(self, self.start, self.stop, self.points, self.daq, self.gaussmeter, self.delay)

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
        sweep_field_to_zero(self.stop/self.calibration_constant, self.calibration_constant, int((self.stop/self.calibration_constant)/10), self.daq)



# test = FieldCalibrationMode("ff", "dfd", 'Dev4/ao0', 'GPIB1::12::INSTR',[0,5,1], 2)
# test.initializing()
# test.operating()
# sleep(5)
# test.end()

