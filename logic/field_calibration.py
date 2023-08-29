
from noise_system.hardware.daq import DAQ

class FieldCalibration(): 
    def __init__(self):
        self.daq = DAQ("6124/ao0")

    def set_field(self, value):
        self.calibration_constant = 1
        self.daq.set_voltage(value/self.calibration_constant)


        
field = FieldCalibration()

field.set_field(0.1)
