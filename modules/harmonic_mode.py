from time import sleep
import math
import numpy as np
import logging
from hardware.daq import DAQ

from app import SpinLabMeasurement
from modules.measurement_mode import MeasurementMode

from hardware.lakeshore import Lakeshore
from hardware.GM_700 import GM700
from hardware.sr830 import SR830
from hardware.dummy_lockin import DummyLockin
from hardware.dummy_gaussmeter import DummyGaussmeter
from hardware.dummy_field import DummyField
from hardware.rotation_stage import RotationStage
from hardware.rotation_stage_dummy import RotationStageDummy
from logic.vector import Vector
from logic.lockin_parameters import _lockin_timeconstant, _lockin_sensitivity
from logic.sweep_field_to_zero import sweep_field_to_zero
from logic.sweep_field_to_value import sweep_field_to_value

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class HarmonicMode(MeasurementMode):
    def __init__(
        self,
        procedure: SpinLabMeasurement,
        # set_automaticstation: bool,
        # set_lockin: str,
        # set_field: str,
        # set_gaussmeter: str,
        # set_roationstation: bool,
        # address_lockin: str,
        # address_gaussmeter: str,
        # vector: list,
        # delay_field: float,
        # delay_lockin: float,
        # delay_bias: float,
        # lockin_average,
        # lockin_input_coupling,
        # lockin_reference_source,
        # lockin_dynamic_reserve,
        # lockin_input_connection,
        # lockin_sensitivity,
        # lockin_timeconstant,
        # lockin_autophase,
        # lockin_frequency,
        # lockin_harmonic,
        # lockin_sine_amplitude,
        # lockin_channel1,
        # lockin_channel2,
        # field_constant,
        # gaussmeter_range,
        # gaussmeter_resolution,
        # address_daq: str,
        # field_step: float,
        # rotationstation: bool,
        # rotationstation_port: str,
        # constant_field_value: float,
        # rotation_axis: str,
        # rotation_polar_constant: float,
        # rotation_azimuth_constant: float,
        # set_polar_angle: float,
        # set_azimuthal_angle: float,
        # hold_the_field_after_measurement: bool,
        # return_the_rotationstation: bool,
    ) -> None:

        self.p = procedure

        # self.set_automaticstation = set_automaticstation
        # self.set_lockin = set_lockin
        # self.set_field = set_field
        # self.set_gaussmeter = set_gaussmeter
        # self.set_roationstation = set_roationstation
        # self.address_lockin = address_lockin
        # self.address_gaussmeter = address_gaussmeter
        # self.vector = vector
        # self.delay_field = delay_field
        # self.delay_lockin = delay_lockin
        # self.delay_bias = delay_bias
        # self.lockin_average = lockin_average
        # self.lockin_input_coupling = lockin_input_coupling
        # self.lockin_reference_source = lockin_reference_source
        # self.lockin_dynamic_reserve = lockin_dynamic_reserve
        # self.lockin_input_connection = lockin_input_connection
        # self.lockin_sensitivity = lockin_sensitivity
        # self.lockin_timeconstant = lockin_timeconstant
        # self.lockin_autophase = lockin_autophase
        # self.lockin_frequency = lockin_frequency
        # self.lockin_harmonic = lockin_harmonic
        # self.lockin_sine_amplitude = lockin_sine_amplitude
        # self.lockin_channel1 = lockin_channel1
        # self.lockin_channel2 = lockin_channel2

        # self.field_constant = field_constant
        # self.gaussmeter_range = gaussmeter_range
        # self.gaussmeter_resolution = gaussmeter_resolution
        # self.address_daq = address_daq
        # self.field_step = field_step
        # self.rotationstation_port = rotationstation_port
        # self.constant_field_value = constant_field_value
        # self.rotation_axis = rotation_axis
        # self.rotation_polar_constant = rotation_polar_constant
        # self.rotation_azimuth_constant = rotation_azimuth_constant
        # self.rotationstation = rotationstation
        # self.set_polar_angle = set_polar_angle
        # self.set_azimuthal_angle = set_azimuthal_angle
        # self.hold_the_field_after_measurement = hold_the_field_after_measurement
        # self.return_the_rotationstation = return_the_rotationstation

    ## INITIALIZATION:

    # def generate_points(self):
    #     # Vector initialization
    #     if self.vector != "":
    #         self.vector_obj = Vector()
    #         self.point_list = self.vector_obj.generate_vector(self.vector)
    #         print(self.point_list)
    #     else:
    #         log.error("Vector is not defined")
    #         self.point_list = [1]
    #     return self.point_list

    def initializing(self):

        # Hardware objects initialization
        match self.p.set_lockin:
            case "SR830":
                try:
                    self.lockin_obj = SR830(self.p.address_lockin)
                except:
                    self.lockin_obj = DummyLockin()
                    log.warning("Used dummy Lockin.")

            case "Zurich":
                pass
            case _:
                self.lockin_obj = DummyLockin()
                log.warning("Used dummy Lockin.")

        match self.p.set_gaussmeter:
            case "Lakeshore":
                self.gaussmeter_obj = Lakeshore(self.p.address_gaussmeter)
            case "GM700":
                self.gaussmeter_obj = GM700(self.p.address_gaussmeter)
            case _:
                self.gaussmeter_obj = DummyGaussmeter(self.p.address_gaussmeter)
                log.warning("Used dummy Gaussmeter.")

        match self.p.set_field:
            case "DAQ":
                self.field_obj = DAQ(self.p.address_daq)
            case _:
                self.field_obj = DummyField(self.p.address_daq)
                log.warning("Used dummy DAQ.")

        match self.p.set_automaticstation:
            case True:
                pass
            case _:
                pass

        # Lockin initialization
        self.lockin_obj.frequency = self.p.lockin_frequency
        if self.p.lockin_sensitivity == "Auto Gain":
            self.lockin_obj.auto_gain()
        else:
            self.lockin_obj.sensitivity = _lockin_sensitivity(self.p.lockin_sensitivity)
        self.lockin_obj.time_constant = _lockin_timeconstant(self.p.lockin_timeconstant)
        self.lockin_obj.harmonic = self.p.lockin_harmonic
        self.lockin_obj.sine_voltage = self.p.lockin_sine_amplitude
        self.lockin_obj.channel1 = self.p.lockin_channel1
        self.lockin_obj.channel2 = self.p.lockin_channel2
        self.lockin_obj.input_config = self.p.lockin_input_connection
        self.lockin_obj.input_coupling = self.p.lockin_input_coupling
        self.lockin_obj.reference_source = self.p.lockin_reference_source

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
        if self.p.set_rotationstation:
            sweep_field_to_value(0.0, float(self.p.constant_field_value), self.p.field_constant, self.p.field_step, self.field_obj)
        else:
            sweep_field_to_value(0.0, self.point_list[0], self.p.field_constant, self.p.field_step, self.field_obj)

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
                    self.field_obj.set_field(point * self.p.field_constant)
                    self.polar_angle = self.p.set_polar_angle
                    self.azimuthal_angle = self.p.set_azimuthal_angle
                    sleep(self.p.delay_field)

        else:
            # set_field
            self.field_obj.set_field(point * self.p.field_constant)
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
            "Voltage (V)": math.nan,
            "Current (A)": math.nan,
            "Resistance (ohm)": self.result1 if self.p.lockin_channel1 == "R" else (self.result2 if self.p.lockin_channel2 == "R" else math.nan),
            "Field (Oe)": self.tmp_field,
            "Frequency (Hz)": math.nan,
            "X (V)": self.result1 if self.p.lockin_channel1 == "X" else (self.result2 if self.p.lockin_channel2 == "X" else math.nan),
            "Y (V)": self.result1 if self.p.lockin_channel1 == "Y" else (self.result2 if self.p.lockin_channel2 == "Y" else math.nan),
            "Phase": self.result1 if self.p.lockin_channel1 == "Theta" else (self.result2 if self.p.lockin_channel2 == "Theta" else math.nan),
            "Polar angle (deg)": self.polar_angle if self.p.set_rotationstation == True else math.nan,
            "Azimuthal angle (deg)": self.azimuthal_angle if self.p.set_rotationstation == True else math.nan,
        }

        return data

    def end(self):
        HarmonicMode.idle(self)

    def idle(self):

        if self.p.hold_the_field_after_measurement == False:
            sweep_field_to_zero(self.tmp_field, self.p.field_constant, self.p.field_step, self.field_obj)

        if self.p.return_the_rotationstation and self.p.set_rotationstation == True:
            self.rotationstation_obj.goToZero()
