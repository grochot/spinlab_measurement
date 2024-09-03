import pyvisa as visa
import time


class Esp300():
    # Enable Visa port
    rm = visa.ResourceManager()
    my_instrument = rm.open_resource('GPIB0::20::INSTR')
    # del my_instrument.timeout
    _address = 'GPIB0::20::INSTR'


    # init
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timeout = 2


    def write(self, cmd):
        self.my_instrument.timeout = 25000
        self.my_instrument.write(cmd)
        self.my_instrument.read_termination = '\r'


    def ask(self, cmd):
        self.my_instrument.timeout = 25000
        position = self.my_instrument.query(cmd)
        self.my_instrument.read_termination = '\r'
        return position
    

    def enable(self):
        self.write("M0; M1; M2")
        print("Motions Enabled")

    def disable(self):
        self.write("MF0; MF1; MF2")
        print("Motions Enabled")

    "There is Z axis"
    def goTo_1(self, position, wait=False):
        #print("goto:", position)
        units = position
        self.write("1PA" + str(units)+ ";1WS500")
        if (wait == True):
            while (self.get_motion_status() != 0):
                sleep(0.10)

    "There is X axis"
    def goTo_2(self, position, wait=False):
        #print("goto:", position)
        units = position
        self.write("2PA" + str(units)+ ";2WS500")
        #callback_read_position()
        if (wait == True):
            while (self.get_motion_status() != 0):
                sleep(0.10)

    "There is Y axis"
    def goTo_3(self, position, wait = False):
        #print("goto:", position)
        units = position
        self.write("3PA" + str(units)+ ";3WS500")
        #callback_read_position()
        if (wait == True):
            while (self.get_motion_status() != 0):
                sleep(0.10)

if __name__ == "__main__":
    dev=Esp300()
    dev.enable()
    dev.goTo_1(0.25)
    dev.goTo_2(0.5)
    dev.goTo_3(0.45)
    dev.disable()
