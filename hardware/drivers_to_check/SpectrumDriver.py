import pyvisa
import time
from scanf import scanf
from plotSleep import *

class SpectrumDriver:
    def __init__(self, port):
        rm = pyvisa.ResourceManager()
        self.dev = rm.open_resource(port)
        print("spectrum_dev = " + self.dev.query('*IDN?').strip())
        self.dev.write('*ESE 61;*SRE 48;*CLS;')
        self.dev.write(':INST:NSEL 1;:FORM ASC;')
        self.dev.write(':CONF:SAN;')
        self.waitAcqComplete()
        self.dev.write(':FEED:AREF OFF;:CORR:IMP 50;:INP:COUP AC;:CORR:SA:GAIN 0.000000;:ROSC:SOUR:TYPE SENS;')

    def setRBW(self, RBW):
        RBW = int(RBW)
        self.dev.write(
            ':BWID:VID:RAT:AUTO ON;:SWE:TIME:AUTO ON;:BWID:AUTO OFF;:BWID {:d};:BWID:VID:AUTO ON;'.format(RBW))

    def setRef(self, ref):
        self.dev.write(
            ':UNIT:POW DBM;:DISP:WIND:TRAC:Y:RLEV {:.6f};:DISP:WIND:TRAC:Y:RLEV:OFFS 0.000000;'
            ':POW:ATT:AUTO OFF;:POW:ATT 0.000000;:POW:ATT:STEP 2;'.format(ref))
        self.dev.write(':POW:GAIN ON;')
        self.dev.write(':POW:GAIN:BAND FULL;')

    def setAvg(self, avg):
        self.dev.write(':TRAC1:TYPE AVER;:TRAC1:UPD ON;:TRAC1:DISP ON;')
        self.dev.write(':AVER:TYPE LOG;:AVER:COUN {:d};'.format(avg))

    def setFrequencyRange(self, start, stop):
        self.dev.write(':FREQ:START {:.6E};:FREQ:STOP {:.6E};'.format(start, stop))

    def setPoints(self, points):
        self.dev.write(
            ':DET:TRAC1:AUTO OFF;:DET:TRAC1 AVER;:SWE:POIN {:d};:DISP:WIND:TRAC:Y:SPAC LOG;'.format(points))

    def setScale(self, scale):
        self.dev.write(':DISP:WIND:TRAC:Y:PDIV {:.6f};:INIT:CONT OFF;'.format(scale))

    def getMeasurement(self, timeout=60.0):
        self.dev.write(':INIT:SAN;')
        self.waitAcqComplete(timeout)
        self.dev.write(':FETC:SAN1?;')
        result = self.dev.read().strip()
        freq = list()
        power = list()
        while len(result) > 0:
            tmp = scanf('%f,%f,%s', result)
            if not tmp:
                x, y = scanf('%f,%f', result)
                result = ''
            else:
                x = tmp[0]
                y = tmp[1]
                result = tmp[2]
            freq.append(x)
            power.append(y)

        return freq, power


    def errorQuery(self):
        return self.dev.query('SYST:ERR?')

    def waitAcqComplete(self, timeout=10.0):
        self.dev.write('*CLS')
        self.dev.write('*OPC')
        start_time = time.time()
        while time.time() - start_time <= timeout:
            result = int(self.dev.query('*STB?').strip())
            if result & (1<<5):
                break
            plotSleep(0.01)

