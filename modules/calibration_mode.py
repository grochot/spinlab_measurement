from time import sleep
import logging

from modules.measurement_mode import MeasurementMode

from logic.sweep_field_to_zero import sweep_field_to_zero
from scipy.stats import linregress

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class FieldCalibrationMode(MeasurementMode):

    def initializing(self):    
        self.daq = self.hardware_manager.create_field_cntrl()
        self.gaussmeter = self.hardware_manager.create_gaussmeter()
        self.daq.field_constant = self.p.field_constant
        self.field_vector = []

    def operating(self, point):

        self.daq.set_voltage(point)
        sleep(self.p.delay_field)
        result = self.gaussmeter.measure()

        if type(result) != int and type(result) != float:
            result = 0

        self.field_vector.append(result)

        data = {
            "Voltage (V)": point,
            "Field (Oe)": result,
        }
        return data

    def end(self):
        slope, intercept, r, p, std_err = linregress(self.point_list, self.field_vector)
        log.info("Previous field constant: {} [V/Oe]".format(self.p.field_constant))
        try:
            self.p.field_constant = 1 / slope
            self.daq.field_constant = self.p.field_constant
        except ZeroDivisionError:
            log.error("Voltage to field conversion factor is zero.")
        log.info(f"Field constant: {self.p.field_constant} [V/Oe]")

        FieldCalibrationMode.idle(self)

    def idle(self):
        sweep_field_to_zero(self.point_list[-1] / self.p.field_constant, self.p.field_constant, self.p.field_step, self.daq)
