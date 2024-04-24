from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set
from time import sleep

import time
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class SIM928(Instrument):
    def __init__(self, adapter, read_termination="\n", **kwargs):
        super().__init__(
            adapter,
            "SRS Sim928 Voltage Source" ,
            read_termination=read_termination,
            **kwargs
        )

    def enabled(self):
        self.write("OPON")
   
    def disabled(self):
        self.write("OPOF")

    def voltage_setpoint(self, vol = 0): 
        sleep(0.5)
        print("VOLT:{}".format(vol/1000))
        self.write("VOLT {}".format(round(vol/1000,3)))
        sleep(0.5)
    

    voltage = Instrument.measurement(
        "VOLT?",
        """Reads the voltage (in Volt) the dc power supply is putting out.
        """,
    )

    def run_to_zero(self): 
        self.voltage_setpoint(0)
        sleep(0.3)
        self.disabled()



    @property
    def error(self):
        """ Returns a tuple of an error code and message from a
        single error. """
        err = self.values(":system:error?")
        if len(err) < 2:
            err = self.read()  # Try reading again
        code = err[0]
        message = err[1].replace('"', "")
        return (code, message)

    def check_errors(self):
        """ Logs any system errors reported by the instrument.
        """
        code, message = self.error
        while code != 0:
            t = time.time()
            log.info("SIM928 reported error: %d, %s" % (code, message))
            code, message = self.error
            if (time.time() - t) > 10:
                log.warning("Timed out for SIM 928 error retrieval.")

    def shutdown(self):
        """ Disable output, call parent function"""
        self.enabled = False
        super().shutdown()
