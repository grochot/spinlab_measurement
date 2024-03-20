import numpy as np
from time import sleep
def sweep_field_to_value(start_value, stop_value, field_constant, step, daq):

    if stop_value-start_value>0:
        vector = np.arange(start_value*field_constant, stop_value*field_constant, step*field_constant)
    else:
        vector = np.arange(start_value*field_constant, stop_value*field_constant, -1*step*field_constant)
    
    for i in vector: 

        daq.set_field(i)
        print("i",i)
        sleep(0.3)
    
    return 0
