#biblioteki
from time import sleep
import math
import numpy as np
import logging
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
from hardware.tektronix_10070a import Tektronix10070a
from hardware.dummy_sourcemeter import DummySourcemeter
from hardware.dummy_multimeter import DummyMultimeter
from hardware.dummy_gaussmeter import DummyGaussmeter
from hardware.dummy_pulsegenerator import DummyPulsegenerator
from hardware.dummy_field import DummyField
from hardware.dummy_relay import DummyRelay
from hardware.rotation_stage import RotationStage
from hardware.rotation_stage_dummy import RotationStageDummy
from logic.vector import Vector
from logic.sweep_field_to_zero import sweep_field_to_zero 
from logic.sweep_field_to_value import sweep_field_to_value
log = logging.getLogger(__name__) 
log.addHandler(logging.NullHandler()) 

class CIMSMode():
    def __init__(self, vector:str, mode_cims_relays:bool,  sourcemeter_bias:float, sourcemeter:str, multimeter:str,pulsegenerator:str, gaussmeter:str, field:str, automaticstation:bool, switch: bool, kriostat:bool, rotationstation: bool,return_the_rotationstation:bool, address_sourcemeter:str, address_multimeter:str,address_pulsegenerator:str, address_gaussmeter:str, address_switch:str, delay_field:float, delay_measurement:float, delay_bias:float, sourcemeter_source:str, sourcemeter_compliance:float, sourcemter_channel: str, sourcemeter_limit:str, sourcemeter_nplc:float, sourcemeter_average:str, multimeter_function:str, multimeter_resolution:float, multimeter_autorange:bool, multimeter_range:int, multimeter_average:int, field_constant:float, gaussmeter_range:str, gaussmeter_resolution:str, multimeter_nplc:str, address_daq:str, field_step:float, rotationstation_port:str, constant_field_value:float, rotation_axis:str, rotation_polar_constant:float, rotation_azimuth_constant:float,pulsegenerator_duration,pulsegenerator_offset,pulsegenerator_pulsetype,pulsegenerator_channel,set_relay,address_relay,pulsegenerator_compliance,pulsegenerator_source_range,field_bias_value) -> None:
    
        ## parameter initialization
        self.sourcemeter = sourcemeter
        #self.multimeter = multimeter
        self.pulsegenerator=pulsegenerator
        self.gaussmeter = gaussmeter
        self.field = field
        self.automaticstation = automaticstation
        #self.swich = switch
        #self.kriostat = kriostat
        self.rotationstation = rotationstation
        self.return_the_rotationstation=return_the_rotationstation
        self.address_sourcemeter = address_sourcemeter
        #self.address_multimeter = address_multimeter
        self.address_pulsegenerator=address_pulsegenerator
        self.address_gaussmeter = address_gaussmeter
        self.address_switch = address_switch
        self.delay_field = delay_field
        self.delay_measurement = delay_measurement
        self.delay_bias = delay_bias
        self.sourcemeter_source = sourcemeter_source
        self.sourcemeter_compliance = sourcemeter_compliance
        self.sourcemeter_channel = sourcemter_channel
        self.sourcemeter_limit = sourcemeter_limit
        self.sourcemeter_nplc = sourcemeter_nplc
        self.sourcemeter_bias = sourcemeter_bias
        self.sourcemeter_average = sourcemeter_average 
        #self.multimeter_function = multimeter_function
        #self.multimeter_resolution = multimeter_resolution
        #self.multimeter_autorange = multimeter_autorange
        #self.multimeter_range = multimeter_range
        #self.multimeter_average = multimeter_average
        #self.multimeter_nplc = multimeter_nplc
        self.field_constant = field_constant
        self.gaussmeter_range = gaussmeter_range
        self.gaussmeter_resolution = gaussmeter_resolution
        self.vector = vector
        self.mode_cims_relays = mode_cims_relays
        self.address_daq = address_daq
        self.field_step = field_step
        self.rotationstation_port = rotationstation_port
        self.constant_field_value = constant_field_value
        self.rotation_axis = rotation_axis
        self.rotation_polar_constant = rotation_polar_constant
        self.rotation_azimuth_constant = rotation_azimuth_constant

        self.pulsegenerator_duration=pulsegenerator_duration
        self.pulsegenerator_offset=pulsegenerator_offset
        self.pulsegenerator_pulsetype=pulsegenerator_pulsetype
        self.pulsegenerator_channel=pulsegenerator_channel
        self.pulsegenerator_compliance=pulsegenerator_compliance
        self.pulsegenerator_source_range=pulsegenerator_source_range

        self.set_relay=set_relay
        self.address_relay=address_relay

        self.field_bias_value=field_bias_value

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
        match self.sourcemeter:
            case "Keithley 2400":
                self.sourcemeter_obj = Keithley2400(self.address_sourcemeter)
                self.sourcemeter_obj.config_average(self.sourcemeter_average)
            case "Keithley 2636":
                if self.sourcemeter_channel=="Channel A":
                    self.sourcemeter_obj = Keithley2636(self.address_sourcemeter).ChA
                else:
                    self.sourcemeter_obj = Keithley2636(self.address_sourcemeter).ChB
                #self.sourcemeter_obj.set_channel(self.sourcemeter_channel)
               
            case "Agilent 2912":
                if self.sourcemeter_channel=="Channel A":
                    self.sourcemeter_obj = Agilent2912(self.address_sourcemeter).ChA
                else:
                    self.sourcemeter_obj = Agilent2912(self.address_sourcemeter).ChB
                self.sourcemeter_obj.func_shape="DC"
            case _: 
                self.sourcemeter_obj = DummySourcemeter(self.address_sourcemeter)
                log.warning('Used dummy Sourcemeter.')

        match self.pulsegenerator:
            case "Tektronix 10,070A":
                self.pulsegenerator_obj=Tektronix10070a(self.address_pulsegenerator)
                self.pulsegenerator_obj.trigger_source="GPIB"
            case "Agilent 2912":
                if self.pulsegenerator_channel=="Channel A":
                    self.pulsegenerator_obj = Agilent2912(self.address_pulsegenerator).ChA
                else:
                    self.pulsegenerator_obj = Agilent2912(self.address_pulsegenerator).ChB

                self.pulsegenerator_obj.source_mode=self.pulsegenerator_pulsetype
                self.pulsegenerator_obj.func_shape="PULSE"
                self.pulsegenerator_obj.trigger_source="BUS"
                self.pulsegenerator_obj.trigger_bypass="ONCE"
                

            case "Keithley 2636":
                if self.pulsegenerator_channel=="Channel A":
                    self.pulsegenerator_obj=Keithley2636(self.address_pulsegenerator).ChA
                else:
                    self.pulsegenerator_obj=Keithley2636(self.address_pulsegenerator).ChB
                
                self.pulsegenerator_obj.single_pulse_prepare()
            case _:
                pass
                self.pulsegenerator_obj = DummyPulsegenerator(self.address_pulsegenerator)
                log.warning('Used dummy Pulsegemerator.')
                
        
        match self.gaussmeter: 
            case "Lakeshore": 
                self.gaussmeter_obj = Lakeshore(self.address_gaussmeter)
            case _:
                self.gaussmeter_obj = DummyGaussmeter(self.address_gaussmeter)
                log.warning('Used dummy Gaussmeter.')
        
        match self.field:
            case "DAQ": 
                self.field_obj = DAQ(self.address_daq)
            case _:
                self.field_obj = DummyField(self.address_daq)
                log.warning('Used dummy DAQ.')

        
        match self.set_relay:
            case "THIS_DEVICE":
                pass
                log.warning("Used THIS_DEVICE")
            case _:
                self.relay_obj = DummyRelay(self.address_daq)
                log.warning('Used dummy relay.')              
        #Rotation_station object initialization
        if self.rotationstation: 
            try:
                self.rotationstation_obj = RotationStage(self.rotationstation_port)
                match self.rotation_axis:
                    case "Polar": 
                        self.rotationstation_obj.goToAzimuth(self.rotation_azimuth_constant)
                    case "Azimuthal": 
                        self.rotationstation_obj.goToPolar(self.rotation_polar_constant)
            except:
                log.error("Rotation station is not initialized")
                self.rotationstation_obj = RotationStageDummy(self.rotationstation_port)

        #Sourcemeter initialization
        self.sourcemeter_obj.source_mode = self.sourcemeter_source #Set source type 
        if self.sourcemeter_source == "VOLT":
            self.sourcemeter_obj.current_range = self.sourcemeter_limit
            self.sourcemeter_obj.compliance_current = self.sourcemeter_compliance
            self.sourcemeter_obj.source_voltage = self.sourcemeter_bias
            if self.mode_cims_relays:
                self.sourcemeter_obj.disable_source()
            else:
                self.sourcemeter_obj.enable_source()
            self.sourcemeter_obj.measure_current(self.sourcemeter_nplc, self.sourcemeter_limit)
        else: 
            self.sourcemeter_obj.voltage_range = self.sourcemeter_limit
            self.sourcemeter_obj.compliance_voltage = self.sourcemeter_compliance
            self.sourcemeter_obj.source_current = self.sourcemeter_bias
            if self.mode_cims_relays:
                self.sourcemeter_obj.disable_source()
            else:
                self.sourcemeter_obj.enable_source()
            self.sourcemeter_obj.measure_voltage(self.sourcemeter_nplc, self.sourcemeter_limit)
        

        #Lakeshore initalization 
        self.gaussmeter_obj.range(self.gaussmeter_range)
        self.gaussmeter_obj.resolution(self.gaussmeter_resolution)
      

        #Field initialization 
        if self.rotationstation:
            sweep_field_to_value(0, self.constant_field_value, self.field_constant, self.field_step, self.field_obj)
        else:
            sweep_field_to_value(0, self.point_list[0], self.field_constant, self.field_step, self.field_obj)

        self.actual_set_field = self.field_obj.set_field(self.field_bias_value*self.field_constant)

        #pulsegenerator initialization
        self.pulsegenerator_obj.duration=self.pulsegenerator_duration
        self.pulsegenerator_obj.source_range=(self.pulsegenerator_pulsetype,self.pulsegenerator_source_range)
        self.pulsegenerator_obj.offset=(self.pulsegenerator_pulsetype,self.pulsegenerator_offset)
        if self.pulsegenerator_pulsetype == "VOLT":
            self.pulsegenerator_obj.compliance_current=self.pulsegenerator_compliance
        else:
            self.pulsegenerator_obj.compliance_voltage=self.pulsegenerator_compliance
        

            
        


    def operating(self, point):
        if self.rotationstation:
            match self.rotation_axis:
                case "Polar":
                    self.rotationstation_obj.goToPolar(point)
                    self.polar_angle = point
                    self.azimuthal_angle = self.rotation_azimuth_constant
                   
                case "Azimuthal":
                    self.rotationstation_obj.goToAzimuth(point)
                    self.polar_angle = self.rotation_polar_constant
                    self.azimuthal_angle = point
                   

        else:
            pass
            


        #measure field
        if self.gaussmeter == "none":
            self.tmp_field = point
        else: 
            self.tmp_field = self.gaussmeter_obj.measure()
        sleep(self.delay_bias)



        

        sleep(self.delay_measurement)
        #----Give pulse-----------------------------------------------------
        self.pulsegenerator_obj.amplitude=[(self.pulsegenerator_pulsetype,point),point][self.pulsegenerator=="Tektronix 10,070A"]
        self.pulsegenerator_obj.enable_source()
        self.pulsegenerator_obj.init()
        self.pulsegenerator_obj.trigger()

        
        #-------------------------------------------------------------------

        #wyłączam output generatora
        if self.mode_cims_relays:
            self.pulsegenerator_obj.disable_source()

        sleep(self.delay_measurement)
        #turn on sourcemeter inputs
        if self.mode_cims_relays:
            self.sourcemeter_obj.enable_source()

        #Measure voltage/current/resistance
        if self.sourcemeter_source == "VOLT":
            if self.sourcemeter_bias != 0:
                self.tmp_voltage = self.sourcemeter_bias
            else: 
                self.tmp_voltage = 1e-9
            self.tmp_current = self.sourcemeter_obj.current
            if type(self.tmp_current) == list:
                self.tmp_current =np.average(self.tmp_current)
            print(self.tmp_current)
            self.tmp_resistance = self.tmp_voltage/self.tmp_current
        else:
            self.tmp_voltage =  self.sourcemeter_obj.voltage
            if type(self.tmp_voltage) == list:
                self.tmp_voltage =np.average(self.tmp_voltage)
            print(self.tmp_voltage)
            if self.sourcemeter_bias != 0:
                self.tmp_current =  self.sourcemeter_bias
            else: 
                self.tmp_current = 1e-9
            self.tmp_resistance = self.tmp_voltage/self.tmp_current



        #odlaczenie miernika
        if self.mode_cims_relays:
            self.sourcemeter_obj.disable_source()
            
        data = {
            'Voltage (V)':self.tmp_voltage, 
            'Current (A)':self.tmp_current, 
            'Resistance (ohm)': self.tmp_resistance, 
            'Field (Oe)': self.tmp_field, 
            'Frequency (Hz)': math.nan, 
            'X (V)': math.nan, 
            'Y (V)': math.nan, 
            'Phase':math.nan,
            'Polar angle (deg)': self.polar_angle if self.rotationstation == True else math.nan,
            'Azimuthal angle (deg)': self.azimuthal_angle if self.rotationstation == True else math.nan,
            'Applied voltage (V)': point
            }
        
        return data 

    def idle(self):
        self.sourcemeter_obj.shutdown()
        self.pulsegenerator_obj.shutdown()
        sweep_field_to_zero(self.tmp_field, self.field_constant, self.field_step, self.field_obj)
        if self.rotationstation and self.return_the_rotationstation: 
            self.rotationstation_obj.goToZero() 

    def end(self):
        CIMSMode.idle(self)