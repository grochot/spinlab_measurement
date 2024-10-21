import numpy as np
from time import sleep


def sweep_field_to_value(start_field: float, end_field: float, field_step: float, daq, abort_callback=None, emit_info_callback=None) -> float:
    """
    Gradually sweeps the magnetic field from a starting value to a target value, adjusting the voltage in increments
    to ensure a smooth transition.

    Args:
        start_field (float): The initial magnetic field value in Oersteds (Oe).
        end_field (float): The target magnetic field value in Oersteds (Oe).
        field_step (float): The increment size for changing the magnetic field in Oersteds (Oe).
        daq (object): The DAQ device used to set the field during the sweep.
        abort_callback (function, optional): A function that returns True if the sweep should be aborted. Defaults to None.
        emit_info_callback (function, optional): A function that emits information about the sweep. Defaults to None.

    Returns:
        float: The final magnetic field value that was set.
    """
    last_set_field = start_field
    step_direction = field_step if end_field > start_field else -field_step
    field_values = np.arange(start_field, end_field, step_direction)
    wasAborted = False

    if len(field_values) == 0 or field_values[-1] != end_field:
        field_values = np.append(field_values, end_field)

    # set print options to avoid printing large arrays to console
    np.set_printoptions(threshold=10)
    print(f"Sweeping field from: {start_field} to: {end_field} with {len(field_values)} steps: {field_values}")
    # reset print options to default
    np.set_printoptions(threshold=1000)

    if emit_info_callback:
        emit_info_callback("info", f"Sweeping field from: {start_field} to: {end_field} [Oe]")

    for field in field_values:
        
        if abort_callback and abort_callback():
            wasAborted = True
            print("Aborting sweep")
            break
        
        daq.set_field(field)
        last_set_field = field
        sleep(0.3)
    
    if emit_info_callback:
        emit_info_callback("info", "")

    return last_set_field, wasAborted
