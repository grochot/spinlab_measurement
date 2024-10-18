import pyvisa as visa
from pymeasure.instruments import Instrument
import time
import logging
log = logging.getLogger(__name__) 
log.addHandler(logging.NullHandler()) 


class Esp300():
    TAKE_OFF_PROTECTION=0.05
    def __init__(self,address,**kwargs):
        #super().__init__(**kwargs)
        self.timeout = 2
        rm = visa.ResourceManager()
        self.my_instrument = rm.open_resource(address)
        
        


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
    

    def is_motor_1_active(self):
        return self.ask("1MO?")
    
    def is_motor_2_active(self):
        return self.ask("2MO?")
    
    def is_motor_3_active(self):
        return self.ask("3MO?")

    def test(self):
        print("work mo",self.ask("2MO?"))

#HighLevel part
    def disconnect(self,sample_in_plane,disconnect_length):
        if sample_in_plane:
            z_pos=self.pos_3()

            self.goTo_3(z_pos-disconnect_length) #Disconnecting

            if abs((z_pos-disconnect_length)-self.pos_3())>self.TAKE_OFF_PROTECTION:
                self.disable()
                print("Take off Failure")
                log.error("Automati station - Take off Failure")

        else:
            z_pos=self.pos_1()

            self.goTo_1(z_pos-disconnect_length) #Disconnecting
            if abs((z_pos-disconnect_length)-self.pos_1())>self.TAKE_OFF_PROTECTION:
                self.disable()
                print("Take off Failure")
                log.error("Automati station - Take off Failure")

        self.pos_1() #Non sense reading position to stop program
        return z_pos


    def high_level_motion_driver(self,global_xyname,sample_in_plane,disconnect_length):
        if sample_in_plane:
            z_pos=self.disconnect(sample_in_plane,disconnect_length)

            self.goTo_2(float(global_xyname[0]))
            self.goTo_1(float(global_xyname[1]))

            self.goTo_3(z_pos) #Connecting

        else:
            z_pos=self.disconnect(sample_in_plane,disconnect_length)
            
            self.goTo_2(float(global_xyname[0]))
            self.goTo_3(float(global_xyname[1]))

            self.goTo_1(z_pos) #Connecting


        self.pos_1() #Non sense reading position to stop program

if __name__ == "__main__":
    dev=Esp300("GPIB0::20::INSTR")
    dev.test()
    #dev.enable()
    #dev.goTo_1(0.15)
    #dev.goTo_2(0.45)
    #dev.goTo_3(0.35)
    #dev.disable()
