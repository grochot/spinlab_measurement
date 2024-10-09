from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set
from time import sleep
import nidaqmx

import time
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class DAQ:
    def __init__(self, adapter, polarity_control_enabled=False, address_polarity_control=None):
        self.adapter = adapter
        self.polarity_control_enabled = polarity_control_enabled
        self.address_polarity = address_polarity_control
        self.polarity = False

    def set_field(self, value=1):
        if self.polarity_control_enabled:
            polarity_changed = False
            if self.address_polarity is None:
                raise ValueError("Address polarity must be specified if polarity control is enabled")
            
            if value < 0:
                value = -value
                if not self.polarity:
                    self.polarity = True
                    with nidaqmx.Task() as task:
                        task.do_channels.add_do_chan(self.address_polarity)
                        task.write(self.polarity)
                    polarity_changed = True
            elif value >= 0 and self.polarity:
                self.polarity = False
                with nidaqmx.Task() as task:
                    task.do_channels.add_do_chan(self.address_polarity)
                    task.write(self.polarity)
                polarity_changed = True
            if polarity_changed:
                time.sleep(2)
        
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan(self.adapter)
            task.write(value)
        return value

    def shutdown(self):
        """Disable output, call parent function"""
        self.set_field(0)


# d = DAQ('Dev4/ao0')
# d.set_field(1)
# d.shutdown()
# print(d.read_field())
