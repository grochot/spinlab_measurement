from time import sleep
import numpy as np
import logging

from modules.measurement_mode import MeasurementMode

from hardware.rotation_stage import RotationStage
from hardware.rotation_stage_dummy import RotationStageDummy
from logic.sweep_field_to_zero import sweep_field_to_zero
from logic.sweep_field_to_value import sweep_field_to_value
from hardware.esp300 import Esp300
from hardware.dummy_motion_driver import DummyMotionDriver

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ResistanceMode(MeasurementMode):

    def initializing(self):
        # Hardware objects initialization
        self.sourcemeter_obj = self.hardware_manager.create_sourcemeter()
        self.multimeter_obj = self.hardware_manager.create_multimeter()
        self.gaussmeter_obj = self.hardware_manager.create_gaussmeter()
        self.field_obj = self.hardware_manager.create_field_cntrl()

        # Rotation_station object initialization
        if self.p.set_rotationstation:
            try:
                self.rotationstation_obj = RotationStage(self.p.address_rotationstation)
                match self.p.rotation_axis:
                    case "Polar":
                        self.rotationstation_obj.goToAzimuth(self.p.rotation_azimuth_constant)
                    case "Azimuthal":
                        self.rotationstation_obj.goToPolar(self.p.rotation_polar_constant)
            except:
                log.error("Rotation station is not initialized")
                self.rotationstation_obj = RotationStageDummy(self.p.address_rotationstation)

        if self.p.rotation_axis == "None":
            try:
                self.rotationstation_obj = RotationStage(self.p.address_rotationstation)
                self.rotationstation_obj.goToAzimuth(self.p.set_azimuthal_angle)
                self.rotationstation_obj.goToPolar(self.p.set_polar_angle)
            except:
                log.error("Rotation station is not initialized")
                self.rotationstation_obj = RotationStageDummy(self.p.address_rotationstation)

        # Sourcemeter initialization
        self.sourcemeter_obj.source_mode = self.p.sourcemeter_source  # Set source type
        if self.p.sourcemeter_source == "VOLT":
            self.sourcemeter_obj.current_range = self.p.sourcemeter_limit
            self.sourcemeter_obj.compliance_current = self.p.sourcemeter_compliance
            self.sourcemeter_obj.source_voltage = self.p.sourcemeter_bias
            self.sourcemeter_obj.enable_source()
            self.sourcemeter_obj.measure_current(self.p.sourcemeter_nplc, self.p.sourcemeter_limit)
        else:
            self.sourcemeter_obj.voltage_range = self.p.sourcemeter_limit
            self.sourcemeter_obj.compliance_voltage = self.p.sourcemeter_compliance
            self.sourcemeter_obj.source_current = self.p.sourcemeter_bias
            self.sourcemeter_obj.enable_source()
            self.sourcemeter_obj.measure_voltage(self.p.sourcemeter_nplc, self.p.sourcemeter_limit)

        # Multimeter initialization
        self.hardware_manager.initialize_multimeter(self.multimeter_obj)

        # Lakeshore initalization
        self.gaussmeter_obj.range(self.p.gaussmeter_range)
        self.gaussmeter_obj.resolution(self.p.gaussmeter_resolution)

        # Field initialization
        self.field_obj.field_constant = self.p.field_constant
        if self.p.set_rotationstation:
            sweep_field_to_value(0, self.p.constant_field_value, self.p.field_step, self.field_obj)
            self.tmp_field = self.p.constant_field_value
        else:
            sweep_field_to_value(0, self.point_list[0], self.p.field_step, self.field_obj)
            self.tmp_field = self.point_list[0]

        # MotionDriver
        if self.p.set_automaticstation:
            if self.p.address_automaticstation == "None":
                self.MotionDriver = DummyMotionDriver("sth")
            else:
                self.MotionDriver = Esp300(self.p.address_automaticstation)
                self.MotionDriver.high_level_motion_driver(self.p.global_xyname, self.p.sample_in_plane, self.p.disconnect_length)

    def operating(self, point):
        if self.p.set_rotationstation:
            match self.p.rotation_axis:
                case "Polar":
                    self.rotationstation_obj.goToPolar(point)
                    self.polar_angle = point
                    self.azimuthal_angle = self.p.rotation_azimuth_constant

                case "Azimuthal":
                    self.rotationstation_obj.goToAzimuth(point)
                    self.polar_angle = self.p.rotation_polar_constant
                    self.azimuthal_angle = point

        else:
            pass
        self.field_obj.set_field(point)
        sleep(self.p.delay_field)

        # measure field
        if self.p.set_gaussmeter == "none":
            self.tmp_field = point
        else:
            self.tmp_field = self.gaussmeter_obj.measure()
        sleep(self.p.delay_bias)

        # Measure voltage/current/resistance
        if self.p.mode_resistance:
            if self.p.sourcemeter_source == "VOLT":
                self.tmp_voltage = self.p.sourcemeter_bias
                self.tmp_current = np.average(self.multimeter_obj.reading)
                self.tmp_resistance = self.tmp_voltage / self.tmp_current
            else:
                self.tmp_voltage = np.average(self.multimeter_obj.reading)
                self.tmp_current = self.p.sourcemeter_bias
                self.tmp_resistance = self.tmp_voltage / self.tmp_current
        else:
            if self.p.sourcemeter_source == "VOLT":
                if self.p.sourcemeter_bias != 0:
                    self.tmp_voltage = self.p.sourcemeter_bias
                else:
                    self.tmp_voltage = 1e-9
                self.tmp_current = self.sourcemeter_obj.current
                if type(self.tmp_current) == list:
                    self.tmp_current = np.average(self.tmp_current)
                print(self.tmp_current)
                self.tmp_resistance = self.tmp_voltage / self.tmp_current
            else:
                self.tmp_voltage = self.sourcemeter_obj.voltage
                if type(self.tmp_voltage) == list:
                    self.tmp_voltage = np.average(self.tmp_voltage)
                print(self.tmp_voltage)
                if self.p.sourcemeter_bias != 0:
                    self.tmp_current = self.p.sourcemeter_bias
                else:
                    self.tmp_current = 1e-9
                self.tmp_resistance = self.tmp_voltage / self.tmp_current

        data = {
            "Voltage (V)": self.tmp_voltage,
            "Current (A)": self.tmp_current,
            "Resistance (ohm)": self.tmp_resistance,
            "Field (Oe)": self.tmp_field,
            "Polar angle (deg)": self.polar_angle if self.p.set_rotationstation == True else np.nan,
            "Azimuthal angle (deg)": self.azimuthal_angle if self.p.set_rotationstation == True else np.nan,
        }

        return data

    def end(self):
        ResistanceMode.idle(self)

    def idle(self):
        self.sourcemeter_obj.shutdown()
        sweep_field_to_zero(self.tmp_field, self.p.field_constant, self.p.field_step, self.field_obj)
        if (self.p.set_rotationstation or self.p.rotation_axis == "None") and self.p.return_the_rotationstation:
            self.rotationstation_obj.goToZero()

        if not self.p.has_next_callback() and self.p.set_automaticstation and self.p.go_init_position:
            self.MotionDriver.disconnect(self.p.sample_in_plane,self.p.disconnect_length)
            self.MotionDriver.init_position(self.p.sample_in_plane)
