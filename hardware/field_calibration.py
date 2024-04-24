
from daq import DAQ

class FieldCalibration(): 
    def __init__(self):
        self.daq = DAQ("6124/ao0")

    def set_field(self, value):
        self.calibration_constant = 10 #Oe-V
        self.daq.set_voltage(value/self.calibration_constant)


