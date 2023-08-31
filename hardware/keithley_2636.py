from pymeasure.instruments import Instrument

class Keithley2636(Instrument):
    def __init__(self, adapter, name, includeSCPI=True, preprocess_reply=None, **kwargs):
        super().__init__(adapter, name, includeSCPI, preprocess_reply, **kwargs)


    def set_channel(self, channel):
        pass

