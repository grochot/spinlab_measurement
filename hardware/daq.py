from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set
from time import sleep
from logic.sweep_field_to_zero import sweep_field_to_zero
import nidaqmx

from numpy import sign

import time
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class DAQ:
    def __init__(self, adapter):
        self.adapter = adapter
        self.field_constant = None
        self.polarity_control_enabled = False
        self.address_polarity_control = None
        self.prev_value = 0
        self.field_step = 100
        self.polarity = False

    def set_field(self, value: float) -> float:
        """Convert field value to voltage using field constant and set voltage

        Args:
            value (float): Field value to set

        Raises:
            ValueError: If field constant is not set before setting field or if polarity control is enabled and address polarity is not set

        Returns:
            float: Field value set
        """

        if self.field_constant is None:
            raise ValueError("Field constant must be set before setting field")

        # Convert field value to voltage
        voltage = value * self.field_constant
        voltage = self.set_voltage(voltage)
        return voltage
        

    def set_voltage(self, value: float) -> float:
        """Set the voltage value on specified analog output channel. If polarity control is enabled, set the address polarity control digital port to high if value is negative, low otherwise.

        Args:
            value (float): Voltage value to set

        Returns:
            float: Voltage value set
        """

        if self.polarity_control_enabled:
            if self.address_polarity_control is None:
                raise ValueError("Address polarity must be specified if polarity control is enabled")
            
            polarity_changed = False
            

            if sign(self.prev_value) * sign(value) == -1:
                sweep_field_to_zero(self.prev_value/self.field_constant, self.field_constant, self.field_step, self)
                time.sleep(1)

            self.prev_value = value

            
            if value < 0:
                value = -value
                if not self.polarity:
                    self.polarity = True
                    with nidaqmx.Task() as task:
                        task.do_channels.add_do_chan(self.address_polarity_control)
                        task.write(self.polarity)
                    polarity_changed = True
            elif value >= 0 and self.polarity:
                self.polarity = False
                with nidaqmx.Task() as task:
                    task.do_channels.add_do_chan(self.address_polarity_control)
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
