import pyvisa


class PowerSupplyDriver:
    def __init__(self, port):
        rm = pyvisa.ResourceManager()
        self.dev = rm.open_resource(port)
        print("PowerSupply_dev = " + self.dev.query('*IDN?').strip())
        self.dev.write('*RST')

    def errorQuery(self):
        return self.dev.query('SYST:ERR?')

    def setOutput(self, on):
        if on:
            outp = 'ON'
        else:
            outp = 'OFF'
        self.dev.write('OUTP '+outp+';')

    def setHighVoltage(self, on):
        if on:
            outp = 'P20V'
        else:
            outp = 'P8V'
        self.dev.write('VOLT:RANG ' + outp + ';')

    def setVoltage(self, voltage):
        self.dev.write('VOLT {:.6f};'.format(voltage))

    def setCurrent(self, current):
        self.dev.write('CURR {:.6f};'.format(current))

    def selChannel(self, channel):
        if channel not in [1, 2]:
            channel = 1
            print("PowerSupply: channel out of range")
        self.dev.write('INST:SEL OUT{:d};'.format(channel))

    def measureCurrent(self):
        resp = self.dev.query('MEAS:CURR?;')
        return float(resp)

    def measureVoltage(self):
        resp = self.dev.query('MEAS:VOLT?;')
        return float(resp)

