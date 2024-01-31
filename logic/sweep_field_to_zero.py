import numpy as np
from time import sleep
def sweep_field_to_zero(start_value, field_constant, step, daq):
    vector = np.arange(start_value*field_constant, 0, -1*step*field_constant)
    for i in vector: 

        daq.set_field(i)
        sleep(0.3)
    
    daq.set_field(0)
    
    return 0
