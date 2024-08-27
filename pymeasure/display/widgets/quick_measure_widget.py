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

        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.setStyleSheet("font-size: 14pt;")

        # self.device_cb = QtWidgets.QComboBox()
        # self.device_cb.addItems(self.devices.values())

        self.measure_btn = QtWidgets.QPushButton("Measure")
        self.measure_btn.clicked.connect(self.measure)

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

    def _layout(self):
        main_layout = QtWidgets.QVBoxLayout()

        # v_layout = QtWidgets.QVBoxLayout()
        # v_layout.addStretch()
        # v_layout.addWidget(self.device_cb)
        # v_layout.addWidget(self.measure_btn)
        # v_layout.addStretch()
        # main_layout.addLayout(v_layout, stretch=1)
        main_layout.addStretch()
        main_layout.addWidget(self.volt_le, stretch=2)
        main_layout.addWidget(self.curr_le, stretch=2)
        main_layout.addWidget(self.res_le, stretch=2)
        main_layout.addWidget(self.measure_btn, stretch=1)
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

    def measure(self):
        meas_device = self.get("set_measdevice_qm")

        if meas_device == "Sourcemeter":
            device = self.get("set_sourcemeter")
            if device in ["None", "none", None]:
                log.error("QuickMeasure: device not selected!")
                return

            sourcemeter_address = self.get("address_sourcemeter")
            if sourcemeter_address in ["None", "none", None]:
                log.error("QuickMeasure: device address not selected!")
                return

            sourcemeter_channel = self.get("sourcemeter_channel")

            match device:
                case "Keithley 2400":
                    device = Keithley2400(sourcemeter_address)
                    device.config_average(self.get("sourcemeter_average"))
                case "Keithley 2636":
                    if sourcemeter_channel == "Channel A":
                        device = Keithley2636(sourcemeter_address).ChA
                    else:
                        device = Keithley2636(sourcemeter_address).ChB
                case "Agilent 2912":
                    if sourcemeter_channel == "Channel A":
                        device = Agilent2912(sourcemeter_address).ChA
                    else:
                        device = Agilent2912(sourcemeter_address).ChB
                case _:
                    log.error("Device not implemented!")
                    return

            sourcemeter_source = self.get("sourcemter_source")
            device.source_mode = sourcemeter_source
            if sourcemeter_source == "VOLT":
                device.current_range = self.get("sourcemeter_limit")
                device.compliance_current = self.get("sourcemeter_compliance")
                device.source_voltage = self.get("sourcemeter_bias")
                device.enable_source()
                device.measure_current(self.get("sourcemeter_nplc"), self.get("sourcemeter_limit)"))
            else:
                device.voltage_range = self.get("sourcemeter_limit")
                device.compliance_voltage = self.get("sourcemeter_compliance")
                device.source_current = self.get("sourcemeter_bias")
                device.enable_source()
                device.measure_voltage(self.get("sourcemeter_nplc"), self.get("sourcemeter_limit)"))

            if sourcemeter_source == "VOLT":
                if self.get("sourcemeter_bias") != 0:
                    tmp_voltage = self.get("sourcemeter_bias")
                else:
                    tmp_voltage = 1e-9
                tmp_current = device.current
                if type(tmp_current) == list:
                    tmp_current = np.average(tmp_current)
                print(tmp_current)
                tmp_resistance = tmp_voltage / tmp_current
            else:
                tmp_voltage = device.voltage
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
            device = self.get("set_multimeter")

            match device:
                case "Agilent 34400":
                    device = Agilent34410A(self.get("address_multimeter"))
                case _:
                    log.error("Device not implemented!")
                    return

            autorange = self.get("multimeter_autorange")

            if not autorange:
                device.resolution = self.get("multimeter_resolution")
            device.range_ = self.get("multimeter_range")
            device.autorange = autorange
            multimeter_function = self.get("multimeter_function")
            device.function_ = multimeter_function
            device.trigger_delay = "MIN"
            device.trigger_count = self.get("multimeter_average")
            device.nplc = self.get("multimeter_nplc")

            reading = np.average(device.reading)

            self.clear_le()

            if multimeter_function in ["ACV", "DCV", "DCV_RATIO"]:
                self.set_le(reading, "V")
            elif multimeter_function in ["ACI", "DCI"]:
                self.set_le(reading, "A")
            elif multimeter_function in ["R2W", "R4W"]:
                self.set_le(reading, "Ω")
            else:
                log.error("Function not implemented!")
                return
