from ..Qt import QtWidgets, QtCore, QtGui
from .tab_widget import TabWidget
from .inputs_widget import InputsWidget
from typing import Dict
import logging
import numpy as np

from hardware.keithley2400 import Keithley2400
from hardware.keithley_2636 import Keithley2636
from hardware.agilent_2912 import Agilent2912
from hardware.agilent_34410a import Agilent34410A

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def to_prefix(value):
    prefixes = {
        24: "Y",  # yotta
        21: "Z",  # zetta
        18: "E",  # exa
        15: "P",  # peta
        12: "T",  # tera
        9: "G",  # giga
        6: "M",  # mega
        3: "k",  # kilo
        0: "",  # no prefix
        -3: "m",  # milli
        -6: "µ",  # micro
        -9: "n",  # nano
        -12: "p",  # pico
        -15: "f",  # femto
        -18: "a",  # atto
        -21: "z",  # zepto
        -24: "y",  # yocto
    }

    if value == 0:
        return "0 "

    exponent = int("{:.0e}".format(value).split("e")[1])
    exponent = 3 * (exponent // 3)

    exponent = max(min(exponent, 24), -24)

    value_scaled = value / (10**exponent)

    prefix = prefixes[exponent]

    return f"{round_sig(value_scaled)} [{prefix}"


def round_sig(x: float, sig: int = 6):
    if x == 0:
        return 0
    return round(x, sig - int(np.floor(np.log10(abs(x)))) - 1)


class QuickMeasureWidget(TabWidget, QtWidgets.QWidget):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)

        self.tab_index = None

        self.inputs: InputsWidget = None
        self.prev_mode: str = ""

        self.isRunning = False

        self.device = None
        self.meas_device = None

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.measure)

        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.setStyleSheet("font-size: 14pt;")

        self.init_button = QtWidgets.QPushButton("Initialize")
        self.init_button.clicked.connect(self.init)

        self.volt_le = QtWidgets.QLineEdit("- [V]")
        self.volt_le.setReadOnly(True)
        self.volt_le.setAlignment(QtCore.Qt.AlignCenter)
        self.volt_le.setFixedHeight(100)

        self.curr_le = QtWidgets.QLineEdit("- [A]")
        self.curr_le.setReadOnly(True)
        self.curr_le.setAlignment(QtCore.Qt.AlignCenter)
        self.curr_le.setFixedHeight(100)

        self.res_le = QtWidgets.QLineEdit("- [Ω]")
        self.res_le.setReadOnly(True)
        self.res_le.setAlignment(QtCore.Qt.AlignCenter)
        self.res_le.setFixedHeight(100)

        self.single_btn = QtWidgets.QPushButton("Single")
        self.single_btn.clicked.connect(self.single_measure)

        self.start_btn = QtWidgets.QPushButton("Start")
        self.start_btn.clicked.connect(self.continous_measure)

    def _layout(self):
        main_layout = QtWidgets.QVBoxLayout()

        main_layout.addStretch()
        main_layout.addWidget(self.init_button, stretch=1)
        main_layout.addWidget(self.volt_le, stretch=2)
        main_layout.addWidget(self.curr_le, stretch=2)
        main_layout.addWidget(self.res_le, stretch=2)

        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addWidget(self.single_btn, stretch=1)
        h_layout.addWidget(self.start_btn, stretch=1)
        main_layout.addLayout(h_layout)

        main_layout.addStretch()

        self.setLayout(main_layout)

    def clear_le(self):
        self.volt_le.setText("- [V]")
        self.curr_le.setText("- [A]")
        self.res_le.setText("- [Ω]")

    def set_le(self, value, unit: str):
        text_to_set = to_prefix(value) + f"{unit}]"
        match unit:
            case "V":
                self.volt_le.setText(text_to_set)
            case "A":
                self.curr_le.setText(text_to_set)
            case "Ω":
                self.res_le.setText(text_to_set)

    def on_tab_change(self, index: int):
        if self.tab_index is None:
            return

        if index != self.tab_index:
            if self.prev_mode:
                self.inputs.mode.setValue(self.prev_mode)
                self.prev_mode = ""
            return

        self.prev_mode = self.inputs.mode.value()
        self.inputs.mode.setValue("QuickMeasurement")

    def get(self, attr: str):
        return getattr(self.inputs, attr).value()

    def init(self):
        self.meas_device = self.get("set_measdevice_qm")

        if self.meas_device == "Sourcemeter":
            device_name = self.get("set_sourcemeter")
            if device_name in ["None", "none", None]:
                log.error("QuickMeasure: device not selected!")
                return

            device_address = self.get("address_sourcemeter")
            if device_address in ["None", "none", None]:
                log.error("QuickMeasure: device address not selected!")
                return

            sourcemeter_channel = self.get("sourcemeter_channel")

            match device_name:
                case "Keithley 2400":
                    self.device = Keithley2400(device_address)
                    self.device.config_average(self.get("sourcemeter_average"))
                case "Keithley 2636":
                    if sourcemeter_channel == "Channel A":
                        self.device = Keithley2636(device_address).ChA
                    else:
                        self.device = Keithley2636(device_address).ChB
                case "Agilent 2912":
                    if sourcemeter_channel == "Channel A":
                        self.device = Agilent2912(device_address).ChA
                    else:
                        self.device = Agilent2912(device_address).ChB
                case _:
                    log.error("Device not implemented!")
                    return

            sourcemeter_source = self.get("sourcemter_source")
            self.device.source_mode = sourcemeter_source
            if sourcemeter_source == "VOLT":
                self.device.current_range = self.get("sourcemeter_limit")
                self.device.compliance_current = self.get("sourcemeter_compliance")
                self.device.source_voltage = self.get("sourcemeter_bias")
                self.device.enable_source()
                self.device.measure_current(self.get("sourcemeter_nplc"), self.get("sourcemeter_limit"))
            else:
                self.device.voltage_range = self.get("sourcemeter_limit")
                self.device.compliance_voltage = self.get("sourcemeter_compliance")
                self.device.source_current = self.get("sourcemeter_bias")
                self.device.enable_source()
                self.device.measure_voltage(self.get("sourcemeter_nplc"), self.get("sourcemeter_limit"))

        elif self.meas_device == "Multimeter":
            device_name = self.get("set_multimeter")

            if device_name in ["None", "none", None]:
                log.error("QuickMeasure: device not selected!")
                return

            device_address = self.get("address_multimeter")
            if device_address in ["None", "none", None]:
                log.error("QuickMeasure: device address not selected!")
                return

            match device_name:
                case "Agilent 34400":
                    self.device = Agilent34410A(device_address)
                case _:
                    log.error("Device not implemented!")
                    return

            autorange = self.get("multimeter_autorange")

            if not autorange:
                self.device.resolution = self.get("multimeter_resolution")
            self.device.range_ = self.get("multimeter_range")
            self.device.autorange = autorange
            self.multimeter_function = self.get("multimeter_function")
            self.device.function_ = self.multimeter_function
            self.device.trigger_delay = "MIN"
            self.device.trigger_count = self.get("multimeter_average")
            self.device.nplc = self.get("multimeter_nplc")
        else:
            raise ValueError("Invalid measurement device!")

    def measure(self):
        if self.device is None:
            log.error("QuickMeasure: device not initialized!")
            if self.isRunning:
                self.stop_measure()
            return

        if self.meas_device == "Sourcemeter":
            sourcemeter_source = self.get("sourcemter_source")

            if sourcemeter_source == "VOLT":
                if self.get("sourcemeter_bias") != 0:
                    tmp_voltage = self.get("sourcemeter_bias")
                else:
                    tmp_voltage = 1e-9
                tmp_current = self.device.current
                if type(tmp_current) == list:
                    tmp_current = np.average(tmp_current)
                print(tmp_current)
                tmp_resistance = tmp_voltage / tmp_current
            else:
                tmp_voltage = self.device.voltage
                if type(tmp_voltage) == list:
                    tmp_voltage = np.average(tmp_voltage)
                print(tmp_voltage)
                if self.get("sourcemeter_bias") != 0:
                    tmp_current = self.get("sourcemeter_bias")
                else:
                    tmp_current = 1e-9
                tmp_resistance = tmp_voltage / tmp_current

                self.clear_le()
                self.set_le(tmp_voltage, "V")
                self.set_le(tmp_current, "A")
                self.set_le(tmp_resistance, "Ω")
        else:
            reading = np.average(self.device.reading)

            self.clear_le()

            if self.multimeter_function in ["ACV", "DCV", "DCV_RATIO"]:
                self.set_le(reading, "V")
            elif self.multimeter_function in ["ACI", "DCI"]:
                self.set_le(reading, "A")
            elif self.multimeter_function in ["R2W", "R4W"]:
                self.set_le(reading, "Ω")
            else:
                log.error("Function not implemented!")
                if self.isRunning:
                    self.stop_measure()
                return

    def stop_device(self):
        if self.device is not None:
            if self.meas_device == "Sourcemeter":
                self.device.disable_source()

    def single_measure(self):
        self.measure()
        self.stop_device()

    def continous_measure(self):
        if self.isRunning:
            self.stop_measure()
        else:
            self.start_measure()

    def stop_measure(self):
        self.timer.stop()
        self.stop_device()

        self.isRunning = False
        self.start_btn.setText("Start")
        self.single_btn.setEnabled(True)
        self.init_button.setEnabled(True)

    def start_measure(self):
        self.timer.start(500)
        self.isRunning = True
        self.start_btn.setText("Stop")
        self.single_btn.setEnabled(False)
        self.init_button.setEnabled(False)
