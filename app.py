import logging
import sys
from time import time
from logic.find_instrument import FindInstrument
from logic.save_results_path import SaveFilePath
from pymeasure.experiment.procedure import Procedure
from pymeasure.display.Qt import QtWidgets, QtCore
from pymeasure.display.windows.managed_dock_window import ManagedDockWindow
from pymeasure.experiment import Procedure, FloatParameter, BooleanParameter, IntegerParameter, Parameter, ListParameter, Metadata
from logic.find_instrument import FindInstrument
from logic.save_parameters import SaveParameters
from logic.convert_value import convert_value
from datetime import datetime
from datetime import timedelta

from modules.control_widget_water_cooler import WaterCoolerControl
from modules.control_widget_lakeshore336 import Lakeshore336Control
from modules.control_widget_camera import CameraControl
from modules.generator_widget_automatic_station import AutomaticStationGenerator

from pymeasure.display.inputs import Input

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)  # enable highdpi scaling
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)  # use highdpi icons

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class SpinLabMeasurement(Procedure):
    # licznik = 1 # licznik
    parameters = {}
    find_instruments = FindInstrument()
    save_parameter = SaveParameters()

    SETTINGS, PARAMETERS, NOT_VISIBLE = 0, 1, 2

    finded_instruments = find_instruments.show_instrument()
    daq_channels = [addr for addr in finded_instruments if "Dev" in addr]
    used_parameters_list=['mode', 'sample_name', 'vector', 'mode_resistance', 'mode_fmr', 'set_measdevice_fmr', 'set_measdevice_qm', 'set_sourcemeter', 'set_multimeter','set_pulsegenerator', 'set_gaussmeter', 'set_field_cntrl', 'set_lockin', 'set_automaticstation', 'set_rotationstation','set_switch', 'set_kriostat', 'set_lfgen', 'set_analyzer', 'set_generator', 'address_sourcemeter', 'address_multimeter','address_daq', 'address_polarity_control' , 'address_gaussmeter', 'address_lockin', 'address_switch', 'address_analyzer', 'address_generator', 'address_lfgen','address_pulsegenerator','address_automaticstation','sourcemeter_source', 'sourcemeter_compliance', 'sourcemeter_channel', 'sourcemeter_limit', 'sourcemeter_nplc', 'sourcemeter_average', 'sourcemeter_bias', 'multimeter_function', 'multimeter_resolution','multimeter_nplc', 'multimeter_autorange', 'multimeter_range', 'multimeter_average', 'field_constant', 'gaussmeter_range', 'gaussmeter_resolution', 'lockin_average', 'lockin_input_coupling', 'lockin_reference_source', 'lockin_dynamic_reserve', 'lockin_input_connection', 'lockin_sensitivity','lockin_frequency', 'lockin_harmonic','lockin_sine_amplitude',  'lockin_timeconstant', 'lockin_slope', 'lockin_channel1','lockin_channel2' ,'lockin_autophase','generator_frequency', 'generator_power','generator_channel','lfgen_freq', 'lfgen_amp','set_field_value_fmr', 'field_step', 'delay_field', 'delay_lockin', 'delay_bias', 'rotation_axis', 'rotation_polar_constant', 'rotation_azimuth_constant', 'constant_field_value', 'address_rotationstation', 'mode_cims_relays','pulsegenerator_offset','pulsegenerator_duration','pulsegenerator_pulsetype','pulsegenerator_channel','delay_measurement','pulsegenerator_compliance','pulsegenerator_source_range','return_the_rotationstation','field_bias_value', 'polarity_control_enabled', 'remagnetization','remagnetization_value','remagnetization_time','hold_the_field_after_measurement','remanency_correction','set_polar_angle','set_azimuthal_angle','set_polar_angle_fmr','set_azimuthal_angle_fmr','remanency_correction_time', 'layout_type', 'kriostat_temperature','disconnect_length','sample_in_plane','go_init_position']
    parameters_from_file = save_parameter.ReadFile()
    #################################################################### METADATA #####################################################################
    time_of_measurement = Metadata("Measurement start time", default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    #################################################################### PARAMETERS #####################################################################
    mode = ListParameter("Mode", default="ResistanceMode", choices=['QuickMeasurement', 'ResistanceMode', 'FMRMode', 'VSMMode', 'HarmonicMode', 'CalibrationFieldMode', 'PulseMode','CIMSMode'], vis_cond=(PARAMETERS))
    mode_resistance = BooleanParameter("Use 4-points measurement", default = False, vis_cond=(PARAMETERS, lambda mode: mode == "ResistanceMode"))
    mode_fmr = ListParameter("FMR Mode", default = "V-FMR", choices = ["V-FMR", "ST-FMR"], vis_cond=(SETTINGS, lambda mode: mode == "FMRMode"))
    mode_cims_relays = BooleanParameter("Use relays", default = False, vis_cond=(SETTINGS, lambda mode: mode == "CIMSMode"))

    return_the_rotationstation = BooleanParameter("Return the rotationstation", default = True, vis_cond=(PARAMETERS, lambda mode, set_rotationstation: (mode == "CIMSMode" or mode == "ResistanceMode" or mode == "HarmonicMode" or mode == "FMRMode") and set_rotationstation == True))

    remagnetization=BooleanParameter("Remagnetize sample", default = False, vis_cond=(SETTINGS, lambda mode: mode == "CIMSMode"))
    remagnetization_value=FloatParameter("Remagnetization value", default = 0, units="Oe", vis_cond=(SETTINGS, lambda mode: mode == "CIMSMode"))
    remagnetization_time=FloatParameter("Remagnetization time", default = 0, units="s", vis_cond=(SETTINGS, lambda mode: mode == "CIMSMode"))

    remanency_correction = BooleanParameter("Remanency correction", default = False, vis_cond=(SETTINGS, lambda mode: mode == "CIMSMode"))
    remanency_correction_time=FloatParameter("Remanency correction time", default = 0, units="s", vis_cond=(SETTINGS, lambda mode: mode == "CIMSMode"))

    hold_the_field_after_measurement=BooleanParameter("Hold the field after measurement", default = False, vis_cond=(PARAMETERS, lambda mode: mode == "CIMSMode" or mode == "HarmonicMode" or mode == "FMRMode"))

    # Hardware
    set_sourcemeter=ListParameter("Sourcemeter", choices=["None", "Keithley 2400", "Keithley 2636", "Agilent 2912"], vis_cond=(SETTINGS, lambda mode, set_measdevice_qm: mode == "ResistanceMode" or mode == "CIMSMode" or (mode == "QuickMeasurement" and set_measdevice_qm == "Sourcemeter")))
    set_multimeter = ListParameter("Multimeter", choices=["None", "Agilent 34400"], vis_cond=(SETTINGS, lambda mode, mode_resistance, set_measdevice_fmr, set_measdevice_qm: (mode == "ResistanceMode" and mode_resistance == True) or (mode == "FMRMode" and set_measdevice_fmr == "Multimeter") or (mode == "QuickMeasurement" and set_measdevice_qm == "Multimeter")))
    set_gaussmeter = ListParameter("Gaussmeter", choices=["None", "Lakeshore", "GM700"], vis_cond=(SETTINGS, lambda mode: mode == "ResistanceMode" or mode == "HarmonicMode" or mode == "FMRMode" or mode == "CalibrationFieldMode" or mode=="CIMSMode"))
    set_field_cntrl = ListParameter("Magnetic Field Controller", choices = ["None", "DAQ", "Lockin"], vis_cond=(SETTINGS, lambda mode: mode == "ResistanceMode" or mode == "HarmonicMode" or mode == "FMRMode" or mode == "CalibrationFieldMode" or mode=="CIMSMode"))
    set_lockin = ListParameter("Lockin", choices = ["None", "Zurich", "SR830"], vis_cond=(SETTINGS, lambda mode, set_measdevice_fmr: mode == "HarmonicMode" or (mode == "FMRMode" and set_measdevice_fmr == "LockIn")))
    set_automaticstation = BooleanParameter("Automatic Station",  default =  False, vis_cond=(PARAMETERS, lambda mode: mode != "CalibrationFieldMode" and mode != "HarmonicMode" and mode != "QuickMeasurement"))
    set_rotationstation = BooleanParameter("Rotation Station", default = False, vis_cond=(PARAMETERS, lambda mode: mode != "CalibrationFieldMode" and mode != "QuickMeasurement"))
    set_switch = BooleanParameter("Switch", default = False, vis_cond=(PARAMETERS, lambda mode: mode != "CalibrationFieldMode" and mode != "QuickMeasurement" and mode != "FMRMode" and mode != "HarmonicMode"))
    set_kriostat = BooleanParameter("Kriostat", default = False, vis_cond=(PARAMETERS, lambda mode: mode != "QuickMeasurement"))
    set_lfgen = ListParameter("LF Generator", choices = ["None", "SR830", "HP33120A"], vis_cond=(SETTINGS, lambda mode: mode == "FMRMode"))
    set_analyzer = ListParameter("Vector Analyzer", choices = ["None", 'VectorAnalyzer'], vis_cond=(SETTINGS, lambda mode: mode == "VSMMode"))
    set_generator = ListParameter("RF Generator", choices = ["None", "Agilent", "Windfreak"], vis_cond=(SETTINGS, lambda mode: mode == "FMRMode"))
    set_pulsegenerator=ListParameter("Pulse Generator", choices=["None", "Agilent 2912","Tektronix 10,070A","Keithley 2636"], vis_cond=(SETTINGS, lambda mode: mode == "CIMSMode"))
    set_measdevice_fmr = ListParameter("Measurement Device FMR", choices=["LockIn", "Multimeter"], vis_cond=(SETTINGS, lambda mode: mode == "FMRMode"))
    set_measdevice_qm = ListParameter("Measurement Device QM", choices=["Sourcemeter", "Multimeter"], vis_cond=(SETTINGS, lambda mode: mode == "QuickMeasurement"))

    # Hardware address
    address_sourcemeter=ListParameter("Sourcemeter address", choices=finded_instruments, vis_cond=(SETTINGS, lambda mode, set_sourcemeter, set_measdevice_qm: (mode == "ResistanceMode" or mode == "CIMSMode" or (mode == "QuickMeasurement" and set_measdevice_qm == "Sourcemeter")) and set_sourcemeter != "None"))
    address_multimeter=ListParameter("Multimeter address", choices=finded_instruments, vis_cond=(SETTINGS, lambda mode, set_measdevice_fmr, set_multimeter, mode_resistance, set_measdevice_qm: ((mode == "FMRMode" and set_measdevice_fmr == "Multimeter") or (mode == "ResistanceMode" and mode_resistance == True) or (mode == "QuickMeasurement" and set_measdevice_qm == "Multimeter")) and set_multimeter != "None"))
    address_gaussmeter=ListParameter("Gaussmeter address", choices=finded_instruments, vis_cond=(SETTINGS, lambda mode, set_gaussmeter: (mode == "ResistanceMode" or mode == "HarmonicMode" or mode == "FMRMode" or mode == "CalibrationFieldMode" or mode=="CIMSMode") and set_gaussmeter != "None"))
    address_lockin=ListParameter("Lockin address", choices=finded_instruments, vis_cond=(SETTINGS, lambda mode, set_measdevice_fmr: mode == "HarmonicMode" or (mode == "FMRMode" and set_measdevice_fmr == "LockIn")))
    address_switch=ListParameter("Switch address", choices=finded_instruments, vis_cond=(SETTINGS, lambda mode: mode == "ResistanceMode"))
    address_analyzer=ListParameter("Analyzer address", choices=finded_instruments, vis_cond=(SETTINGS, lambda mode: mode == "VSMMode"))
    address_generator=ListParameter("Generator address", choices=finded_instruments, vis_cond=(SETTINGS, lambda mode, set_generator: mode == "FMRMode" and set_generator != "None"))
    address_daq = ListParameter("DAQ address",  choices=["None"] + daq_channels, vis_cond=(SETTINGS, lambda mode, set_field_cntrl: (mode == "ResistanceMode" or mode == "HarmonicMode" or mode == "FMRMode" or mode == "CalibrationFieldMode" or mode=="CIMSMode") and set_field_cntrl != "None"))
    address_polarity_control = ListParameter("Polarity control address", choices=["None"] + daq_channels, vis_cond=(SETTINGS, lambda mode, polarity_control_enabled: polarity_control_enabled == True and mode=="FMRMode"))
    address_lfgen = ListParameter("LF Generator address", choices=finded_instruments, vis_cond=(SETTINGS, lambda mode, set_lfgen: mode == "FMRMode" and set_lfgen != "None" and set_lfgen != "SR830"))
    address_automaticstation=ListParameter("Automatic station address", choices=finded_instruments, vis_cond=(SETTINGS, lambda mode, set_automaticstation: (mode == "ResistanceMode" or mode == "CIMSMode") and set_automaticstation == True))
    if set_rotationstation:
        address_rotationstation=Parameter("RotationStation address", default = "None", vis_cond=(SETTINGS, lambda set_rotationstation: set_rotationstation == True))

    address_pulsegenerator=ListParameter("Pulse generator address", choices=finded_instruments, vis_cond=(SETTINGS, lambda mode, set_pulsegenerator: mode == "CIMSMode" and set_pulsegenerator != "None"))

    address_list = ["address_sourcemeter", "address_multimeter", "address_gaussmeter", "address_lockin", "address_switch", "address_analyzer", "address_generator", "address_daq", "address_polarity_control","address_lfgen", "address_pulsegenerator", "address_automaticstation"]

    # MeasurementParameters
    sample_name = Parameter("Sample name", default = "None", vis_cond=(NOT_VISIBLE)) 
    vector = Parameter("Vector", vis_cond=(PARAMETERS))
    delay_field = FloatParameter("Delay Field", default = 1, units="s", vis_cond=(PARAMETERS, lambda mode: mode != "QuickMeasurement"))
    delay_lockin = FloatParameter("Delay Lockin", default = 0.5, units="s", vis_cond=(PARAMETERS, lambda mode: mode == "HarmonicMode" or mode == "FMRMode"))
    delay_bias = FloatParameter("Delay Bias", default = 0.5, units="s", vis_cond=(PARAMETERS, lambda mode: mode == "ResistanceMode"))
    delay_measurement = FloatParameter("Delay sourcemeter measurement", default = 0.5, units="s", vis_cond=(SETTINGS, lambda mode: mode == "CIMSMode"))

    #########  SETTINGS PARAMETERS ##############
    # SourcemeterParameters
    sourcemeter_params_vis_cond = (SETTINGS ,lambda mode, set_sourcemeter, address_sourcemeter, set_measdevice_qm: (mode == "ResistanceMode" or mode == "CIMSMode" or (mode == "QuickMeasurement" and set_measdevice_qm == "Sourcemeter")) and set_sourcemeter != "None" and address_sourcemeter != "None")
    sourcemeter_source = ListParameter("Sourcemeter Source", choices=["VOLT", "CURR"],  vis_cond=sourcemeter_params_vis_cond)
    sourcemeter_compliance = FloatParameter("Sourcemeter compliance", default = parameters_from_file["sourcemeter_compliance"],  vis_cond=sourcemeter_params_vis_cond)
    sourcemeter_channel = ListParameter("Sourcemeter CH", choices = ["Channel A", "Channel B"],  vis_cond=sourcemeter_params_vis_cond)
    sourcemeter_limit = FloatParameter("Sourcemeter limit", default = parameters_from_file["sourcemeter_limit"],  vis_cond=sourcemeter_params_vis_cond)
    sourcemeter_nplc = FloatParameter("Sourcemeter NPLC", default = 1,  vis_cond=sourcemeter_params_vis_cond)
    sourcemeter_average = IntegerParameter("Sourcemeter average", default = 3,  vis_cond=sourcemeter_params_vis_cond)
    sourcemeter_bias = FloatParameter("Sourcemeter bias", default = 0,  vis_cond=sourcemeter_params_vis_cond)

    # MultimeterParameters
    multimeter_params_vis_cond = (SETTINGS, lambda mode, set_measdevice_fmr, set_multimeter, address_multimeter, mode_resistance, set_measdevice_qm: set_multimeter != "None" and address_multimeter != "None" and ((mode == "ResistanceMode" and mode_resistance == True) or (mode == "FMRMode" and set_measdevice_fmr == "Multimeter") or (mode == "QuickMeasurement" and set_measdevice_qm == "Multimeter")))
    multimeter_function = ListParameter("Multimeter function", choices=[ "DCV", "DCV_RATIO", "ACV", "DCI", "ACI", "R2W", "R4W", "FREQ", "PERIOD", "CONTINUITY", "DIODE"], vis_cond=multimeter_params_vis_cond)
    multimeter_resolution = FloatParameter("Multimeter resolution",default = parameters_from_file["multimeter_resolution"], vis_cond=multimeter_params_vis_cond)
    multimeter_autorange = BooleanParameter("Multimeter autorange", default = True, vis_cond=multimeter_params_vis_cond)
    multimeter_range = FloatParameter("Multimeter range", default = parameters_from_file["multimeter_range"], vis_cond=multimeter_params_vis_cond)
    multimeter_average = IntegerParameter("Multimeter average", default = 3, vis_cond=multimeter_params_vis_cond)
    multimeter_nplc = ListParameter("Multimeter NPLC", default = 1, choices=[0.02, 0.2, 1, 10, 100, 'MIN', 'MAX'], vis_cond=multimeter_params_vis_cond)

    # LockinParameters
    lockin_params_vis_cond = (SETTINGS, lambda mode, set_measdevice_fmr, set_lockin, address_lockin: set_lockin != "None" and address_lockin != "None" and (mode == "HarmonicMode" or (mode == "FMRMode" and set_measdevice_fmr == "LockIn")))
    lockin_average = IntegerParameter("Lockin Average", default = 3, vis_cond=lockin_params_vis_cond)
    lockin_input_coupling = ListParameter("Lockin Input Coupling", choices = ["AC", "DC"], vis_cond=lockin_params_vis_cond)
    lockin_reference_source = ListParameter("Lockin Reference Source", choices=["Internal", "External"], vis_cond=lockin_params_vis_cond)
    lockin_dynamic_reserve = ListParameter("Lockin Dynamic Reserve", default = "Normal", choices=['High Reserve', 'Normal', 'Low Noise'], vis_cond=lockin_params_vis_cond)
    lockin_input_connection = ListParameter("Lockin Input Connection", choices = ["A", "A - B"], vis_cond=lockin_params_vis_cond)
    lockin_sensitivity = ListParameter("Lockin Sensitivity", default = "20 uV/pA", choices=["2 nV/fA", "5 nV/fA", "10 nV/fA", "20 nV/fA", "50 nV/fA", "100 nV/fA", "200 nV/fA", "500 nV/fA", "1 uV/pA", "2 uV/pA", "5 uV/pA", "10 uV/pA", "20 uV/pA", "50 uV/pA", "100 uV/pA", "200 uV/pA", "500 uV/pA", "1 mV/nA", "2 mV/nA", "5 mV/nA", "10 mV/nA", "20 mV/nA", "50 mV/nA", "100 mV/nA", "200 mV/nA", "500 mV/nA", "1 V/uA"], vis_cond=lockin_params_vis_cond)
    lockin_timeconstant = ListParameter("Lockin Time Constant", default = "30 ms", choices = ["10 us", "30 us", "100 us", "300 us", "1 ms", "3 ms", "10 ms", "30 ms", "100 ms", "300 ms", "1 s", "3 s", "10 s", "30 s", "100 s", "300 s", "1 ks", "3 ks", "10 ks", "30 ks"],vis_cond=lockin_params_vis_cond)
    lockin_slope = ListParameter("Lockin Slope", default="24 dB/Oct", choices = ["6 dB/Oct", "12 dB/Oct", "18 dB/Oct", "24 dB/Oct"], vis_cond=lockin_params_vis_cond)
    lockin_autophase = BooleanParameter("Lockin Autophase", default = False, vis_cond=lockin_params_vis_cond)
    lockin_channel1 = ListParameter("Lockin Channel 1", default = "X", choices = ["X", "Y", "R", "Theta", "Aux In 1", "Aux In 2", "Aux In 3", "Aux In 4"], vis_cond=lockin_params_vis_cond)
    lockin_channel2 = ListParameter("Lockin Channel 2", default = "Y", choices = ["X", "Y", "R", "Theta", "Aux In 1", "Aux In 2", "Aux In 3", "Aux In 4"], vis_cond=lockin_params_vis_cond)

    lockin_frequency = FloatParameter("Lockin Frequency", default = 1000, units="Hz", vis_cond = (SETTINGS ,lambda mode, set_measdevice_fmr, set_lockin, address_lockin, lockin_reference_source: set_lockin != "None" and address_lockin != "None" and (mode == "HarmonicMode" or (mode == "FMRMode" and set_measdevice_fmr == "LockIn")) and lockin_reference_source == "Internal"))
    lockin_harmonic = IntegerParameter("Lockin Harmonic", default = 1, vis_cond = (SETTINGS ,lambda mode, set_measdevice_fmr, set_lockin, address_lockin, lockin_reference_source: set_lockin != "None" and address_lockin != "None" and (mode == "HarmonicMode" or (mode == "FMRMode" and set_measdevice_fmr == "LockIn")) and lockin_reference_source == "Internal"))
    lockin_sine_amplitude = FloatParameter("Lockin Sine Amplitude", default = 1, units="V", vis_cond = (SETTINGS ,lambda mode, set_measdevice_fmr, set_lockin, address_lockin, lockin_reference_source: set_lockin != "None" and address_lockin != "None" and (mode == "HarmonicMode" or (mode == "FMRMode" and set_measdevice_fmr == "LockIn")) and lockin_reference_source == "Internal"))

    # FieldParameters
    field_constant = FloatParameter("Field Calibration Constant", default = 0, vis_cond=(SETTINGS, lambda mode: mode != "QuickMeasurement"))
    field_step = FloatParameter("Field sweep step", default = 100, units="Oe", vis_cond=(PARAMETERS, lambda mode: mode != "CalibrationFieldMode" and mode != "QuickMeasurement"))
    constant_field_value =  FloatParameter("Set Constant Field Value", default = 0, units="Oe", vis_cond=(PARAMETERS, lambda mode, set_rotationstation, mode_fmr: set_rotationstation == True and mode != "QuickMeasurement" or (mode == "FMRMode" and mode_fmr == "ST-FMR")))
    field_bias_value= FloatParameter("Set Field Bias Value", default = 0, units="Oe", vis_cond=(PARAMETERS, lambda mode: mode == "CIMSMode"))
    polarity_control_enabled = BooleanParameter("Polarity control", default = False, vis_cond=(SETTINGS, lambda mode: mode=="FMRMode"))

    # GeneratorParameters
    generator_params_vis_cond = (PARAMETERS, lambda mode, set_generator: mode == "FMRMode" and set_generator != "None")
    generator_frequency = FloatParameter("RF Generator Frequency", default = 3e9, units="Hz", maximum=31.8e9, vis_cond=generator_params_vis_cond)
    generator_power = FloatParameter("RF Generator Power", default = 0, units="dBm", vis_cond=generator_params_vis_cond)
    generator_channel = ListParameter("RF Generator Channel", choices=["A", "B"], vis_cond=(SETTINGS, lambda mode, set_generator: mode == "FMRMode" and set_generator != "None"))

    # GaussmeterParameters
    gaussmeter_params_vis_cond =  (SETTINGS, lambda mode, set_gaussmeter: mode != "QuickMeasurement" and set_gaussmeter == "Lakeshore")
    gaussmeter_range = ListParameter("Gaussmeter Range", default = 5, choices=[1,2,3,4,5], vis_cond =gaussmeter_params_vis_cond)
    gaussmeter_resolution = ListParameter("Gaussmeter Resolution", default = "4 digits", choices=["3 digits", "4 digits", "5 digits"], vis_cond =gaussmeter_params_vis_cond)

    # LFGeneratorParameters
    lf_gen_params_vis_cond = (PARAMETERS, lambda mode, set_lfgen: mode == "FMRMode" and set_lfgen != "None" and set_lfgen != "SR830")
    lfgen_freq = FloatParameter("LF Generator Frequency", default = 1000, units="Hz", vis_cond =lf_gen_params_vis_cond)
    lfgen_amp = FloatParameter("LF Generator Amplitude", default = 1, units="V", vis_cond =lf_gen_params_vis_cond)

    # RotationStationParameter
    rotation_axis = ListParameter("Rotation axis", default = parameters_from_file["rotation_axis"], choices=["Polar", "Azimuthal", "None"], vis_cond=(PARAMETERS, lambda mode, set_rotationstation: mode != "FMRMode" and set_rotationstation == True))
    rotation_polar_constant  = FloatParameter("Polar constant angle", default = parameters_from_file["rotation_polar_constant"],  vis_cond=(PARAMETERS, lambda mode, set_rotationstation, rotation_axis: set_rotationstation == True and rotation_axis == "Azimuthal" and mode != "FMRMode"))
    rotation_azimuth_constant =  FloatParameter("Azimuthal constant angle", default = parameters_from_file["rotation_azimuth_constant"], vis_cond=(PARAMETERS, lambda mode, set_rotationstation, rotation_axis: set_rotationstation == True and rotation_axis == "Polar" and mode != "FMRMode"))
    set_polar_angle=FloatParameter("Set polar angle", default = parameters_from_file["set_polar_angle"], units="Deg", vis_cond=(PARAMETERS, lambda set_rotationstation, rotation_axis: set_rotationstation == True and rotation_axis == "None"))
    set_azimuthal_angle=FloatParameter("Set azimuthal angle", default = parameters_from_file["set_azimuthal_angle"], units="Deg", vis_cond=(PARAMETERS, lambda set_rotationstation, rotation_axis: set_rotationstation == True and rotation_axis == "None"))
    set_polar_angle_fmr=FloatParameter("Set polar angle", default = parameters_from_file["set_polar_angle_fmr"], units="Deg", vis_cond=(PARAMETERS, lambda set_rotationstation, mode: set_rotationstation == True and mode == "FMRMode"))
    set_azimuthal_angle_fmr=FloatParameter("Set azimuthal angle", default = parameters_from_file["set_azimuthal_angle_fmr"], units="Deg", vis_cond=(PARAMETERS, lambda set_rotationstation, mode: set_rotationstation == True and mode == "FMRMode"))

    # pulsegenerator parameters
    pulsegenerator_offset=FloatParameter("pulsegenerator offset", default = parameters_from_file["pulsegenerator_offset"], vis_cond=(SETTINGS, lambda mode, set_pulsegenerator: mode == "CIMSMode" and set_pulsegenerator != "None"))
    pulsegenerator_duration= FloatParameter("pulsegenerator duration", default = parameters_from_file["pulsegenerator_duration"], units="s", vis_cond=(SETTINGS, lambda mode, set_pulsegenerator: mode == "CIMSMode" and set_pulsegenerator != "None"))
    pulsegenerator_pulsetype=ListParameter("pulsegenerator pulsetype", choices=["VOLT", "CURR"], vis_cond=(SETTINGS, lambda mode, set_pulsegenerator: mode == "CIMSMode" and set_pulsegenerator != "None" and set_pulsegenerator != "Tektronix 10,070A"))
    pulsegenerator_channel=ListParameter("pulsegenerator channel", choices=["Channel A","Channel B"], vis_cond=(SETTINGS, lambda mode, set_pulsegenerator: mode == "CIMSMode" and set_pulsegenerator != "None" and set_pulsegenerator != "Tektronix 10,070A"))
    pulsegenerator_compliance = FloatParameter("Pulsegenerator compliance", default = parameters_from_file["pulsegenerator_compliance"], vis_cond=(SETTINGS, lambda mode, set_pulsegenerator: mode == "CIMSMode" and set_pulsegenerator != "None" and set_pulsegenerator != "Tektronix 10,070A"))
    pulsegenerator_source_range=FloatParameter("Pulsegenerator sourcerange", default = parameters_from_file["pulsegenerator_source_range"], vis_cond=(SETTINGS, lambda mode, set_pulsegenerator: mode == "CIMSMode" and set_pulsegenerator == "Keithley 2636"))

    # kriostat parameters
    kriostat_temperature = FloatParameter("Kriostat Temperature", default = 290, units="K", vis_cond=(PARAMETERS, lambda set_kriostat: set_kriostat == True))

    # AutomaticStationParameters
    global_xyname=Parameter("Global \"[x,y,name]\"",default='', vis_cond=(NOT_VISIBLE))
    disconnect_length=FloatParameter("Disconnect length", default = 0.5, vis_cond=(PARAMETERS, lambda set_automaticstation: set_automaticstation == True))
    sample_in_plane=BooleanParameter("Perpendicular?", default=False,  vis_cond=(PARAMETERS, lambda set_automaticstation: set_automaticstation == True))
    go_init_position=BooleanParameter("Go to initialize position", default=False,  vis_cond=(PARAMETERS, lambda set_automaticstation: set_automaticstation == True))

    # Other parameters
    layout_type = BooleanParameter("Layout type", default=PARAMETERS, vis_cond=(NOT_VISIBLE))
    point_meas_duration = FloatParameter("Single measurement duration", default = 0, units="s", vis_cond=(NOT_VISIBLE))
    number_of_points = IntegerParameter("Number of points", default = 0, vis_cond=(NOT_VISIBLE))
    iterator= IntegerParameter("Iterator", default = 0, vis_cond=(NOT_VISIBLE))

    DEBUG = 1
    DATA_COLUMNS = [
        "Voltage (V)",
        "Current (A)",
        "Resistance (ohm)",
        "Field (Oe)",
        "Frequency (Hz)",
        "X (V)",
        "Y (V)",
        "Phase",
        "Polar angle (deg)",
        "Azimuthal angle (deg)",
        "Applied Voltage (V)",
    ]
    path_file = SaveFilePath()

    def refresh_parameters(self):
        """Enforces that all the parameters are re-cast and updated in the meta
        dictionary (from parents function of the same name). Additionally checks if the address is available and if not sets the parameter to None.
        """

        for name, parameter in self._parameters.items():
            value = getattr(self, name)
            try:
                parameter.value = value
            except ValueError as e:
                if name in self.address_list:
                    parameter.value = "None"
                    log.warning(f"Address: '{value}' not available! Setting parameter: '{name}' to 'None'")
                else:
                    raise e
            setattr(self, name, parameter.value)

    ################ STARTUP ##################
    def startup(self):
        # self.sample_name = window.filename_getter()

        self.time_of_measurement = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.has_next_callback=window.manager.experiments.has_next
        self.last_set_field = 0

        for param_name in self.used_parameters_list:
            param = getattr(self, param_name)
            self.parameters[param_name] = param

        self.save_parameter.WriteFile(self.parameters, window.directory, window.file_input.filename_base)

        if self.set_kriostat:
            try:
                window.devices_widget.lakeshore336_control.set_setpoint_wait(self.kriostat_temperature, window.manager.aborted)
            except AttributeError as e:
                logging.error("No kriostat control")

        from modules.measurement_mode import MeasurementMode
        from modules.resistance_mode import ResistanceMode
        from modules.harmonic_mode import HarmonicMode
        from modules.fmr_mode import FMRMode
        from modules.calibration_mode import FieldCalibrationMode
        from modules.cims_mode import CIMSMode

        self.update_field_constant = False
        self.selected_mode: MeasurementMode = None

        match self.mode:
            case "ResistanceMode":
                self.selected_mode = ResistanceMode(procedure=self)
            case "HarmonicMode":
                self.selected_mode = HarmonicMode(procedure=self)
            case "FMRMode":
                self.selected_mode = FMRMode(procedure=self)
            case "CalibrationFieldMode":
                self.selected_mode = FieldCalibrationMode(procedure=self)
                self.update_field_constant = True
            case "CIMSMode":
                self.selected_mode = CIMSMode(procedure=self)
            case _:
                raise NotImplementedError(f"Mode: '{self.mode}' is not implemented!")

        self.points = self.selected_mode.generate_points()
        self.selected_mode.initializing()

        window.inputs.number_of_points.setValue(len(self.points))

    #################################### PROCEDURE##############################################
    def execute(self):
        self.counter = 0

        for point in self.points:
            if self.should_stop():
                log.warning("Caught the stop flag in the procedure")
                break

            start_time = time()

            self.result = self.selected_mode.operating(point)
            self.counter = self.counter + 1

            self.emit("results", self.result)
            self.emit("progress", 100 * self.counter / len(self.points))
            self.emit("current_point", point)

            window.inputs.point_meas_duration.setValue(time() - start_time)

        self.selected_mode.end()
        if self.update_field_constant:
            window.set_calibration_constant(self.field_constant)
            self.update_field_constant = False
            
        self.emit("info", "")

    def shutdown(self):
        pass

    def get_estimates(self, sequence_length=None, sequence=None):
        duration = self.point_meas_duration * self.number_of_points
        total_duration = round(duration)
        if sequence_length is not None:
            total_duration = round(duration * (sequence_length if sequence_length > 0 else 1))
        estimates = [
            ("Single:", str(timedelta(seconds=round(duration)))),
            ("Total:", str(timedelta(seconds=total_duration))),
            ("Measurement finished at", str((datetime.now() + timedelta(seconds=total_duration)).strftime("%Y-%m-%d %H:%M:%S"))),
        ]
        return estimates


class MainWindow(ManagedDockWindow):
    def __init__(self):
        super().__init__(
            procedure_class= SpinLabMeasurement,
            inputs = ['mode', 'sample_name', 'vector', 'mode_resistance', 'mode_fmr', 'set_measdevice_qm', 'set_sourcemeter','set_pulsegenerator', 'set_measdevice_fmr', 'set_multimeter', 'set_gaussmeter', 'set_field_cntrl','address_daq', 'polarity_control_enabled', 'address_polarity_control', 'set_lockin', 'set_automaticstation', 'set_rotationstation','address_rotationstation','rotation_axis', 'set_polar_angle','set_azimuthal_angle','set_polar_angle_fmr','set_azimuthal_angle_fmr', 'rotation_polar_constant', 'rotation_azimuth_constant','set_switch', 'set_kriostat', "kriostat_temperature", 'set_lfgen', 'set_analyzer', 'set_generator', 'address_generator','generator_channel','address_sourcemeter', 'address_multimeter', 'address_gaussmeter', 'address_lockin', 'address_switch', 'address_analyzer', 'address_lfgen','address_pulsegenerator','address_automaticstation','sourcemeter_source', 'sourcemeter_compliance', 'sourcemeter_channel', 'sourcemeter_limit', 'sourcemeter_nplc', 'sourcemeter_average', 'sourcemeter_bias', 'multimeter_function', 'multimeter_resolution','multimeter_nplc', 'multimeter_autorange', 'multimeter_range', 'multimeter_average', 'field_constant', 'constant_field_value', 'gaussmeter_range', 'gaussmeter_resolution', 'lockin_average', 'lockin_input_coupling', 'lockin_reference_source', 'lockin_dynamic_reserve', 'lockin_input_connection', 'lockin_sensitivity','lockin_frequency', 'lockin_harmonic','lockin_sine_amplitude',  'lockin_timeconstant', 'lockin_slope', 'lockin_channel1','lockin_channel2' ,'lockin_autophase','generator_frequency', 'generator_power', 'lfgen_freq', 'lfgen_amp', 'field_step', 'delay_field', 'delay_lockin', 'delay_bias','mode_cims_relays','pulsegenerator_offset','pulsegenerator_duration','pulsegenerator_pulsetype','pulsegenerator_channel','pulsegenerator_compliance','pulsegenerator_source_range','delay_measurement','field_bias_value','remanency_correction','remanency_correction_time','remagnetization','remagnetization_value','remagnetization_time','hold_the_field_after_measurement','return_the_rotationstation', 'layout_type', 'point_meas_duration', 'number_of_points','global_xyname','disconnect_length','sample_in_plane','go_init_position'],
            x_axis=['Field (Oe)', 'Voltage (V)'],
            y_axis=['Field (Oe)', 'Resistance (ohm)'],
            # directory_input=True,  
            sequencer=True,
            
            sequencer_inputs=['constant_field_value',"generator_frequency", "kriostat_temperature", "global_xyname","iterator"],
            inputs_in_scrollarea=True,
            ext_devices = [CameraControl, WaterCoolerControl, Lakeshore336Control, AutomaticStationGenerator],
            
        )

        self.setWindowTitle("SpinLabAPP v.1.00")
        directory, filename = self.procedure_class.path_file.ReadFile()
        self.directory = directory
        self.filename = filename
        self.store_measurement = False  # Controls the 'Save data' toggle
        self.file_input.extensions = ["csv", "txt", "data"]  # Sets recognized extensions, first entry is the default extension
        self.file_input.filename_fixed = False
        self.tabs.currentChanged.connect(self.on_tab_change)
        
        self.read_settings()

    def set_calibration_constant(self, value):
        self.inputs.field_constant.setValue(value)

    def set_calibration_filename(self, value):
        self.inputs.sample_name.setValue(value)

    def refresh_addresses(self):
        find_instruments = FindInstrument()
        choices = find_instruments.show_instrument()

        for address in self.procedure_class.address_list:
            getattr(self.procedure_class, address)._choices = dict(zip(choices, choices))
            input_widget = getattr(self.inputs, address)
            old_address = input_widget.value()
            input_widget._parameter._choices = dict(zip(choices, choices))
            input_widget.clear()
            input_widget.addItems(choices)

            if old_address in choices:
                input_widget.setValue(str(old_address))
                continue
            input_widget.setValue("None")

    def set_sample_name(self, value):
        self.inputs.sample_name.setValue(value)

    def on_tab_change(self, index: int):
        self.quick_measure_widget.on_tab_change(index)
        if self.quick_measure_widget.tab_index == index:
            self.change_layout_type(False)

    def filename_getter(self):
        return self.file_input.filename
    
    def read_settings(self):
        log.info("Reading settings...")
        self.change_layout_type(settings.value("layout_type", True, type=bool))
        for name, attr in self.inputs.__dict__.items():
            if isinstance(attr, Input):
                value = settings.value(name)
                value = convert_value(value)
                if value is not None:
                    try:
                        attr.setValue(value)
                    except ValueError as e:
                        log.warning(f"Failed to set value: '{value}' for parameter: '{name}' due to error: {e}. Leaving the default value.")
        log.info("Reading settings done.")
                    
    def save_settings(self):
        for name , attr in self.inputs.__dict__.items():
            if isinstance(attr, Input):
                value = attr.value()
                settings.setValue(name, value)
    
    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    settings = QtCore.QSettings("settings.ini", QtCore.QSettings.IniFormat)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
