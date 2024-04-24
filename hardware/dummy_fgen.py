import pyvisa


class DummyFgenDriver:
    def __init__(self):
        pass

    def errorQuery(self):
        pass

    def setFreq(self, freq_hz):
        pass

    def setPower(self, power_dbm):
        pass

    def setOutput(self, on, mod=False):
        pass
    
    def initialization(self):
        pass

    def set_lf_signal(self):
        pass

