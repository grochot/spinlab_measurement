# biblioteki
from time import sleep
import numpy as np
import logging

from modules.measurement_mode import MeasurementMode

from hardware.keithley2400 import Keithley2400
from hardware.keithley_2636 import Keithley2636
from hardware.agilent_2912 import Agilent2912
from hardware.tektronix_10070a import Tektronix10070a
from hardware.dummy_sourcemeter import DummySourcemeter
from hardware.dummy_pulsegenerator import DummyPulsegenerator
from hardware.rotation_stage import RotationStage
from hardware.rotation_stage_dummy import RotationStageDummy
from logic.sweep_field_to_zero import sweep_field_to_zero
from logic.sweep_field_to_value import sweep_field_to_value
from hardware.esp300 import Esp300
from hardware.dummy_motion_driver import DummyMotionDriver

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class CIMSMode(MeasurementMode):

    def initializing(self):
        # Hardware objects initialization
        match self.p.set_sourcemeter:
            case "Keithley 2400":
                self.sourcemeter_obj = Keithley2400(self.p.address_sourcemeter)
                # self.sourcemeter_obj.reset()
                self.sourcemeter_obj.config_average(self.p.sourcemeter_average)
            case "Keithley 2636":
                if self.p.sourcemeter_channel == "Channel A":
                    self.sourcemeter_obj = Keithley2636(self.p.address_sourcemeter).ChA
                else:
                    self.sourcemeter_obj = Keithley2636(self.p.address_sourcemeter).ChB
                # self.sourcemeter_obj.reset()
            case "Agilent 2912":
                if self.p.sourcemeter_channel == "Channel A":
                    self.sourcemeter_obj = Agilent2912(self.p.address_sourcemeter).ChA
                else:
                    self.sourcemeter_obj = Agilent2912(self.p.address_sourcemeter).ChB
                # self.sourcemeter_obj.reset()
                self.sourcemeter_obj.func_shape = "DC"
            case _:
                self.sourcemeter_obj = DummySourcemeter(self.p.address_sourcemeter)
                log.warning("Used dummy Sourcemeter.")

        match self.p.set_pulsegenerator:
            case "Tektronix 10,070A":
                self.pulsegenerator_obj = Tektronix10070a(self.p.address_pulsegenerator)
                # self.sourcemeter_obj.reset()
                self.pulsegenerator_obj.trigger_source = "GPIB"
            case "Agilent 2912":
                if self.p.pulsegenerator_channel == "Channel A":
                    self.pulsegenerator_obj = Agilent2912(self.p.address_pulsegenerator).ChA
                else:
                    self.pulsegenerator_obj = Agilent2912(self.p.address_pulsegenerator).ChB
                # self.sourcemeter_obj.reset()
                self.pulsegenerator_obj.source_mode = self.p.pulsegenerator_pulsetype
                self.pulsegenerator_obj.func_shape = "PULSE"
                self.pulsegenerator_obj.trigger_source = "BUS"
                self.pulsegenerator_obj.trigger_bypass = "ONCE"
            case "Keithley 2636":
                if self.p.pulsegenerator_channel == "Channel A":
                    self.pulsegenerator_obj = Keithley2636(self.p.address_pulsegenerator).ChA
                else:
                    self.pulsegenerator_obj = Keithley2636(self.p.address_pulsegenerator).ChB
                # self.sourcemeter_obj.reset()
                self.pulsegenerator_obj.single_pulse_prepare()
            case _:
                self.pulsegenerator_obj = DummyPulsegenerator(self.p.address_pulsegenerator)
                log.warning("Used dummy Pulsegemerator.")

        self.gaussmeter_obj = self.hardware_manager.create_gaussmeter()
        self.field_obj = self.hardware_manager.create_field_cntrl()

        # Sourcemeter initialization
        self.sourcemeter_obj.source_mode = self.p.sourcemeter_source  # Set source type
        if self.p.sourcemeter_source == "VOLT":
            self.sourcemeter_obj.current_range = self.p.sourcemeter_limit
            self.sourcemeter_obj.compliance_current = self.p.sourcemeter_compliance
            self.sourcemeter_obj.source_voltage = self.p.sourcemeter_bias
            if self.p.mode_cims_relays:
                self.sourcemeter_obj.disable_source()
            else:
                self.sourcemeter_obj.enable_source()
            self.sourcemeter_obj.measure_current(self.p.sourcemeter_nplc, self.p.sourcemeter_limit)
        else:
            self.sourcemeter_obj.voltage_range = self.p.sourcemeter_limit
            self.sourcemeter_obj.compliance_voltage = self.p.sourcemeter_compliance
            self.sourcemeter_obj.source_current = self.p.sourcemeter_bias
            if self.p.mode_cims_relays:
                self.sourcemeter_obj.disable_source()
            else:
                self.sourcemeter_obj.enable_source()
            self.sourcemeter_obj.measure_voltage(self.p.sourcemeter_nplc, self.p.sourcemeter_limit)

        # Rotation station for const angle initizalization
        if self.p.rotation_axis == "None":
            try:
                self.rotationstation_obj = RotationStage(self.p.address_rotationstation)
                self.rotationstation_obj.goToAzimuth(self.p.set_azimuthal_angle)
                self.rotationstation_obj.goToPolar(self.p.set_polar_angle)
            except:
                log.error("Rotation station is not initialized")
                self.rotationstation_obj = RotationStageDummy(self.p.address_rotationstation)

        # Lakeshore initalization
        self.gaussmeter_obj.range(self.p.gaussmeter_range)
        self.gaussmeter_obj.resolution(self.p.gaussmeter_resolution)

        self.field_obj.field_constant = self.p.field_constant

        # Field remagnetization
        if self.p.remagnetization:
            # first remanency corection for remagnetization
            if self.p.remanency_correction:
                sleep(self.p.remanency_correction_time)

                self.actual_remanency = self.gaussmeter_obj.measure()
                sweep_field_to_value(0, self.p.remagnetization_value - self.actual_remanency, self.p.field_step, self.field_obj)
                sleep(self.p.remagnetization_time)
                print("to zero:")
                sweep_field_to_value(
                    self.p.remagnetization_value - self.actual_remanency,
                    self.p.field_bias_value,
                    self.p.field_step,
                    self.field_obj,
                )
                sleep(self.p.remanency_correction_time)

                self.actual_remanency = self.gaussmeter_obj.measure()
                sweep_field_to_value(
                    self.p.field_bias_value,
                    self.p.field_bias_value + (self.p.field_bias_value - self.actual_remanency),
                    self.p.field_step,
                    self.field_obj,
                )
            else:
                self.actual_remanency = 0
                sweep_field_to_value(0, self.p.remagnetization_value, self.p.field_step, self.field_obj)
                sleep(self.p.remagnetization_time)
                print("to zero:")
                sweep_field_to_value(self.p.remagnetization_value, self.p.field_bias_value, self.p.field_step, self.field_obj)

        else:
            if self.p.remanency_correction:
                sleep(self.p.remanency_correction_time)

                self.actual_remanency = self.gaussmeter_obj.measure()
                print("Remanency:", self.actual_remanency)
                sweep_field_to_value(0, self.p.field_bias_value - self.actual_remanency, self.p.field_step, self.field_obj)

            else:
                self.actual_remanency = 0
                sweep_field_to_value(0, self.p.field_bias_value, self.p.field_step, self.field_obj)

        # pulsegenerator initialization
        self.pulsegenerator_obj.duration = self.p.pulsegenerator_duration
        self.pulsegenerator_obj.source_range = (self.p.pulsegenerator_pulsetype, self.p.pulsegenerator_source_range)
        self.pulsegenerator_obj.offset = (self.p.pulsegenerator_pulsetype, self.p.pulsegenerator_offset)
        if self.p.pulsegenerator_pulsetype == "VOLT":
            self.pulsegenerator_obj.generator_compliance_current = self.p.pulsegenerator_compliance
        else:
            self.pulsegenerator_obj.generator_compliance_voltage = self.p.pulsegenerator_compliance

        # MotionDriver
        if self.p.set_automaticstation:
            if self.p.address_automaticstation == "None":
                self.MotionDriver = DummyMotionDriver("sth")
            else:
                self.MotionDriver = Esp300(self.p.address_automaticstation)
            self.MotionDriver.high_level_motion_driver(self.p.global_xyname, self.p.sample_in_plane, self.p.disconnect_length)

    def operating(self, point):
        # measure field
        if self.p.set_gaussmeter == "none":
            self.tmp_field = point
        else:
            self.tmp_field = self.gaussmeter_obj.measure()
        sleep(self.p.delay_bias)

        sleep(self.p.delay_measurement)
        # ----Give pulse-----------------------------------------------------
        self.pulsegenerator_obj.amplitude = [(self.p.pulsegenerator_pulsetype, point), point][self.p.set_pulsegenerator == "Tektronix 10,070A"]
        self.pulsegenerator_obj.enable_source()
        self.pulsegenerator_obj.init()
        self.pulsegenerator_obj.trigger()

        # -------------------------------------------------------------------

        # turn off generator output
        if self.p.mode_cims_relays:
            self.pulsegenerator_obj.disable_source()

        sleep(self.p.delay_measurement)
        # turn on sourcemeter inputs
        if self.p.mode_cims_relays:
            self.sourcemeter_obj.enable_source()

        # Measure voltage/current/resistance
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

        # odlaczenie miernika
        if self.p.mode_cims_relays:
            self.sourcemeter_obj.disable_source()

        data = {
            "Voltage (V)": self.tmp_voltage,
            "Current (A)": self.tmp_current,
            "Resistance (ohm)": self.tmp_resistance,
            "Field (Oe)": self.tmp_field,
            "Polar angle (deg)": self.p.set_polar_angle if self.p.set_rotationstation == True else np.nan,
            "Azimuthal angle (deg)": self.p.set_azimuthal_angle if self.p.set_rotationstation == True else np.nan,
            "Applied Voltage (V)": point,
        }

        return data

    def idle(self):
        self.sourcemeter_obj.shutdown()
        self.pulsegenerator_obj.shutdown()

        if self.p.hold_the_field_after_measurement:
            if self.p.field_bias_value - self.actual_remanency > 100:
                log.warning("Too much field to hold on. Setting field to zero")
                sweep_field_to_zero(self.p.field_bias_value - self.actual_remanency, self.p.field_constant, self.p.field_step, self.field_obj)

        else:
            sweep_field_to_zero(self.p.field_bias_value - self.actual_remanency, self.p.field_constant, self.p.field_step, self.field_obj)

        if self.p.rotation_axis == "None" and self.p.return_the_rotationstation:
            self.rotationstation_obj.goToZero()

    def end(self):
        CIMSMode.idle(self)
