import pyvisa
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range



class DummyLFGenDriver(Instrument):
    def __init__(self):
        pass

    def set_shape(self, shape):
        pass

    def set_freq(self, freq):
        pass

    def set_amp(self, amp):
        pass