import pyvisa
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range



class LFGenDriver(Instrument):
    def __init__(self, adapter, name="HP 33120a",
                 **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

    def set_shape(self, shape):
        """ Sets output shape.

        :param shape: SINusoid, SQUare, TRIangle, RAMP, NOISe, USER, DC 
        """
        self.write("FUNC:SHAP " + shape)

    def set_freq(self, freq):
        """ Sets output frequency.

        :param freq:
        """

        self.write("FREQ %f" % (freq))

    def set_amp(self, amp):
        """ Sets output amplitude.

        :param amp:
        """

        self.write("VOLT %f" % (amp))
