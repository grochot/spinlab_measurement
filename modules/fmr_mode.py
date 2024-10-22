from time import sleep
import numpy as np
import logging

from modules.measurement_mode import MeasurementMode

from logic.hardware_creator import DummyMultimeter, DummyLockin, DummyLFGenDriver
from hardware.rotation_stage import RotationStage
from hardware.rotation_stage_dummy import RotationStageDummy

from logic.lockin_parameters import _lockin_timeconstant, _lockin_sensitivity, _lockin_filter_slope
from logic.sweep_field_to_zero import sweep_field_to_zero
from logic.sweep_field_to_value import sweep_field_to_value

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class FMRMode(MeasurementMode):
    def create_measurement_device(self):
        if self.p.set_measdevice_fmr == "LockIn":
            self.lockin_obj = self.hardware_creator.create_lockin()
            self.multimeter_obj = DummyMultimeter(self.p.address_multimeter)
        elif self.p.set_measdevice_fmr == "Multimeter":
            self.multimeter_obj = self.hardware_creator.create_multimeter()
            self.lockin_obj = DummyLockin()
        else:
            raise ValueError(f"Measurement device: '{self.p.set_measdevice_fmr}' not supported")

    def create_lfgen(self):
        self.lfgen_obj = self.hardware_creator.create_lf_generator()
        if self.p.set_lfgen == "SR830" and isinstance(self.lockin_obj, DummyLockin):
            self.lockin_obj = self.lfgen_obj
            self.lfgen_obj = DummyLFGenDriver()

    def initializing(self):
        # Hardware objects initialization
        self.create_measurement_device()
        self.gaussmeter_obj = self.hardware_creator.create_gaussmeter()
        self.field_obj = self.hardware_creator.create_field_cntrl()
        self.generator_obj = self.hardware_creator.create_hf_generator()
        self.create_lfgen()

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
        else:
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

        self.generator_obj.setFreq(initial_freq)
        self.generator_obj.setPower(self.p.generator_power)

        sweep_field_to_value(0, initial_field, self.p.field_step, self.field_obj, emit_info_callback=self.p.emit)
        self.tmp_field = initial_field

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
            "Polar angle (deg)": self.p.rotation_polar_constant if self.p.set_rotationstation == True else np.nan,
            "Azimuthal angle (deg)": self.p.rotation_azimuth_constant if self.p.set_rotationstation == True else np.nan,
        }

        return data

    def end(self):
        FMRMode.idle(self)

    def idle(self):
        if self.p.hold_the_field_after_measurement == False:
            sweep_field_to_zero(self.tmp_field, self.p.field_constant, self.p.field_step, self.field_obj, emit_info_callback=self.p.emit)
        self.generator_obj.setOutput(False)
        if self.p.return_the_rotationstation and self.p.set_rotationstation == True:
            self.rotationstation_obj.goToZero()
