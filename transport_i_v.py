from ast import Num
from email.policy import default
import logging
import pandas as pd 

import math
import sys
import random
from time import sleep, time
import traceback
from logic.find_instrument import FindInstrument
from logic.save_results_path import SaveFilePath

import numpy as np
from logic.scope_rate import scope_rate

from pymeasure.display.Qt import QtGui
from pymeasure.display.Qt import QtWidgets
from pymeasure.display.windows import ManagedWindow
from pymeasure.display.windows import ManagedWindowBase
# from pymeasure.display.widgets import TableWidget, LogWidget, PlotWidget
#from pymeasure.display.windows.managed_dock_window import ManagedDockWindow
from pymeasure.experiment import (
    Procedure, FloatParameter, BooleanParameter, IntegerParameter, Parameter,ListParameter, Results, VectorParameter
)
from logic.unique_name import unique_name

from hardware.keithley2400 import Keithley2400
from logic.vector import Vector
from hardware.agilent_34410a import Agilent34410A
from modules.compute_diff import ComputeDiff
from modules.computer_resisrance import ComputerResistance
from modules.Lockin_calibration import LockinCalibration
from modules.Lockin_field import LockinField 
from modules.Lockin_frequency import LockinFrequency
from modules.Lockin_time import LockinTime
from logic.measure_field import measure_field
from hardware.field_sensor_noise_new import FieldSensor
from hardware.dummy_field_sensor_iv import DummyFieldSensor

log = logging.getLogger(__name__) 
log.addHandler(logging.NullHandler()) 



class IVTransfer(Procedure):
    licznik = 1 # licznik
    find_instruments = FindInstrument()
    finded_instruments = find_instruments.show_instrument() 
    print(finded_instruments)
#################################################################### PARAMETERS #####################################################################
    mode = ListParameter("Mode",  default='HDCMode', choices=['HDCMode', 'Fast Resistance', 'HDCACMode', 'ScopeMode'])
    mode_lockin = ListParameter("Lockin mode", choices = ['Lockin field', 'Lockin frequency'],group_by='mode', group_condition=lambda v: v =='HDCACMode')
    agilent = BooleanParameter("Agilent", default=False, group_by='mode', group_condition=lambda v: v =='HDCMode')
    agilent34401a_adress = Parameter("Agilent34401a adress", default="GPIB1::22::INSTR", group_by='agilent', group_condition=lambda v: v ==True)
    acquire_type = ListParameter("Acquire type", choices = ['I(Hmb) | set Vb', 'V(Hmb) |set Ib', 'I(Vb) | set Hmb', 'V(Ib) | set Hmb'],group_by='mode', group_condition=lambda v: v =='HDCMode')
    keithley_adress = ListParameter("Keithley2400 adress",group_by='mode', group_condition=lambda v: v =='HDCMode', choices=["GPIB1::24::INSTR"])
    field_sensor_adress = Parameter("Field_sensor",  default="COM3")
    #keithley_source_type = ListParameter("Source type", default = "Current", choices = ['Current', 'Voltage'])
    keithley_compliance_current = FloatParameter('Compliance current', units='A', default=0.1, group_by={'acquire_type':lambda v: v =='I(Hmb) | set Vb' or v == 'I(Vb) | set Hmb', 'mode':lambda v: v =='HDCMode'})
    keithley_compliance_voltage = FloatParameter('Compliance voltage', units='V', default=1,group_by={'acquire_type': lambda v: v =='V(Hmb) |set Ib' or v == 'V(Ib) | set Hmb', 'mode':lambda v: v =='HDCMode'})
    keithley_current_bias = FloatParameter('Current bias', units='A', default=0, group_by={'acquire_type':'V(Hmb) |set Ib', 'mode':lambda v: v =='HDCMode'})
    keithley_voltage_bias = FloatParameter('Volage bias', units='V', default=0.1, group_by={'acquire_type':'I(Hmb) | set Vb', 'mode':lambda v: v =='HDCMode' or v == 'Fast Resistance'})
    agilent_adress = Parameter("Agilent E3648A adress", default="COM9",group_by={'field_device':lambda v: v =='Agilent E3648A'} )
    field_device = ListParameter("Field device", choices = ["DAQ", "Agilent E3648A"], default = "DAQ", group_by='mode', group_condition=lambda v: v =='HDCMode')
    field_bias = FloatParameter('Field bias', units='Oe', default=10, group_by={'acquire_type':lambda v: v =='I(Vb) | set Hmb' or v == 'V(Ib) | set Hmb', 'mode':lambda v: v =='HDCMode'})
    coil = ListParameter("Coil",  choices=["Large", "Small"], group_by='mode', group_condition=lambda v: v =='HDCMode')
    vector_param = Parameter("Vector", group_by='mode', group_condition=lambda v: v =='HDCMode')
    # stop = FloatParameter("Stop", group_by='mode', group_condition=lambda v: v =='HDCMode')
    # no_points = IntegerParameter("No Points", group_by='mode', group_condition=lambda v: v =='HDCMode')
    reverse_field = BooleanParameter("Reverse field", default=False, group_by='mode', group_condition=lambda v: v =='HDCMode')
    delay = FloatParameter("Delay", units = "ms", default = 1000, group_by='mode', group_condition=lambda v: v =='HDCMode')
    sample_name = Parameter("Sample Name", default="sample name")
    bias_voltage = FloatParameter('Bias Voltage', units='mV', default=100,group_by='mode', group_condition=lambda v: v =='HDCACMode' or v =="ScopeMode")


#Lockin mode: 
    lockin_adress = Parameter("Lockin adress", default="192.168.66.202", group_by='mode', group_condition=lambda v: v =='HDCACMode' or v == "ScopeMode")
    input_type = ListParameter("Input type", choices=["Voltage input", "Current input"], group_by='mode', group_condition=lambda v: v=="HDCACMode" or v == "ScopeMode")
    dc_field = FloatParameter('DC Field', units='Oe', default=0,group_by='mode', group_condition=lambda v: v =='HDCACMode' or v == "ScopeMode")
    ac_field_amplitude = FloatParameter('AC Field Amplitude', units='Oe', default=0,group_by=['mode'], group_condition=lambda v: v =='HDCACMode' or v == "ScopeMode")   
    ac_field_frequency = FloatParameter('AC Field Frequency', units='Hz', default=0,group_by=['mode'], group_condition=lambda v: v =='HDCACMode'or v == "ScopeMode")
    differential_signal = BooleanParameter('Differential voltage input', default=False, group_by=[mode,input_type], group_condition=[lambda v: v =='HDCACMode'or v == "ScopeMode", lambda v: v == "Voltage input"])
    lockin_frequency = FloatParameter('Lockin Frequency', units='Hz', default=0,group_by=['mode', 'mode_lockin'], group_condition=[lambda v: v =='HDCACMode'or v == "ScopeMode",'Lockin field'])
    avergaging_rate = IntegerParameter("Avergaging rate", default=1,group_by='mode', group_condition=lambda v: v =='HDCACMode'or v == "ScopeMode" )
    scope_rate = ListParameter("Scope Rate", choices = ["60MHz", "30MHz", "15MHz", "7.5MHz", "3.75MHz", "1.88MHz", "938kHz", "469kHz", "234kHz", "117kHz", "58.6kHz", "29.3kHz", "14.6kHz", "7.32kHz", "3.66kHz", "1.83kHz", "916Hz"], default = "60MHz", group_by='mode', group_condition=lambda v: v =='ScopeMode' )
    scope_time = FloatParameter("Scope Length",  default = 16348, group_by='mode', group_condition=lambda v: v =='ScopeMode' )
    kepco = BooleanParameter("Kepco?", default=False, group_by='mode', group_condition=lambda v: v =='HDCACMode'or v == "ScopeMode")
    coil = FloatParameter("Coil constant",units='Oe/A', group_by='mode', default = 30, group_condition=lambda v: v =='HDCACMode'or v == "ScopeMode")
    start_f = FloatParameter("Start Freq",units='Hz', group_by=['mode', 'amplitude_vec'], group_condition=[lambda v: v =='HDCACMode', False])
    stop_f = FloatParameter("Stop Freq", units='Hz', group_by=['mode', 'amplitude_vec'], group_condition=[lambda v: v =='HDCACMode', False])
    no_points_f = IntegerParameter("No Points Freq",default = 1, group_by=['mode', 'amplitude_vec'], group_condition=[lambda v: v =='HDCACMode', False])
    amplitude_vec = BooleanParameter("Sweep field", default=False, group_by=['mode', 'mode_lockin'], group_condition=[lambda v: v =='HDCACMode','Lockin field'])
    start_v = FloatParameter("Start H AC",units='Oe', group_by=['mode', 'amplitude_vec'], group_condition=[lambda v: v =='HDCACMode', True])
    stop_v = FloatParameter("Stop H AC", units='Oe', group_by=['mode', 'amplitude_vec'], group_condition=[lambda v: v =='HDCACMode', True])
    no_points_v = IntegerParameter("No Points H AC",default = 1,group_by=['mode', 'amplitude_vec'], group_condition=[lambda v: v =='HDCACMode', True])
    


##############################################################################################################################################################


    DEBUG = 1
    DATA_COLUMNS = ['time (s)','Voltage (V)', 'frequency (Hz)','AC field amplitude (Oe)', 'Sense Voltage (V)','Bias voltage (V)','Current (A)','Phase', 'Resistance (ohm)', 'dX/dH', 'dR/dH', 'diff_I', 'diff_V', 'X field (Oe)', 'Y field (Oe)', 'Z field (Oe)','Field set (Oe)'] #data columns

    path_file = SaveFilePath() 
   
    
    ################ STARTUP ##################3
    def startup(self):
        self.vector_obj = Vector()
        if self.mode == 'HDCMode':
            log.info("Finding instruments...")
            sleep(0.1)
            log.info("Finded: {}".format(self.finded_instruments))
            
        
        ### Init field device 
            if self.field_device == "DAQ":
                log.info('Start config DAQ') 
                try:
                    from hardware.daq import DAQ
                    self.field = DAQ("6124/ao0")
                    log.info("Config DAQ done")
                except Exception as e:
                    print(e)
                    log.error("Config DAQ failed")
                try:
                    if self.reverse_field == True: 
                        self.vector_to = self.vector_obj.generate_vector(self.vector_param)
                        self.vector_rev = self.vector_to[::-1]
                        self.vector = np.append(self.vector_to[0:-1], self.vector_rev)
                    else: 
                        self.vector = self.vector_obj.generate_vector(self.vector_param)
                except Exception as e:
                    print(e)
                    log.error("Vector set failed")
                print(self.vector)
            else: 
                log.info('Start config Keisight E3648A')
                ##Bias field:
                try:
                    from hardware.keisight_e3600a import E3600a
                    self.field = E3600a(self.agilent_adress) #connction to field controller
                    self.field.remote()
                    sleep(1)
                except Exception as e:
                    print(e)
                    log.error("Config Keisight E3648A failed")
                try:
                    if self.reverse_field == True: 
                        self.vector_to = self.vector_obj.generate_vector(self.vector_param)
                        self.vector_rev = self.vector_to[::-1]
                        self.vector = np.append(self.vector_to[0:-1], self.vector_rev)
                    else: 
                        self.vector = self.vector_obj.generate_vector(self.vector_param)
                except Exception as e:
                    print(e)
                    log.error("Vector set failed")
            


            
            
            ############## KEITHLEY CONFIG ###############
            log.info("Start config Keithley")
            try:
                
                self.keithley = Keithley2400(self.keithley_adress)
                if self.acquire_type == 'I(Hmb) | set Vb': 
                    self.keithley.apply_voltage()
                    self.keithley.source_voltage_range = 20
                    self.keithley.compliance_current = self.keithley_compliance_current
                    self.keithley.source_voltage = self.keithley_voltage_bias             # Sets the source current to 0 mA
                    self.keithley.enable_source()                # Enables the source output
                    self.keithley.measure_current()  
                elif self.acquire_type == 'V(Hmb) |set Ib': 
                    self.keithley.apply_current()
                    self.keithley.source_current_range = 0.1
                    self.keithley.compliance_voltage = self.keithley_compliance_voltage
                    self.keithley.source_current= self.keithley_current_bias            # Sets the source current to 0 mA
                    self.keithley.enable_source()                # Enables the source output
                    self.keithley.measure_voltage()         
                elif self.acquire_type == 'I(Vb) | set Hmb': 
                    self.keithley.apply_voltage()
                    self.keithley.source_voltage_range = 20
                    self.keithley.compliance_current = self.keithley_compliance_current
                    self.keithley.source_voltage =  0         # Sets the source current to 0 mA
                    self.keithley.enable_source()                # Enables the source output
                    self.keithley.measure_current()
                    if self.coil == "Large":
                        self.field_const = 5
                    else:
                        self.field_const = 10
                    self.set_field = self.field.set_field(self.field_bias/self.field_const)
                elif self.acquire_type == 'V(Ib) | set Hmb': 
                    self.keithley.apply_current()
                    self.keithley.source_current_range = 0.1
                    self.keithley.compliance_voltage = self.keithley_compliance_voltage
                    self.keithley.source_current=  0         # Sets the source current to 0 mA
                    self.keithley.enable_source()                # Enables the source output
                    self.keithley.measure_voltage()
                    if self.coil == "Large":
                        self.field_const = 5
                    else:
                        self.field_const = 10 
                    self.set_field = self.field.set_field(self.field_bias/self.field_const)
                log.info("Config Keithley done")

            except:
                log.error("Config Keithley failed")
                

        
            
            ####### Config FieldSensor ######## 
            log.info("Config Field Sensor")
            try:
                self.field_sensor = FieldSensor(self.field_sensor_adress)
                self.field_sensor.read_field_init()
                log.info("Config FieldSensor done")
            except:
                log.error("Config FieldSensor failed")
                self.field_sensor = DummyFieldSensor()
                log.info("Use DummyFieldSensor")

            ####### Config Agilent 34410A ########
            if self.agilent == True: 
                log.info("Config Agilent 34410A")
                try:
                    self.agilent_34410 = Agilent34410A(self.agilent34401a_adress)
                    if self.coil == "Large":
                        self.field_const = 5
                    else:
                        self.field_const = 10
                    if self.acquire_type == 'I(Vb) | set Hmb': 
                        self.set_field = self.field.set_field(self.field_bias/self.field_const)
                    elif self.acquire_type == 'V(Ib) | set Hmb':
                        self.set_field = self.field.set_field(self.field_bias/self.field_const)
                    log.info("Config Agilent 34410A done")
                except:
                    log.error("Config Agilent 34410A failed")
                   
                   

        
################FAST RESISTANCE######################
        
        
        elif self.mode == "Fast Resistance": 
            
            ############## KEITHLEY CONFIG ###############
           
            try:
                self.keithley = Keithley2400(self.keithley_adress)
                self.keithley.apply_voltage()
                self.keithley.source_voltage_range = 1
                self.keithley.compliance_current = 0.1
                self.keithley.source_voltage = self.keithley_voltage_bias             # Sets the source current to 0 mA
                self.keithley.enable_source()                # Enables the source output
                self.keithley.measure_resistance()  

            except:
                log.error("Config Keithley failed")

        elif self.mode =="HDCACMode":

            if self.mode_lockin == "Lockin field":

                
                try:
                    self.field_sensor = FieldSensor(self.field_sensor_adress)
                    self.field_sensor.read_field_init()
                    log.info("Config FieldSensor done")
                except:
                    log.error("Config FieldSensor failed")
                    self.field_sensor = DummyFieldSensor()
                    log.info("Use DummyFieldSensor")
                try:
                    self.lockin = LockinField(self.lockin_adress)
                    if self.input_type == "Current input":
                        self.lockin.init(1, False) 
                    else: 
                        if self.differential_signal == True:
                            self.lockin.init(0, True)
                        else:
                            self.lockin.init(0, False)
                    log.info("Lockin initialized")
                except: 
                    log.error("Lockin init failed")
                if self.amplitude_vec == True:
                    self.vector = np.linspace(self.start_v, self.stop_v,self.no_points_v)
                else: 
                    self.vector = np.linspace(self.start_f, self.stop_f,self.no_points_f)
                
                self.lockin.set_constant_vbias(self.bias_voltage)
                sleep(1)
                

                
            elif self.mode_lockin == "Lockin frequency": 
                 
                try:
                    self.field_sensor = FieldSensor(self.field_sensor_adress)
                    self.field_sensor.read_field_init()
                    log.info("Config FieldSensor done")
                except:
                    log.error("Config FieldSensor failed")
                    self.field_sensor = DummyFieldSensor()
                    log.info("Use DummyFieldSensor")
                
                self.lockin = LockinFrequency(self.lockin_adress)
                if self.input_type == "Current input":
                        self.lockin.init(1) 
                else: 
                        if self.differential_signal == True:
                            self.lockin.init(0, True)
                        else:
                            self.lockin.init(0, False)
                self.vector = np.linspace(self.start_f, self.stop_f,self.no_points_f)
                self.lockin.set_constant_field(self.dc_field/0.6)
                sleep(1)
                self.lockin.set_constant_vbias(self.bias_voltage)
                sleep(1)
               
            elif self.mode == "Lockin calibration":
                pass


        elif self.mode == "ScopeMode":
            self.rate_index = scope_rate(self.scope_rate)
            try:
                self.field_sensor = FieldSensor(self.field_sensor_adress)
                self.field_sensor.read_field_init()
                log.info("Config FieldSensor done")
            except:
                log.error("Config FieldSensor failed")
                self.field_sensor = DummyFieldSensor()
                log.info("Use DummyFieldSensor")
            try:
                self.lockin = LockinTime(self.lockin_adress)
                if self.input_type == "Current input":
                    self.lockin.init_lockin(1, False)
                    self.lockin.init_scope(self.avergaging_rate, 1, self.rate_index, self.scope_time)
                else: 
                        if self.differential_signal == True:
                            self.lockin.init_lockin(0, True)
                        else:
                            self.lockin.init_lockin(0, False)
                    self.lockin.init_scope(self.avergaging_rate, 0, self.rate_index, self.scope_time)

                log.info("Lockin initialized")
            except: 
                log.error("Lockin init failed")
            
            self.lockin.set_constant_vbias(self.bias_voltage)
            sleep(1)
#################################### PROCEDURE##############################################
    def execute(self):
        diff = ComputeDiff()
        res = ComputerResistance()
        tmp_voltage = []
        tmp_current = []
        tmp_field_x = []
        tmp_field_y = []
        tmp_field_z = []
        tmp_resistance = []
        tmp_field_set = []
        tmp_diff_x = []
        tmp_diff_R = []
        tmp_diff_I = []
        tmp_diff_V = []

        if self.mode == "HDCMode":
            if self.acquire_type == 'I(Hmb) | set Vb':
                log.info("Starting to sweep through field")
                if self.coil == "Large":
                    self.field_const = 5
                else:
                    self.field_const = 10 
                w = 0
                for i in self.vector:
                    self.last_value = i
                    self.field.set_field(i/self.field_const)
                    tmp_field_set.append(i)
                    sleep(self.delay*0.001)
                    self.tmp_field = self.field_sensor.read_field()
                    tmp_field_x.append(self.tmp_field[0])
                    tmp_field_y.append(self.tmp_field[1])
                    tmp_field_z.append(self.tmp_field[2])
                    sleep(self.delay*0.001)
                    if self.agilent == True:
                        self.tmp_current = self.agilent_34410.current_dc
                    else:
                        self.tmp_current= self.keithley.current
                    tmp_current.append(self.tmp_current)
                    tmp_voltage.append(self.keithley_voltage_bias)
                    tmp_resistance.append(float(self.keithley_voltage_bias)/float(self.tmp_current))
                    self.emit('progress', 100 * w / len(self.vector))
                    
                    if i == 0:
                        tmp_diff_x = np.nan #diff.diff(tmp_current, tmp_field_set)
                        tmp_diff_R = np.nan # diff.diff(tmp_resistance, tmp_field_set)
                        tmp_diff_I = np.nan #diff.diffIV(tmp_current)
                        tmp_diff_V = np.nan #diff.diffIV(tmp_voltage)
                    else: 
                        tmp_diff_x = diff.diff(tmp_current[w-1], tmp_current[w],tmp_field_set[w-1], tmp_field_set[w])
                        tmp_diff_R = diff.diff(tmp_resistance[w-1], tmp_resistance[w], tmp_field_set[w-1], tmp_field_set[w])
                        tmp_diff_I = diff.diffIV(tmp_current[w-1],tmp_current[w])
                        tmp_diff_V = diff.diffIV(tmp_voltage[w-1], tmp_voltage[w])
                    

                    data = {
                        'time (s)': math.nan,
                        'frequency (Hz)': math.nan,  
                        'AC field amplitude (Oe)': math.nan,
                        'Sense Voltage (V)': math.nan,
                        'Bias voltage (V)': math.nan,
                        'Voltage (V)':  tmp_voltage[w],
                        'Current (A)':  tmp_current[w],
                        'Phase': math.nan,
                        'Resistance (ohm)': tmp_resistance[w],
                        'X field (Oe)': tmp_field_x[w],
                        'Y field (Oe)': tmp_field_y[w],
                        'Z field (Oe)': tmp_field_z[w],
                        'Field set (Oe)': tmp_field_set[w],
                        'dX/dH': tmp_diff_x,
                        'dR/dH': tmp_diff_R,
                        'diff_I': tmp_diff_I,
                        'diff_V': tmp_diff_V,

                        }
                    w = w + 1
                    self.emit('results', data) 
               
                   



            elif self.acquire_type == 'V(Hmb) |set Ib':
                if self.coil == "Large":
                        self.field_const = 5
                else:
                        self.field_const = 10 
                w = 0
                log.info("Starting to sweep through field")
                for i in self.vector:
                    self.last_value = i
                    self.set_field = self.field.set_field(i/self.field_const)
                    tmp_field_set.append(i)
                    sleep(self.delay*0.001)
                    self.tmp_field = self.field_sensor.read_field()
                    tmp_field_x.append(self.tmp_field[0])
                    tmp_field_y.append(self.tmp_field[1])
                    tmp_field_z.append(self.tmp_field[2])
                    sleep(self.delay*0.001)
                    if self.agilent == True:
                        self.tmp_volatage = self.agilent_34410.voltage_dc
                    else:
                        self.tmp_volatage = self.keithley.voltage
                    tmp_current.append(self.keithley_current_bias)
                    tmp_voltage.append(self.tmp_volatage)
                    tmp_resistance.append(float(self.tmp_volatage)/float(self.keithley_current_bias) if self.keithley_current_bias != 0 else np.nan )
                    self.emit('progress', 100 * w / len(self.vector))
                    if i == 0:
                        tmp_diff_x = np.nan #diff.diff(tmp_current, tmp_field_set)
                        tmp_diff_R = np.nan # diff.diff(tmp_resistance, tmp_field_set)
                        tmp_diff_I = np.nan #diff.diffIV(tmp_current)
                        tmp_diff_V = np.nan #diff.diffIV(tmp_voltage)
                    else: 
                        tmp_diff_x = diff.diff(tmp_current[w-1], tmp_current[w],tmp_field_set[w-1], tmp_field_set[w])
                        tmp_diff_R = diff.diff(tmp_resistance[w-1], tmp_resistance[w], tmp_field_set[w-1], tmp_field_set[w])
                        tmp_diff_I = diff.diffIV(tmp_current[w-1],tmp_current[w])
                        tmp_diff_V = diff.diffIV(tmp_voltage[w-1], tmp_voltage[w])
                    

                    data = {
                        'time (s)': math.nan,
                        'frequency (Hz)': math.nan,  
                        'AC field amplitude (Oe)': math.nan,
                        'Sense Voltage (V)': math.nan,
                        'Bias voltage (V)': math.nan,
                        'Voltage (V)':  tmp_voltage[w],
                        'Current (A)':  tmp_current[w],
                        'Phase': math.nan,
                        'Resistance (ohm)': tmp_resistance[w],
                        'X field (Oe)': tmp_field_x[w],
                        'Y field (Oe)': tmp_field_y[w],
                        'Z field (Oe)': tmp_field_z[w],
                        'Field set (Oe)': tmp_field_set[w],
                        'dX/dH': tmp_diff_x,
                        'dR/dH': tmp_diff_R,
                        'diff_I': tmp_diff_I,
                        'diff_V': tmp_diff_V,

                        }
                    w = w + 1
                    self.emit('results', data) 
               
                    
            elif self.acquire_type == 'I(Vb) | set Hmb':
                log.info("Starting to sweep through voltage")
                w = 0


                for i in self.vector:
                    tmp_field_set.append(self.field_bias)
                   
                    self.keithley.source_voltage =  i
                    sleep(self.delay*0.001)
                    if self.agilent == True:
                        self.tmp_current = self.agilent_34410.current_dc
                    else:
                        self.tmp_current = self.keithley.current
                    sleep(self.delay*0.001)
                    self.tmp_field = self.field_sensor.read_field()
                    tmp_field_x.append(self.tmp_field[0])
                    tmp_field_y.append(self.tmp_field[1])
                    tmp_field_z.append(self.tmp_field[2])
                    tmp_current.append(self.tmp_current)
                    tmp_voltage.append(i)
                    tmp_resistance.append(float(i)/float(self.tmp_current))
                    self.emit('progress', 100 * w / len(self.vector))
                    if i == 0:
                        tmp_diff_x = np.nan #diff.diff(tmp_current, tmp_field_set)
                        tmp_diff_R = np.nan # diff.diff(tmp_resistance, tmp_field_set)
                        tmp_diff_I = np.nan #diff.diffIV(tmp_current)
                        tmp_diff_V = np.nan #diff.diffIV(tmp_voltage)
                    else: 
                        tmp_diff_x = np.nan#diff.diff(tmp_current[w-1], tmp_current[w],tmp_field_set[w-1], tmp_field_set[w])
                        tmp_diff_R = np.nan #diff.diff(tmp_resistance[w-1], tmp_resistance[w], tmp_field_set[w-1], tmp_field_set[w])
                        tmp_diff_I = diff.diffIV(tmp_current[w-1],tmp_current[w])
                        tmp_diff_V = diff.diffIV(tmp_voltage[w-1], tmp_voltage[w])
                    

                    data = {
                        'time (s)': math.nan,
                        'frequency (Hz)': math.nan,  
                        'AC field amplitude (Oe)': math.nan,
                        'Sense Voltage (V)': math.nan,
                        'Bias voltage (V)': math.nan,
                        'Voltage (V)':  tmp_voltage[w],
                        'Current (A)':  tmp_current[w],
                        'Phase': math.nan,
                        'Resistance (ohm)': tmp_resistance[w],
                        'X field (Oe)': tmp_field_x[w],
                        'Y field (Oe)': tmp_field_y[w],
                        'Z field (Oe)': tmp_field_z[w],
                        'Field set (Oe)': tmp_field_set[w],
                        'dX/dH': tmp_diff_x,
                        'dR/dH': tmp_diff_R,
                        'diff_I': tmp_diff_I,
                        'diff_V': tmp_diff_V,

                        }
                    w = w + 1
                    self.emit('results', data) 
               
                
            elif self.acquire_type == 'V(Ib) | set Hmb':
                log.info("Starting to sweep through current")
                w = 0
                for i in self.vector:
                    tmp_field_set.append(self.field_bias)
                    self.keithley.source_current =  i
                    sleep(self.delay*0.001)
                    if self.agilent == True:
                        self.tmp_volatage = self.agilent_34410.voltage_dc
                    else:
                        self.tmp_volatage = self.keithley.voltage
                    sleep(self.delay*0.001)
                    self.tmp_field = self.field_sensor.read_field()
                    tmp_field_x.append(self.tmp_field[0])
                    tmp_field_y.append(self.tmp_field[1])
                    tmp_field_z.append(self.tmp_field[2])
                    tmp_current.append(i)
                    tmp_voltage.append(self.tmp_volatage)
                    tmp_resistance.append(float(self.tmp_volatage)/(i if i != 0 else 1e-9))
                    self.emit('progress', 100 * w / len(self.vector))
                    if i == 0:
                        tmp_diff_x = np.nan #diff.diff(tmp_current, tmp_field_set)
                        tmp_diff_R = np.nan # diff.diff(tmp_resistance, tmp_field_set)
                        tmp_diff_I = np.nan #diff.diffIV(tmp_current)
                        tmp_diff_V = np.nan #diff.diffIV(tmp_voltage)
                    else: 
                        tmp_diff_x = np.nan #diff.diff(tmp_current[w-1], tmp_current[w],tmp_field_set[w-1], tmp_field_set[w])
                        tmp_diff_R = np.nan #diff.diff(tmp_resistance[w-1], tmp_resistance[w], tmp_field_set[w-1], tmp_field_set[w])
                        tmp_diff_I = diff.diffIV(tmp_current[w-1],tmp_current[w])
                        tmp_diff_V = diff.diffIV(tmp_voltage[w-1], tmp_voltage[w])
                    

                    data = {
                        'time (s)': math.nan,
                        'frequency (Hz)': math.nan,  
                        'AC field amplitude (Oe)': math.nan,
                        'Sense Voltage (V)': math.nan,
                        'Bias voltage (V)': math.nan,
                        'Voltage (V)':  tmp_voltage[w],
                        'Current (A)':  tmp_current[w],
                        'Phase': math.nan,
                        'Resistance (ohm)': tmp_resistance[w],
                        'X field (Oe)': tmp_field_x[w],
                        'Y field (Oe)': tmp_field_y[w],
                        'Z field (Oe)': tmp_field_z[w],
                        'Field set (Oe)': tmp_field_set[w],
                        'dX/dH': tmp_diff_x,
                        'dR/dH': tmp_diff_R,
                        'diff_I': tmp_diff_I,
                        'diff_V': tmp_diff_V,

                        }
                    w = w + 1
                    self.emit('results', data) 
               
        elif self.mode == "Fast Resistance":
            self.tmp_resistance = self.keithley.resistance
            log.info(self.tmp_resistance)
            # self.emit('results',  data = {
            #             'Voltage (V)':  0,
            #             'Current (A)':  0,
            #             'X field (Oe)': 0,
            #             'Y field (Oe)': 0,
            #             'Z field (Oe)': 0,
            #             'Field set (Oe)': 0,
        
        #Lockin mode:
        
        elif self.mode == 'HDCACMode':
            if self.mode_lockin == "Lockin field":
              
                if self.kepco == False:
                    self.calibration_field = LockinCalibration(self.lockin, self.ac_field_frequency,self.dc_field, self.coil)
                    self.cal_field_const = self.calibration_field.calibrate()
                    self.lockin.set_dc_field(self.dc_field/0.6)
                else: 
                    self.cal_field_const = 15
                    self.lockin.set_dc_field(self.dc_field/15)
               
                self.lockin.set_lockin_freq(self.lockin_frequency)
                self.counter = 0
                
                for i in self.vector:
                    if self.amplitude_vec == True:
                        self.lockin.set_ac_field(i/self.cal_field_const,self.ac_field_frequency)
                    else:
                        self.lockin.set_ac_field(self.ac_field_amplitude/self.cal_field_const,i)
                    if i != 0:
                        sleep(2/i)
                    else: 
                        sleep(1)
                    
                    r = self.lockin.lockin_measure_R(0,self.avergaging_rate)
                    theta = self.lockin.lockin_measure_phase(0,self.avergaging_rate)
                    self.counter = self.counter + 1
                        
                    self.emit('progress', 100 * self.counter / len(self.vector))
                   
                    try:
              
                        data_lockin = {
                            'time (s)': math.nan,
                            'frequency (Hz)': i if self.amplitude_vec == False else self.ac_field_frequency, 
                            'AC field amplitude (Oe)': i if self.amplitude_vec == True else self.ac_field_amplitude,
                            'Sense Voltage (V)': r if self.input_type == "Voltage input" else math.nan,
                            'Bias voltage (V)': self.bias_voltage,
                            'X field (Oe)': i+self.dc_field if self.amplitude_vec == True else self.ac_field_amplitude+self.dc_field,
                            'Y field (Oe)':0,
                            'Z field (Oe)': 0,
                            'Voltage (V)':  math.nan,
                            'Current (A)':  r if self.input_type == "Current input" else math.nan,
                            'Phase': theta,
                            'Resistance (ohm)': math.nan,
                            'Field set (Oe)': math.nan,
                            'dX/dH':math.nan,
                            'dR/dH': math.nan,
                            'diff_I':math.nan,
                            'diff_V': math.nan
                            }
                        
                     
                        self.emit('results', data_lockin) 
                    except Exception as e:
                        print(e)
                        self.should_stop()
                    if self.should_stop():
                        log.warning("Caught the stop flag in the procedure")
                        break








            elif self.mode_lockin == "Lockin frequency":
                self.field_value = measure_field(1,self.field_sensor, self.should_stop )
                self.counter = 0
                for i in self.vector:
                    self.lockin.set_lockin_freq(i) 
                    if i != 0:
                        sleep(2/i)
                    else: 
                        sleep(0.1)
                    r = self.lockin.lockin_measure_R(0,self.avergaging_rate)
                    theta = self.lockin.lockin_measure_phase(0,self.avergaging_rate)
                    self.counter = self.counter + 1
                    self.emit('progress', 100 * self.counter / len(self.vector))
                    try:
                        data_lockin = {
                            'time (s)': math.nan,
                            'frequency (Hz)': i,  
                            'AC field amplitude (Oe)': math.nan,
                            'Sense Voltage (V)':  r if self.input_type == "Voltage input" else math.nan,
                            'Bias voltage (V)': self.bias_voltage,
                            'X field (Oe)':self.field_value[0],
                            'Y field (Oe)':self.field_value[1],
                            'Z field (Oe)': self.field_value[2],
                            'Voltage (V)':  math.nan,
                            'Current (A)':   r if self.input_type == "Current input" else math.nan,
                            'Phase': theta,
                            'Resistance (ohm)': math.nan,
                            'Field set (Oe)': math.nan,
                            'dX/dH':math.nan,
                            'dR/dH': math.nan,
                            'diff_I':math.nan,
                            'diff_V': math.nan
                            }
                    

                        self.emit('results', data_lockin) 
                    except:
                        self.should_stop()
                    if self.should_stop():
                        log.warning("Caught the stop flag in the procedure")
                        break   
        

        elif self.mode == "ScopeMode":

              
            if self.kepco == False:
                self.calibration_field = LockinCalibration(self.lockin, self.ac_field_frequency,self.dc_field, self.coil)
                self.cal_field_const = self.calibration_field.calibrate()
                self.lockin.set_dc_field(self.dc_field/0.6)
            else: 
                self.cal_field_const = 15
                self.lockin.set_dc_field(self.dc_field/15)
           
            self.lockin.set_lockin_freq(self.lockin_frequency)
            
           
               
            self.lockin.set_ac_field(self.ac_field_amplitude/self.cal_field_const,self.ac_field_frequency)
                
            sleep(2)
                
            scope_signal = self.lockin.get_wave()
                
                
                
                    
            self.emit('progress', 100)
               
            try:
                for w in range(len(scope_signal[0])):
                    data_lockin = {
                        'time (s)': scope_signal[0][w],
                        'frequency (Hz)': self.ac_field_frequency, 
                        'AC field amplitude (Oe)':self.ac_field_amplitude,
                        'Sense Voltage (V)': float(scope_signal[1][w]) if self.input_type == "Voltage input" else math.nan,
                        'Bias voltage (V)': self.bias_voltage,
                        'X field (Oe)': 0,
                        'Y field (Oe)':0,
                        'Z field (Oe)': 0,
                        'Voltage (V)':  math.nan,
                        'Current (A)':  float(scope_signal[1][w]) if self.input_type == "Current input" else math.nan,
                        'Phase': math.nan,
                        'Resistance (ohm)': math.nan,
                        'Field set (Oe)': self.ac_field_amplitude+self.dc_field,
                        'dX/dH':math.nan,
                        'dR/dH': math.nan,
                        'diff_I':math.nan,
                        'diff_V': math.nan
                        }
                    
                 
                    self.emit('results', data_lockin) 
            except Exception as e:
                print(e)
                self.should_stop()
            if self.should_stop():
                log.warning("Caught the stop flag in the procedure")
                

    def shutdown(self):

        if MainWindow.last == True or IVTransfer.licznik == MainWindow.wynik:
            if self.mode == "HDCMode":
                if self.field_device == "DAQ":
                    self.field.shutdown()
                    pass
                else: 
                    if self.acquire_type == 'I(Hmb) | set Vb' or self.acquire_type == 'V(Hmb) |set Ib':         
                        self.field.shutdown(self.last_value/self.field_const)
                    else:
                        self.field.shutdown(self.field_bias/self.field_const)
                sleep(0.2)
            
                self.keithley.shutdown()
                print("keithley shutdown done")
                IVTransfer.licznik = 0
            elif self.mode == "HDCACMode": 
                self.lockin.shutdown()
        else:
            if self.mode == "HDCMode":
                self.keithley.shutdown()
                print("keithley shutdown done")
                print("go next loop...")
        IVTransfer.licznik += 1
        print(IVTransfer.licznik)
        

class MainWindow(ManagedWindow):
    last = False
    wynik = 0
    wynik_list = []
    def __init__(self):
        super().__init__(
            procedure_class= IVTransfer,
            inputs=['mode','mode_lockin','sample_name','vector_param','coil','acquire_type','keithley_adress','agilent','agilent34401a_adress','field_sensor_adress', 'keithley_compliance_current', 'keithley_compliance_voltage',
            'keithley_current_bias', 'keithley_voltage_bias', 'field_device', 'field_bias', 'agilent_adress', 'delay', 'reverse_field', 'lockin_adress','input_type','differential_signal', 'kepco', 'coil', 'dc_field','bias_voltage', 'ac_field_amplitude', 'ac_field_frequency', 'lockin_frequency', 'avergaging_rate','scope_rate', 'scope_time', 'amplitude_vec','start_f', 'stop_f', 'no_points_f',  'start_v', 'stop_v', 'no_points_v'],
            displays=['sample_name', 'acquire_type', 'field_bias', 'keithley_current_bias', 'keithley_voltage_bias'],
            x_axis='Current (A)',
            y_axis='Voltage (V)',
            directory_input=True,  
            sequencer=True,                                  
            sequencer_inputs=['field_bias', 'keithley_current_bias', 'keithley_voltage_bias','ac_field_amplitude', 'ac_field_frequency'],
            inputs_in_scrollarea=True,
            
        )
       
        self.setWindowTitle('IV Measurement System v.0.99')
        self.directory = self.procedure_class.path_file.ReadFile()
        

    def queue(self, procedure=None):
        directory = self.directory  # Change this to the desired directory
        self.procedure_class.path_file.WriteFile(directory)
        
        if procedure is None:
            procedure = self.make_procedure()
       
        name_of_file = procedure.sample_name
        filename = unique_name(directory, prefix="{}_".format(name_of_file))
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)
        self.manager.queue(experiment)
        
        
        

        try:
            
            MainWindow.wynik =  procedure.seq
            MainWindow.wynik_list.append(procedure.seq)
            MainWindow.wynik = max(MainWindow.wynik_list)
            MainWindow.last = False
            

                
        except:     
            print("No procedure")
            MainWindow.last = True
            
            # while run:
            #     sleep(0.2)
            #     run = self.manager.is_running()
            # procedure.shutdown_definetly()
            
 
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())