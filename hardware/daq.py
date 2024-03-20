from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set
from time import sleep
import nidaqmx
from nidaqmx.stream_readers import AnalogMultiChannelReader

import time
import logging

import numpy as np

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())




class DAQ():
    def __init__(self, adapter):
        self.adapter = adapter
        
   
    def set_field(self, value =1):


        #with nidaqmx.Task() as task:
    
        task1=nidaqmx.Task()
        task2=nidaqmx.Task()

        task1.ao_channels.add_ao_voltage_chan(self.adapter)
        task1.write(value)
        task2.ai_channels.add_ai_voltage_chan("Dev4/ai0")
            #task.read()
        print(task2.read())
        task1.close()
        task2.close()
            #tmp=np.array(1)
            #q=AnalogMultiChannelReader(task)
            #q.read_one_sample(tmp)
            #print(tmp)
            #tmp=task.timing.cfg_samp_clk_timing(256)
           
            
            #AnalogMultiChannelReader.read_one_sample(tmp)
            #task.ao_channels.add_ao_voltage_chan('Dev1/ao4')
            #data = task.write('Dev4/_ao0_vs_aognd')
            #print(tmp)
        return value



    

    def shutdown(self):
        """ Disable output, call parent function"""
        self.set_field(0)





d = DAQ('Dev4/ao0')
d.set_field(1)
#d.shutdown()

# print(d.read_field())


