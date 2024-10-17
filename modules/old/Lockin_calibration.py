import numpy as np
from time import sleep
class LockinCalibration:
    def __init__(self, lockin, ac_frequency, dc_field, coil_const):
        self.lockin = lockin
        self.ac_frequency = ac_frequency
        self.dc_field = dc_field
        self.coil_const = coil_const
     
    
    def calibrate(self):
        self.lockin.set_dc_field(0)
        sleep(0.1)
        self.lockin.set_ac_field(1,self.ac_frequency)
        sleep(3)
        self.lockin.set_lockin_freq(self.ac_frequency)
        sleep(10)
        self.v_ac =((self.lockin.lockin_measure_R(0,6)))
        print(self.v_ac)
        self.hac = ((self.v_ac)/50)*self.coil_const
        print(self.hac)
        self.calib_ac = self.hac/(1)
        print(self.calib_ac)
        return self.calib_ac
        
        
        
        
    

