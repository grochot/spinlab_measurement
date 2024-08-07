
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set
import numpy as np

class Agilent34410A(Instrument):
    def __init__(self, adapter, name="HP 34401A", **kwargs):
        super().__init__(
            adapter,
            name,
            asrl={'baud_rate': 9600, 'data_bits': 7, 'parity': 2},
            **kwargs
        )
    FUNCTIONS = {"DCV": "VOLT", "DCV_RATIO": "VOLT:RAT",
                 "ACV": "VOLT:AC", "DCI": "CURR", "ACI": "CURR:AC",
                 "R2W": "RES", "R4W": "FRES", "FREQ": "FREQ",
                 "PERIOD": "PER", "CONTINUITY": "CONT", "DIODE": "DIOD"}

    FUNCTIONS_WITH_RANGE = {
        "DCV": "VOLT", "ACV": "VOLT:AC", "DCI": "CURR",
        "ACI": "CURR:AC", "R2W": "RES", "R4W": "FRES",
        "FREQ": "FREQ", "PERIOD": "PER"}

    BOOL_MAPPINGS = {True: 1, False: 0}

    range_ = Instrument.control(
        "{function_prefix_for_range}:RANG?", "{function_prefix_for_range}:RANG %s",
        """Control the range for the currently active function.

        For frequency and period measurements, ranging applies to
        the signal's input voltage, not its frequency""",
    )
    autorange = Instrument.control(
        "{function_prefix_for_range}:RANG:AUTO?",
        "{function_prefix_for_range}:RANG:AUTO %d",
        """Control the autorange state for the currently active function.""",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True,
    )

    resolution = Instrument.control(
        "{function}:RES?", "{function}:RES %g",
        """Control the resolution of the measurements.

        Not valid for frequency, period, or ratio.
        Specify the resolution in the same units as the
        measurement function, not in number of digits.
        Results in a "Settings Conflict" error if autorange is enabled.
        MIN selects the smallest value accepted, which gives the most resolution.
        MAX selects the largest value accepted which gives the least resolution.""",
    )
    function_ = Instrument.control(
        "FUNC?", "FUNC \"%s\"",
        """Control the measurement function.

        Allowed values: "DCV", "DCV_RATIO", "ACV", "DCI", "ACI",
        "R2W", "R4W", "FREQ", "PERIOD", "CONTINUITY", "DIODE".""",
        validator=strict_discrete_set,
        values=FUNCTIONS,
        map_values=True,
        get_process=lambda v: v.strip('"'),
    )

    # def set_average(self, average):
    #     Agilent34410A.trigger_count = average
    #     Agilent34410A.trigger_delay = "MIN"
    
    # def get_average(self):
    #     self.results = Agilent34410A.reading
    #     avg = np.average(self.results)
    #     return avg 
        
        
    
    trigger_delay = Instrument.control(
        "TRIG:DEL?", "TRIG:DEL %s",
        """Control the trigger delay in seconds.

        Valid values (incl. floats): 0 to 3600 seconds, "MIN", "MAX".""",
    )
    reading = Instrument.measurement(
        "READ?",
        """Take a measurement of the currently selected function.

        Reading this property is equivalent to calling `init_trigger()`,
        waiting for completion and fetching the reading(s).""",
    )
    trigger_count = Instrument.control(
        "TRIG:COUN?", "TRIG:COUN %s",
        """Control the number of triggers accepted before returning to the "idle" state.

        Valid values: 1 to 50000, "MIN", "MAX", "INF".
        The INFinite parameter instructs the multimeter to continuously accept triggers
        (you must send a device clear to return to the "idle" state).""",
    )
    terminals_used = Instrument.measurement(
        "ROUT:TERM?",
        """Query the multimeter to determine if the front or rear input terminals
        are selected.

        Returns "FRONT" or "REAR".""",
        values={"FRONT": "FRON", "REAR": "REAR"},
        map_values=True,
    )
    nplc = Instrument.control(
        "{function}:NPLC?", "{function}:NPLC %s",
        """Control the integration time in number of power line cycles (NPLC).

        Valid values: 0.02, 0.2, 1, 10, 100, "MIN", "MAX".
        This command is valid only for dc volts, ratio, dc current,
        2-wire ohms, and 4-wire ohms.""",
        validator=strict_discrete_set,
        values=[0.02, 0.2, 1, 10, 100, "MIN", "MAX"],
    )

    def write(self, command):
        """Write a command to the instrument."""
        if "{function_prefix_for_range}" in command:
            command = command.replace("{function_prefix_for_range}",
                                      self._get_function_prefix_for_range())
        elif "{function}" in command:
            command = command.replace("{function}", Agilent34410A.FUNCTIONS[self.function_])
        super().write(command)

    def _get_function_prefix_for_range(self):
        function_prefix = Agilent34410A.FUNCTIONS_WITH_RANGE[self.function_]
        if function_prefix in ["FREQ", "PER"]:
            function_prefix += ":VOLT"
        return function_prefix



# dmm = Agilent34410A("GPIB0::28::INSTR")

# dmm.function_ = "DCV"
# # print(dmm.reading)  # -> Single float reading

# dmm.nplc = 10
# dmm.set_average(1)

# print(dmm.reading)  # -> Single float reading