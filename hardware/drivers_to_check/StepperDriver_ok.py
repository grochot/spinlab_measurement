import pyvisa
import time
from crc8dallas import crc8calc
from plotSleep import *

class StepperDriver:
    def __init__(self, port):
        rm = pyvisa.ResourceManager()
        self.dev = rm.open_resource(port)
        self.dev.baud_rate = 115200
        print("stepper_dev = " +str(self.dev))
        self.POffset = 0
        self.PGain = 1
        self.AOffset = 0
        self.AGain = 1
        self.setCallibration()
        self.move(0, 0)
        self.move(1, 0)

    def setCallibration(self, POffset=0.0, PGain=142.22, AOffset=0.0, AGain=155.0):
        self.POffset = POffset
        self.PGain = PGain
        self.AOffset = AOffset
        self.AGain = AGain

    def query(self, cmd):
        crc = crc8calc(cmd)
        result = self.dev.query(cmd + '{:03d};'.format(crc)).strip()
        crc_rec = int(result[-4:-1])
        result = result[0:-4]
        crc = crc8calc(result)
        if crc != crc_rec:
            return False
        return result

    def move(self, motor, steps):
        return self.query('MOVE {:d};{:d};'.format(motor, steps)) == 'OK;'

    def goToRaw(self, motor, pos):
        return self.query('POS {:d};{:d};'.format(motor, pos)) == 'OK;'

    def goToPolar(self, angle):
        return self.goToRaw(1, int(angle * self.PGain + self.POffset))

    def goToAzimuth(self, angle):
        return self.goToRaw(0, int(angle * self.AGain + self.AOffset))

    def checkBusyPolar(self):
        return self.query('MOVE {:d};{:d};'.format(1, 0)) == 'BUSY;'

    def checkBusyAzimuth(self):
        return self.query('MOVE {:d};{:d};'.format(0, 0)) == 'BUSY;'

    def waitBusy(self):
        while self.checkBusyAzimuth():
            plotSleep(0.25)
        while self.checkBusyPolar():
            plotSleep(0.25)

s = StepperDriver('ASRL3::INSTR')
s.goToPolar(10)
print(s.checkBusyAzimuth())
