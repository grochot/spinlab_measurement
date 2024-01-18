from time import sleep
import math
import numpy as np
import logging
from hardware.daq import DAQ

from hardware.lakeshore import Lakeshore

from hardware.sr830 import SR830
from hardware.dummy_lockin import DummyLockin
from hardware.dummy_gaussmeter import DummyGaussmeter
from hardware.dummy_field import DummyField
from logic.vector import Vector
from logic.lockin_parameters import _lockin_timeconstant, _lockin_sensitivity 
log = logging.getLogger(__name__) 
log.addHandler(logging.NullHandler()) 

class HarmonicMode():
    def __init__(self, set_automaticstation:bool, set_lockin:str, set_field:str, set_gaussmeter:str, set_roationstation:bool,address_lockin:str, address_gaussmeter:str, vector:list, delay_field:float, delay_lockin:float,delay_bias:float, lockin_average, lockin_input_coupling,lockin_reference_source,lockin_dynamic_reserve,lockin_input_connection,lockin_sensitivity,lockin_timeconstant,lockin_autophase,lockin_frequency, lockin_harmonic, lockin_sine_amplitude, lockin_channel1, lockin_channel2,set_field_value ,field_constant,gaussmeter_range, gaussmeter_resolution, address_daq:str ) -> None: 
        self.set_automaticstation = set_automaticstation
        self.set_lockin = set_lockin
        self.set_field = set_field
        self.set_field_value = set_field_value
        self.set_gaussmeter = set_gaussmeter
        self.set_roationstation = set_roationstation
        self.address_lockin = address_lockin
        self.address_gaussmeter = address_gaussmeter
        self.vector = vector
        self.delay_field = delay_field
        self.delay_lockin = delay_lockin
        self.delay_bias = delay_bias
        self.lockin_average = lockin_average
        self.lockin_input_coupling = lockin_input_coupling
        self.lockin_reference_source = lockin_reference_source
        self.lockin_dynamic_reserve = lockin_dynamic_reserve
        self.lockin_input_connection = lockin_input_connection
        self.lockin_sensitivity = lockin_sensitivity
        self.lockin_timeconstant = lockin_timeconstant
        self.lockin_autophase = lockin_autophase
        self.lockin_frequency = lockin_frequency
        self.lockin_harmonic = lockin_harmonic
        self.lockin_sine_amplitude = lockin_sine_amplitude
        self.lockin_channel1 = lockin_channel1
        self.lockin_channel2 = lockin_channel2

        self.field_constant = field_constant
        self.gaussmeter_range = gaussmeter_range
        self.gaussmeter_resolution = gaussmeter_resolution  
        self.address_daq = address_daq
        ## parameter initialization 
        
        
        
    def generate_points(self):
        #Vector initialization
        if self.vector != "":
            self.vector_obj = Vector()
            self.point_list = self.vector_obj.generate_vector(self.vector)
        else:
            log.error("Vector is not defined")
            self.point_list = [1]
        return self.point_list


    def initializing(self):
        # Hardware objects initialization
        match self.set_lockin:
            case "SR830":
                self.lockin_obj = SR830(self.address_lockin)
            case "Zurich":
                pass
            case _: 
                self.lockin_obj = DummyLockin()
        
        match self.set_gaussmeter: 
            case "Lakeshore": 
                self.gaussmeter_obj = Lakeshore(self.address_gaussmeter)
            case _:
                self.gaussmeter_obj = DummyGaussmeter(self.address_gaussmeter)
        
        match self.set_field:
            case "DAQ": 
                self.field_obj = DAQ(self.address_daq)
            case _:
                self.field_obj = DummyField()

        match self.set_automaticstation:
            case True: 
                pass
            case _: 
                pass
       
        #Lockin initialization
        self.lockin_obj.frequency = self.lockin_frequency
        if self.lockin_sensitivity == "Auto Gain":
            self.lockin_obj.auto_gain()
        else:
            self.lockin_obj.sensitivity = _lockin_sensitivity(self.lockin_sensitivity)
        self.lockin_obj.time_constant = _lockin_timeconstant(self.lockin_timeconstant)
        self.lockin_obj.harmonic = self.lockin_harmonic
        self.lockin_obj.sine_voltage = self.lockin_sine_amplitude
        self.lockin_obj.channel1 = self.lockin_channel1
        self.lockin_obj.channel2 = self.lockin_channel2
        self.lockin_obj.input_config = self.lockin_input_connection
        self.lockin_obj.input_coupling = self.lockin_input_coupling
        self.lockin_obj.reference_source = self.lockin_reference_source
   

        #Lakeshore initalization 
        self.gaussmeter_obj.range(self.gaussmeter_range)
        self.gaussmeter_obj.resolution(self.gaussmeter_resolution)
      
        #Field initialization 
        self.field_obj.set_field(self.point_list[0])
    
    def operating(self, point):
        #set temporary result list
        self.result_list = []
        #set_field
        self.field_obj.set_field(point)
        sleep(self.delay_field)
        #measure_field
        if self.set_gaussmeter == "none":
            self.tmp_field = point
        else: 
            self.tmp_field = self.gaussmeter_obj.measure()
        sleep(self.delay_bias)

        #measure_lockin 
        for i in range(self.lockin_average):
            self.result = self.lockin_obj.snap("{}".format(self.lockin_channel1), "{}".format(self.lockin_channel2))
            self.result_list.append(self.result)
        
        #calculate average:
        self.result1 = np.average([i[0] for i in self.result_list])
        self.result2 = np.average([i[1] for i in self.result_list])
            
        data = {
            'Voltage (V)': math.nan,
            'Current (A)': math.nan,
            'Resistance (ohm)': self.result1 if self.lockin_channel1 == "R" else (self.result2 if self.lockin_channel2 == "R" else math.nan), 
            'Field (Oe)': self.tmp_field,
            'Frequency (Hz)': math.nan, 
            'X (V)':  self.result1 if self.lockin_channel1 == "X" else (self.result2 if self.lockin_channel2 == "X" else math.nan),   
            'Y (V)':  self.result1 if self.lockin_channel1 == "Y" else (self.result2 if self.lockin_channel2 == "Y" else math.nan), 
            'Phase': self.result1 if self.lockin_channel1 == "Phase" else (self.result2 if self.lockin_channel2 == "Phase" else math.nan),
            'Polar angle (deg)': np.nan,
            'Azimuthal angle (deg)': math.nan
            }
        
        return data 
        

    def end(self):
        HarmonicMode.idle(self)

    def idle(self):
        self.field_obj.set_field(0)