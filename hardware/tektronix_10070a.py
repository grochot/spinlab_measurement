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

    
    def disable():
        self.write('DIS')

    def enable():
        self.write('ENAB')

    def duration():
        self.write('DUR')

    def offset(offset):
        self.write('OFFS')

    def period(period):
        self.write('PER %d'%period)

    def reset():
        self.write('*RST')
    
    def trigger():
        self.write('*TRG')

    def trigger_source(trigger_source):
        #possible values = "INT", "EXT", "MAN", "GPIB"
        self.write('TRIG %s'%trigger_source)

    

    
    

    