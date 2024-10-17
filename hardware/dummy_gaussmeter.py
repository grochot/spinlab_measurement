import numpy as np
from random import random
class DummyGaussmeter:
    def __init__(self, resource_name):
        pass
    def range(self, range):
        pass
    def resolution(self, resolution):
        pass
    def measure(self):
        return random() * 1000