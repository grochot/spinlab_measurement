import numpy as np
from time import sleep
def sweep_field_to_value(start_value, stop_value, field_constant, step, daq):

    if stop_value-start_value>0.0:
        vector = np.arange(start_value, stop_value, step)
    else:
        vector = np.arange(start_value, stop_value, -1*step)
    
    print("vector.shape[0]",vector.shape[0])
    #if vector[-1]==start_value:
    #    vector=np.concatenate((vector,[stop_value*field_constant]))

    if vector.shape[0]==0:
        vector=np.array([stop_value])
    else:
        if vector[-1]!=stop_value:
            vector=np.concatenate((vector,[stop_value]))


    print("[sweep_field_to_value.py] - vector:",vector)
    for i in vector: 

        daq.set_field(i)
        sleep(0.3)
    
    return 0