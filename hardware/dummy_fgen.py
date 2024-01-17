import pyvisa


class DummyFgenDriver:
    def __init__(self, port):
        pass

    def errorQuery(self):
        pass

    def setFreq(self, freq_hz):
        pass

    def setPower(self, power_dbm):
        pass

    def setOutput(self, on, mod=False):
        pass

