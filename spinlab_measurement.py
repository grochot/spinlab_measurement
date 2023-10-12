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
from logic.find_instrument import FindInstrument


log = logging.getLogger(__name__) 
log.addHandler(logging.NullHandler()) 



class SpinLabMeasurement(Procedure):
    # licznik = 1 # licznik
    find_instruments = FindInstrument()
    finded_instruments = find_instruments.show_instrument() 
    print(finded_instruments)
#################################################################### PARAMETERS #####################################################################
    mode = ListParameter("Mode", choices=['ResistanceMode', 'FMRMode', 'VSMMode', 'HarmonicMode', 'CalibrationFieldMode', 'PulseMode'])
    mode_resistance = BooleanParameter("4-points", default=False, group_by="mode", group_condition=lambda v: v=="ResistanceMode")
    mode_fmr = ListParameter("FMR Mode", choices = ["V-FMR", "ST-FMR"], group_by={"mode": lambda v: v == "FMRMode"})
    mode_harmonic = ListParameter("Harmonic mode", choices = ["Field harmonic", "Angular harmonic"], group_by = {"mode": lambda v: v == "HarmonicMode"})
    
    #Hardware
    set_sourcemeter=ListParameter("Sourcemeter", choices=["Keithley 2400", "Keithley 2636", "Agilent 2912", "none"], default = "none", group_by="mode", group_condition=lambda v: v == "ResistanceMode")
    set_multimeter = ListParameter("Multimeter", choices=["Agilent 34400", "none"], default = "none", group_by={"mode": lambda v: v=="ResistanceMode", "mode_resistance": lambda v: v=="4-points"})
    set_gaussmeter = ListParameter("Gaussmeter", choices=["Lakeshore", "none"], group_by={"mode":lambda v: v == "ResistanceMode"})
    set_field = ListParameter("Magnetic Field", choices = ["DAQ", "Lockin", "none"], group_by = {"mode": lambda v: v == "ResistanceMode"})
    set_lockin = ListParameter("Lockin", choices = ["Zurich", "SR830"], group_by = {"mode": lambda v: v == "HarmonicMode" or v == "FMRMode"})
    set_automaticstation = BooleanParameter("Automatic Station", default = False)
    set_rotationstation = BooleanParameter("Rotation Station", default = False)
    set_switch = BooleanParameter("Switch", default = False)
    set_kriostat = BooleanParameter("Kriostat", default = False)
    set_analyzer = ListParameter("Vector Analyzer", choices = ['VectorAnalyzer', 'none'], group_by={'mode': lambda v: v=='VSMMode'})
    set_generator = ListParameter("RF Generator", choices = ["Agilent", "none"], group_by = {"mode": lambda v: v == "FMRMode"})
   
    #Hardware address
    address_sourcemeter=ListParameter("Sourcemeter address", choices=finded_instruments, group_by = {"mode": lambda v: v=="ResistanceMode"})
    address_multimeter=ListParameter("Multimeter address", choices=finded_instruments, group_by = {"mode": lambda v: v=="ResistanceMode"})
    address_gaussmeter=ListParameter("Gaussmeter address",  choices=finded_instruments, group_by = {"mode": lambda v: v=="ResistanceMode"})
    address_lockin=ListParameter("Lockin address",  choices=finded_instruments, group_by = {"mode": lambda v: v=="ResistanceMode"})
    address_switch=ListParameter("Switch address",  choices=finded_instruments, group_by = {"mode": lambda v: v=="ResistanceMode"})
    address_analyzer=ListParameter("Analyzer address",  choices=finded_instruments, group_by = {"mode": lambda v: v=="ResistanceMode"})
    address_generator=ListParameter("Generator address",  choices=finded_instruments, group_by = {"mode": lambda v: v=="ResistanceMode"})

    #MeasurementParameters
    sample_name = Parameter("Sample name") 
    vector = Parameter("Vector")
    delay_field = FloatParameter("Delay Field", default=0, units="s", group_by={"mode": lambda v: v == "ResistanceMode"})
    delay_lockin = FloatParameter("Delay Lockin", default=0, units="s", group_by={"mode": lambda v: v == "ResistanceMode"})
    delay_bias = FloatParameter("Delay Bias", default=0, units="s", group_by={"mode": lambda v: v == "ResistanceMode"})
    
    #########  SETTINGS PARAMETERS ##############
    #SourcemeterParameters 
    sourcemter_source = ListParameter("Source", choices=["Voltage", "Current"], group_by={"mode": lambda v: v == "ResistanceMode"})
    sourcemeter_compliance = FloatParameter("Compliance", default=0, group_by={"mode": lambda v: v == "ResistanceMode"})
    sourcemeter_channel = ListParameter("Channel", choices = ["Channel A", "Channel B"], group_by={"mode": lambda v: v == "ResistanceMode"})
    sourcemeter_limit = FloatParameter("Limit", default=0, group_by={"mode": lambda v: v == "ResistanceMode"})
    sourcemeter_nplc = FloatParameter("NPLC", default=0, group_by={"mode": lambda v: v == "ResistanceMode"})
    sourcemeter_average = IntegerParameter("Average", default=0, group_by={"mode": lambda v: v == "ResistanceMode"})
    sourcemeter_bias = FloatParameter("Bias", default=0, group_by={"mode": lambda v: v == "ResistanceMode"})

    #MultimeterParameters 
    multimeter_function = ListParameter("Function", choices=["DC Voltage", "AC Voltage", "DC Current", "AC Current", "2-wire Resistance", "4-wire Resistance"], group_by={"mode": lambda v: v == "ResistanceMode"})
    multimeter_resolution = ListParameter("Resolution", choices=["3.5 digits", "4.5 digits", "5.5 digits", "6.5 digits"], group_by={"mode": lambda v: v == "ResistanceMode"})
    multimeter_autorange = BooleanParameter("Autorange", default=False, group_by={"mode": lambda v: v == "ResistanceMode"})
    multimeter_range = FloatParameter("Range", default=0, group_by={"mode": lambda v: v == "ResistanceMode"})
    multimeter_average = IntegerParameter("Average", default=0, group_by={"mode": lambda v: v == "ResistanceMode"})
    
    #LockinParameters
    lockin_average = IntegerParameter("Average", default=0, group_by={"mode": lambda v: v == "HarmonicMode"})
    lockin_input_coupling = ListParameter("Input Coupling", choices = ["AC", "DC"], group_by={"mode": lambda v: v == "HarmonicMode"})
    lockin_reference_source = ListParameter("Reference Source", choices=["Internal", "External"], group_by={"mode": lambda v: v == "HarmonicMode"})
    lockin_dynamic_reserve = ListParameter("Dynamic Reserve", choices=["High Reserve", "Normal", "Low Noise", "Auto Reserve"], group_by={"mode": lambda v: v == "HarmonicMode"})
    lockin_input_connection = ListParameter("Input Connection", choices = ["Single Voltage", "Differential Voltage"], group_by={"mode": lambda v: v == "HarmonicMode"})
    lockin_sensitivity = ListParameter("Sensitivity", choices=["Auto Gain", "2 nV/fA", "5 nV/fA", "10 nV/fA", "20 nV/fA", "50 nV/fA", "100 nV/fA", "200 nV/fA", "500 nV/fA", "1 uV/pA", "2 uV/pA", "5 uV/pA", "10 uV/pA", "20 uV/pA", "50 uV/pA", "100 uV/pA", "200 uV/pA", "500 uV/pA", "1 mV/nA", "2 mV/nA", "5 mV/nA", "10 mV/nA", "20 mV/nA", "50 mV/nA", "100 mV/nA", "200 mV/nA", "500 mV/nA", "1 V/uA"], group_by={"mode": lambda v: v == "HarmonicMode"})
    lockin_timeconstant = ListParameter("Time Constant", choices = ["10 us", "30 us", "100 us", "300 us", "1 ms", "3 ms", "10 ms", "30 ms", "100 ms", "300 ms", "1 s", "3 s", "10 s", "30 s", "100 s", "300 s", "1 ks", "3 ks", "10 ks", "30 ks"], group_by={"mode": lambda v: v == "HarmonicMode"})
    lockin_autophase = BooleanParameter("Autophase", default=False, group_by={"mode": lambda v: v == "HarmonicMode"})

    #FieldParameters 
    field_constant = FloatParameter("Constant", default=0)
    #GeneratorParameters 

    #Analyzer Parameters 

    #GaussmeterParameters 
    gaussmeter_range = ListParameter("Range", default=1, choices=[1,2,3,4,5], group_by={"mode": lambda v: v == "ResistanceMode"})
    gaussmeter_resolution = ListParameter("Resolution", default = "5 digits",choices=["3 digits", "4 digits", "5 digits"], group_by={"mode": lambda v: v == "ResistanceMode"})


    DEBUG = 1
    DATA_COLUMNS = ['Voltage (V)', 'Current (A)', 'Resistance (ohm)', 'Field (Oe)', 'Frequency (Hz)', 'X (V)', 'Y (V)', 'Phase']
    path_file = SaveFilePath() 
   
    
    ################ STARTUP ##################3
    def startup(self):
     
        match self.mode:
            case "ResistanceMode":
                self.resistancemode = ResistanceMode(self.vector, self.mode_resistance, self.sourcemeter_bias, self.set_sourcemeter, self.set_multimeter, self.set_gaussmeter, self.set_field, self.set_automaticstation, self.set_switch, self.set_kriostat, self.set_rotationstation, self.address_sourcemeter, self.address_multimeter, self.address_gaussmeter, self.address_switch, self.delay_field, self.delay_lockin, self.delay_bias, self.sourcemter_source, self.sourcemeter_compliance, self.sourcemeter_channel, self.sourcemeter_limit, self.sourcemeter_nplc, self.sourcemeter_average, self.multimeter_function, self.multimeter_resolution, self.multimeter_autorange, self.multimeter_range, self.multimeter_average, self.field_constant, self.gaussmeter_range, self.gaussmeter_resolution)
                self.points = self.resistancemode.generate_points()
                self.resistancemode.initializing()

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

    
    def shutdown(self):
         match self.mode:
            case "ResistanceMode":
                 pass
        

class MainWindow(ManagedDockWindow):
    # last = False
    # wynik = 0
    # wynik_list = []
    def __init__(self):
        super().__init__(
            procedure_class= SpinLabMeasurement,
            inputs=['mode', 'sample_name', 'vector', 'mode_resistance', 'mode_fmr', 'mode_harmonic', 'set_sourcemeter', 'set_multimeter', 'set_gaussmeter', 'set_field', 'set_lockin', 'set_automaticstation', 'set_rotationstation','set_switch', 'set_kriostat', 'set_analyzer', 'set_generator', 'address_sourcemeter', 'address_multimeter', 'address_gaussmeter', 'address_lockin', 'address_switch', 'address_analyzer', 'address_generator', 'sourcemter_source', 'sourcemeter_compliance', 'sourcemeter_channel', 'sourcemeter_limit', 'sourcemeter_nplc', 'sourcemeter_average', 'sourcemeter_bias', 'multimeter_function', 'multimeter_resolution', 'multimeter_autorange', 'multimeter_range', 'multimeter_average', 'field_constant', 'gaussmeter_range', 'gaussmeter_resolution', 'lockin_average', 'lockin_input_coupling', 'lockin_reference_source', 'lockin_dynamic_reserve', 'lockin_input_connection', 'lockin_sensitivity', 'lockin_timeconstant', 'lockin_autophase', 'delay_field', 'delay_lockin', 'delay_bias'],
            x_axis=['Field (Oe)', 'Voltage (V)'],
            y_axis=['Field (Oe)', 'Resistance (ohm)'],
            directory_input=True,  
            sequencer=True,                                  
            sequencer_inputs=[],
            inputs_in_scrollarea=True,
            
        )
       
        self.setWindowTitle('SpinLab Measurement System v.0.1')
        # self.directory = self.procedure_class.path_file.ReadFile()
        

    def queue(self, procedure=None):
        directory = self.directory  # Change this to the desired directory
        # self.procedure_class.path_file.WriteFile(directory)
        
        if procedure is None:
            procedure = self.make_procedure()
       
        name_of_file = procedure.sample_name
        filename = unique_name(directory, prefix="{}_".format(name_of_file))
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)
        self.manager.queue(experiment)
        
    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())