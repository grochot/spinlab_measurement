from time import sleep
import math

from hardware.keithley2400 import Keithley2400
from hardware.agilent_34410a import Agilent34410A
from hardware.daq import DAQ
from hardware.keisight_e3600a import E3600a
from hardware.keithley_2636 import Keithley2636
from hardware.lakeshore import Lakeshore
from hardware.autostation import AutoStation
from hardware.kriostat import Kriostat
from hardware.switch import Switch
from hardware.agilent_2912 import Agilent2912
from hardware.dummy_sourcemeter import DummySourcemeter
from hardware.dummy_multimeter import DummyMultimeter
from hardware.dummy_gaussmeter import DummyGaussmeter
from hardware.dummy_field import DummyField
from logic.vector import Vector

class ResistanceMode():
    def __init__(self, vector:str, fourpoints:bool,  sourcemeter_bias:float, sourcemeter:str, multimeter:str, gaussmeter:str, field:str, automaticstation:bool, switch: bool, kriostat:bool, rotationstation: bool, address_sourcemeter:str, address_multimeter:str, address_gaussmeter:str, address_switch:str, delay_field:float, delay_lockin:float, delay_bias:float, sourcemeter_source:str, sourcemeter_compliance:float, sourcemter_channel: str, sourcemeter_limit:str, sourcemeter_nplc:float, sourcemeter_average:str, multimeter_function:str, multimeter_resolution:float, multimeter_autorange:bool, multimeter_range:int, multimeter_average:int, field_constant:float, gaussmeter_range:str, gaussmeter_resolution:str ) -> None:   
        ## parameter initialization 
        self.sourcemeter = sourcemeter
        self.multimeter = multimeter
        self.gaussmeter = gaussmeter
        self.field = field
        self.automaticstation = automaticstation
        self.swich = switch
        self.kriostat = kriostat
        self.rotationstation = rotationstation
        self.address_sourcemeter = address_sourcemeter
        self.address_multimeter = address_multimeter 
        self.address_gaussmeter = address_gaussmeter
        self.address_switch = address_switch
        self.delay_field = delay_field
        self.delay_lockin = delay_lockin
        self.delay_bias = delay_bias
        self.sourcemeter_source = sourcemeter_source
        self.sourcemeter_compliance = sourcemeter_compliance
        self.sourcemeter_channel = sourcemter_channel
        self.sourcemeter_limit = sourcemeter_limit
        self.sourcemeter_nplc = sourcemeter_nplc
        self.sourcemeter_bias = sourcemeter_bias
        self.sourcemeter_average = sourcemeter_average 
        self.multimeter_function = multimeter_function
        self.multimeter_resolution = multimeter_resolution
        self.multimeter_autorange = multimeter_autorange
        self.multimeter_range = multimeter_range
        self.multimeter_average = multimeter_average
        self.field_constant = field_constant
        self.gaussmeter_range = gaussmeter_range
        self.gaussmeter_resolution = gaussmeter_resolution
        self.vector = vector
        self.fourpoints = fourpoints
        self.vector_obj = Vector()
        


    def initializing(self):
         #Vector initialization

        self.point_list = self.vector_obj.generate_vector(self.vector)

        # Hardware initialization
        match self.sourcemeter:
            case "Keithley 2400":
                self.sourcemeter_obj = Keithley2400(self.address_sourcemeter)
            case "Keithley 2636": 
                self.sourcemeter_obj = Keithley2636(self.address_sourcemeter)
                self.sourcemeter_obj.set_channel(self.sourcemeter_channel)
            case "Agilent 2912": 
                self.sourcemeter_obj = Agilent2912(self.address_sourcemeter)
            case _: 
                self.sourcemeter_obj = DummySourcemeter()
        
        match self.multimeter:
            case "Agilent 34400": 
                self.multimeter_obj = Agilent34410A(self.address_multimeter)
            case _: 
                self.multimeter_obj = DummyMultimeter()
        
        match self.gaussmeter: 
            case "Lakeshore": 
                self.gaussmeter_obj = Lakeshore(self.address_gaussmeter)
            case _:
                self.gaussmeter_obj = DummyGaussmeter()
        
        match self.field:
            case "DAQ": 
                self.field_obj = DAQ()
            case _:
                self.field_obj = DummyField()

        #Sourcemeter initialization
        self.sourcemeter_obj.source_mode(self.sourcemeter_source) #Set source type 
        if self.sourcemeter_source == "VOLT":
            self.sourcemeter_obj.source_voltage_range(self.sourcemeter_compliance)
            self.sourcemeter_obj.compliance_current(self.sourcemeter_compliance)
            self.sourcemeter_obj.source_voltage = self.sourcemeter_bias
            self.sourcemeter_obj.voltage_nplc(self.sourcemeter_nplc)
            self.sourcemeter_obj.enable_source()
            self.sourcemeter_obj.measure_current()
        else: 
            self.sourcemeter_obj.source_current_range(self.sourcemeter_compliance)
            self.sourcemeter_obj.compliance_voltage(self.sourcemeter_compliance)
            self.sourcemeter_obj.source_current = self.sourcemeter_bias
            self.sourcemeter_obj.current_nplc(self.sourcemeter_nplc)
            self.sourcemeter_obj.enable_source()
            self.sourcemeter_obj.measure_voltage()
        
        #Multimeter initialization 
        self.multimeter_obj.resolution(self.multimeter_resolution)
        self.multimeter_obj.range(self.multimeter_range)
        self.multimeter_obj.autorange(self.multimeter_autorange)
        self.multimeter_obj.function(self.multimeter_function)
        self.multimeter_obj.average(self.multimeter_average)

        #Lakeshore initalization 
        self.gaussmeter_obj.range(self.gaussmeter_range)
        self.gaussmeter_obj.resolution(self.gaussmeter_resolution)
      

        #Field initialization 
        self.field_obj.set_field(self.point_list[0])

        return self.point_list

    
    def operating(self, point):
        self.field_obj.set_field(point)
        sleep(self.delay_field)
        if self.gaussmeter == "none":
            self.tmp_field = point
        else: 
            self.tmp_field = self.gaussmeter.measure()
        sleep(self.delay_bias)

        if self.fourpoints:
            if self.sourcemeter_source == "VOLT":
                self.tmp_voltage = self.sourcemeter_bias
                self.tmp_current = self.multimeter_obj.current_dc
                self.tmp_resistance = self.tmp_voltage/self.tmp_current
            else:
                self.tmp_voltage =  self.multimeter_obj.voltage_dc
                self.tmp_current =  self.sourcemeter_bias
                self.tmp_resistance = self.tmp_voltage/self.tmp_current
            
        else: 
            if self.sourcemeter_source == "VOLT":
                self.tmp_voltage = self.sourcemeter_bias
                self.tmp_current = self.sourcemeter_obj.current
                self.tmp_resistance = self.tmp_voltage/self.tmp_current
            else:
                self.tmp_voltage =  self.sourcemeter_obj.voltage
                self.tmp_current =  self.sourcemeter_bias
                self.tmp_resistance = self.tmp_voltage/self.tmp_current
            
        data = {
            'Voltage (V)':self.tmp_voltage, 
            'Current (A)':self.tmp_current, 
            'Resistance (ohm)': self.tmp_resistance, 
            'Field (Oe)': self.tmp_field, 
            'Frequency (Hz)': math.nan, 
            'X (V)': math.nan, 
            'Y (V)': math.nan, 
            'Phase':math.nan
            }
        
        return data 

    def shutdown(self):
        self.sourcemeter_obj.shutdown()
        self.field_obj.shutdown()
        ResistanceMode.idle()

    def idle(self):
        pass