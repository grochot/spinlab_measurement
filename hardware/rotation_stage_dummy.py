import pyvisa
import time
from hardware.crc8dallas import crc8calc


class RotationStageDummy:
    def __init__(self, port):
        pass

    def setCallibration(self, POffset=0.0, PGain=142.22, AOffset=0.0, AGain=155.0):
        pass

    def query(self, cmd):
        pass

    def move(self, motor, steps):
        pass

    def goToRaw(self, motor, pos):
        pass

    def goToPolar(self, angle):
        pass

    def goToAzimuth(self, angle):
        pass

    def checkBusyPolar(self):
        pass

    def checkBusyAzimuth(self):
        pass

    def goToZero(self):
        pass
