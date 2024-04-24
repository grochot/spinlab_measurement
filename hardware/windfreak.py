from windfreak import SynthHD


class Windfreak:
    def __init__(self, address):
        self.address = address
        self.rfgen = SynthHD(address)

    def __enter__(self):
        self.rfgen.init()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("########### RFGen close method ###########\n"
              "    disabling and closing communication\n"
              "###########################################")
        self.disable(0)
        self.disable(1)
        self.rfgen.close()

    def enable(self, channel: int):
        self.rfgen[channel].enable = True

    def disable(self, channel: int):
        self.rfgen[channel].enable = False

    def set_frequency(self, channel, frequency):
        self.rfgen[channel].frequency = frequency

    def set_power(self, channel, power):
        self.rfgen[channel].power = power


