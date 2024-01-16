import pyvisa
import time
import numpy as np
import sys
from plotSleep import *

class FieldDriverLockIn:
    def __init__(self, port, gain, step, delay, dac):
        rm = pyvisa.ResourceManager()
        self.dev = rm.open_resource(port)
        self.gain = gain
        self.dac = dac
        self.step = step
        self.delay = delay
        print("field_dev = " + self.query('ID')[0].strip())
        self.write('DD 44')

    def query(self, command):
        for i in range(10):
            try:
                self.dev.write(command)
                # wait for DAV bit
                while not (self.dev.read_stb() & (1 << 7)):
                    plotSleep(0.01)
                plotSleep(0.05)
                response = self.dev.read()
                return response.split(',')
            except:
                print("Oops!", sys.exc_info()[0], "occurred.")

    def write(self, command):
        for i in range(10):
            try:
                self.dev.write(command)
                # wait for command done bit
                while not (self.dev.read_stb() & (1 << 0)):
                    plotSleep(0.01)
            except:
                print("Oops!", sys.exc_info()[0], "occurred.")

    def readDAC(self, dac):
        if dac == 1:
            b1 = int(self.query('PEEK 65624')[0])
            b2 = int(self.query('PEEK 65625')[0])
        else:
            b1 = int(self.query('PEEK 65622')[0])
            b2 = int(self.query('PEEK 65623')[0])
        if b2 < 0:
            b2 = b2 + 256
        b2 = b2 / 2
        b1 = b1 / 2
        b1 = b1 * 256
        v = b1 + b2
        v = v / 1000
        return v

    def setDAC(self, dac, voltage):
        voltage = voltage * 1000
        self.write('DAC {:d} {:d}'.format(dac, int(voltage)))

    def setRAW(self, voltage):
        self.setDAC(self.dac, voltage)

    def setField(self, field):
        self.setRAW(field * self.gain)

    def getField(self):
        return self.readDAC(self.dac) / self.gain

    def setFieldSlow(self, field):
        step = self.step
        plotSleep(0.05)
        actField = self.getField()
        if abs(actField - field) > step:
            if actField > field:
                step = -step
            for f in np.arange(actField + step, field, step):
                self.setField(f)
                plotSleep(self.delay)
        self.setField(field)

    def setGain(self, gain):
        self.gain = gain
