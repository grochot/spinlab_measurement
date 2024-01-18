import re
import time
import numpy as np
from enum import IntFlag
from pymeasure.instruments import Instrument, discreteTruncate
from pymeasure.instruments.validators import strict_discrete_set, \
    truncated_discrete_set, truncated_range


class LIAStatus(IntFlag):
    """ IntFlag type that is returned by the lia_status property.
    """
    NO_ERROR = 0
    INPUT_OVERLOAD = 1
    FILTER_OVERLOAD = 2
    OUTPUT_OVERLOAD = 4
    REF_UNLOCK = 8
    FREQ_RANGE_CHANGE = 16
    TC_CHANGE = 32
    TRIGGER = 64
    UNUSED = 128


class ERRStatus(IntFlag):
    """ IntFlag type that is returned by the err_status property.
    """
    NO_ERROR = 0
    BACKUP_ERR = 2
    RAM_ERR = 4
    ROM_ERR = 16
    GPIB_ERR = 32
    DSP_ERR = 64
    MATH_ERR = 128


class DummyLockin():

    SAMPLE_FREQUENCIES = [
        62.5e-3, 125e-3, 250e-3, 500e-3, 1, 2, 4, 8, 16,
        32, 64, 128, 256, 512
    ]
    SENSITIVITIES = [
        2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9,
        500e-9, 1e-6, 2e-6, 5e-6, 10e-6, 20e-6, 50e-6, 100e-6,
        200e-6, 500e-6, 1e-3, 2e-3, 5e-3, 10e-3, 20e-3,
        50e-3, 100e-3, 200e-3, 500e-3, 1
    ]
    TIME_CONSTANTS = [
        10e-6, 30e-6, 100e-6, 300e-6, 1e-3, 3e-3, 10e-3,
        30e-3, 100e-3, 300e-3, 1, 3, 10, 30, 100, 300, 1e3,
        3e3, 10e3, 30e3
    ]
    FILTER_SLOPES = [6, 12, 18, 24]
    EXPANSION_VALUES = [1, 10, 100]
    RESERVE_VALUES = ['High Reserve', 'Normal', 'Low Noise']
    CHANNELS = ['X', 'Y', 'R']
    INPUT_CONFIGS = ['A', 'A - B', 'I (1 MOhm)', 'I (100 MOhm)']
    INPUT_GROUNDINGS = ['Float', 'Ground']
    INPUT_COUPLINGS = ['AC', 'DC']
    INPUT_NOTCH_CONFIGS = ['None', 'Line', '2 x Line', 'Both']
    REFERENCE_SOURCES = ['External', 'Internal']
    SNAP_ENUMERATION = {"x": 1, "y": 2, "r": 3, "theta": 4,
                        "aux in 1": 5, "aux in 2": 6, "aux in 3": 7, "aux in 4": 8,
                        "frequency": 9, "ch1": 10, "ch2": 11}
    REFERENCE_SOURCE_TRIGGER = ['SINE', 'POS EDGE', 'NEG EDGE']
    INPUT_FILTER = ['Off', 'On']

    sine_voltage = 0
    frequency = 0
    
    phase = 0
    x = 0  
    y = 0

    lia_status = 0

    err_status = 0

    @property
    def xy(self):
        pass

    magnitude = 0
    theta = 0
    channel1 = 0
    channel2 = 0
    sensitivity = 0
    time_constant = 0
    filter_slope = 0
    filter_synchronous = 0
    harmonic = 0
    input_config =0
    input_grounding =0
    input_coupling = 0
    input_notch_config = 0
    reference_source = 0
    reference_source_trigger = 0

    aux_out_1 = 0
    # For consistency with other lock-in instrument classes
    dac1 = aux_out_1

    aux_out_2 = 0
    # For consistency with other lock-in instrument classes
    dac2 = aux_out_2

    aux_out_3 =0
    # For consistency with other lock-in instrument classes
    dac3 = aux_out_3

    aux_out_4 = 0
    # For consistency with other lock-in instrument classes
    dac4 = aux_out_4

    aux_in_1 = 0
    # For consistency with other lock-in instrument classes
    adc1 = aux_in_1

    aux_in_2 = 0
    # For consistency with other lock-in instrument classes
    adc2 = aux_in_2

    aux_in_3 = 0
    # For consistency with other lock-in instrument classes
    adc3 = aux_in_3

    aux_in_4 = 0
    # For consistency with other lock-in instrument classes
    adc4 = aux_in_4

    def __init__(self,**kwargs):
        pass

    def auto_gain(self):
        pass

    def auto_reserve(self):
        pass

    def auto_phase(self):
        pass

    def auto_offset(self, channel):
        pass

    def get_scaling(self, channel):
        pass

    def set_scaling(self, channel, precent, expand=0):
        pass

    def output_conversion(self, channel):
        pass

    @property
    def sample_frequency(self):
        pass

    @sample_frequency.setter
    def sample_frequency(self, frequency):
        pass

    def aquireOnTrigger(self, enable=True):
        pass

    @property
    def reserve(self):
        pass

    @reserve.setter
    def reserve(self, reserve):
        pass

    def is_out_of_range(self):
        pass

    def quick_range(self):
        pass

    @property
    def buffer_count(self):
        pass
    
    def buffer_count2(self):
        pass

    def fill_buffer(self, count, has_aborted=lambda: False, delay=0.001):
        pass

    def buffer_measure(self, count, stopRequest=None, delay=1e-3):
        pass

    def pause_buffer(self):
        pass

    def start_buffer(self, fast=False):
        pass

    def wait_for_buffer(self, count, has_aborted=lambda: False):
        pass

    def get_buffer(self, channel=1, start=0, end=None):
        pass

    def reset_buffer(self):
        pass

    def trigger(self):
        pass

    def snap(self, val1="X", val2="Y", *vals):
        return [0,0]
    

# loc = SR830('GPIB0::8::INSTR')

# loc.frequency = 284
# loc.sensitivity = 1e-6
# loc.time_constant = 0.3
# loc.harmonic = 1
# loc.sine_voltage = 2.3
# loc.channel1 = 'X'
# loc.channel2 = 'Y'
# loc.input_config = 'A'
# loc.input_coupling = 'AC'
# loc.reference_source = 'Internal'
#loc.reset_buffer()
# loc.start_buffer()
# time.sleep(2)
# loc.pause_buffer()
# loc.wait_for_buffer(10)
# # print(loc.get_buffer())
# pp = []
# for i in range(10):

#     qu = loc.snap('R', 'Theta')
#     pp.append(qu)

# print(pp)

