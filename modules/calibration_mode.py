from time import sleep
import math
import numpy as np
import logging
from hardware.daq import DAQ
from hardware.dummy_field import DummyField
from hardware.lakeshore import Lakeshore
from hardware.GM_700 import GM700
from hardware.dummy_gaussmeter import DummyGaussmeter
from logic.field_calibration import calibration, set_calibrated_field
from logic.sweep_field_to_zero import sweep_field_to_zero

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class FieldCalibrationMode:
    def __init__(self, set_field, set_gaussmeter, address_daq, address_gaussmeter, vector, delay) -> None:
        self.set_field = set_field
        self.set_gaussmeter = set_gaussmeter
        self.address_gaussmeter = address_gaussmeter
        self.address_daq = address_daq
        self.vector = vector
        self.delay = delay

        ## parameter initialization

    def generate_points(self):
        vector = self.vector.split(",")
        self.start_volt = float(vector[0])
        self.stop_volt = float(vector[2])
        self.num_points = int(vector[1])

        vector = np.linspace(self.start_volt, self.stop_volt, self.num_points)

        if any(i < 0 for i in vector):
            raise ValueError("All voltages must be greater or equal to 0")

        if len(vector) < 2:
            raise ValueError("The number of points must be greater than 1")

        return vector

    def initializing(self):
        if self.set_field == "none":
            self.daq = DummyField(self.address_daq)
            log.warning("Used dummy DAQ")
        else:
            self.daq = DAQ(self.address_daq)

        if self.set_gaussmeter == "none":
            self.gaussmeter = DummyGaussmeter(self.address_gaussmeter)
            log.warning("Used dummy Gaussmeter")
        elif self.set_gaussmeter == "GM700":
            self.gaussmeter = GM700(self.address_gaussmeter)
        elif self.set_gaussmeter == "Lakeshore":
            self.gaussmeter = Lakeshore(self.address_gaussmeter)
        else:
            raise ValueError("Gaussmeter not supported")

    def operating(self):
        self.calibration_constant = calibration(self, self.start_volt, self.stop_volt, self.num_points, self.daq, self.gaussmeter, self.delay)
        self.daq.field_constant = self.calibration_constant

        data = {
            "Voltage (V)": math.nan,
            "Current (A)": math.nan,
            "Resistance (ohm)": math.nan,
            "Field (Oe)": math.nan,
            "Frequency (Hz)": math.nan,
            "X (V)": math.nan,
            "Y (V)": math.nan,
            "Phase": math.nan,
            "Polar angle (deg)": math.nan,
            "Azimuthal angle (deg)": math.nan,
        }
        return data, self.calibration_constant

    def end(self):
        FieldCalibrationMode.idle(self)

    def idle(self):
        sweep_field_to_zero(
            self.stop_volt / self.calibration_constant, self.calibration_constant, int((self.stop_volt / self.calibration_constant) / 10), self.daq
        )  # czy tutaj nie powinno byc mnozenia?


# test = FieldCalibrationMode("ff", "dfd", 'Dev4/ao0', 'GPIB1::12::INSTR',[0,5,1], 2)
# test.initializing()
# test.operating()
# sleep(5)
# test.end()
