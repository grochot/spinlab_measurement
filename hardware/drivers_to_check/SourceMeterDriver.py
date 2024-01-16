import pyvisa


class SourceMeterDriver:
    def __init__(self, port):
        rm = pyvisa.ResourceManager()
        self.dev = rm.open_resource(port)
        print("sourceMeter_dev = " + self.dev.query('*IDN?').strip())
        self.dev.write('*RST')
        self.dev.write('*ESE 60;*SRE 48;*CLS;')

    def errorQuery(self):
        return self.dev.query('SYST:ERR?')

    def configureSource(self, voltage=0, Vrange=2):
        self.dev.write(':SOUR1:VOLT {:.6f};VOLT:TRIG 0.000000;RANG {:.6f};:SOUR1:FUNC DC;'
                       'FUNC:MODE VOLT;TRIG:CONT ON;:SOUR1:VOLT:RANG:AUTO ON;AUTO:LLIM 2.000000'.format(voltage, Vrange))

    def configureResistanceMeasurement(self, nplc=0.01):
        self.dev.write(':SENS1:FUNC:OFF:ALL;:SENS1:FUNC "CURR","VOLT","RES";')
        self.dev.write(':SENS1:RES:OCOM OFF;:SENS1:RES:NPLC {:.6f};RANG 2.000000;MODE MAN;'
                       'NPLC:AUTO OFF;:SENS1:RES:RANG:AUTO ON;AUTO:LLIM 2.000000;ULIM 2.000000E+8;'.format(nplc))

    def configureLimit(self, Ilimit=0.01, Vlimit=20.0):
        self.dev.write(':SENS1:CURR:PROT {:.6f};:OUTP1:PROT ON;:SENS1:VOLT:PROT {:.6f};'.format(Ilimit, Vlimit))

    def configureOutput(self):
        self.dev.write(':OUTP1:OFF:AUTO OFF;:OUTP1:LOW GRO;HCAP OFF;OFF:MODE NORM;:OUTP1:ON:AUTO OFF;')

    def setOutput(self, on):
        if on:
            outp = 'ON'
        else:
            outp = 'OFF'
        self.dev.write(':OUTP1 '+outp+';')

    def measureGeneral(self, typ):
        return float(self.dev.query(':MEAS:'+typ+'? (@1);'))

    def measureResistance(self):
        return self.measureGeneral('RES')

    def measureVoltage(self):
        return self.measureGeneral('VOLT')

    def measureCurrent(self):
        return self.measureGeneral('CURR')

    def setContinous(self):
        self.dev.write(':trig:acq:sour aint')
        self.dev.write(':trig:acq:coun inf')
        self.dev.write(':init:acq (@1)')
