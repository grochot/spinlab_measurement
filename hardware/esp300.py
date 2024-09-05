""" This file contains the Qudi Driver file for ESP300 driver controller
Created by  Dawid Gadziała AGH Kraków, Polska 2022"""

import pyvisa as visa
import time
#from qtpy import QtCore
from newportESP import ESP
#from core.util.helpers import in_range
from enum import Enum
import pandas as pd
import numpy as np
from core.module import Base
from time import sleep
from wx import GetTextFromUser
from loguru import logger
from core.connector import Connector
import core


class Esp300(Base):
    # Enable Visa port
    rm = visa.ResourceManager()
    #my_instrument = rm.open_resource('GPIB0::20::INSTR')
    # del my_instrument.timeout
    #_address = 'GPIB0::20::INSTR'


    # init
    def __init__(self, config, **kwargs):
        super().__init__(config=config, **kwargs)
        self.interval = 0.01
        self.config = ["interval"]
        self.timeout = 2
        self.sizeofsquare = 0.2 #0.2mm, there is size of square
        self.last_positionX = 0
        self.last_positionY = 0


    def on_activate(self):
        rm = visa.ResourceManager()
        try:
            self._my_instrument = rm.open_resource(self._address, write_termination='\n', read_termination='\n')
        except visa.VisaIOError:
            self.log.error('Could not connect to hardware, check power supply or cables')

    def calculate_walking(self, espCalculate):
        self.unit_walking_one_pixel = self.sizeofsquare / espCalculate
        print(f"1 pixel = {self.unit_walking_one_pixel} mm for ESP controller")
        return self.unit_walking_one_pixel

    "Convert from write to query, this command I use for set command to ESP 300"

    def write(self, cmd):
        self.my_instrument.timeout = 25000
        self.my_instrument.write(cmd)
        self.my_instrument.read_termination = '\r'


    def ask(self, cmd):
        self.my_instrument.timeout = 25000
        position = self.my_instrument.query(cmd)
        self.my_instrument.read_termination = '\r'
        return position

    def errorclear(self):
        error = 1
        while (error != 0):
            error = int(self.ask("TE?"))

    def initialize(self):
        self.write('2OR1; 2DH; 3OR1; 3DH')  # define HOME as zero
        print("I have set home position")


    def homing(self):
        # check whether device is responding
        print("Start home position:")
        self.write("1PA0;2PA0")  # go HOME as zero

    # Enable motions for asix

    @logger.catch
    def enable(self):
            self.write("M0; M1; M2")
            print("Motions Enabled")

    def disable(self):
        print("NOT IMPLEMENTED YET!")

    def connect(self):
        """ Connects to the esp
            @param (string) port: VISA port of the device
            @return (int): 0: OK, -1: ERROR
        """
        self.my_instrument.timeout(2500)
        self.my_instrument = self._my_instrument
        # self.instr = self._inst
        time.sleep(0.5)
        # TODO: check connection
        return 0

    # Read actual positions from all motions
    def read_positions(self):
        "Read positions from 3 axis"
        return self.pos_1(), self.pos_2(), self.pos_3()
    # reset
    def reset(self):
        print("reset ESP")
        self.initialize()


    "Quick stop motions"
    def stop(self):
        print("Stop motions!")
        return self.stop_1(), self.stop_2(), self.stop_3()

    def stop_1(self):
        self.write("1ST")

    def stop_2(self):
        self.write("2ST")

    def stop_3(self):
        self.write("3ST")

    "Set absolute position for Z,X,Y axis"
    "There is Z axis"
    def goTo_1(self, position, wait=False):
        #print("goto:", position)
        units = position
        self.write("1PA" + str(units)+ ";1WS500")
        if (wait == True):
            while (self.get_motion_status() != 0):
                sleep(0.10)

    "There is X axis"
    def goTo_2(self, position, callback_read_position, wait=False):
        #print("goto:", position)
        units = position
        self.write("2PA" + str(units)+ ";2WS500")
        #callback_read_position()
        if (wait == True):
            while (self.get_motion_status() != 0):
                sleep(0.10)

    "There is Y axis"
    def goTo_3(self, position, callback_read_position, wait = False):
        #print("goto:", position)
        units = position
        self.write("3PA" + str(units)+ ";3WS500")
        #callback_read_position()
        if (wait == True):
            while (self.get_motion_status() != 0):
                sleep(0.10)

    "In below command I call all 3 axis: Z,X,Y axis"
    def goTo_Global(self, positionX, positionY, wait = False):
        #print("gotoX:", positionX, "gotoY:", positionY)
        unitsX = positionX
        unitsY = positionY
        self.write("2PA" + str(unitsX)+";3PA" + str(unitsY))
        #callback_read_position()
        if (wait == True):
            while (self.get_motion_status() != 0):
                sleep(0.10)

    # jog module

    def jog_1(self, step, read_Actual_position):
        units = step
        self.write("1PR" + str(units))
        #print("Z axis moving in jog mode")
        #read_Actual_position()


    def jog_2(self, step, read_Actual_position):
        units = step
        self.write("2PR" + str(units))
        #print("X axis moving in jog mode")
        #read_Actual_position()


    def jog_3(self, step, read_Actual_position):
        units = step
        self.write("3PR" + str(units))
        #print("Y axis moving in jog mode")
        #read_Actual_position()



    # read current position
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

    def pos_2_offset(self):
        try:
            units = self.ask("2TP")
            units = float(units)
            self.last_positionX = units
            print(self.last_positionX)

        except:
            print("ERROR while reading position on axis X!")
            units = self.last_positionX
        return units

    def pos_3_offset(self):
        try:
            units = self.ask("3TP")
            units = float(units)
            self.last_positionY = units
            print(self.last_positionY)
        except:
            print("ERROR while reading position on axis Y!")
            units = self.last_positionY
        return units

    "relative motions for algoritm"
    "Set absolute position for Z,X,Y axis"
    "There is X axis"

    def relative_goTo_1(self, position,read_Actual_position, wait=False):
        # if (self.get_motion_status() != 0):
        # self.stop()
        print("goto:", position)
        units = position
        self.write("1PR" + str(units) + ";1WS500")
        read_Actual_position()
        if (wait == True):
            while (self.get_motion_status() != 0):
                sleep(0.10)

    "There is X axis"

    def relative_goTo_2(self, position,read_Actual_position, wait=False):
        print("goto:", position)
        units = position
        self.write("2PR" + str(units) + ";2WS500")
        read_Actual_position()
        if (wait == True):
            while (self.get_motion_status() != 0):
                sleep(0.10)

    "There is Y axis"

    def relative_goTo_3(self, position,read_Actual_position, wait=False):
        print("goto:", position)
        units = position
        self.write("3PR" + str(units) + ";3WS500")
        read_Actual_position()
        if (wait == True):
            while (self.get_motion_status() != 0):
                sleep(0.10)

    "In below command I call all 2 axis: X,Y axis"

    def relative_goTo_Global(self, positionX, positionY,read_Actual_position, wait=False):
        print("gotoX:", positionX, "gotoY:", positionY)
        unitsX = positionX
        unitsY = positionY
        self.write("2PR" + str(unitsX) + ";3PR" + str(unitsY))
        read_Actual_position()
        if (wait == True):
            while (self.get_motion_status() != 0):
                sleep(0.10)

    def goTo_1_walking(self, position, wait=False):
        print("goto:", position)
        units = position
        self.write("1PA" + str(units)+ ";1WS500")
        if (wait == True):
            while (self.get_motion_status() != 0):
                sleep(0.10)

    "There is X axis"
    def goTo_2_walking(self, position, wait=False):
        print("goto:", position)
        units = position * self.unit_walking_one_pixel
        self.write("2PA" + str(units)+ ";2WS500")
        if (wait == True):
            while (self.get_motion_status() != 0):
                sleep(0.10)

    "There is Y axis"
    def goTo_3_walking(self, position, wait = False):
        print("goto:", position)
        units = position * self.unit_walking_one_pixel
        self.write("3PA" + str(units)+ ";3WS500")
        if (wait == True):
            while (self.get_motion_status() != 0):
                sleep(0.10)

    "In below command I call all 3 axis: Z,X,Y axis"
    def goTo_Global_walking(self, positionX, positionY, wait = False):
        print("gotoX:", positionX, "gotoY:", positionY)
        unitsX = self.last_positionX + (positionX * self.unit_walking_one_pixel)
        unitsY = self.last_positionY + (positionY * self.unit_walking_one_pixel)
        #unitsZ = positionZ / self.psperunit
        #+ str(self.last_positionX) to wsadzic do srodka
        self.write("2PA" + str(unitsX) + ";3PA" + str(unitsY))
        #self.read_positions()
        if (wait == True):
            while (self.get_motion_status() != 0):
                sleep(0.10)


    # home position
    def home(self):
        if (self.get_motion_status() != 0):
            self.stop()
        self.goTo(0)




    def on_deactivate(self):
        pass


if __name__ == "__main__":
    dev=Esp300(["interval"],manager="rs232?",name="COM3")
    dev.calculate_walking(0.2)
    #print("Hello world")
    dev.goTo_1(0.25)
    dev.goTo_2(0.5)
    dev.goTo_3(0.45)
    print("Position:",dev.read_positions())
    dev.relative_goTo_1(0.35,dev.pos_1)
    #dev.homing()
    print("Position1:",dev.read_positions())
    #tmp
    print("Position2:",dev.read_positions())
    dev.goTo_Global(0.3,0.3)
    sleep(5)
    print("Position3:",dev.read_positions())

