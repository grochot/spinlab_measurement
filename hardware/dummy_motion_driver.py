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

    def goTo_1(self,position):
        print("go_to1",position)

    def goTo_2(self,position):
        print("go_to2",position)

    def goTo_3(self,position):
        print("go_to3",position)

    def pos_1(self):
        return 0.387
