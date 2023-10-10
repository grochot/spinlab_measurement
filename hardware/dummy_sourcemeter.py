import numpy as np
class DummySourcemeter:

    def __init__(self, resource_name):
        pass
    def source_mode(self, source_type):
        pass
    def source_voltage_range(self, voltage):
        pass
    def compliance_current(self, current):
        pass 
    def enable_source(self):
        pass 
    def measure_current(self):
        pass 
    def source_current_range(self, range):
        pass
    def voltage_nplc(self, nplc):
        pass
    def compliance_voltage(self, voltage):
        pass
    def current_nplc(self, nplc):
        pass
    def measure_voltage(self):
        pass
    def shutdown(self):
        pass
    def source_voltage(self, voltage):
        pass
    def source_current(self, current):
        pass
    def current(self):
        return np.nan
    def voltage(self):
        return np.nan



