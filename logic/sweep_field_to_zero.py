import numpy as np
from time import sleep
def sweep_field_to_zero(start_value, field_constant, step, daq):
    if field_constant > 2: #tego if'a bym wywalil przy mergowaniu
        daq.set_field(0)
    else:

        print("start_value",start_value)
        if start_value<0:
            vector = np.arange(start_value, 0, step)
        else:
            vector = np.arange(start_value, 0, -1*step)


        print("sweep_field_to_zero()-vector",vector)
        for i in vector: 

            daq.set_field(i)
            sleep(0.3)
        
        daq.set_field(0)
    
    return 0
