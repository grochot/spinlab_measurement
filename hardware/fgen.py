import pyvisa


class FgenDriver:
    def __init__(self, port):
        rm = pyvisa.ResourceManager()
        self.dev = rm.open_resource(port)
        print("fgen_dev = " + self.dev.query('*IDN?').strip())
        self.dev.write('*RST')
        self.dev.write('*ESE 61;*SRE 48;*CLS;')

    def errorQuery(self):
        return self.dev.query('SYST:ERR?')

    def setFreq(self, freq_hz):
        #print("fgen_freq = " + str(freq_hz/1e9) + " GHz")
        self.dev.write(
            ':FREQ:MODE FIX;:FREQ {:.6f} HZ;:FREQ:REF:STAT OFF;:FREQ:'
            'OFFS 0.000000 HZ;:FREQ:MULT 1.000000;:PHAS 0.000000 RAD;'.format(
                freq_hz))

    def setPower(self, power_dbm):
        #print("fgen_power = " + str(power_dbm) + " dBm")
        self.dev.write(
            ':POW:MODE FIX;:POW {:.6f} DBM;:POW:REF:STAT OFF;:POW:OFFS 0.000000 DB;:POW:ATT:AUTO ON;'.format(
                power_dbm))

    def setOutput(self, on, mod=False):
        if on:
            outp = 'ON'
        else:
            outp = 'OFF'

        if mod:
            outpMod = 'ON'
        else:
            outpMod = 'OFF'
        #print("fgen_output = "+outp)
        #print("fgen_modulation = " + outpMod)
        self.dev.write(':OUTP '+outp+';:OUTP:MOD '+outpMod+';:OUTP:BLAN:AUTO ON;:OUTP:BLAN:STAT ON;:OUTP:PROT ON;')

