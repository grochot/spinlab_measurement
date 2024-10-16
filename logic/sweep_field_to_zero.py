import numpy as np
from time import sleep

from hardware.daq import DAQ


def sweep_field_to_zero(start_field: float, field_constant: float, field_step: float, daq: DAQ) -> float:
    """
    Gradually sweeps the magnetic field from a starting value to zero, adjusting the voltage in increments to avoid abrupt changes.

    Args:
        start_field (float): The initial magnetic field value in Oersteds (Oe).
        field_constant (float): The conversion factor between field and voltage in Volts per Oersted (V/Oe).
                                If greater than 2, the field is directly set to zero.
        field_step (float): The step size for decreasing the field value in Oersteds (Oe).
        daq (object): The DAQ device used to set the field during the sweep.

    Returns:
        float: The final magnetic field value that was set.
    """
    last_set_field = start_field
    if field_constant > 2:  # tego if'a bym wywalil przy mergowaniu
        daq.set_field(0)
        return 0.0
    else:
        step_direction = field_step if start_field < 0 else -field_step
        field_values = np.arange(start_field, 0, step_direction)
        field_values = np.append(field_values, 0)

        print(f"Sweeping field from: {start_field} to: 0 with {len(field_values)} steps: {field_values}")

        for field in field_values:
            daq.set_field(field)
            last_set_field = field
            sleep(0.3)

    return last_set_field
