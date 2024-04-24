from ast import Num
from email.policy import default
import logging
import math
import sys
import random
from time import sleep, time
import traceback
from logic.find_instrument import FindInstrument
from logic.save_results_path import SaveFilePath
from pymeasure.experiment import Procedure, Results
from pymeasure.display.Qt import QtWidgets
from pymeasure.display.windows.managed_dock_window import ManagedDockWindow
from pymeasure.experiment import (
    Procedure, FloatParameter, BooleanParameter, IntegerParameter, Parameter,ListParameter, Results, VectorParameter
)
from logic.unique_name import unique_name
from modules.resistance_mode import ResistanceMode
from modules.harmonic_mode import HarmonicMode
from modules.fmr_mode import FMRMode
from modules.cims_mode import CIMSMode
from modules.calibration_mode import FieldCalibrationMode
from logic.find_instrument import FindInstrument
from logic.save_parameters import SaveParameters

from numpy import linspace

from datetime import datetime
from datetime import timedelta

log = logging.getLogger(__name__) 
log.addHandler(logging.NullHandler()) 



class SpinLabMeasurement(Procedure):
    # licznik = 1 # licznik
    parameters = {}
    find_instruments = FindInstrument()
    save_parameter = SaveParameters()
    finded_instruments = find_instruments.show_instrument() 

    used_parameters_list=['mode', 'sample_name', 'vector', 'mode_resistance', 'mode_fmr', 'mode_harmonic', 'set_sourcemeter', 'set_multimeter','set_pulsegenerator', 'set_gaussmeter', 'set_field', 'set_lockin', 'set_automaticstation', 'set_rotationstation','set_switch', 'set_kriostat', 'set_lfgen', 'set_analyzer', 'set_generator', 'address_sourcemeter', 'address_multimeter','address_daq' , 'address_gaussmeter', 'address_lockin', 'address_switch', 'address_analyzer', 'address_generator', 'address_lfgen','address_pulsegenerator','sourcemter_source', 'sourcemeter_compliance', 'sourcemeter_channel', 'sourcemeter_limit', 'sourcemeter_nplc', 'sourcemeter_average', 'sourcemeter_bias', 'multimeter_function', 'multimeter_resolution','multimeter_nplc', 'multimeter_autorange', 'multimeter_range', 'multimeter_average', 'field_constant', 'gaussmeter_range', 'gaussmeter_resolution', 'lockin_average', 'lockin_input_coupling', 'lockin_reference_source', 'lockin_dynamic_reserve', 'lockin_input_connection', 'lockin_sensitivity','lockin_frequency', 'lockin_harmonic','lockin_sine_amplitude',  'lockin_timeconstant', 'lockin_channel1','lockin_channel2' ,'lockin_autophase','generator_frequency', 'generator_power','lfgen_freq', 'lfgen_amp', 'set_field_value','set_field_value_fmr', 'field_step', 'delay_field', 'delay_lockin', 'delay_bias', 'rotation_axis', 'rotation_polar_constant', 'rotation_azimuth_constant', 'constant_field_value', 'address_rotationstation', 'mode_cims_relays','pulsegenerator_offset','pulsegenerator_duration','pulsegenerator_pulsetype','pulsegenerator_channel','delay_measurement','pulsegenerator_compliance','pulsegenerator_source_range','return_the_rotationstation','field_bias_value','remagnetization','remagnetization_value','remagnetization_time','hold_the_field_after_measurement','remanency_correction','set_polar_angle','set_azimuthal_angle','set_rotationstation_const_angle','remanency_correction_time']

    parameters_from_file = save_parameter.ReadFile()
#################################################################### PARAMETERS #####################################################################
    mode = ListParameter("Mode", default = parameters_from_file["mode"] , choices=['ResistanceMode', 'FMRMode', 'VSMMode', 'HarmonicMode', 'CalibrationFieldMode', 'PulseMode','CIMSMode'])
    mode_resistance = BooleanParameter("4-points", default = parameters_from_file["mode_resistance"], group_by="mode", group_condition=lambda v: v=="ResistanceMode")
    mode_fmr = ListParameter("FMR Mode",default = parameters_from_file["mode_fmr"], choices = ["const f", "const H"], group_by={"mode": lambda v: v == "FMRMode"})
    mode_harmonic = ListParameter("Harmonic mode",default = parameters_from_file["mode_harmonic"],  choices = ["Field harmonic", "Angular harmonic"], group_by = {"mode": lambda v: v == "HarmonicMode"})
    mode_cims_relays = BooleanParameter("Use relays", default = parameters_from_file["mode_cims_relays"], group_by="mode", group_condition=lambda v: v=="CIMSMode")
    return_the_rotationstation = BooleanParameter("Return the rotationstation", default = parameters_from_file["return_the_rotationstation"], group_by="mode", group_condition=lambda v: v=="CIMSMode" or v=="ResistanceMode")
    remagnetization=BooleanParameter("Remagnetize sample", default = parameters_from_file["remagnetization"], group_by = {"mode": lambda v: v == "CIMSMode"})
    remagnetization_value=FloatParameter("Remagnetization value", default = parameters_from_file["remagnetization_value"], units="Oe", group_by={"mode": lambda v: v == "CIMSMode"})
    remagnetization_time=FloatParameter("Remagnetization time", default = parameters_from_file["remagnetization_time"], units="s", group_by={"mode": lambda v: v == "CIMSMode"})
    hold_the_field_after_measurement=BooleanParameter("Hold the field after measurement", default = parameters_from_file["hold_the_field_after_measurement"], group_by = {"mode": lambda v: v == "CIMSMode"})
    remanency_correction = BooleanParameter("Remanency correction", default = parameters_from_file["remanency_correction"], group_by = {"mode": lambda v: v == "CIMSMode"})
    remanency_correction_time=FloatParameter("Remanency correction time", default = parameters_from_file["remanency_correction_time"], units="s", group_by={"mode": lambda v: v == "CIMSMode"})



    #Hardware

    set_sourcemeter=ListParameter("Sourcemeter", choices=["Keithley 2400", "Keithley 2636", "Agilent 2912", "none"], default = parameters_from_file["set_sourcemeter"], group_by="mode", group_condition=lambda v: v == "ResistanceMode")
    set_multimeter = ListParameter("Multimeter", choices=["Agilent 34400", "none"],default = parameters_from_file["set_multimeter"], group_by={"mode": lambda v: v=="ResistanceMode" or v == "FMRMode", "set_measdevice":"Multimeter"})
    set_gaussmeter = ListParameter("Gaussmeter", default = parameters_from_file["set_gaussmeter"], choices=["Lakeshore", "none"], group_by={"mode":lambda v: v == "ResistanceMode" or v == "HarmonicMode" or v == "FMRMode" or v == "CalibrationFieldMode" })
    set_field = ListParameter("Magnetic Field", default = parameters_from_file["set_field"], choices = ["DAQ", "Lockin", "none"], group_by = {"mode": lambda v: v == "ResistanceMode" or v == "HarmonicMode" or v == "FMRMode" or v == "CalibrationFieldMode" })
    set_lockin = ListParameter("Lockin", default = parameters_from_file["set_lockin"], choices = ["Zurich", "SR830", "none"], group_by = {"mode": lambda v: v == "HarmonicMode" or v == "FMRMode", "set_measdevice":lambda v: v=="LockIn"})

    set_automaticstation = BooleanParameter("Automatic Station",  default = parameters_from_file["set_automaticstation"], group_by={"mode": lambda v: v != "CalibrationFieldMode"})
    set_rotationstation = BooleanParameter("Rotation Station", default = parameters_from_file["set_rotationstation"], group_by={"mode": lambda v: v != "CalibrationFieldMode"})
    set_rotationstation_const_angle = BooleanParameter("Rotation Station for constant angle", default = parameters_from_file["set_rotationstation_const_angle"], group_by={"mode": lambda v: v != "CalibrationFieldMode"})
    set_switch = BooleanParameter("Switch", default = parameters_from_file["set_switch"], group_by={"mode": lambda v: v != "CalibrationFieldMode"})
    set_kriostat = BooleanParameter("Kriostat", default = parameters_from_file["set_kriostat"], group_by={"mode": lambda v: v != "CalibrationFieldMode"})
    set_lfgen = ListParameter("LF Generator", default = parameters_from_file["set_lfgen"], choices = ["SR830", "HP33120A","none"], group_by = {"mode": lambda v: v == "FMRMode", "set_measdevice":lambda v: v=="LockIn"})
    set_analyzer = ListParameter("Vector Analyzer", default = parameters_from_file["set_analyzer"], choices = ['VectorAnalyzer', 'none'], group_by={'mode': lambda v: v=='VSMMode'})
    set_generator = ListParameter("RF Generator", default = parameters_from_file["set_generator"], choices = ["Agilent","WindFreak", "none"], group_by = {"mode": lambda v: v == "FMRMode"})
    set_pulsegenerator=ListParameter("Pulse Generator", choices=["Agilent 2912","Tektronix 10,070A","Keithley 2636", "none"], default = parameters_from_file["set_pulsegenerator"], group_by="mode", group_condition=lambda v: v=="CIMSMode")


    #Hardware address

    address_sourcemeter=ListParameter("Sourcemeter address", default = parameters_from_file["address_sourcemeter"] if parameters_from_file["address_sourcemeter"] in finded_instruments else 'None', choices=finded_instruments, group_by = {"mode": lambda v: v=="ResistanceMode" or v=="CIMSMode", "set_sourcemeter": lambda v: v != "none"})
    address_multimeter=ListParameter("Multimeter address", default = parameters_from_file["address_multimeter"] if parameters_from_file["address_multimeter"] in finded_instruments else 'None', choices=finded_instruments, group_by = {"mode": lambda v: v=="ResistanceMode", "mode_resistance": lambda v: v == "4-points"})
    address_gaussmeter=ListParameter("Gaussmeter address",default = parameters_from_file["address_gaussmeter"] if parameters_from_file["address_gaussmeter"] in finded_instruments else 'None',   choices=finded_instruments, group_by = {"mode": lambda v: v=="ResistanceMode" or v == "HarmonicMode" or v == "FMRMode" or v == "CalibrationFieldMode" or v=="CIMSMode" , "set_gaussmeter": lambda v: v != "none"})
    address_lockin=ListParameter("Lockin address", default = parameters_from_file["address_lockin"] if parameters_from_file["address_lockin"] in finded_instruments else 'None',  choices=finded_instruments, group_by = {"mode": lambda v: v=="HarmonicMode" or v == "FMRMode", "set_lockin": lambda v: v!="none"})
    address_switch=ListParameter("Switch address",default = parameters_from_file["address_switch"] if parameters_from_file["address_switch"] in finded_instruments else 'None',  choices=finded_instruments, group_by = {"mode": lambda v: v=="ResistanceMode"})
    address_analyzer=ListParameter("Analyzer address",default = parameters_from_file["address_analyzer"] if parameters_from_file["address_analyzer"] in finded_instruments else 'None',  choices=finded_instruments, group_by = {"mode": lambda v: v=="VSMMode"})
    address_generator=ListParameter("Generator address", default = parameters_from_file["address_generator"] if parameters_from_file["address_generator"] in finded_instruments else 'None',  choices=finded_instruments, group_by = {"mode":lambda v: v == "FMRMode", "set_generator": lambda v: v != "none"})
    address_daq = ListParameter("DAQ address", default = parameters_from_file["address_daq"],  choices=["Dev4/ao0"], group_by = {"mode": lambda v: v=="ResistanceMode" or v == "HarmonicMode" or v == "FMRMode" or v == "CalibrationFieldMode" or v=="CIMSMode" , "set_field": lambda v: v != "none"})
    address_lfgen = ListParameter("LF Generator address", default = parameters_from_file["address_lfgen"] if parameters_from_file["address_lfgen"] in finded_instruments else 'None',  choices=finded_instruments, group_by = {"mode": lambda v: v=="FMRMode", "set_lfgen": lambda v: v != "none" and  v != "SR830"})
    
    if set_rotationstation:
        address_rotationstation=Parameter("RotationStation address", default = parameters_from_file["address_rotationstation"], group_by = {"set_rotationstation": lambda v: v==True})
    if set_rotationstation_const_angle:
        address_rotationstation=Parameter("RotationStation address", default = parameters_from_file["address_rotationstation"], group_by = {"set_rotationstation_const_angle": lambda v: v==True})
  
    address_pulsegenerator=ListParameter("Pulse generator address", default = parameters_from_file["address_pulsegenerator"] if parameters_from_file["address_pulsegenerator"] in finded_instruments else 'None', choices=finded_instruments, group_by = {"mode": lambda v: v=="CIMSMode", "set_pulsegenerator": lambda v: v != "none"})


    
    
    
   
    #MeasurementParameters
    set_measdevice = ListParameter("Measurement Device", choices=["LockIn", "Multimeter"], default=parameters_from_file["set_measdevice"], group_by={"mode": lambda v: v=="FMRMode"})
    sample_name = Parameter("Sample name", default = parameters_from_file["sample_name"], group_by={"mode": lambda v: v != "CalibrationFieldMode"}) 
    vector = Parameter("Vector", default = parameters_from_file["vector"])
    delay_field = FloatParameter("Delay Field", default = parameters_from_file["delay_field"], units="s")
    delay_lockin = FloatParameter("Delay Measurement", default = parameters_from_file["delay_lockin"], units="s", group_by={"mode": lambda v: v == "HarmonicMode" or v == "FMRMode", "set_measdevice":lambda v: v=="LockIn"})
    delay_bias = FloatParameter("Delay Bias", default = parameters_from_file["delay_bias"], units="s", group_by={"mode": lambda v: v == "ResistanceMode"})

    single_measurement_duration = FloatParameter("Single Measurement Duration", default = 0, units="s")
    

    delay_measurement = FloatParameter("Delay sourcemeter measurement", default = parameters_from_file["delay_measurement"], units="s", group_by={"mode": lambda v: v == "CIMSMode"})


    #########  SETTINGS PARAMETERS ##############
    #SourcemeterParameters 
    sourcemter_source = ListParameter("Sourcemeter Source", default = parameters_from_file["sourcemter_source"], choices=["VOLT", "CURR"], group_by={"mode": lambda v: v == "ResistanceMode" or "CIMSMode", "set_sourcemeter": lambda v: v != "none"})
    sourcemeter_compliance = FloatParameter("Sourcemeter compliance", default = parameters_from_file["sourcemeter_compliance"], group_by={"mode": lambda v: v == "ResistanceMode" or "CIMSMode", "set_sourcemeter": lambda v: v != "none"})
    sourcemeter_channel = ListParameter("Sourcemeter CH", default = parameters_from_file["sourcemeter_channel"], choices = ["Channel A", "Channel B"], group_by={"mode": lambda v: v == "ResistanceMode" or "CIMSMode", "set_sourcemeter": lambda v: v != "none"})
    sourcemeter_limit = FloatParameter("Sourcemeter limit", default = parameters_from_file["sourcemeter_limit"], group_by={"mode": lambda v: v == "ResistanceMode" or "CIMSMode", "set_sourcemeter": lambda v: v != "none"})
    sourcemeter_nplc = FloatParameter("Sourcemeter NPLC", default = parameters_from_file["sourcemeter_nplc"], group_by={"mode": lambda v: v == "ResistanceMode" or "CIMSMode", "set_sourcemeter": lambda v: v != "none"})
    sourcemeter_average = IntegerParameter("Sourcemeter average", default = parameters_from_file["sourcemeter_average"], group_by={"mode": lambda v: v == "ResistanceMode" or "CIMSMode", "set_sourcemeter": lambda v: v != "none"})
    sourcemeter_bias = FloatParameter("Sourcemeter bias", default = parameters_from_file["sourcemeter_bias"], group_by={"mode": lambda v: v == "ResistanceMode" or "CIMSMode", "set_sourcemeter": lambda v: v != "none"})

    #MultimeterParameters 
    multimeter_function = ListParameter("Multimeter function", default = parameters_from_file["multimeter_function"], choices=[ "DCV", "DCV_RATIO", "ACV", "DCI", "ACI", "R2W", "R4W", "FREQ", "PERIOD", "CONTINUITY", "DIODE"], group_by={"mode": lambda v: v == "ResistanceMode" or "FMRMode", "set_measdevice":"Multimeter"})
    multimeter_resolution = FloatParameter("Multimeter resolution",default = parameters_from_file["multimeter_resolution"], group_by={"mode": lambda v: v == "ResistanceMode" or "FMRMode", "set_measdevice":"Multimeter"})
    multimeter_autorange = BooleanParameter("Multimeter autorange", default = parameters_from_file["multimeter_autorange"], group_by={"mode": lambda v: v == "ResistanceMode" or "FMRMode", "set_measdevice":"Multimeter"})
    multimeter_range = FloatParameter("Multimeter range", default = parameters_from_file["multimeter_range"], group_by={"mode": lambda v: v == "ResistanceMode" or "FMRMode", "set_measdevice":"Multimeter"})
    multimeter_average = IntegerParameter("Multimeter average", default = parameters_from_file["multimeter_average"], group_by={"mode": lambda v: v == "ResistanceMode" or "FMRMode", "set_measdevice":"Multimeter"})
    multimeter_nplc = ListParameter("Multimeter NPLC", default = parameters_from_file["multimeter_nplc"], choices=[0.02, 0.2, 1, 10, 100, 'MIN', 'MAX'], group_by={"mode": lambda v: v == "ResistanceMode" or "FMRMode", "set_measdevice":"Multimeter"})
    
    #LockinParameters
    lockin_average = IntegerParameter("Lockin Average", default = parameters_from_file["lockin_average"], group_by={"mode": lambda v: v == "HarmonicMode" or v == "FMRMode", "set_lockin": lambda v: v != "none", "set_measdevice":lambda v: v=="LockIn"})
    lockin_input_coupling = ListParameter("Lockin Input Coupling", default = parameters_from_file["lockin_input_coupling"], choices = ["AC", "DC"], group_by={"mode": lambda v: v == "HarmonicMode" or v == "FMRMode", "set_lockin": lambda v: v != "none", "set_measdevice":lambda v: v=="LockIn"})
    lockin_reference_source = ListParameter("Lockin Reference Source", default = parameters_from_file["lockin_reference_source"], choices=["Internal", "External"], group_by={"mode": lambda v: v == "HarmonicMode" or v == "FMRMode", "set_lockin": lambda v: v != "none", "set_measdevice":lambda v: v=="LockIn"})
    lockin_dynamic_reserve = ListParameter("Lockin Dynamic Reserve", default = parameters_from_file["lockin_dynamic_reserve"], choices=["High Reserve", "Normal", "Low Noise", "Auto Reserve"], group_by={"mode": lambda v: v == "HarmonicMode" or v == "FMRMode", "set_lockin": lambda v: v != "none", "set_measdevice":lambda v: v=="LockIn"})
    lockin_input_connection = ListParameter("Lockin Input Connection", default = parameters_from_file["lockin_input_connection"], choices = ["A", "A - B"], group_by={"mode": lambda v: v == "HarmonicMode" or v == "FMRMode", "set_lockin": lambda v: v != "none", "set_measdevice":lambda v: v=="LockIn"})
    lockin_sensitivity = ListParameter("Lockin Sensitivity",default = parameters_from_file["lockin_sensitivity"], choices=["Auto Gain", "2 nV/fA", "5 nV/fA", "10 nV/fA", "20 nV/fA", "50 nV/fA", "100 nV/fA", "200 nV/fA", "500 nV/fA", "1 uV/pA", "2 uV/pA", "5 uV/pA", "10 uV/pA", "20 uV/pA", "50 uV/pA", "100 uV/pA", "200 uV/pA", "500 uV/pA", "1 mV/nA", "2 mV/nA", "5 mV/nA", "10 mV/nA", "20 mV/nA", "50 mV/nA", "100 mV/nA", "200 mV/nA", "500 mV/nA", "1 V/uA"], group_by={"mode": lambda v: v == "HarmonicMode" or v == "FMRMode", "set_lockin": lambda v: v != "none", "set_measdevice":lambda v: v=="LockIn"})
    lockin_timeconstant = ListParameter("Lockin Time Constant", default = parameters_from_file["lockin_timeconstant"], choices = ["10 us", "30 us", "100 us", "300 us", "1 ms", "3 ms", "10 ms", "30 ms", "100 ms", "300 ms", "1 s", "3 s", "10 s", "30 s", "100 s", "300 s", "1 ks", "3 ks", "10 ks", "30 ks"],group_by={"mode": lambda v: v == "HarmonicMode" or v == "FMRMode", "set_lockin": lambda v: v != "none", "set_measdevice":lambda v: v=="LockIn"})
    lockin_autophase = BooleanParameter("Lockin Autophase", default = parameters_from_file["lockin_autophase"], group_by={"mode": lambda v: v == "HarmonicMode" or v == "FMRMode", "set_lockin": lambda v: v != "none", "set_measdevice":lambda v: v=="LockIn"})
    lockin_frequency = FloatParameter("Lockin Frequency", default = parameters_from_file["lockin_frequency"], units="Hz", group_by={"mode": lambda v: v == "HarmonicMode" or v == "FMRMode", "set_lockin": lambda v: v != "none", "lockin_reference_source": lambda v: v == "Internal", "set_measdevice":lambda v: v=="LockIn"} )
    lockin_harmonic = IntegerParameter("Lockin Harmonic", default = parameters_from_file["lockin_harmonic"],group_by={"mode": lambda v: v == "HarmonicMode" or v == "FMRMode", "set_lockin": lambda v: v != "none", "lockin_reference_source": lambda v: v == "Internal", "set_measdevice":lambda v: v=="LockIn"})
    lockin_sine_amplitude = FloatParameter("Lockin Sine Amplitude", default = parameters_from_file["lockin_sine_amplitude"], units="V", group_by={"mode": lambda v: v == "HarmonicMode" or v == "FMRMode", "set_lockin": lambda v: v != "none", "lockin_reference_source": lambda v: v == "Internal", "set_measdevice":lambda v: v=="LockIn"})
    lockin_channel1 = ListParameter("Lockin Channel 1", default = parameters_from_file["lockin_channel1"], choices = ["X", "Y", "R", "Theta", "Aux In 1", "Aux In 2", "Aux In 3", "Aux In 4"], group_by={"mode": lambda v: v == "HarmonicMode" or v == "FMRMode", "set_lockin": lambda v: v != "none", "set_measdevice":lambda v: v=="LockIn"})
    lockin_channel2 = ListParameter("Lockin Channel 2", default = parameters_from_file["lockin_channel2"], choices = ["X", "Y", "R", "Theta", "Aux In 1", "Aux In 2", "Aux In 3", "Aux In 4"], group_by={"mode": lambda v: v == "HarmonicMode" or v == "FMRMode", "set_lockin": lambda v: v != "none", "set_measdevice":lambda v: v=="LockIn"})
    
    
    #FieldParameters 
    field_constant = FloatParameter("Field Calibration Constant", default = parameters_from_file["field_constant"])
    set_field_value_fmr= FloatParameter("Constant Field Value", default = parameters_from_file["set_field_value_fmr"], units="Oe", group_by={"mode_fmr": lambda v: v == "const H", "mode": lambda v: v == "FMRMode" })
    set_field_value= FloatParameter("Constant Field Value", default = parameters_from_file["set_field_value"], units="Oe", group_by={ "set_rotationstation": lambda v: v == True, "mode": lambda v: v != "CalibrationFieldMode" })
    field_step = FloatParameter("Field sweep step", default = parameters_from_file["field_step"], units="Oe", group_by={"mode": lambda v: v != "CalibrationFieldMode"})

    constant_field_value =  FloatParameter("Set Constant Field Value", default = parameters_from_file["constant_field_value"], units="Oe", group_by={"set_rotationstation": lambda v: v ==True })
    field_bias_value= FloatParameter("Set Field Bias Value", default = parameters_from_file['field_bias_value'], units="Oe", group_by={"mode": lambda v: v =="CIMSMode" })


    
    #GeneratorParameters 
    generator_frequency = FloatParameter("Generator Frequency", default = parameters_from_file["generator_frequency"], units="Hz", maximum=31.8e9, group_by={"mode": lambda v: v == "FMRMode", "set_generator": lambda v: v != "none", "mode_fmr": lambda v: v == "const f"})
    generator_power = FloatParameter("Generator Power", default = parameters_from_file["generator_power"], units="dBm", group_by={"mode": lambda v: v == "FMRMode", "set_generator": lambda v: v != "none"})
    
    #Analyzer Parameters 

    #GaussmeterParameters 
    gaussmeter_range = ListParameter("Gaussmeter Range", default = parameters_from_file["gaussmeter_range"], choices=[1,2,3,4,5], group_by={"set_gaussmeter": lambda v: v == "Lakeshore"})
    gaussmeter_resolution = ListParameter("Gaussmeter Resolution", default = parameters_from_file["gaussmeter_resolution"],choices=["3 digits", "4 digits", "5 digits"], group_by={"set_gaussmeter": lambda v: v == "Lakeshore"})

    #LFGeneratorParamters
    lfgen_freq = FloatParameter("LF Generator Frequency", default = parameters_from_file["lfgen_freq"], units="Hz", group_by = {"mode": lambda v: v == "FMRMode", "set_lfgen": lambda v: v != "none" and  v != "SR830", "set_measdevice":lambda v: v=="LockIn"})
    lfgen_amp = FloatParameter("LF Generator Amplitude", default = parameters_from_file["lfgen_amp"], units="V", group_by = {"mode": lambda v: v == "FMRMode", "set_lfgen": lambda v: v != "none" and  v != "SR830", "set_measdevice":lambda v: v=="LockIn"})
    
    #RotationStationParameters 
    rotation_axis = ListParameter("Rotation axis", default = parameters_from_file["rotation_axis"], choices=["Polar", "Azimuthal"], group_by={"set_rotationstation": lambda v: v == True})
    rotation_polar_constant  = FloatParameter("Polar constant angle", default = parameters_from_file["rotation_polar_constant"],  group_by={"set_rotationstation": lambda v: v == True, "rotation_axis": lambda v: v == "Azimuthal"})
    rotation_azimuth_constant =  FloatParameter("Azimuthal constant angle", default = parameters_from_file["rotation_azimuth_constant"], group_by={"set_rotationstation": lambda v: v == True, "rotation_axis": lambda v: v == "Polar"})
    set_polar_angle=FloatParameter("Set polar angle", default = parameters_from_file["set_polar_angle"], units="Deg", group_by={"set_rotationstation_const_angle": lambda v: v == True})
    set_azimuthal_angle=FloatParameter("Set azimuthal angle", default = parameters_from_file["set_azimuthal_angle"], units="Deg", group_by={"set_rotationstation_const_angle": lambda v: v == True})

    #pulsegenerator parameters
    pulsegenerator_offset=FloatParameter("pulsegenerator offset", default = parameters_from_file["pulsegenerator_offset"], group_by={"mode": lambda v: v == "CIMSMode", "set_pulsegenerator": lambda v: v == "Agilent 2912" or v=="Tektronix 10,070A" or v=="Keithley 2636"})
    pulsegenerator_duration=FloatParameter("pulsegenerator duration", default = parameters_from_file["pulsegenerator_duration"], group_by={"mode": lambda v: v == "CIMSMode", "set_pulsegenerator": lambda v: v != "none"})
    pulsegenerator_pulsetype=ListParameter("pulsegenerator pulsetype", default = parameters_from_file["pulsegenerator_pulsetype"],choices=["VOLT", "CURR"], group_by={"mode": lambda v: v == "CIMSMode", "set_pulsegenerator": lambda v: v != "none" and v!="Tektronix 10,070A"})
    pulsegenerator_channel=ListParameter("pulsegenerator channel", default = parameters_from_file["pulsegenerator_channel"],choices=["Channel A","Channel B"], group_by={"mode": lambda v: v == "CIMSMode", "set_pulsegenerator": lambda v: v != "none" and v!="Tektronix 10,070A"})
    pulsegenerator_compliance = FloatParameter("Pulsegenerator compliance", default = parameters_from_file["pulsegenerator_compliance"], group_by={"mode": lambda v: v == "CIMSMode", "set_pulsegenerator": lambda v: v != "none" and v!="Tektronix 10,070A"})
    pulsegenerator_source_range=FloatParameter("Pulsegenerator sourcerange", default = parameters_from_file["pulsegenerator_source_range"], group_by={"mode": lambda v: v == "CIMSMode", "set_pulsegenerator": lambda v: v == "Keithley 2636"})

    DEBUG = 1

    DATA_COLUMNS = ['Voltage (V)', 'Normalized voltage (a.u.)', 'Current (A)', 'Resistance (ohm)', 'Field (Oe)', 'Frequency (Hz)', 'X (V)', 'Normalized X (a.u.)', 'Y (V)', 'Phase', 'Polar angle (deg)', 'Azimuthal angle (deg)' ]

    path_file = SaveFilePath() 

    
    ################ STARTUP ################## 
    def startup(self):
        for i in self.used_parameters_list:
            self.param = eval("self."+i)
            self.parameters[i] = self.param
        
        self.save_parameter.WriteFile(self.parameters)
        
        match self.mode:
            case "ResistanceMode":
                self.resistancemode = ResistanceMode(self.vector, self.mode_resistance, self.sourcemeter_bias, self.set_sourcemeter, self.set_multimeter, self.set_gaussmeter, self.set_field, self.set_automaticstation, self.set_switch, self.set_kriostat, self.set_rotationstation,self.set_rotationstation_const_angle,self.return_the_rotationstation, self.address_sourcemeter, self.address_multimeter, self.address_gaussmeter, self.address_switch, self.delay_field, self.delay_lockin, self.delay_bias, self.sourcemter_source, self.sourcemeter_compliance, self.sourcemeter_channel, self.sourcemeter_limit, self.sourcemeter_nplc, self.sourcemeter_average, self.multimeter_function, self.multimeter_resolution, self.multimeter_autorange, self.multimeter_range, self.multimeter_average, self.field_constant, self.gaussmeter_range, self.gaussmeter_resolution, self.multimeter_nplc, self.address_daq, self.field_step, self.address_rotationstation, self.constant_field_value,self.rotation_axis, self.rotation_polar_constant, self.rotation_azimuth_constant,self.set_polar_angle,self.set_azimuthal_angle)
                self.points = self.resistancemode.generate_points()
                self.resistancemode.initializing()
            case "HarmonicMode":
                self.harmonicmode = HarmonicMode(self.set_automaticstation, 
                 self.set_lockin, self.set_field, self.set_gaussmeter,  self.set_rotationstation, self.address_lockin, self.address_gaussmeter, self.vector, self.delay_field, self.delay_lockin, self.delay_bias, self.lockin_average, self.lockin_input_coupling, self.lockin_reference_source, self.lockin_dynamic_reserve, self.lockin_input_connection, self.lockin_sensitivity, self.lockin_timeconstant, self.lockin_autophase, self.lockin_frequency, self.lockin_harmonic, self.lockin_sine_amplitude,  self.lockin_channel1, self.lockin_channel2, self.set_field_value, self.field_constant, self.gaussmeter_range, self.gaussmeter_resolution, self.address_daq, self.field_step) 
                self.points = self.harmonicmode.generate_points()
                self.harmonicmode.initializing()
            case "FMRMode":
                self.fmrmode = FMRMode(self.set_automaticstation, self.set_lockin, self.set_field, self.set_gaussmeter, self.set_generator, self.set_rotationstation, self.address_lockin, self.address_gaussmeter, self.vector, self.delay_field, self.delay_lockin, self.delay_bias, self.lockin_average, self.lockin_input_coupling, self.lockin_reference_source,self.lockin_dynamic_reserve, self.lockin_input_connection, self.lockin_sensitivity, self.lockin_timeconstant, self.lockin_autophase, self.lockin_frequency, self.lockin_harmonic, self.lockin_sine_amplitude, self.lockin_channel1, self.lockin_channel2, self.set_field_value, self.field_constant, self.gaussmeter_range, self.gaussmeter_resolution, self.address_generator, self.set_field_value_fmr, self.generator_frequency, self.generator_power,  self.mode_fmr, self.address_daq, self.set_lfgen, self.address_lfgen, self.lfgen_freq, self.lfgen_amp, self.field_step, self.set_rotationstation, self.address_rotationstation, None, self.rotation_axis, self. rotation_polar_constant, self.rotation_azimuth_constant, self.set_multimeter, self.address_multimeter, self.multimeter_function, self.multimeter_resolution, self.multimeter_autorange, self.multimeter_range, self.multimeter_average, self.multimeter_nplc, self.set_measdevice)
                self.points = self.fmrmode.generate_points()
                self.fmrmode.initializing()
                self.fmrmode.begin(self.points[0])
            case "CalibrationFieldMode": 
                self.calibrationmode = FieldCalibrationMode(self.set_field, self.set_gaussmeter, self.address_daq, self.address_gaussmeter, self.vector, self.delay_field)
                self.calibrationmode.initializing()


            case "CIMSMode":
                self.CIMSmode = CIMSMode(self.vector, self.mode_cims_relays, self.sourcemeter_bias, self.set_sourcemeter, self.set_multimeter,self.set_pulsegenerator, self.set_gaussmeter, self.set_field, self.set_automaticstation, self.set_switch, self.set_kriostat, self.set_rotationstation,self.set_rotationstation_const_angle,self.return_the_rotationstation, self.address_sourcemeter, self.address_multimeter,self.address_pulsegenerator, self.address_gaussmeter, self.address_switch, self.delay_field, self.delay_measurement, self.delay_bias, self.sourcemter_source, self.sourcemeter_compliance, self.sourcemeter_channel, self.sourcemeter_limit, self.sourcemeter_nplc, self.sourcemeter_average, self.multimeter_function, self.multimeter_resolution, self.multimeter_autorange, self.multimeter_range, self.multimeter_average, self.field_constant, self.gaussmeter_range, self.gaussmeter_resolution, self.multimeter_nplc, self.address_daq, self.field_step, self.address_rotationstation, self.constant_field_value,self.rotation_axis, self.rotation_polar_constant, self.rotation_azimuth_constant,self.pulsegenerator_duration,self.pulsegenerator_offset,self.pulsegenerator_pulsetype,self.pulsegenerator_channel,self.pulsegenerator_compliance,self.pulsegenerator_source_range,self.field_bias_value,self.remagnetization,self. remagnetization_value,self.remagnetization_time,self.hold_the_field_after_measurement,self.remanency_correction,self.remanency_correction_time,self.set_polar_angle,self.set_azimuthal_angle)
                self.points = self.CIMSmode.generate_points()
                self.CIMSmode.initializing()

                


#################################### PROCEDURE##############################################
    def execute(self):
        match self.mode:
            case "ResistanceMode":
                self.counter = 0
                for point in self.points:
                   self.result = self.resistancemode.operating(point)
                   self.emit('results', self.result) 
                   self.emit('progress', 100 * self.counter / len(self.points))
                   self.counter = self.counter + 1
                   if self.should_stop():
                    log.warning("Caught the stop flag in the procedure")
                    break
                self.resistancemode.end()
            case "HarmonicMode":
                self.counter = 0
                for point in self.points:
                   self.result = self.harmonicmode.operating(point)
                   self.emit('results', self.result) 
                   self.emit('progress', 100 * self.counter / len(self.points))
                   self.counter = self.counter + 1
                   if self.should_stop():
                    log.warning("Caught the stop flag in the procedure")
                    break
                self.harmonicmode.end()
            case "FMRMode":
                self.counter = 0
                sleep(10)
                
                results_class: Results = window.manager.running_experiment().results                    
                
                for point in self.points:
                    
                    start = time()
                    self.result = self.fmrmode.operating(point)
                    window.set_single_measurement_duration(round(time() - start))
                    
                    self.emit('results', self.result)
                   
                    if self.fmrmode.do_recal_norm:
                        data = results_class.data
                        with open(results_class.data_filename, "w") as f:
                            f.write(results_class.header())
                            f.write(results_class.labels())
                            for row in range(len(data)):
                                if self.set_measdevice == "LockIn":
                                    data.loc[row, 'Normalized X (a.u.)'] = (float(data.loc[row, 'X (V)']) - self.fmrmode.min_x) / (self.fmrmode.max_x - self.fmrmode.min_x)
                                else:
                                    data.loc[row, 'Normalized voltage (a.u.)'] = (float(data.loc[row, 'Voltage (V)']) - self.fmrmode.min_voltage) / (self.fmrmode.max_voltage - self.fmrmode.min_voltage)
                                f.write(results_class.format(data.iloc[row].to_dict()) + "\n")
                    
                    self.emit('progress', 100 * self.counter / len(self.points))
                    self.counter = self.counter + 1
                    if self.should_stop():
                        log.warning("Caught the stop flag in the procedure")
                        break
                self.fmrmode.end()
                #    self.set_calibration_constant(self.result[1])
            case "CalibrationFieldMode": 
                self.result = self.calibrationmode.operating()
                self.emit('results', self.result[0])
                window.set_calibration_constant(self.result[1])
                self.calibrationmode.end()
                
                self.parameters["field_constant"] = self.result[1]
                self.save_parameter.WriteFile(self.parameters)
                

            case "CIMSMode":
                self.counter = 0
                for point in self.points:
                   self.result = self.CIMSmode.operating(point)
                   self.emit('results', self.result) 
                   self.emit('progress', 100 * self.counter / len(self.points))
                   self.counter = self.counter + 1
                   if self.should_stop():
                    log.warning("Caught the stop flag in the procedure")
                    break
                self.CIMSmode.end()

    
    def shutdown(self):
        pass
    
    # def get_estimates(self, sequence_length=None):
    #                 start, number, stop =self.vector.split(',')
    #                 iterations = len(linspace(float(start), float(stop), int(number)))
    #                 self.delay = self.single_measurement_duration
    #                 duration = iterations * self.delay
    #                 total_duration = duration * (sequence_length if sequence_length else 1)
    #                 estimates = [
    #                     ("Total duration", str(timedelta(seconds=total_duration))),
    #                     ('Measurement finished at', str((datetime.now() + timedelta(seconds=duration)).strftime("%Y-%m-%d %H:%M:%S"))),
    #                 ]
    #                 return estimates
        

class MainWindow(ManagedDockWindow):
    # last = False
    # wynik = 0
    # wynik_list = []
    def __init__(self):
        super().__init__(
            procedure_class= SpinLabMeasurement,

            inputs = ['mode', 'sample_name', 'vector', 'mode_resistance', 'mode_fmr', 'mode_harmonic', 'set_sourcemeter','set_pulsegenerator', 'set_multimeter', 'set_gaussmeter', 'set_field', 'set_lockin', 'set_automaticstation', 'set_rotationstation','set_rotationstation_const_angle','address_rotationstation','set_polar_angle','set_azimuthal_angle','rotation_axis', 'rotation_polar_constant', 'rotation_azimuth_constant','set_switch', 'set_kriostat', 'set_lfgen', 'set_analyzer', 'set_generator', 'address_sourcemeter', 'address_multimeter','address_daq' , 'address_gaussmeter', 'address_lockin', 'address_switch', 'address_analyzer', 'address_generator', 'address_lfgen','address_pulsegenerator','sourcemter_source', 'sourcemeter_compliance', 'sourcemeter_channel', 'sourcemeter_limit', 'sourcemeter_nplc', 'sourcemeter_average', 'sourcemeter_bias', 'multimeter_function', 'multimeter_resolution','multimeter_nplc', 'multimeter_autorange', 'multimeter_range', 'multimeter_average', 'field_constant', 'constant_field_value', 'gaussmeter_range', 'gaussmeter_resolution', 'lockin_average', 'lockin_input_coupling', 'lockin_reference_source', 'lockin_dynamic_reserve', 'lockin_input_connection', 'lockin_sensitivity','lockin_frequency', 'lockin_harmonic','lockin_sine_amplitude',  'lockin_timeconstant', 'lockin_channel1','lockin_channel2' ,'lockin_autophase','generator_frequency', 'generator_power','lfgen_freq', 'lfgen_amp', 'set_field_value','set_field_value_fmr', 'field_step', 'delay_field', 'delay_lockin', 'delay_bias','mode_cims_relays','pulsegenerator_offset','pulsegenerator_duration','pulsegenerator_pulsetype','pulsegenerator_channel','pulsegenerator_compliance','pulsegenerator_source_range','delay_measurement','field_bias_value','remanency_correction','remanency_correction_time','remagnetization','remagnetization_value','remagnetization_time','hold_the_field_after_measurement','return_the_rotationstation'],
            x_axis=['Field (Oe)', 'Voltage (V)'],
            y_axis=['Field (Oe)', 'Resistance (ohm)'],
            directory_input=True,  
            sequencer=True,                               
            sequencer_inputs=["sourcemeter_bias","lockin_frequency","field_constant","set_field_value_fmr", "set_field_value", "field_step","constant_field_value","field_bias_value", "generator_frequency", "generator_power", "lfgen_freq", "lfgen_amp", "rotation_polar_constant", "rotation_azimuth_constant", "set_polar_angle", "set_azimuthal_angle", "pulsegenerator_offset", "pulsegenerator_duration"],
            inputs_in_scrollarea=True,
        )
       
        self.setWindowTitle('SpinLab Measurement System v.0.90')

        #self.directory = self.procedure_class.path_file.ReadFile()
        
        self.inputs.single_measurement_duration.setEnabled(False)

        self.directory = self.procedure_class.path_file.ReadFile()

    
    def set_calibration_constant(self, value):
        self.inputs.field_constant.setValue(value)
    
    def set_calibration_filename(self, value):
        self.inputs.sample_name.setValue(value)
        
    def set_single_measurement_duration(self, value):
        self.inputs.single_measurement_duration.setValue(value)
        

    def queue(self, procedure=None):
        directory = self.directory
        self.procedure_class.path_file.WriteFile(directory)
        
        if procedure is None:
            procedure = self.make_procedure()
        if procedure.mode == "CalibrationFieldMode":
            procedure.sample_name = "calibration"
        name_of_file = procedure.sample_name
        filename = unique_name(directory, prefix="{0}__{1}_".format(name_of_file,procedure.mode))
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)
        self.manager.queue(experiment)
        
    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
