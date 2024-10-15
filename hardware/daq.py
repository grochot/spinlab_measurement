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
        self.prev_voltage = 0
        self.field_step = 100
        self.polarity = False

    def set_field(self, field: float) -> float:
        """
        Convert a magnetic field value to a voltage using the field constant [V/Oe], then set the corresponding voltage.

        The field value is multiplied by the field constant to calculate the voltage. If polarity control is enabled,
        the voltage may be adjusted accordingly.

        Args:
            field (float): The magnetic field value to set, in Oersteds (Oe).

        Raises:
            ValueError: If the field constant is not set before setting the field, or if polarity control is enabled
                        but the address for polarity control is not set.

        Returns:
            float: The voltage value that was set.
        """

        if self.field_constant is None:
            raise ValueError("Field constant must be set before setting field")

        # Convert field value to voltage
        voltage = field * self.field_constant  # field_constant is in [V/Oe]
        voltage = self.set_voltage(voltage)
        return voltage

    def set_voltage(self, voltage: float) -> float:
        """
        Set the voltage on the analog output channel specified by the /self.adapter/ address.
        If polarity control is enabled and the voltage is negative, the digital port specified by
        /self.address_polarity_control/ is set to high; otherwise, it is set to low.

        If the polarity needs to be switched (i.e., if the sign of the new voltage is different
        from the previous voltage), the field is swept to zero before switching to avoid abrupt changes.

        Args:
            voltage (float): The voltage value to set.

        Returns:
            float: The voltage value that was set.

        Raises:
            ValueError: If polarity control is enabled but no address for polarity control is specified.
        """

        # Handle polarity control if enabled
        if self.polarity_control_enabled:
            if self.address_polarity_control is None:
                raise ValueError("Address polarity must be specified if polarity control is enabled")

            # If voltage is 0, ensure polarity is set to False (positive)
            if voltage == 0:
                if self.polarity:
                    self._switch_polarity(False)  # Switch to positive polarity if it's currently negative
                self.prev_voltage = 0  # Set previous voltage to 0
            else:
                # If voltage sign changes, sweep the field to zero before switching polarity
                if sign(self.prev_voltage) * sign(voltage) == -1:
                    log.info("Field Controller: Sweeping field to 0 for polarity switch...")
                    sweep_field_to_zero(self.prev_voltage / self.field_constant, self.field_constant, self.field_step, self)

                # Update polarity if necessary
                new_polarity = voltage < 0
                if new_polarity != self.polarity:
                    self._switch_polarity(new_polarity)

                self.prev_voltage = voltage
                voltage = abs(voltage)  # Use positive voltage after polarity adjustment

        # Set the voltage on the analog output channel
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan(self.adapter)
            task.write(voltage)

        return voltage

    def _switch_polarity(self, new_polarity: bool):
        """Helper function to switch polarity on the control channel."""
        log.info(f"Field Controller: Switching polarity to {'negative' if new_polarity else 'positive'}...")
        with nidaqmx.Task() as task:
            task.do_channels.add_do_chan(self.address_polarity_control)
            task.write(new_polarity)
        self.polarity = new_polarity
        time.sleep(5)

    def shutdown(self):
        """Disable output, call parent function"""
        self.set_field(0)


# d = DAQ('Dev4/ao0')
# d.set_field(1)
# d.shutdown()
# print(d.read_field())
