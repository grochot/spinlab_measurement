import sys
sys.path.append('..')

from hardware.zurich import Zurich
import sys
sys.path.append('.')
from hardware.hmc8043 import HMC8043
# from hardware.picoscope4626 import PicoScope
from hardware.field_sensor_noise_new import FieldSensor 
from hardware.dummy_field_sensor_iv import DummyFieldSensor
from hardware.zurich import Zurich
from logic.fit_parameters_to_file import fit_parameters_to_file, fit_parameters_from_file
from logic.vbiascalibration import vbiascalibration, calculationbias, func, linear_func
from time import sleep
import numpy as np
from time import sleep
import numpy as np
class LockinTime():
    def __init__(self, server=""):
        self.lockin = Zurich(server)

    
    def init_scope(self, av:int = 1, input_sel: int = 1, rate: float = 0, length:float = 16348 ):
        self.lockin.scope_init(av, input_sel, rate, length)
        
    def init_lockin(self, input_type = 0, differential =False):                  
        self.lockin.oscillatorfreq(0,0) 
        self.lockin.oscillatorfreq(1,0)
        self.lockin.siginscaling(0,1)
        self.lockin.siginfloat(0,1)
        self.lockin.siginimp50(0,0)
        self.lockin.sigindiff(0,differential)
        self.lockin.setosc(0,0)
        self.lockin.setosc(1,1)
        self.lockin.setadc(0,input_type) # 0 - voltage, 1 - current
        self.lockin.settimeconst(0, 0.3)
        self.lockin.setorder(0, 2)
        self.lockin.setharmonic(0, 1)
        self.lockin.setharmonic(1, 1)
        self.lockin.outputamplitude(0,0)
        self.lockin.enableoutput(1,1)
        self.lockin.outputoffset(0,0)
        self.lockin.outputon(0,1)
        self.lockin.siginrange(0,10)
        self.lockin.outputrange(0,10)
        self.lockin.enabledemod(0,1)
        self.lockin.aux_set_manual(1)
        self.lockin.auxout(1,0)
         

   
    def get_wave(self):
        value = self.lockin.get_wave()
        time = self.lockin.to_timestamp(value)

        return time, value[0]['wave'][0]

    def set_ac_field(self, value=0, freq=1): # TO DO
        self.lockin.oscillatorfreq(1,freq)
        self.lockin.outputamplitude(1,value)
       
    def set_dc_field(self, value=0):
        self.lockin.outputoffset(0,value)
      
    def lockin_measure_R(self,demod, averaging_rate):
        results = []
        avg = 0
        for samp in range(averaging_rate):
           sample = self.lockin.getsample(demod)
           avg += np.sqrt(sample['x'][0]**2+sample['y'][0]**2)
        results = avg/averaging_rate
        return results
    
    def set_constant_vbias(self, value=0):
         self.lockin.auxout(1,value/1000)
    
    def set_lockin_freq(self,freq):
        self.lockin.oscillatorfreq(0, freq)


    def shutdown(self):
        self.lockin.auxout(1,0)
        self.lockin.outputamplitude(0,0)
        self.lockin.outputoffset(0,0)    
        self.lockin.outputon(0,0)
    
    def set_field(self, value_dc=0, value_ac=0, freq=1, calib_dc=1, calib_ac = 1):
        self.dc_value = (value_dc*50)/calib_dc
        self.set_dc_field(self.dc_value)
        self.ac_value = (value_ac*50)/calib_ac
        self.set_ac_field(self.ac_value, freq)
        
# ########################### Test ###########################3
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
# from matplotlib import style
# style.use('fivethirtyeight')
# fig = plt.figure()
# ax1 = fig.add_subplot(1,1,1)
# loc = LockinTime('192.168.66.202')

# loc.init(1,1,0,16348)

# data = loc.get_wave()

# import matplotlib.pyplot as plt
# plt.plot(data[0], data[1])
# plt.show()


########################### Test ###########
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
# from matplotlib import style
# style.use('fivethirtyeight')
# fig = plt.figure()
# ax1 = fig.add_subplot(1,1,1)
# loc = LockinTime("192.168.66.202")

# loc.init_lockin(1)
# loc.init_scope(1,1,9,1000)




# loc.set_constant_vbias(50)

# y = loc.get_wave()
# plt.plot(y[0], y[1], "ro-")
# plt.title("Real Time plot")
# plt.xlabel("x")

    
# plt.show()

   
  
    


  


    