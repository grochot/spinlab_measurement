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
class LockinFrequency():
    def __init__(self, server=""):
        self.lockin = Zurich(server)

    def init(self, input_type=0, differential=False):
        self.lockin.setadc(0,input_type) # 0 - voltage, 1 - current
        self.lockin.siginfloat(0,1)
        self.lockin.oscillatorfreq(0,0)
        self.lockin.siginimp50(0,0)
        self.lockin.sigindiff(0,differential)
        self.lockin.settimeconst(0, 0.3)
        self.lockin.setorder(0, 2)
        self.lockin.setharmonic(0, 1)
        self.lockin.outputon(0,0)
        self.lockin.siginrange(0,10)
        self.lockin.aux_set_manual(0)
        self.lockin.aux_set_manual(1)
        self.lockin.enabledemod(0,1)
        self.lockin.auxout(0,0)
        self.lockin.auxout(1,0)
    

   
    def set_constant_field(self, value=0):
        self.lockin.auxout(0,value)
        

    def set_constant_vbias(self, value=0):
        self.lockin.auxout(1,value/1000)
        

    def set_lockin_freq(self,freq):
        self.lockin.oscillatorfreq(0, freq)

    def lockin_measure_R(self,demod, averaging_rate):
        results = []
        avg = 0
        for samp in range(averaging_rate):
           sample = self.lockin.getsample(demod)
           print(sample)
           avg += np.sqrt(sample['x'][0]**2+sample['y'][0]**2)
        results = avg/averaging_rate
        return results
    
    def lockin_measure_phase(self,demod, averaging_rate):
        results = []
        avg = 0
        for samp in range(averaging_rate):
           sample = self.lockin.getsample(demod)
           print(sample)
           avg += np.arctan(sample['y'][0]/sample['x'][0])
        results = avg/averaging_rate
        return results

    def shutdown(self):
        self.lockin.auxout(1,0)
        self.lockin.auxout(0,0)


# # ########################### Test ###########
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
# from matplotlib import style
# # style.use('fivethirtyeight')
# # fig = plt.figure()
# # ax1 = fig.add_subplot(1,1,1)
# loc = LockinFrequency()

# loc.init()

# start = 0 
# stop = 0
# no_points = 20

# vector_to = np.linspace(start, stop, no_points)

# for k in vector_to: 
#     onstant_vbias(4)
#     sleep(1)
#     loc.set_lockin_freq(k)
#     sleep(1)
#     y = loc.lockin_measure_point(0,10)
#     x = k
#     plt.scatter(x, y, color = 'red', marker = 'x')
#     plt.title("Real Time plot")
#     plt.xlabel("x")
#     plt.pause(0.05)
# plt.show()