from time import sleep
import math
import numpy as np
import logging

from modules.measurement_mode import MeasurementMode, Vector
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
from hardware.esp300 import Esp300
from hardware.dummy_motion_driver import DummyMotionDriver

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class CIMSOneDeviceMode(MeasurementMode):
    def __init__(self, procedure: SpinLabMeasurement) -> None:
        self.p = procedure
        self.is_iterable=True

    def generate_points(self):
        vector_string = self.p.vector
        v = Vector()
        self.ranges = v.generate_ranges(vector_string)
        self.n_measurement=sum(self.ranges[1])
        return range(self.n_measurement)

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

        match self.p.set_gaussmeter:
            case "Lakeshore":
                self.gaussmeter_obj = Lakeshore(self.p.address_gaussmeter)
            case "GM700":
                self.gaussmeter_obj = GM700(self.p.address_gaussmeter)
            case _:
                self.gaussmeter_obj = DummyGaussmeter(self.p.address_gaussmeter)
                log.warning("Used dummy Gaussmeter.")

        match self.p.set_field_cntrl:
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
            #self.sourcemeter_obj.enable_source()
            #self.sourcemeter_obj.measure_current(self.p.sourcemeter_nplc, self.p.sourcemeter_limit)
        else:
            self.sourcemeter_obj.voltage_range = self.p.sourcemeter_limit
            self.sourcemeter_obj.compliance_voltage = self.p.sourcemeter_compliance
            self.sourcemeter_obj.source_current = self.p.sourcemeter_bias
            #self.sourcemeter_obj.enable_source()
            #self.sourcemeter_obj.measure_voltage(self.p.sourcemeter_nplc, self.p.sourcemeter_limit)

        # Lakeshore initalization
        self.gaussmeter_obj.range(self.p.gaussmeter_range)
        self.gaussmeter_obj.resolution(self.p.gaussmeter_resolution)

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

        #MotionDriver
        if self.p.set_automaticstation:
            if self.p.address_automaticstation == "None":
                self.MotionDriver = DummyMotionDriver("sth")
            else:
                self.MotionDriver = Esp300(self.p.address_automaticstation)
                self.MotionDriver.high_level_motion_driver(self.p.global_xyname, self.p.sample_in_plane, self.p.disconnect_length)


        #Script inside device initialization and measurement
        self.sourcemeter_obj.enable_source()

        self.current_measurement=[]
        self.voltage_measurement=[]
        for i in range(len(self.ranges[0])):
            print(self.ranges[2][i])
            self.sourcemeter_obj.prepare_ConfigPulseVMeasureISweepLin(self.p.pulsegenerator_offset, self.ranges[0][i], self.ranges[2][i],self.p.pulsegenerator_compliance, self.p.pulsegenerator_ton, self.p.pulsegenerator_toff, self.ranges[1][i], 3)
            self.sourcemeter_obj.InitiatePulseTest(3)
            self.current_measurement+=self.sourcemeter_obj.downolad_data_from_buffer(self.ranges[1][i],'rbs.i')
            self.voltage_measurement+=self.sourcemeter_obj.downolad_data_from_buffer(self.ranges[1][i],'rbs.v')
            print( self.voltage_measurement)

        #self.current_measurement=np.array(self.current_measurement)
        #self.voltage_measurement=np.array(self.voltage_measurement)
        
        # measure field
        if self.p.set_gaussmeter == "none":
            self.tmp_field = self.p.field_bias_value
        else:
            self.tmp_field = self.gaussmeter_obj.measure()
        sleep(self.p.delay_bias)


    def operating(self, iterator):
        #self.field_obj.set_field(point)
        #sleep(self.p.delay_field)

        voltage=float(self.voltage_measurement[iterator])
        current=float(self.current_measurement[iterator])

        data = {
            "Voltage (V)": voltage,
            "Current (A)": current,
            "Resistance (ohm)": voltage/current,
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
        CIMSOneDeviceMode.idle(self)

    def idle(self):
        self.sourcemeter_obj.shutdown()
        sweep_field_to_zero(self.tmp_field, self.p.field_constant, self.p.field_step, self.field_obj)
        if (self.p.set_rotationstation or self.p.rotation_axis == "None") and self.p.return_the_rotationstation:
            self.rotationstation_obj.goToZero()

        if not self.p.has_next_callback() and self.p.set_automaticstation and self.p.go_init_position:
            self.MotionDriver.disconnect(self.p.sample_in_plane,self.p.disconnect_length)
            self.MotionDriver.init_position(self.p.sample_in_plane)
