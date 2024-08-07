def _lockin_sensitivity(choice:str):
    SENSITIVITIES = {
       "2 nV/fA": 2e-9, 
       "5 nV/fA": 5e-9, 
       "10 nV/fA": 10e-9, 
       "20 nV/fA": 20e-9, 
       "50 nV/fA": 50e-9, 
       "100 nV/fA": 100e-9, 
       "200 nV/fA": 200e-9,
       "500 nV/fA": 500e-9,
       "1 uV/pA": 1e-6, 
       "2 uV/pA": 2e-6, 
       "5 uV/pA": 5e-6, 
       "10 uV/pA": 10e-6, 
       "20 uV/pA": 20e-6, 
       "50 uV/pA": 50e-6, 
       "100 uV/pA": 100e-6,
       "200 uV/pA":  200e-6, 
       "500 uV/pA": 500e-6, 
       "1 mV/nA": 1e-3, 
       "2 mV/nA": 2e-3, 
       "5 mV/nA": 5e-3, 
       "10 mV/nA": 10e-3, 
       "20 mV/nA": 20e-3,
       "50 mV/nA": 50e-3, 
       "100 mV/nA": 100e-3, 
       "200 mV/nA": 200e-3, 
       "500 mV/nA": 500e-3, 
       "1 V/uA": 1}
    return SENSITIVITIES[choice]

def _lockin_timeconstant(choice:str):

    TIME_CONSTANTS = {
        "10 us": 10e-6, 
        "30 us": 30e-6, 
       "100 us":  100e-6, 
       "300 us":  300e-6, 
        "1 ms":  1e-3, 
       "3 ms":  3e-3, 
       "10 ms": 10e-3,
       "30 ms": 30e-3, 
       "100 ms": 100e-3, 
       "300 ms": 300e-3, 
       "1 s": 1, 
       "3 s": 3, 
       "10 s": 10, 
       "30 s": 30, 
        "100 s": 100, 
       "300 s": 300, 
       "1 ks": 1e3,
       "3 ks": 3e3, 
       "10 ks": 10e3, 
       "30 ks": 30e3
    }
    return TIME_CONSTANTS[choice]