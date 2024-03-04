from pymeasure.instruments import Instrument 
import pyvisa 
from time import sleep
import numpy as np

class Tektronix10070a(Instrument):
    def __init__(self, adapter, read_termination="\n", **kwargs):
        super().__init__(
            adapter,
            "Tektronix 10070a" ,
            read_termination=read_termination,
            **kwargs
        )
    
    def amplitude(amplitude):
        self.write('AMPL %d'%amplitude)

    
    def disable_source(self):
        self.write('DIS')

    def enable_source(self):
        self.write('ENAB')

    def duration(self):
        self.write('DUR')

    def offset(self,offset):
        self.write('OFFS')

    def period(self,period):
        self.write('PER %d'%period)

    def reset(self):
        self.write('*RST')
    
    def trigger(self):
        self.write('*TRG')

    def trigger_source(self,trigger_source):
        #possible values = "INT", "EXT", "MAN", "GPIB"
        self.write('TRIG %s'%trigger_source)

    

    
    

    