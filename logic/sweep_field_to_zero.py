import numpy as np
from time import sleep


def sweep_field_to_zero(start_field: float, field_constant: float, field_step: float, daq) -> int:
    """
    Gradually sweeps the magnetic field from a starting value to zero, adjusting the voltage in increments to avoid abrupt changes.

    If the field constant exceeds a certain threshold, the field is set directly to zero. Otherwise, it decreases step-by-step
    to ensure a smooth transition.

    Args:
        start_field (float): The initial magnetic field value from which to start the sweep in [Oe].
        field_constant (float): The conversion factor between field and voltage in [V/Oe].
                                If greater than 2, the field is directly set to zero.
        field_step (float): The step size for decreasing the field value in [Oe].
        daq (object): The DAQ device used to set the field during the sweep.

    Returns:
        int: Returns 0 after successfully sweeping the field to zero.
    """

    if field_constant > 2:  # tego if'a bym wywalil przy mergowaniu
        daq.set_field(0)
    else:

        print("start_value", start_field)
        if start_field < 0:
            vector = np.arange(start_field, 0, field_step)
        else:
            vector = np.arange(start_field, 0, -1 * field_step)

        print("sweep_field_to_zero()-vector", vector)
        for field in vector:

            daq.set_field(field)
            sleep(0.3)

        daq.set_field(0)

    return 0
