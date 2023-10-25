from time import sleep
import math
import numpy as np

from hardware.pspl_10070 import PSPL10070
from hardware.stm32_damper import STM32Damper
from hardware.keithley2400 import Keithley2400
from hardware.keithley_2636 import Keithley2636
from hardware.agilent_2912 import Agilent2912
from hardware.lakeshore import Lakeshore

from hardware.dummy_pulsegenerator import DummyPulseGenerator
from hardware.dummy_field import DummyField
from hardware.daq import DAQ
from hardware.dummy_damper import DummyDamper
from hardware.dummy_sourcemeter import DummySourcemeter
from hardware.dummy_gaussmeter import DummyGaussmeter
from hardware.dummy_field import DummyField

from logic.vector import Vector
import logging
log = logging.getLogger(__name__) 
log.addHandler(logging.NullHandler())


class CIMSMode():
    def __init__(self,vector:str,address_gaussmeter:float,sourcemeter_channel:float,address_sourcemeter:float,address_pulsegenerator:str,sourcemeter:str,set_pulsegenerator:str,pulsegenerator_amplitude:float,pulsegenerator_duration:float,pulsegenerator_frequency:float,set_damper:str,address_damper:str) -> None:
         ## parameter initialization 
        self.pulsegenerator_amplitude = pulsegenerator_amplitude
        self.pulsegenerator_duration=pulsegenerator_duration
        self.pulsegenerator_frequency=pulsegenerator_frequency
        self.set_pulsegenerator=set_pulsegenerator
        self.set_damper=set_damper
        self.address_pulsegenerator=address_pulsegenerator
        self.address_damper=address_damper
        self.sourcemeter=sourcemeter
        self.address_sourcemeter=address_sourcemeter
        self.sourcemeter_channel=sourcemeter_channel
        self.address_gaussmeter=address_gaussmeter
        self.vector=vector

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
        match self.set_pulsegenerator: 
            case "(Tektronix) PSPL10070A": 
                self.pulsegenerator_obj = PSPL10070(self.address_pulsegenerator)
            case _:
                self.pulsegenerator_obj = DummyPulseGenerator(self.address_pulsegenerator)

        match self.field:
            case "DAQ": 
                self.field_obj = DAQ()
            case _:
                self.field_obj = DummyField()

        match self.sourcemeter:
            case "Keithley 2400":
                self.sourcemeter_obj = Keithley2400(self.address_sourcemeter)
            case "Keithley 2636": 
                self.sourcemeter_obj = Keithley2636(self.address_sourcemeter)
                self.sourcemeter_obj.set_channel(self.sourcemeter_channel)
            case "Agilent 2912": 
                self.sourcemeter_obj = Agilent2912(self.address_sourcemeter)
            case _: 
                self.sourcemeter_obj = DummySourcemeter(self.address_sourcemeter)


        match self.gaussmeter: 
            case "Lakeshore": 
                self.gaussmeter_obj = Lakeshore(self.address_gaussmeter)
            case _:
                self.gaussmeter_obj = DummyGaussmeter(self.address_gaussmeter)

        match self.set_dammper:
            case "STM32-dumper":
                self.damper_obj=STM32Damper(self.address_damper)

            case _:
                self.damper_obj=DummyDamper(self.address_damper)

        

        #PulseGenerator initialization
        self.pulsegenerator_obj.amplitude(self.pulsegenerator_amplitude)
        self.pulsegenerator_obj.duration(self.pulsegenerator_duration)
        self.pulsegenerator_obj.frequency(self.pulsegenerator_frequency)

        #Damper initialization
        #self.dumper_obj.set_amplitude

        #Field initialization 
        self.field_obj.set_field(self.point_list[0])

        #Lakeshore initalization 
        self.gaussmeter_obj.range(self.gaussmeter_range)
        self.gaussmeter_obj.resolution(self.gaussmeter_resolution)

        #Sourcemeter initialization
        self.sourcemeter_obj.source_mode = self.sourcemeter_source #Set source type 
        if self.sourcemeter_source == "VOLT":
            self.sourcemeter_obj.voltage_range = self.sourcemeter_limit
            self.sourcemeter_obj.compliance_current = self.sourcemeter_compliance
            self.sourcemeter_obj.source_voltage = self.sourcemeter_bias
            self.sourcemeter_obj.enable_source()
            self.sourcemeter_obj.measure_current(nplc =self.sourcemeter_nplc)
        else: 
            self.sourcemeter_obj.current_range = self.sourcemeter_limit
            self.sourcemeter_obj.compliance_voltage = self.sourcemeter_compliance
            self.sourcemeter_obj.source_current = self.sourcemeter_bias
            self.sourcemeter_obj.enable_source()
            self.sourcemeter_obj.measure_voltage(nplc = self.sourcemeter_nplc)



    def operating(self, point):
        self.damper_obj.set_amplitude(point) #tu powinno byc od dampera sterownik
        sleep(self.delay_field)
        if self.gaussmeter == "none":
            self.tmp_field = point
        else: 
            self.tmp_field = self.gaussmeter_obj.measure()
        sleep(self.delay_bias)

        if self.fourpoints:
            if self.sourcemeter_source == "VOLT":
                self.tmp_voltage = self.sourcemeter_bias
                self.tmp_current = self.multimeter_obj.current_dc()
                self.tmp_resistance = self.tmp_voltage/self.tmp_current
            else:
                self.tmp_voltage =  self.multimeter_obj.voltage_dc()
                self.tmp_current =  self.sourcemeter_bias
                self.tmp_resistance = self.tmp_voltage/self.tmp_current
            
        else: 
            if self.sourcemeter_source == "VOLT":
                if self.sourcemeter_bias != 0:
                    self.tmp_voltage = self.sourcemeter_bias
                else: 
                    self.tmp_voltage = 1e-9
                self.tmp_current = self.sourcemeter_obj.current
               
                self.tmp_resistance = self.tmp_voltage/self.tmp_current
            else:
                self.tmp_voltage =  self.sourcemeter_obj.voltage
                if self.sourcemeter_bias != 0:
                    self.tmp_current =  self.sourcemeter_bias
                else: 
                    self.tmp_current = 1e-9
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



