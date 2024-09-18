from time import sleep
import math
import numpy as np
import logging

from app import SpinLabMeasurement
from modules.measurement_mode import MeasurementMode

from hardware.daq import DAQ
from hardware.lakeshore import Lakeshore
from hardware.GM_700 import GM700
from hardware.windfreak import Windfreak
from hardware.sr830 import SR830
from hardware.generator_agilent import FGenDriver
from hardware.hp_33120a import LFGenDriver
from hardware.dummy_fgen import DummyFgenDriver
from hardware.dummy_lfgen import DummyLFGenDriver
from hardware.dummy_lockin import DummyLockin
from hardware.dummy_gaussmeter import DummyGaussmeter
from hardware.dummy_field import DummyField
from hardware.agilent_34410a import Agilent34410A
from hardware.dummy_multimeter import DummyMultimeter
from hardware.rotation_stage import RotationStage
from hardware.rotation_stage_dummy import RotationStageDummy

from logic.vector import Vector
from logic.lockin_parameters import _lockin_timeconstant, _lockin_sensitivity
from logic.sweep_field_to_zero import sweep_field_to_zero
from logic.sweep_field_to_value import sweep_field_to_value

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class FMRMode(MeasurementMode):
    def __init__(
        self,
        procedure: SpinLabMeasurement,
        # set_automaticstation: bool,
        # set_lockin: str,
        # set_field: str,
        # set_gaussmeter: str,
        # set_generator: str,
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
        # address_generator: str,
        # set_field_constant_value: float,
        # set_frequency_constant_value: float,
        # generator_power: float,
        # generator_measurement_mode: str,
        # address_daq: str,
        # set_lfgen: str,
        # address_lfgen: str,
        # lfgen_freq: float,
        # lfgen_amp: float,
        # field_step: float,
        # rotationstation: bool,
        # rotationstation_port: str,
        # constant_field_value: float,
        # rotation_axis: str,
        # rotation_polar_constant: float,
        # rotation_azimuth_constant: float,
        # hold_the_field_after_measurement: bool,
        # return_the_rotationstation: bool,
        # set_multimeter: str,
        # address_multimeter: str,
        # multimeter_function: str,
        # multimeter_resolution: float,
        # multimeter_autorange: bool,
        # multimeter_range: int,
        # multimeter_average: int,
        # multimeter_nplc: str,
        # measdevice: str,
    ) -> None:

        self.p = procedure

        # self.set_automaticstation = set_automaticstation
        # self.set_lockin = set_lockin
        # self.set_field = set_field
        # self.set_gaussmeter = set_gaussmeter
        # self.set_roationstation = set_roationstation
        # self.set_generator = set_generator
        # self.address_lockin = address_lockin
        # self.address_gaussmeter = address_gaussmeter
        # self.address_generator = address_generator
        # self.address_lfgen = address_lfgen
        # self.vector = vector
        # self.set_field_constant_value = set_field_constant_value
        # self.set_frequency_constant_value = set_frequency_constant_value
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

        # self.generator_power = generator_power
        # self.generator_measurement_mode = generator_measurement_mode
        # self.address_daq = address_daq

        # self.set_lfgen = set_lfgen
        # self.lfgen_freq = lfgen_freq
        # self.lfgen_amp = lfgen_amp
        # self.field_step = field_step
        # self.rotationstation = rotationstation
        # self.rotationstation_port = rotationstation_port
        # self.constant_field_value = constant_field_value
        # self.rotation_axis = rotation_axis
        # self.rotation_polar_constant = rotation_polar_constant
        # self.rotation_azimuth_constant = rotation_azimuth_constant
        # self.hold_the_field_after_measurement = hold_the_field_after_measurement
        # self.return_the_rotationstation = return_the_rotationstation

        # self.set_multimeter = set_multimeter
        # self.address_multimeter = address_multimeter
        # self.multimeter_function = multimeter_function
        # self.multimeter_resolution = multimeter_resolution
        # self.multimeter_autorange = multimeter_autorange
        # self.multimeter_range = multimeter_range
        # self.multimeter_average = multimeter_average
        # self.multimeter_nplc = multimeter_nplc

        # self.measdevice = measdevice

        ## parameter initialization

    # def generate_points(self):
    #     # Vector initialization
    #     if self.p.vector != "":
    #         self.vector_obj = Vector()
    #         self.point_list = self.vector_obj.generate_vector(self.p.vector)
    #     else:
    #         log.error("Vector is not defined")
    #         self.point_list = [1]
    #     return self.point_list

    def initializing(self):
        # Hardware objects initialization
        if self.p.set_measdevice_fmr == "LockIn":
            match self.p.set_lockin:
                case "SR830":
                    self.lockin_obj = SR830(self.p.address_lockin)
                case "Zurich":
                    pass
                case _:
                    self.lockin_obj = DummyLockin()
                    log.warning("Used dummy Lockin.")

            self.multimeter_obj = DummyMultimeter(self.p.address_multimeter)
        else:
            match self.p.set_multimeter:
                case "Agilent 34400":
                    self.multimeter_obj = Agilent34410A(self.p.address_multimeter)
                case _:
                    self.multimeter_obj = DummyMultimeter(self.p.address_multimeter)
                    log.warning("Used dummy Multimeter.")

            self.lockin_obj = DummyLockin()
            self.p.set_lfgen = "none"

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

        match self.p.set_generator:
            case "Agilent":
                self.generator_obj = FGenDriver(self.p.address_generator)
            case "Windfreak":
                self.generator_obj = Windfreak(self.p.address_generator)
            case _:
                self.generator_obj = DummyFgenDriver()
                log.warning("Used dummy Frequency Generator.")

        match self.p.set_lfgen:
            case "SR830":
                if type(self.lockin_obj) is DummyLockin:
                    self.lockin_obj = SR830(self.p.address_lockin)
            case "HP33120A":
                self.lfgen_obj = LFGenDriver(self.p.address_lfgen)
            case _:
                self.lfgen_obj = DummyLFGenDriver()
                log.warning("Used dummy Modulation Generator.")

        self.generator_obj.initialization()
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

        # Multimeter initialization
        if not self.p.multimeter_autorange:
            self.multimeter_obj.resolution = self.p.multimeter_resolution
        self.multimeter_obj.range_ = self.p.multimeter_range
        self.multimeter_obj.autorange = self.p.multimeter_autorange
        self.multimeter_obj.function_ = self.p.multimeter_function
        self.multimeter_obj.trigger_delay = "MIN"
        self.multimeter_obj.trigger_count = self.p.multimeter_average
        self.multimeter_obj.nplc = self.p.multimeter_nplc

        # Modulation initalization
        if self.p.set_lfgen == "SR830":
            self.lockin_obj.reference_source = "Internal"
        else:
            self.lfgen_obj.set_shape("SIN")
            self.lfgen_obj.set_freq(self.p.lfgen_freq)
            self.lfgen_obj.set_amp(self.p.lfgen_amp)

        # Lakeshore initalization
        self.gaussmeter_obj.range(self.p.gaussmeter_range)
        self.gaussmeter_obj.resolution(self.p.gaussmeter_resolution)

        # RotationStation initialization
        if self.p.set_rotationstation:
            try:
                self.rotationstation_obj = RotationStage(self.p.address_rotationstation)

                self.rotationstation_obj.goToAzimuth(self.p.rotation_azimuth_constant)
                while self.rotationstation_obj.checkBusyAzimuth() == "BUSY;":
                    sleep(0.01)

                self.rotationstation_obj.goToPolar(self.p.rotation_polar_constant)
                while self.rotationstation_obj.checkBusyPolar() == "BUSY;":
                    sleep(0.01)
            except:
                log.error("Rotation station is not initialized")
                self.rotationstation_obj = RotationStageDummy(self.p.address_rotationstation)

        self.begin()

    def begin(self):
        match self.p.mode_fmr:
            case "V-FMR":
                # Generator initialization
                self.generator_obj.setFreq(self.p.generator_frequency)
                self.generator_obj.setPower(self.p.generator_power)
                # Field initialization
                if self.p.set_rotationstation:
                    sweep_field_to_value(0, self.p.constant_field_value, self.p.field_constant, self.p.field_step, self.field_obj)
                else:
                    sweep_field_to_value(0, self.point_list[0], self.p.field_constant, self.p.field_step, self.field_obj)
            case "ST-FMR":
                # Generator initialization
                self.generator_obj.setFreq(self.point_list[0])
                self.generator_obj.setPower(self.p.generator_power)
                # Field initialization
                if self.p.set_rotationstation:
                    sweep_field_to_value(0, self.p.constant_field_value, self.p.field_constant, self.p.field_step, self.field_obj)
                else:
                    sweep_field_to_value(0, self.p.constant_field_value, self.p.field_constant, self.p.field_step, self.field_obj)

        self.generator_obj.set_lf_signal()
        self.generator_obj.setOutput(True, True if (self.p.set_lfgen == "none" and self.p.set_measdevice_fmr == "LockIn") else False)

        # set lockin phase:
        if self.p.set_lfgen == "SR830":
            self.lockin_obj.phase = 0
        else:
            self.lockin_obj.phase = 180

        sleep(1)

    def operating(self, point):
        sleep(self.p.delay_field)
        # set temporary result list
        self.result_list = []

        match self.p.mode_fmr:
            case "V-FMR":
                if self.p.set_rotationstation:
                    match self.p.rotation_axis:
                        case "Polar":
                            self.rotationstation_obj.goToPolar(point)
                            self.polar_angle = point
                            self.azimuthal_angle = np.nan
                            while self.rotationstation_obj.checkBusyPolar() == "BUSY;":
                                sleep(0.01)
                        case "Azimuthal":
                            self.rotationstation_obj.goToAzimuth(point)
                            self.polar_angle = np.nan
                            self.azimuthal_angle = point
                            while self.rotationstation_obj.checkBusyAzimuth() == "BUSY;":
                                sleep(0.01)

                else:
                    self.actual_set_field = self.field_obj.set_field(point * self.p.field_constant)
                    sleep(self.p.delay_field)

                # measure field

                if self.p.set_gaussmeter == "none":
                    self.tmp_field = point
                else:
                    self.tmp_field = self.gaussmeter_obj.measure()

            case "ST-FMR":
                if self.p.set_rotationstation:
                    match self.p.rotation_axis:
                        case "Polar":
                            self.rotationstation_obj.goToPolar(point)
                            self.polar_angle = point
                            self.azimuthal_angle = np.nan
                            while self.rotationstation_obj.checkBusyPolar() == "BUSY;":
                                sleep(0.01)
                        case "Azimuthal":
                            self.rotationstation_obj.goToAzimuth(point)
                            self.polar_angle = np.nan
                            self.azimuthal_angle = point
                            while self.rotationstation_obj.checkBusyAzimuth() == "BUSY;":
                                sleep(0.01)

                else:
                    self.generator_obj.setFreq(point)
                    sleep(self.p.delay_field)

                # measure field
                if self.p.set_gaussmeter == "none":
                    self.tmp_field = point
                else:
                    self.tmp_field = self.gaussmeter_obj.measure()

        sleep(self.p.delay_lockin)

        self.result1 = math.nan
        self.result2 = math.nan

        if self.p.set_measdevice_fmr == "LockIn":
            # measure_lockin
            # measure_lockin
            # measure_lockin
            for i in range(self.p.lockin_average):
                result = self.lockin_obj.snap("{}".format(self.p.lockin_channel1), "{}".format(self.p.lockin_channel2))
                self.result_list.append(result)

            # calculate average:
            self.result1 = np.average([i[0] for i in self.result_list])
            self.result2 = np.average([i[1] for i in self.result_list])
        else:
            # measure_multimeter
            result = np.average(self.multimeter_obj.reading)

        data = {
            "Voltage (V)": result if self.p.set_measdevice_fmr == "Multimeter" else math.nan,
            "Current (A)": math.nan,
            "Resistance (ohm)": self.result1 if self.p.lockin_channel1 == "R" else (self.result2 if self.p.lockin_channel2 == "R" else math.nan),
            "Field (Oe)": self.tmp_field,
            "Frequency (Hz)": self.p.generator_frequency if self.p.mode_fmr == "V-FMR" else point,
            "X (V)": self.result1 if self.p.lockin_channel1 == "X" else (self.result2 if self.p.lockin_channel2 == "X" else math.nan),
            "Y (V)": self.result1 if self.p.lockin_channel1 == "Y" else (self.result2 if self.p.lockin_channel2 == "Y" else math.nan),
            "Phase": self.result1 if self.p.lockin_channel1 == "Theta" else (self.result2 if self.p.lockin_channel2 == "Theta" else math.nan),
            "Polar angle (deg)": self.polar_angle if self.p.set_rotationstation == True else math.nan,
            "Azimuthal angle (deg)": self.azimuthal_angle if self.p.set_rotationstation == True else math.nan,
        }

        return data

    def end(self):
        FMRMode.idle(self)

    def idle(self):
        if self.p.hold_the_field_after_measurement == False:
            sweep_field_to_zero(self.tmp_field, self.p.field_constant, self.p.field_step, self.field_obj)
        self.generator_obj.setOutput(False)
        if self.p.return_the_rotationstation and self.p.set_rotationstation == True:
            self.rotationstation_obj.goToZero()
