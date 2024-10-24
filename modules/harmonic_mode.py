from time import sleep
import numpy as np
import logging

from modules.measurement_mode import MeasurementMode

from hardware.rotation_stage import RotationStage
from hardware.rotation_stage_dummy import RotationStageDummy
from logic.lockin_parameters import _lockin_timeconstant, _lockin_sensitivity, _lockin_filter_slope
from logic.sweep_field_to_zero import sweep_field_to_zero
from logic.sweep_field_to_value import sweep_field_to_value

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class HarmonicMode(MeasurementMode):

    def initializing(self):

        # Hardware objects initialization
        self.lockin_obj = self.hardware_manager.create_lockin()
        self.gaussmeter_obj = self.hardware_manager.create_gaussmeter()
        self.field_obj = self.hardware_manager.create_field_cntrl()

        # Lockin initialization
        self.hardware_manager.initialize_lockin(self.lockin_obj)

        # Lakeshore initalization
        self.gaussmeter_obj.range(self.p.gaussmeter_range)
        self.gaussmeter_obj.resolution(self.p.gaussmeter_resolution)

        ### Set rotation station to constant angle
        if self.p.set_rotationstation:
            try:
                self.rotationstation_obj = RotationStage(self.p.address_rotationstation)
                match self.p.rotation_axis:
                    case "Polar":
                        self.rotationstation_obj.goToAzimuth(self.p.rotation_azimuth_constant)
                        while self.rotationstation_obj.checkBusyAzimuth() == "BUSY;":
                            sleep(0.01)
                    case "Azimuthal":
                        self.rotationstation_obj.goToPolar(self.p.rotation_polar_constant)
                        while self.rotationstation_obj.checkBusyPolar() == "BUSY;":
                            sleep(0.01)
                    case "None":
                        self.rotationstation_obj.goToAzimuth(self.p.set_azimuthal_angle)
                        while self.rotationstation_obj.checkBusyAzimuth() == "BUSY;":
                            sleep(0.01)
                        self.rotationstation_obj.goToPolar(self.p.set_polar_angle)
                        while self.rotationstation_obj.checkBusyPolar() == "BUSY;":
                            sleep(0.01)

            except:
                log.warning("Rotation station is not initialized")
                self.rotationstation_obj = RotationStageDummy(self.p.address_rotationstation)

        # Field initialization
        self.field_obj.field_constant = self.p.field_constant
        if self.p.set_rotationstation:
            sweep_field_to_value(0.0, float(self.p.constant_field_value), self.p.field_step, self.field_obj)
            self.tmp_field = self.p.constant_field_value
        else:
            sweep_field_to_value(0.0, self.point_list[0], self.p.field_step, self.field_obj)
            self.tmp_field = self.point_list[0]

    def operating(self, point):
        # set temporary result list
        self.result_list = []
        if self.p.set_rotationstation:
            match self.p.rotation_axis:
                case "Polar":
                    self.rotationstation_obj.goToPolar(point)
                    self.polar_angle = point
                    self.azimuthal_angle = self.p.rotation_azimuth_constant
                    while self.rotationstation_obj.checkBusyPolar() == "BUSY;":
                        sleep(0.01)
                case "Azimuthal":
                    self.rotationstation_obj.goToAzimuth(point)
                    self.polar_angle = self.p.rotation_polar_constant
                    self.azimuthal_angle = point
                    while self.rotationstation_obj.checkBusyAzimuth() == "BUSY;":
                        sleep(0.01)
                case "None":
                    self.field_obj.set_field(point)
                    self.polar_angle = self.p.set_polar_angle
                    self.azimuthal_angle = self.p.set_azimuthal_angle
                    sleep(self.p.delay_field)

        else:
            # set_field
            self.field_obj.set_field(point)
            sleep(self.p.delay_field)

        # measure_field
        if self.p.set_gaussmeter == "none":
            if self.p.set_rotationstation:
                self.tmp_field = self.p.constant_field_value
            else:
                self.tmp_field = point
        else:
            self.tmp_field = self.gaussmeter_obj.measure()
        sleep(self.p.delay_bias)

        # measure_lockin
        for i in range(self.p.lockin_average):
            self.result = self.lockin_obj.snap("{}".format(self.p.lockin_channel1), "{}".format(self.p.lockin_channel2))
            self.result_list.append(self.result)

        # calculate average:
        self.result1 = np.average([i[0] for i in self.result_list])
        self.result2 = np.average([i[1] for i in self.result_list])

        data = {
            "Resistance (ohm)": self.result1 if self.p.lockin_channel1 == "R" else (self.result2 if self.p.lockin_channel2 == "R" else np.nan),
            "Field (Oe)": self.tmp_field,
            "X (V)": self.result1 if self.p.lockin_channel1 == "X" else (self.result2 if self.p.lockin_channel2 == "X" else np.nan),
            "Y (V)": self.result1 if self.p.lockin_channel1 == "Y" else (self.result2 if self.p.lockin_channel2 == "Y" else np.nan),
            "Phase": self.result1 if self.p.lockin_channel1 == "Theta" else (self.result2 if self.p.lockin_channel2 == "Theta" else np.nan),
            "Polar angle (deg)": self.polar_angle if self.p.set_rotationstation == True else np.nan,
            "Azimuthal angle (deg)": self.azimuthal_angle if self.p.set_rotationstation == True else np.nan,
        }

        return data

    def end(self):
        HarmonicMode.idle(self)

    def idle(self):

        if self.p.hold_the_field_after_measurement == False:
            sweep_field_to_zero(self.tmp_field, self.p.field_constant, self.p.field_step, self.field_obj)

        if self.p.return_the_rotationstation and self.p.set_rotationstation == True:
            self.rotationstation_obj.goToZero()
