import numpy as np
from time import sleep


def sweep_field_to_value(start_field: float, end_field: float, field_step: float, daq) -> int:
    """
    Gradually sweeps the magnetic field from a starting value to a target value, adjusting the voltage in increments to ensure a smooth transition.

    The function creates a sequence of field values between the start and end points, incrementing or decrementing by the given step size.
    If the step size does not align exactly with the end value, the function ensures the final value in the sequence is the desired end field.

    Args:
        start_field (float): The initial magnetic field value in Oersteds (Oe) from which to start the sweep.
        end_field (float): The target magnetic field value in Oersteds (Oe) to reach by the end of the sweep.
        field_step (float): The increment or decrement size for changing the magnetic field in each step, in Oersteds (Oe).
        daq (object): The DAQ device used to set the field during the sweep.

    Returns:
        int: Returns 0 after successfully sweeping the field to the desired value.
    """

    if end_field - start_field > 0.0:
        vector = np.arange(start_field, end_field, field_step)
    else:
        vector = np.arange(start_field, end_field, -1 * field_step)

    print("vector.shape[0]", vector.shape[0])
    # if vector[-1]==start_value:
    #    vector=np.concatenate((vector,[stop_value]))

    if vector.shape[0] == 0:
        vector = np.array([end_field])
    else:
        if vector[-1] != end_field:
            vector = np.concatenate((vector, [end_field]))

    print("[sweep_field_to_value.py] - vector:", vector)
    for field in vector:

        daq.set_field(field)
        sleep(0.3)

    return 0
