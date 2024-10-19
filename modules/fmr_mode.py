from time import sleep
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

from logic.lockin_parameters import _lockin_timeconstant, _lockin_sensitivity, _lockin_filter_slope
from logic.sweep_field_to_zero import sweep_field_to_zero
from logic.sweep_field_to_value import sweep_field_to_value

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class FMRMode(MeasurementMode):
    def __init__(self, procedure: SpinLabMeasurement) -> None:
        self.p = procedure

    def initializing(self):
        # Hardware objects initialization

        # Measurement object device initialization
        if self.p.set_measdevice_fmr == "LockIn":
            # Lockin object initialization
            match self.p.set_lockin:
                case "SR830":
                    self.lockin_obj = SR830(self.p.address_lockin)
                case "Zurich":
                    raise NotImplementedError("Zurich lockin is not implemented")
                case _:
                    self.lockin_obj = DummyLockin()
                    log.warning("Used dummy Lockin.")
            self.multimeter_obj = DummyMultimeter(self.p.address_multimeter)

        elif self.p.set_measdevice_fmr == "Multimeter":
            # Multimeter object initialization
            match self.p.set_multimeter:
                case "Agilent 34400":
                    self.multimeter_obj = Agilent34410A(self.p.address_multimeter)
                case _:
                    self.multimeter_obj = DummyMultimeter(self.p.address_multimeter)
                    log.warning("Used dummy Multimeter.")

            self.lockin_obj = DummyLockin()
            self.p.set_lfgen = "none"
        else:
            raise ValueError(f"Measurement device: '{self.p.set_measdevice_fmr}' not supported")

        # Gaussmeter object initialization
        match self.p.set_gaussmeter:
            case "Lakeshore":
                self.gaussmeter_obj = Lakeshore(self.p.address_gaussmeter)
            case "GM700":
                self.gaussmeter_obj = GM700(self.p.address_gaussmeter)
            case _:
                self.gaussmeter_obj = DummyGaussmeter(self.p.address_gaussmeter)
                log.warning("Used dummy Gaussmeter.")

        # Field controller object initialization
        match self.p.set_field_cntrl:
            case "DAQ":
                self.field_obj = DAQ(self.p.address_daq)
            case _:
                self.field_obj = DummyField(self.p.address_daq)
                log.warning("Used dummy DAQ.")

        # High Frequency Generator object initialization
        match self.p.set_generator:
            case "Agilent":
                self.generator_obj = FGenDriver(self.p.address_generator)
            case "Windfreak":
                channel = 0 if self.p.generator_channel == "A" else 1
                self.generator_obj = Windfreak(self.p.address_generator, channel=channel)
            case _:
                self.generator_obj = DummyFgenDriver()
                log.warning("Used dummy Frequency Generator.")

        # Low Frequency Generator object initialization (Helmholtz coil)
        match self.p.set_lfgen:
            case "SR830":
                if type(self.lockin_obj) is DummyLockin:
                    self.lockin_obj = SR830(self.p.address_lockin)
            case "HP33120A":
                self.lfgen_obj = LFGenDriver(self.p.address_lfgen)
            case _:
                self.lfgen_obj = DummyLFGenDriver()
                log.warning("Used dummy Modulation Generator.")

        # High Frequency Generator initialization
        self.generator_obj.initialization()

        # Lockin initialization
        self.lockin_obj.frequency = self.p.lockin_frequency
        if self.p.lockin_sensitivity == "Auto Gain":
            self.lockin_obj.auto_gain()
        else:
            self.lockin_obj.sensitivity = _lockin_sensitivity(self.p.lockin_sensitivity)
        self.lockin_obj.time_constant = _lockin_timeconstant(self.p.lockin_timeconstant)
        self.lockin_obj.filter_slope = _lockin_filter_slope(self.p.lockin_slope)
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

        # Low Frequency Generator initalization
        if self.p.set_lfgen == "SR830":
            self.lockin_obj.reference_source = "Internal"

        self.lfgen_obj.set_shape("SIN")
        self.lfgen_obj.set_freq(self.p.lfgen_freq)
        self.lfgen_obj.set_amp(self.p.lfgen_amp)

        # Field controller initialization
        self.field_obj.field_constant = self.p.field_constant
        self.field_obj.field_step = self.p.field_step
        self.field_obj.polarity_control_enabled = self.p.polarity_control_enabled
        self.field_obj.address_polarity_control = self.p.address_polarity_control

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
        # V_FMR - constant frequency, sweep field (self.point_list - field values in Oe)
        # ST_FMR - constant field, sweep frequency (self.point_list - frequency values in Hz)
        # set initial values
        initial_freq = 0
        initial_field = 0
        match self.p.mode_fmr:
            case "V-FMR":
                initial_freq = self.p.generator_frequency
                initial_field = self.point_list[0]
            case "ST-FMR":
                initial_freq = self.point_list[0]
                initial_field = self.p.constant_field_value

        if self.p.set_rotationstation:
            initial_field = self.p.constant_field_value

        self.generator_obj.setFreq(initial_freq)
        self.generator_obj.setPower(self.p.generator_power)

        sweep_field_to_value(0, initial_field, self.p.field_step, self.field_obj)

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

        match self.p.mode_fmr:
            case "V-FMR":
                self.field_obj.set_field(point)
            case "ST-FMR":
                self.generator_obj.setFreq(point)

        sleep(self.p.delay_field)

        if self.p.set_gaussmeter == "none":
            self.tmp_field = point
        else:
            self.tmp_field = self.gaussmeter_obj.measure()

        sleep(self.p.delay_lockin)

        result = np.nan
        result1 = np.nan
        result2 = np.nan

        if self.p.set_measdevice_fmr == "LockIn":
            result_list = []
            for i in range(self.p.lockin_average):
                result = self.lockin_obj.snap("{}".format(self.p.lockin_channel1), "{}".format(self.p.lockin_channel2))
                result_list.append(result)

            result1 = np.average([i[0] for i in result_list])
            result2 = np.average([i[1] for i in result_list])
        elif self.p.set_measdevice_fmr == "Multimeter":
            result = np.average(self.multimeter_obj.reading)

        data = {
            "Voltage (V)": result if self.p.set_measdevice_fmr == "Multimeter" else np.nan,
            "Current (A)": np.nan,
            "Resistance (ohm)": result1 if self.p.lockin_channel1 == "R" else (result2 if self.p.lockin_channel2 == "R" else np.nan),
            "Field (Oe)": self.tmp_field,
            "Frequency (Hz)": self.p.generator_frequency if self.p.mode_fmr == "V-FMR" else point,
            "X (V)": result1 if self.p.lockin_channel1 == "X" else (result2 if self.p.lockin_channel2 == "X" else np.nan),
            "Y (V)": result1 if self.p.lockin_channel1 == "Y" else (result2 if self.p.lockin_channel2 == "Y" else np.nan),
            "Phase": result1 if self.p.lockin_channel1 == "Theta" else (result2 if self.p.lockin_channel2 == "Theta" else np.nan),
            "Polar angle (deg)": self.polar_angle if self.p.set_rotationstation == True else np.nan,
            "Azimuthal angle (deg)": self.azimuthal_angle if self.p.set_rotationstation == True else np.nan,
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
