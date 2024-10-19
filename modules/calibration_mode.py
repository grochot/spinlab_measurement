from time import sleep
from numpy import nan
import logging

from app import SpinLabMeasurement
from modules.measurement_mode import MeasurementMode

from hardware.daq import DAQ
from hardware.dummy_field import DummyField
from hardware.lakeshore import Lakeshore
from hardware.GM_700 import GM700
from hardware.dummy_gaussmeter import DummyGaussmeter

from logic.sweep_field_to_zero import sweep_field_to_zero
from scipy.stats import linregress

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class FieldCalibrationMode(MeasurementMode):
    def __init__(self, procedure: SpinLabMeasurement) -> None:
        self.p = procedure
        self.field_vector = []

    def initializing(self):
        if self.p.set_field_cntrl == "none":
            self.daq = DummyField(self.p.address_daq)
            log.warning("Used dummy DAQ")
        else:
            self.daq = DAQ(self.p.address_daq)

        if self.p.set_gaussmeter == "none":
            self.gaussmeter = DummyGaussmeter(self.p.address_gaussmeter)
            log.warning("Used dummy Gaussmeter")
        elif self.p.set_gaussmeter == "GM700":
            self.gaussmeter = GM700(self.p.address_gaussmeter)
        elif self.p.set_gaussmeter == "Lakeshore":
            self.gaussmeter = Lakeshore(self.p.address_gaussmeter)
        else:
            raise ValueError("Gaussmeter not supported")

        self.daq.field_constant = self.p.field_constant

    def operating(self, point):

        self.daq.set_voltage(point)
        sleep(self.p.delay_field)
        result = self.gaussmeter.measure()

        if type(result) != int and type(result) != float:
            result = 0

        self.field_vector.append(result)

        data = {
            "Voltage (V)": point,
            "Current (A)": nan,
            "Resistance (ohm)": nan,
            "Field (Oe)": result,
            "Frequency (Hz)": nan,
            "X (V)": nan,
            "Y (V)": nan,
            "Phase": nan,
            "Polar angle (deg)": nan,
            "Azimuthal angle (deg)": nan,
        }
        return data

    def end(self):
        slope, intercept, r, p, std_err = linregress(self.point_list, self.field_vector)
        log.info("Previous field constant: {} [V/Oe]".format(self.p.field_constant))
        try:
            self.p.field_constant = 1 / slope # type: ignore
        except ZeroDivisionError:
            log.error("Voltage to field conversion factor is zero.")
        log.info(f"Field constant: {self.p.field_constant} [V/Oe]")

        FieldCalibrationMode.idle(self)

    def idle(self):
        sweep_field_to_zero(self.point_list[-1] / self.p.field_constant, self.p.field_constant, self.p.field_step, self.daq)
