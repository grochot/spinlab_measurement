from time import sleep
import math
import numpy as np
import logging

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
from logic.lockin_parameters import _lockin_timeconstant, _lockin_sensitivity, _lockin_filter_slope
from logic.sweep_field_to_zero import sweep_field_to_zero
from logic.sweep_field_to_value import sweep_field_to_value

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class FMRMode:
    def __init__(
        self,
        set_automaticstation: bool,
        set_lockin: str,
        set_field: str,
        set_gaussmeter: str,
        set_generator: str,
        set_roationstation: bool,
        address_lockin: str,
        address_gaussmeter: str,
        vector: list,
        delay_field: float,
        delay_lockin: float,
        delay_bias: float,
        lockin_average,
        lockin_input_coupling,
        lockin_reference_source,
        lockin_dynamic_reserve,
        lockin_input_connection,
        lockin_sensitivity,
        lockin_timeconstant,
        lockin_autophase,
        lockin_frequency,
        lockin_harmonic,
        lockin_sine_amplitude,
        lockin_channel1,
        lockin_channel2,
        field_constant,
        gaussmeter_range,
        gaussmeter_resolution,
        address_generator: str,
        set_field_constant_value: float,
        set_frequency_constant_value: float,
        generator_power: float,
        generator_measurement_mode: str,
        address_daq: str,
        set_lfgen: str,
        address_lfgen: str,
        lfgen_freq: float,
        lfgen_amp: float,
        field_step: float,
        rotationstation: bool,
        rotationstation_port: str,
        constant_field_value: float,
        rotation_axis: str,
        rotation_polar_constant: float,
        rotation_azimuth_constant: float,
        hold_the_field_after_measurement: bool,
        return_the_rotationstation: bool,
        set_multimeter: str,
        address_multimeter: str,
        multimeter_function: str,
        multimeter_resolution: float,
        multimeter_autorange: bool,
        multimeter_range: int,
        multimeter_average: int,
        multimeter_nplc: str,
        measdevice: str,
        generator_channel: str,
        lockin_slope: str,
        polarity_control_enabled: bool,
        address_polarity_control: str,
    ) -> None:

        self.set_automaticstation = set_automaticstation
        self.set_lockin = set_lockin
        self.set_field = set_field
        self.set_gaussmeter = set_gaussmeter
        self.set_roationstation = set_roationstation
        self.set_generator = set_generator
        self.address_lockin = address_lockin
        self.address_gaussmeter = address_gaussmeter
        self.address_generator = address_generator
        self.address_lfgen = address_lfgen
        self.vector = vector
        self.set_field_constant_value = set_field_constant_value
        self.set_frequency_constant_value = set_frequency_constant_value
        self.delay_field = delay_field
        self.delay_lockin = delay_lockin
        self.delay_bias = delay_bias
        self.lockin_average = lockin_average
        self.lockin_input_coupling = lockin_input_coupling
        self.lockin_reference_source = lockin_reference_source
        self.lockin_dynamic_reserve = lockin_dynamic_reserve
        self.lockin_input_connection = lockin_input_connection
        self.lockin_sensitivity = lockin_sensitivity
        self.lockin_timeconstant = lockin_timeconstant
        self.lockin_autophase = lockin_autophase
        self.lockin_frequency = lockin_frequency
        self.lockin_harmonic = lockin_harmonic
        self.lockin_sine_amplitude = lockin_sine_amplitude
        self.lockin_channel1 = lockin_channel1
        self.lockin_channel2 = lockin_channel2

        self.field_constant = field_constant
        self.gaussmeter_range = gaussmeter_range
        self.gaussmeter_resolution = gaussmeter_resolution

        self.generator_power = generator_power
        self.generator_measurement_mode = generator_measurement_mode
        self.address_daq = address_daq

        self.set_lfgen = set_lfgen
        self.lfgen_freq = lfgen_freq
        self.lfgen_amp = lfgen_amp
        self.field_step = field_step
        self.rotationstation = rotationstation
        self.rotationstation_port = rotationstation_port
        self.constant_field_value = constant_field_value
        self.rotation_axis = rotation_axis
        self.rotation_polar_constant = rotation_polar_constant
        self.rotation_azimuth_constant = rotation_azimuth_constant
        self.hold_the_field_after_measurement = hold_the_field_after_measurement
        self.return_the_rotationstation = return_the_rotationstation

        self.set_multimeter = set_multimeter
        self.address_multimeter = address_multimeter
        self.multimeter_function = multimeter_function
        self.multimeter_resolution = multimeter_resolution
        self.multimeter_autorange = multimeter_autorange
        self.multimeter_range = multimeter_range
        self.multimeter_average = multimeter_average
        self.multimeter_nplc = multimeter_nplc

        self.measdevice = measdevice
        self.generator_channel = generator_channel
        
        self.lockin_slope = lockin_slope
        
        self.polarity_control_enabled = polarity_control_enabled
        self.address_polarity_control = address_polarity_control

        ## parameter initialization

    def generate_points(self):
        # Vector initialization
        if self.vector != "":
            self.vector_obj = Vector()
            self.point_list = self.vector_obj.generate_vector(self.vector)
        else:
            log.error("Vector is not defined")
            self.point_list = [1]
        return self.point_list

    def initializing(self):
        # Hardware objects initialization
        if self.measdevice == "LockIn":
            match self.set_lockin:
                case "SR830":
                    self.lockin_obj = SR830(self.address_lockin)
                case "Zurich":
                    pass
                case _:
                    self.lockin_obj = DummyLockin()
                    log.warning("Used dummy Lockin.")

            self.multimeter_obj = DummyMultimeter(self.address_multimeter)
        else:
            match self.set_multimeter:
                case "Agilent 34400":
                    self.multimeter_obj = Agilent34410A(self.address_multimeter)
                case _:
                    self.multimeter_obj = DummyMultimeter(self.address_multimeter)
                    log.warning("Used dummy Multimeter.")

            self.lockin_obj = DummyLockin()
            self.set_lfgen = "none"

        match self.set_gaussmeter:
            case "Lakeshore":
                self.gaussmeter_obj = Lakeshore(self.address_gaussmeter)
            case "GM700":
                self.gaussmeter_obj = GM700(self.address_gaussmeter)
            case _:
                self.gaussmeter_obj = DummyGaussmeter(self.address_gaussmeter)
                log.warning("Used dummy Gaussmeter.")

        match self.set_field:
            case "DAQ":
                self.field_obj = DAQ(self.address_daq)
            case _:
                self.field_obj = DummyField(self.address_daq)
                log.warning("Used dummy DAQ.")

        match self.set_automaticstation:
            case True:
                pass
            case _:
                pass

        match self.set_generator:
            case "Agilent":
                self.generator_obj = FGenDriver(self.address_generator)
            case "Windfreak":
                channel = 0 if self.generator_channel == "A" else 1
                self.generator_obj = Windfreak(self.address_generator, channel=channel)
            case _:
                self.generator_obj = DummyFgenDriver()
                log.warning("Used dummy Frequency Generator.")

        match self.set_lfgen:
            case "SR830":
                if type(self.lockin_obj) is DummyLockin:
                    self.lockin_obj = SR830(self.address_lockin)
            case "HP33120A":
                self.lfgen_obj = LFGenDriver(self.address_lfgen)
            case _:
                self.lfgen_obj = DummyLFGenDriver()
                log.warning("Used dummy Modulation Generator.")

        self.generator_obj.initialization()
        # Lockin initialization
        self.lockin_obj.frequency = self.lockin_frequency
        if self.lockin_sensitivity == "Auto Gain":
            self.lockin_obj.auto_gain()
        else:
            self.lockin_obj.sensitivity = _lockin_sensitivity(self.lockin_sensitivity)
        self.lockin_obj.time_constant = _lockin_timeconstant(self.lockin_timeconstant)
        self.lockin_obj.filter_slope = _lockin_filter_slope(self.lockin_slope)
        self.lockin_obj.harmonic = self.lockin_harmonic
        self.lockin_obj.sine_voltage = self.lockin_sine_amplitude
        self.lockin_obj.channel1 = self.lockin_channel1
        self.lockin_obj.channel2 = self.lockin_channel2
        self.lockin_obj.input_config = self.lockin_input_connection
        self.lockin_obj.input_coupling = self.lockin_input_coupling
        self.lockin_obj.reference_source = self.lockin_reference_source

        # Multimeter initialization
        if not self.multimeter_autorange:
            self.multimeter_obj.resolution = self.multimeter_resolution
        self.multimeter_obj.range_ = self.multimeter_range
        self.multimeter_obj.autorange = self.multimeter_autorange
        self.multimeter_obj.function_ = self.multimeter_function
        self.multimeter_obj.trigger_delay = "MIN"
        self.multimeter_obj.trigger_count = self.multimeter_average
        self.multimeter_obj.nplc = self.multimeter_nplc

        # Modulation initalization
        if self.set_lfgen == "SR830":
            self.lockin_obj.reference_source = "Internal"
        else:
            self.lfgen_obj.set_shape("SIN")
            self.lfgen_obj.set_freq(self.lfgen_freq)
            self.lfgen_obj.set_amp(self.lfgen_amp)
            
        # Field initialization
        self.field_obj.field_constant = self.field_constant
        self.field_step = self.field_step
        self.field_obj.polarity_control_enabled = self.polarity_control_enabled
        self.field_obj.address_polarity_control = self.address_polarity_control

        # Lakeshore initalization
        self.gaussmeter_obj.range(self.gaussmeter_range)
        self.gaussmeter_obj.resolution(self.gaussmeter_resolution)

        # RotationStation initialization
        if self.rotationstation:
            try:
                self.rotationstation_obj = RotationStage(self.rotationstation_port)

                self.rotationstation_obj.goToAzimuth(self.rotation_azimuth_constant)
                while self.rotationstation_obj.checkBusyAzimuth() == "BUSY;":
                    sleep(0.01)

                self.rotationstation_obj.goToPolar(self.rotation_polar_constant)
                while self.rotationstation_obj.checkBusyPolar() == "BUSY;":
                    sleep(0.01)
            except:
                log.error("Rotation station is not initialized")
                self.rotationstation_obj = RotationStageDummy(self.rotationstation_port)

        self.begin()

    def begin(self):
        match self.generator_measurement_mode:
            case "V-FMR":
                # Generator initialization
                self.generator_obj.setFreq(self.set_frequency_constant_value)
                self.generator_obj.setPower(self.generator_power)
                # Field initialization
                if self.rotationstation:
                    sweep_field_to_value(0, self.constant_field_value, self.field_step, self.field_obj)
                else:
                    sweep_field_to_value(0, self.point_list[0], self.field_step, self.field_obj)
            case "ST-FMR":
                # Generator initialization
                self.generator_obj.setFreq(self.point_list[0])
                self.generator_obj.setPower(self.generator_power)
                # Field initialization
                if self.rotationstation:
                    sweep_field_to_value(0, self.constant_field_value, self.field_step, self.field_obj)
                else:
                    sweep_field_to_value(0, self.constant_field_value, self.field_step, self.field_obj)

        self.generator_obj.set_lf_signal()
        self.generator_obj.setOutput(True, True if (self.set_lfgen == "none" and self.measdevice == "LockIn") else False)

        # set lockin phase:
        if self.set_lfgen == "SR830":
            self.lockin_obj.phase = 0
        else:
            self.lockin_obj.phase = 180

        sleep(1)

    def operating(self, point):
        sleep(self.delay_field)
        # set temporary result list
        self.result_list = []

        match self.generator_measurement_mode:
            case "V-FMR":
                if self.rotationstation:
                    match self.rotation_axis:
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
                    self.field_obj.set_field(point)
                    sleep(self.delay_field)

                # measure field
                if self.set_gaussmeter == "none":
                    self.tmp_field = point
                else:
                    self.tmp_field = self.gaussmeter_obj.measure()

            case "ST-FMR":
                if self.rotationstation:
                    match self.rotation_axis:
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
                    sleep(self.delay_field)

                # measure field
                if self.set_gaussmeter == "none":
                    self.tmp_field = point
                else:
                    self.tmp_field = self.gaussmeter_obj.measure()

        sleep(self.delay_lockin)

        self.result1 = math.nan
        self.result2 = math.nan

        if self.measdevice == "LockIn":
            # measure_lockin
            # measure_lockin
            # measure_lockin
            for i in range(self.lockin_average):
                result = self.lockin_obj.snap("{}".format(self.lockin_channel1), "{}".format(self.lockin_channel2))
                self.result_list.append(result)

            # calculate average:
            self.result1 = np.average([i[0] for i in self.result_list])
            self.result2 = np.average([i[1] for i in self.result_list])
        else:
            # measure_multimeter
            result = np.average(self.multimeter_obj.reading)

        data = {
            "Voltage (V)": result if self.measdevice == "Multimeter" else math.nan,
            "Current (A)": math.nan,
            "Resistance (ohm)": self.result1 if self.lockin_channel1 == "R" else (self.result2 if self.lockin_channel2 == "R" else math.nan),
            "Field (Oe)": self.tmp_field,
            "Frequency (Hz)": self.set_frequency_constant_value if self.generator_measurement_mode == "V-FMR" else point,
            "X (V)": self.result1 if self.lockin_channel1 == "X" else (self.result2 if self.lockin_channel2 == "X" else math.nan),
            "Y (V)": self.result1 if self.lockin_channel1 == "Y" else (self.result2 if self.lockin_channel2 == "Y" else math.nan),
            "Phase": self.result1 if self.lockin_channel1 == "Theta" else (self.result2 if self.lockin_channel2 == "Theta" else math.nan),
            "Polar angle (deg)": self.polar_angle if self.rotationstation == True else math.nan,
            "Azimuthal angle (deg)": self.azimuthal_angle if self.rotationstation == True else math.nan,
        }

        return data

    def end(self):
        FMRMode.idle(self)

    def idle(self):
        if self.hold_the_field_after_measurement == False:
            sweep_field_to_zero(self.tmp_field, self.field_constant, self.field_step, self.field_obj)
        self.generator_obj.setOutput(False)
        if self.return_the_rotationstation and self.rotationstation == True:
            self.rotationstation_obj.goToZero()
