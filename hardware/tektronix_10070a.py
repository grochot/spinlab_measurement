from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range, strict_discrete_set
from pymeasure.adapters import Adapter
from time import sleep
import time

import logging
log = logging.getLogger(__name__) 
log.addHandler(logging.NullHandler())

class Tektronix10070a(Instrument):
    def __init__(self, adapter, name="Tektronix 10,070a", **kwargs):
        kwargs.setdefault('read_termination', '\n')
        super().__init__(
            adapter,
            name,
            **kwargs
        )


    amplitude=Instrument.control(
        "AMPL?", "AMPL %s",
        """The amplitude command sets the output pulse amplitude of the instrument.
Resolution is 1 dB, up to a maximum attenuation of 81 dB. The amplitude
setting is accurate only when driving into a 50 ohm load""")
    
    def disable_source(self):
        self.write('DIS')

    def enable_source(self):
        self.write('ENAB')

    def init(self):
        log.info("Tektronix 10,070a - Using excessed function init()")


    duration=Instrument.control(
        "DUR?", "DUR %s",
        """ The duration command sets the output pulse duration. The allowed range is larger
than the specified limit so that the nominal range can be achieved in the presence
of drift.""")
    
    offset=Instrument.control(
        "OFFS?", "OFFS %s",
        """ The offset command sets the baseline offset value. Allowed values range from
-5 V to +5 V, with 1.25 mV resolution. The offset value has 50 ohm source
impedance and is accurate only if driven into a 50 ohm load""")

    period=Instrument.control(
        "PER?", "PER %s",
        """The period command sets the pulse repetition period. Allowed period values are
10 microseconds to 1 second. Resolution is 0.1us. Note that period is linked to
frequency. Changing one changes the other. """)
    

    def reset(self):
        self.write('*RST')

    def trigger(self):
        self.write('*TRG')

    
    trigger_source=Instrument.control(
        "TRIG?", "TRIG %s",
        """ The trigger command selects the trigger source. Its argument can be one of the
following sources: "INT", "EXT", "MAN", or "GPIB".""",
        validator=strict_discrete_set,
        values=["INT", "EXT", "MAN", "GPIB"]

        )
    
#examples
def give_one_pulse():
    dev=Tektronix10070a("GPIB0::1::INSTR")
    #dev.reset()


    dev.trigger_source="GPIB"

    dev.offset=0
    dev.amplitude=2
    dev.duration="1e-9"
    dev.enable_source()
    dev.trigger()

    #sleep(1)
    dev.disable_source()

if __name__ == "__main__":
    dev=Tektronix10070a("GPIB0::1::INSTR")
    give_one_pulse()
    
    

'''    def __init__(self, adapter, read_termination="\n", **kwargs):
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
        self.write('TRIG %s'%trigger_source)'''




    

    
    

    