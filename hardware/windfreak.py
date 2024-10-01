from windfreak import SynthHD


class Windfreak:
    def __init__(self, address, channel=None):
        if address.startswith("ASRL") and address.endswith("::INSTR"):
            self.address = "COM" + address[4:address.index("::")]
        elif address.startswith("COM"):
            self.address = address
        else:
            raise ValueError("Windfreak: Invalid address: '{}'".format(address))
        self.channel = 0 if channel is None else channel
        self.rfgen = SynthHD(self.address)

    def __enter__(self):
        self.rfgen.init()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.rfgen[0].enable = False
        self.rfgen[1].enable = False
        self.rfgen.close()

    def enable(self):
        self.rfgen[self.channel].enable = True

    def disable(self):
        self.rfgen[self.channel].enable = False

    def setChannel(self, channel: int):
        if channel not in [0, 1]:
            raise ValueError("Channel must be 0 or 1. You entered: {}".format(channel))

        self.channel = channel

    def setFreq(self, frequency: float):
        self.rfgen[self.channel].frequency = frequency

    def setPower(self, power: float):
        self.rfgen[self.channel].power = power

    def initialization(self):
        self.rfgen.init()

    def set_lf_signal(self):
        pass

    def setOutput(self, on: bool, mod: bool = False):
        if on:
            self.enable()
        else:
            self.disable()
            self.rfgen.close()
