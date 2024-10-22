import logging
from typing import Union
from app import SpinLabMeasurement

# lockin
from hardware.sr830 import SR830
from hardware.dummy_lockin import DummyLockin
from logic.lockin_parameters import _lockin_timeconstant, _lockin_sensitivity, _lockin_filter_slope

# multimeter
from hardware.agilent_34410a import Agilent34410A
from hardware.dummy_multimeter import DummyMultimeter

# gaussmeter
from hardware.lakeshore import Lakeshore
from hardware.GM_700 import GM700
from hardware.dummy_gaussmeter import DummyGaussmeter

# field controller
from hardware.daq import DAQ
from hardware.dummy_field import DummyField

# high frequency generator
from hardware.generator_agilent import FGenDriver
from hardware.windfreak import Windfreak
from hardware.dummy_fgen import DummyFgenDriver

# low frequency generator
from hardware.hp_33120a import LFGenDriver
from hardware.dummy_lfgen import DummyLFGenDriver

# sourcemeter
from hardware.keithley2400 import Keithley2400
from hardware.keithley_2636 import Keithley2636
from hardware.agilent_2912 import Agilent2912
from hardware.dummy_sourcemeter import DummySourcemeter

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class HardwareManager:
    def __init__(self, procedure: SpinLabMeasurement) -> None:
        self.p: SpinLabMeasurement = procedure

    def create_lockin(self) -> Union[SR830, DummyLockin]:
        match self.p.set_lockin:
            case "SR830":
                lockin_obj = SR830(self.p.address_lockin)
            case "Zurich":
                raise NotImplementedError("Zurich lockin is not implemented")
            case _:
                lockin_obj = DummyLockin()
                log.warning("Used dummy Lockin.")

        return lockin_obj

    def initialize_lockin(self, lockin_obj: Union[SR830, DummyLockin]) -> None:
        lockin_obj.frequency = self.p.lockin_frequency
        if self.p.lockin_sensitivity == "Auto Gain":
            lockin_obj.auto_gain()
        else:
            lockin_obj.sensitivity = _lockin_sensitivity(self.p.lockin_sensitivity)
        lockin_obj.time_constant = _lockin_timeconstant(self.p.lockin_timeconstant)
        lockin_obj.filter_slope = _lockin_filter_slope(self.p.lockin_slope)
        lockin_obj.harmonic = self.p.lockin_harmonic
        lockin_obj.sine_voltage = self.p.lockin_sine_amplitude
        lockin_obj.channel1 = self.p.lockin_channel1
        lockin_obj.channel2 = self.p.lockin_channel2
        lockin_obj.input_config = self.p.lockin_input_connection
        lockin_obj.input_coupling = self.p.lockin_input_coupling
        lockin_obj.reference_source = self.p.lockin_reference_source

    def create_multimeter(self) -> Union[Agilent34410A, DummyMultimeter]:
        match self.p.set_multimeter:
            case "Agilent 34400":
                multimeter_obj = Agilent34410A(self.p.address_multimeter)
            case _:
                multimeter_obj = DummyMultimeter(self.p.address_multimeter)
                log.warning("Used dummy Multimeter.")

        return multimeter_obj
    
    def initialize_multimeter(self, multimeter_obj: Union[Agilent34410A, DummyMultimeter]) -> None:
        if not self.p.multimeter_autorange:
            multimeter_obj.resolution = self.p.multimeter_resolution
        multimeter_obj.range_ = self.p.multimeter_range
        multimeter_obj.autorange = self.p.multimeter_autorange
        multimeter_obj.function_ = self.p.multimeter_function
        multimeter_obj.trigger_delay = "MIN"
        multimeter_obj.trigger_count = self.p.multimeter_average
        multimeter_obj.nplc = self.p.multimeter_nplc

    def create_gaussmeter(self) -> Union[Lakeshore, GM700, DummyGaussmeter]:
        match self.p.set_gaussmeter:
            case "Lakeshore":
                gaussmeter_obj = Lakeshore(self.p.address_gaussmeter)
            case "GM700":
                gaussmeter_obj = GM700(self.p.address_gaussmeter)
            case _:
                gaussmeter_obj = DummyGaussmeter(self.p.address_gaussmeter)
                log.warning("Used dummy Gaussmeter.")

        return gaussmeter_obj

    def create_field_cntrl(self) -> Union[DAQ, DummyField]:
        match self.p.set_field_cntrl:
            case "DAQ":
                field_obj = DAQ(self.p.address_daq)
            case _:
                field_obj = DummyField(self.p.address_daq)
                log.warning("Used dummy DAQ.")

        return field_obj

    def create_hf_generator(self) -> Union[FGenDriver, Windfreak, DummyFgenDriver]:
        match self.p.set_generator:
            case "Agilent":
                generator_obj = FGenDriver(self.p.address_generator)
            case "Windfreak":
                channel = 0 if self.p.generator_channel == "A" else 1
                generator_obj = Windfreak(self.p.address_generator, channel=channel)
            case _:
                generator_obj = DummyFgenDriver()
                log.warning("Used dummy Frequency Generator.")

        return generator_obj

    def create_lf_generator(self) -> Union[SR830, LFGenDriver, DummyLFGenDriver]:
        match self.p.set_lfgen:
            case "SR830":
                lfgen_obj = SR830(self.p.address_lockin)
            case "HP33120A":
                lfgen_obj = LFGenDriver(self.p.address_lfgen)
            case _:
                lfgen_obj = DummyLFGenDriver()
                log.warning("Used dummy Modulation Generator.")

        return lfgen_obj

    def create_sourcemeter(self) -> Union[Keithley2400, Keithley2636, Agilent2912, DummySourcemeter]:
        match self.p.set_sourcemeter:
            case "Keithley 2400":
                sourcemeter_obj = Keithley2400(self.p.address_sourcemeter)
                sourcemeter_obj.config_average(self.p.sourcemeter_average)
            case "Keithley 2636":
                if self.p.sourcemeter_channel == "Channel A":
                    sourcemeter_obj = Keithley2636(self.p.address_sourcemeter).ChA
                else:
                    sourcemeter_obj = Keithley2636(self.p.address_sourcemeter).ChB

            case "Agilent 2912":
                if self.p.sourcemeter_channel == "Channel A":
                    sourcemeter_obj = Agilent2912(self.p.address_sourcemeter).ChA
                else:
                    sourcemeter_obj = Agilent2912(self.p.address_sourcemeter).ChB
            case _:
                sourcemeter_obj = DummySourcemeter(self.p.address_sourcemeter)
                log.warning("Used dummy Sourcemeter.")

        return sourcemeter_obj
