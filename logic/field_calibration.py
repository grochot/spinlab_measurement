import numpy as np 
from scipy.stats import linregress
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
        print(type(self.result))
        if type(self.result) != int and type(self.result) != float:
            self.result = 0
        self.fields.append(self.result)
        log.info("Voltage: {}, Field: {}".format(i,self.result))

    # popt, pcov = curve_fit(linear_func, voltages, self.fields)
    slope, intercept, r, p, std_err = linregress(voltages, self.fields)
    log.info("Field constant: {}".format(1/slope))
    return 1/slope




def set_calibrated_field(self, value, calibration_constant):
    return value/calibration_constant

