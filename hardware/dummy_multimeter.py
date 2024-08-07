import numpy as np
class DummyMultimeter():
    def __init__(self, resource_name):
        pass
    def resolution(self, resolution):
        pass
    def range(self, range):
        pass
    def autorange(self, autorange):
        pass
    def function(self, function):
        pass
    def average(self, average):
        pass
    
    def current_dc(self):
        return np.nan
    def voltage_dc(self):
        return np.nan