import numpy as np 
from scipy.optimize import curve_fit
from time import sleep
import logging
log = logging.getLogger(__name__) 
log.addHandler(logging.NullHandler()) 
    
def calibration(self, start, stop, points, daq, gaussmeter, delay):
    def linear_func(x,a,b):
        return a*x+b
    voltages = np.linspace(start, stop, points)
    self.fields = []
    for i in voltages:
        self.daq.set_field(i)
        sleep(delay)
        self.result = self.gaussmeter.measure()
        self.fields.append(self.result)
        log.info("Voltage: {}, Field: {}".format(i,self.result))

    popt, pcov = curve_fit(linear_func, voltages, self.fields)
    log.info("Field constant: {}".format(1/popt[0]))
    return 1/popt[0]




def set_calibrated_field(self, value, calibration_constant):
    return value/calibration_constant

