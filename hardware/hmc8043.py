from pymeasure.instruments import Instrument
from time import sleep, time
from pymeasure.instruments.validators import truncated_range, strict_discrete_set


import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class HMC8043(Instrument):

    def __init__(self, resourceName, **kwargs):
        kwargs.setdefault('read_termination', '\n')
        super().__init__(
            resourceName,
            "HMC8043",
            includeSCPI=True,
            **kwargs
        )

    def set_channel(self, channel): 
        self.write("INST:NSEL {}".format(channel))
        
    
    def enable_channel(self): 
        self.write("OUTP:CHAN ON") 

    def reset(self): 
        self.write("*RST") 

    def enable_channel_master(self): 
        self.write("OUTP:MAST ON") 
        

    def disable_channel(self): 
        self.write("OUTP:CHAN OFF") 
        sleep(0.2)
        self.write("OUTP:MAST OFF") 
        

    def set_voltage(self, voltage): 
        self.write("VOLT {}".format(voltage))
        

    def shutdown(self):
        """ Turns on the persistent switch,
        ramps down the current to zero, and turns off the persistent switch.
        """
        self.disable_channel()


# zasilacz = HMC8043('USB0::2733::309::032163928::0::INSTR') 
# sleep(1)

# #zasilacz.reset()
# zasilacz.set_voltage(4)
# zasilacz.set_voltage(4)

# zasilacz.enable_channel()
# zasilacz.enable_channel_master()
# sleep(2)
#zasilacz.set_channel(1)
#zasilacz.disable_channel()



