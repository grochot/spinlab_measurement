from pymeasure.instruments import Instrument, RangeException
from pymeasure.instruments.validators import truncated_range, strict_discrete_set



class KeysightB2912A(Instrument):
    def __init__(self, resourceName, **kwargs):
        kwargs.setdefault('read_termination', '\n')
        super().__init__(
            resourceName,
            "Keysight B2912A",
            includeSCPI=True,
            **kwargs
        )
    source_mode = Instrument.control( -ok
        ":SOUR:FUNC?", ":SOUR:FUNC %s",
        """ A string property that controls the source mode, which can
        take the values 'current' or 'voltage'. """,
        validator=strict_discrete_set,
        values={'CURR': 'CURR', 'VOLT': 'VOLT'},
        map_values=True
    )
    voltage_range = Instrument.control( -ok
        ":SOUR:VOLT:RANG?", ":SOUR:VOLT:RANG:AUTO OFF;:SOUR:VOLT:RANG %g",
        """ A floating point property that controls the measurement voltage
        range in Volts, which can take values from -210 to 210 V.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[-210, 210]
    )
    compliance_current = Instrument.control(-ok
        ":SENS:CURR:PROT?", ":SENS:CURR:PROT %g",
        """ A floating point property that controls the compliance current
        in Amps. """,
        validator=truncated_range,
        values=[-3.03, 3.03]
    )

    def enable_source(self): -ok
        self.write(":OUTP ON")
    
    def measure_current(self, nplc=1, current=1.05e-4, auto_range=True):
        """ Configures the measurement of current.

        :param nplc: Number of power line cycles (NPLC) from 0.01 to 10
        :param current: Upper limit of current in Amps, from -3.03 A to 3.03 A
        :param auto_range: Enables auto_range if True, else uses the set current
        """
       
        self.write(":SENS:FUNC 'CURR';"
                    ":SENS:CURR:NPLC %f;:FORM:ELEM:SENS CURR;" % nplc)
        if auto_range:
            self.write(":SOUR:CURR:RANG:AUTO ON;")
        else:
            self.current_range = current
        self.check_errors()

    current_range = Instrument.control(
        ":SOUR:CURR:RANG?", ":SOUR:CURR:RANG:AUTO OFF;:SOUR:CURR:RANG %g",
        """ A floating point property that controls the measurement current
        range in Amps, which can take values between -3.03 and +3.03 A.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[-3.03, 3.03]
    )   
    compliance_voltage = Instrument.control(
        ":SENS:VOLT:PROT?", ":SENS:VOLT:PROT %g",
        """ A floating point property that controls the compliance voltage
        in Volts. """,
        validator=truncated_range,
        values=[-210, 210]
    ) 
    def measure_voltage(self, nplc=1, voltage=21.0, auto_range=True):
        """ Configures the measurement of voltage.

        :param nplc: Number of power line cycles (NPLC) from 0.01 to 10
        :param voltage: Upper limit of voltage in Volts, from -210 V to 210 V
        :param auto_range: Enables auto_range if True, else uses the set voltage
        """
        self.write(":SENS:FUNC 'VOLT';"
                    ":SENS:VOLT:NPLC %f;:FORM:ELEM:SENS VOLT;" % nplc)
        if auto_range:
            self.write(":SOUR:VOLT:RANG:AUTO ON;")
        else:
            self.voltage_range = voltage
        self.check_errors()
    
    def shutdown(self):
        self.write(":OUTP OFF")

    def config_average(self, average):
        # self.write(":SENSe:AVERage:TCONtrol REP")
        # self.write(":SENSe:AVERage:COUNt {}".format(average))
        self.write(":TRIG:COUN {}".format(average))
    
    source_voltage = Instrument.control(
        ":SOUR:VOLT?", ":SOUR:VOLT %g",
        """ A floating point property that controls the source voltage
        in Volts. """
    )
    
    source_current = Instrument.control(
        ":SOUR:CURR?", ":SOUR:CURR %g",
        """ A floating point property that controls the source current
        in Amps. """,
        validator=truncated_range,
        values=[-1.05, 1.05]
    )

    current = Instrument.measurement(
        ":MEAS?",
        """ Reads the current in Amps, if configured for this reading.
        """
    )
   
    voltage = Instrument.measurement(
        ":MEAS?",
        """ Reads the voltage in Volt, if configured for this reading.
        """
    )
