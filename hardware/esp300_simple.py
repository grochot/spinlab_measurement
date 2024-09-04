import pyvisa as visa
from pymeasure.instruments import Instrument
import time


class Esp300():
    # Enable Visa port
    rm = visa.ResourceManager()
    address='GPIB0::20::INSTR'
    my_instrument = rm.open_resource(address)


    # init
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.timeout = 2
        print("ESP300_simple.py, Connected")
        
        


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
        self.write("1MO; 2MO; 3MO")
        print("Motions Enabled")

    def disable(self):
        self.write("1MF; 2MF; 3MF")
        print("Disabled Enabled")

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


    def pos_1(self):
        try:
            units = self.ask("1DP")
            units = float(units)
            print("Units:",units)
        except:
            print("ERROR while reading position on axis Z!")
        return units #* self.psperunit

    def pos_2(self):
        try:
            units = self.ask("2DP")
            units = float(units)
            self.last_position = units
            print(self.last_position)

        except:
            print("ERROR while reading position on axis X!")
            units = self.last_position
        return units

    def pos_3(self):
        try:
            units = self.ask("3DP")
            units = float(units)
            self.last_position = units
        except:
            print("ERROR while reading position on axis Y!")
            units = self.last_position
        return units

if __name__ == "__main__":
    dev=Esp300()
    dev.enable()
    dev.goTo_1(0.15)
    dev.goTo_2(0.45)
    dev.goTo_3(0.35)
    dev.disable()
