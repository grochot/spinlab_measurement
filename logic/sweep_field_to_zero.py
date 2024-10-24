import numpy as np
from time import sleep


def sweep_field_to_zero(start_field: float, field_constant: float, field_step: float, daq, abort_callback=None, emit_info_callback=None) -> float:
    """
    Gradually sweeps the magnetic field from a starting value to zero, adjusting the voltage in increments to avoid abrupt changes.

    Args:
        start_field (float): The initial magnetic field value in Oersteds (Oe).
        field_constant (float): The conversion factor between field and voltage in Volts per Oersted (V/Oe).
        field_step (float): The step size for decreasing the field value in Oersteds (Oe).
        daq (object): The DAQ device used to set the field during the sweep.
        abort_callback (function, optional): A function that returns True if the sweep should be aborted. Defaults to None.
        emit_info_callback (function, optional): A function that emits information about the sweep. Defaults to None.

    Returns:
        float: The final magnetic field value that was set.
    """
    last_set_field = start_field
    wasAborted = False
    
    if abs(start_field) <= field_step:
        daq.set_field(0)
        return 0.0, wasAborted

    step_direction = field_step if start_field < 0 else -field_step
    field_values = np.arange(start_field, 0, step_direction)
    if field_values[-1] != 0:
        field_values = np.append(field_values, 0)

    # set print options to avoid printing large arrays to console
    np.set_printoptions(threshold=10)
    print(f"Sweeping field from: {start_field:.2f} to: 0 with {len(field_values)} steps: {field_values}")
    # reset print options to default
    np.set_printoptions(threshold=1000)

    if emit_info_callback:
        emit_info_callback("info", f"Sweeping field from: {start_field:.2f} to: 0 [Oe]")

    for field in field_values:

        if abort_callback and abort_callback():
            print("Aborting sweep")
            wasAborted = True
            break

        daq.set_field(field)
        last_set_field = field
        sleep(0.3)

    if emit_info_callback:
        emit_info_callback("info", "")

    return last_set_field, wasAborted
