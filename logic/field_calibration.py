
from hardware.daq import DAQ
from hardware.lakeshore import Lakeshore
import numpy as np 
from scipy.optimize import curve_fit
from time import sleep

class FieldCalibration(): 
    def __init__(self, daq_address, gaussmeter_address):
        self.daq = DAQ(daq_address)
        self.gaussmeter = Lakeshore(gaussmeter_address)  
  
    
    
    def calibration(self, start, stop, points):
        def linear_func(x,a,b):
            return a*x+b
        voltages = np.linspace(start, stop, points)
        fields = []
        for i in voltages:
            self.daq.set_field(i)
            sleep(0.5)
            result = self.gaussmeter.measure()
            fields.append(result)


        popt, pcov = curve_fit(linear_func, voltages, fields )
        return popt[0]




    def set_calibrated_field(self, value, calibration_constant):
        return value/calibration_constant



        
# field = FieldCalibration()

# field.set_field(0.1)
