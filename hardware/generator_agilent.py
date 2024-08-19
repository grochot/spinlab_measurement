import pyvisa
from pymeasure.instruments import Instrument


class FGenDriver(Instrument):
    def __init__(self, adapter, name="Agilent E8257D",
                 **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

    def errorQuery(self):
        return self.ask('SYST:ERR?')

    def setFreq(self, freq_hz):
        #print("fgen_freq = " + str(freq_hz/1e9) + " GHz")
        self.write(
            ':FREQ:MODE FIX;:FREQ {:.6f} HZ;:FREQ:REF:STAT OFF;:FREQ:'
            'OFFS 0.000000 HZ;:FREQ:MULT 1.000000;:PHAS 0.000000 RAD;'.format(
                freq_hz))

    def setPower(self, power_dbm):
        #print("fgen_power = " + str(power_dbm) + " dBm")
        self.write(
            ':POW:MODE FIX;:POW {:.6f} DBM;:POW:REF:STAT OFF;:POW:OFFS 0.000000 DB;:POW:ATT:AUTO ON;'.format(
                power_dbm))

    def setOutput(self, on, mod=False):
        if on:
            outp = 'ON'
        else:
            outp = 'OFF'

        if mod:
            outpMod = 'ON'
            self.write(":AM:SOUR INT")
            self.write(":AM:INT:FUNC:SHAP SINE")
            self.write(":AM:INT:FREQ 300 HZ")
            self.write(":AM:INT:FREQ:ALT 300 HZ")
            self.write(":AM:STAT ON")
            self.write(":AM:MODE NORM")
            self.write(":AM:TYPE LIN")
            self.write(":AM:TRAC ON")
            self.write(":AM:DEPTH 90 PCT")
        else:
            outpMod = 'Off'

        self.write(':OUTP '+outp+';:OUTP:MOD '+outpMod+';:OUTP:BLAN:AUTO ON;:OUTP:BLAN:STAT ON;:OUTP:PROT ON;')


        # if mod:
        #     outpMod = 'ON'
        # else:
        #     outpMod = 'OFF'
        # #print("fgen_output = "+outp)
        # #print("fgen_modulation = " + outpMod)
        # self.write(':OUTP '+outp+';:OUTP:MOD '+outpMod+';:OUTP:BLAN:AUTO ON;:OUTP:BLAN:STAT ON;:OUTP:PROT ON;')

        # self.write(":AM:SOUR INT")
        # self.write(":AM:INT:FUNC:SHAP SINE")
        # self.write(":AM:INT:FREQ 300 HZ")
        # self.write(":AM:INT:FREQ:ALT 300 HZ")
        # self.write(":AM:STAT ON")
        # self.write(":AM:MODE NORM")
        # self.write(":AM:TYPE LIN")
        # self.write(":AM:TRAC ON")
        # self.write(":AM:DEPTH 90 PCT")

    
    def initialization(self):
        self.write('*RST')
        self.write('*ESE 61;*SRE 48;*CLS;')
    
    def set_lf_signal(self):
        self.write(':LFO:SOUR INT')
        self.write(':LFO:AMPL 1VP')
        # self.write(':LFO:FUNC1:FREQ 287HZ')
        # self.write(':LFO:FUNC1:SHAP SINE')
        # self.write(":LFO:FUNC1:FREQ:ALT 287HZ")
        self.write(':LFO:STAT ON')

# dd = FGenDriver("GPIB1::19::INSTR")
# dd.setFreq(9e6)