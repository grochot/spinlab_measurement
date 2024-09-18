from time import sleep
import math
import numpy as np
import logging

from modules.measurement_mode import MeasurementMode
from app import SpinLabMeasurement

from hardware.keithley2400 import Keithley2400
from hardware.agilent_34410a import Agilent34410A
from hardware.daq import DAQ
from hardware.keisight_e3600a import E3600a
from hardware.keithley_2636 import Keithley2636
from hardware.lakeshore import Lakeshore
from hardware.GM_700 import GM700
from hardware.autostation import AutoStation
from hardware.kriostat import Kriostat
from hardware.switch import Switch
from hardware.agilent_2912 import Agilent2912
from hardware.dummy_sourcemeter import DummySourcemeter
from hardware.dummy_multimeter import DummyMultimeter
from hardware.dummy_gaussmeter import DummyGaussmeter
from hardware.dummy_field import DummyField
from hardware.rotation_stage import RotationStage
from hardware.rotation_stage_dummy import RotationStageDummy
from logic.vector import Vector
from logic.sweep_field_to_zero import sweep_field_to_zero
from logic.sweep_field_to_value import sweep_field_to_value

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ResistanceMode(MeasurementMode):
    def __init__(
        self,
        procedure: SpinLabMeasurement,
        # vector: str,
        # fourpoints: bool,
        # sourcemeter_bias: float,
        # sourcemeter: str,
        # multimeter: str,
        # gaussmeter: str,
        # field: str,
        # automaticstation: bool,
        # switch: bool,
        # kriostat: bool,
        # rotationstation: bool,
        # return_the_rotationstation: bool,
        # address_sourcemeter: str,
        # address_multimeter: str,
        # address_gaussmeter: str,
        # address_switch: str,
        # delay_field: float,
        # delay_lockin: float,
        # delay_bias: float,
        # sourcemeter_source: str,
        # sourcemeter_compliance: float,
        # sourcemter_channel: str,
        # sourcemeter_limit: str,
        # sourcemeter_nplc: float,
        # sourcemeter_average: str,
        # multimeter_function: str,
        # multimeter_resolution: float,
        # multimeter_autorange: bool,
        # multimeter_range: int,
        # multimeter_average: int,
        # field_constant: float,
        # gaussmeter_range: str,
        # gaussmeter_resolution: str,
        # multimeter_nplc: str,
        # address_daq: str,
        # field_step: float,
        # rotationstation_port: str,
        # constant_field_value: float,
        # rotation_axis: str,
        # rotation_polar_constant: float,
        # rotation_azimuth_constant: float,
        # set_polar_angle,
        # set_azimuthal_angle,
    ) -> None:
        
        self.p = procedure
        
        ## parameter initialization
        # self.sourcemeter = sourcemeter
        # self.multimeter = multimeter
        # self.gaussmeter = gaussmeter
        # self.field = field
        # self.automaticstation = automaticstation
        # self.swich = switch
        # self.kriostat = kriostat
        # self.rotationstation = rotationstation
        # self.return_the_rotationstation = return_the_rotationstation
        # self.address_sourcemeter = address_sourcemeter
        # self.address_multimeter = address_multimeter
        # self.address_gaussmeter = address_gaussmeter
        # self.address_switch = address_switch
        # self.delay_field = delay_field
        # self.delay_lockin = delay_lockin
        # self.delay_bias = delay_bias
        # self.sourcemeter_source = sourcemeter_source
        # self.sourcemeter_compliance = sourcemeter_compliance
        # self.sourcemeter_channel = sourcemter_channel
        # self.sourcemeter_limit = sourcemeter_limit
        # self.sourcemeter_nplc = sourcemeter_nplc
        # self.sourcemeter_bias = sourcemeter_bias
        # self.sourcemeter_average = sourcemeter_average
        # self.multimeter_function = multimeter_function
        # self.multimeter_resolution = multimeter_resolution
        # self.multimeter_autorange = multimeter_autorange
        # self.multimeter_range = multimeter_range
        # self.multimeter_average = multimeter_average
        # self.multimeter_nplc = multimeter_nplc
        # self.field_constant = field_constant
        # self.gaussmeter_range = gaussmeter_range
        # self.gaussmeter_resolution = gaussmeter_resolution
        # self.vector = vector
        # self.fourpoints = fourpoints
        # self.address_daq = address_daq
        # self.field_step = field_step
        # self.rotationstation_port = rotationstation_port
        # self.constant_field_value = constant_field_value
        # self.rotation_axis = rotation_axis
        # self.rotation_polar_constant = rotation_polar_constant
        # self.rotation_azimuth_constant = rotation_azimuth_constant

        # self.set_polar_angle = set_polar_angle
        # self.set_azimuthal_angle = set_azimuthal_angle

    # def generate_points(self):
    #     # Vector initialization
    #     if self.vector != "":
    #         self.vector_obj = Vector()
    #         self.point_list = self.vector_obj.generate_vector(self.vector)
    #     else:
    #         log.error("Vector is not defined")
    #         self.point_list = [1]
    #     return self.point_list

    def initializing(self):
        # Hardware objects initialization
        match self.p.set_sourcemeter:
            case "Keithley 2400":
                self.sourcemeter_obj = Keithley2400(self.p.address_sourcemeter)
                self.sourcemeter_obj.config_average(self.p.sourcemeter_average)
            case "Keithley 2636":
                if self.p.sourcemeter_channel == "Channel A":
                    self.sourcemeter_obj = Keithley2636(self.p.address_sourcemeter).ChA
                else:
                    self.sourcemeter_obj = Keithley2636(self.p.address_sourcemeter).ChB

            case "Agilent 2912":
                if self.p.sourcemeter_channel == "Channel A":
                    self.sourcemeter_obj = Agilent2912(self.p.address_sourcemeter).ChA
                else:
                    self.sourcemeter_obj = Agilent2912(self.p.address_sourcemeter).ChB
            case _:
                self.sourcemeter_obj = DummySourcemeter(self.p.address_sourcemeter)
                log.warning("Used dummy Sourcemeter.")

        match self.p.set_multimeter:
            case "Agilent 34400":
                self.multimeter_obj = Agilent34410A(self.p.address_multimeter)
            case _:
                self.multimeter_obj = DummyMultimeter(self.p.address_multimeter)
                log.warning("Used dummy Multimeter.")

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
        self.multimeter_obj.resolution = self.p.multimeter_resolution
        self.multimeter_obj.range_ = self.p.multimeter_range
        self.multimeter_obj.autorange = self.p.multimeter_autorange
        self.multimeter_obj.function_ = self.p.multimeter_function
        self.multimeter_obj.trigger_delay = "MIN"
        self.multimeter_obj.trigger_count = self.p.multimeter_average
        self.multimeter_obj.nplc = self.p.multimeter_nplc

        # Lakeshore initalization
        self.gaussmeter_obj.range(self.p.gaussmeter_range)
        self.gaussmeter_obj.resolution(self.p.gaussmeter_resolution)

        # Field initialization
        if self.p.set_rotationstation:
            sweep_field_to_value(0, self.p.constant_field_value, self.p.field_constant, self.p.field_step, self.field_obj)
        else:
            sweep_field_to_value(0, self.point_list[0], self.p.field_constant, self.p.field_step, self.field_obj)

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
        self.actual_set_field = self.field_obj.set_field(point * self.p.field_constant)
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
            "Frequency (Hz)": math.nan,
            "X (V)": math.nan,
            "Y (V)": math.nan,
            "Phase": math.nan,
            "Polar angle (deg)": self.polar_angle if self.p.set_rotationstation == True else math.nan,
            "Azimuthal angle (deg)": self.azimuthal_angle if self.p.set_rotationstation == True else math.nan,
        }

        return data

    def end(self):
        ResistanceMode.idle(self)

    def idle(self):
        self.sourcemeter_obj.shutdown()
        sweep_field_to_zero(self.tmp_field, self.p.field_constant, self.p.field_step, self.field_obj)
        if (self.p.set_rotationstation or self.p.rotation_axis == "None") and self.p.return_the_rotationstation:
            self.rotationstation_obj.goToZero()
