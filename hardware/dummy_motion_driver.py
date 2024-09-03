import random as rd

class DummyMotionDriver:
    def __init__(self, resourceName):
        pass

    def pos_1(self):
        return rd.random()

    def pos_2(self):
        return rd.random()

    def pos_3(self):
        return rd.random()
    
    def enable(self):
        print("Enabled")
    
    def disable(self):
        print("Disabled")
    