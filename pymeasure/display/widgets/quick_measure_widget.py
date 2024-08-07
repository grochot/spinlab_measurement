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


class QuickMeasureWidget(TabWidget, QtWidgets.QWidget):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)

        self.inputs: InputsWidget = None
        self.prev_mode: str = ""

        # self.devices: Dict[int, str] = {
        #     0: "Keithley 2400",
        #     1: "Keithley 2636",
        #     2: "Agilent 2912"
        # }

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

    def on_tab_change(self, index: int):
        if index != 3:
            self.inputs.mode.setValue(self.prev_mode)
            return

        self.prev_mode = self.inputs.mode.value()
        self.inputs.mode.setValue("QuickMeasurement")

    def get(self, attr: str):
        return getattr(self.inputs, attr).value()

    def measure(self):
        # device = self.get("set_sourcemeter")
        # if device in ["None", "none", None]:
        #     log.error("QuickMeasure: device not selected!")
        #     return

        # sourcemeter_address = self.get("address_sourcemeter")
        # if sourcemeter_address in ["None", "none", None]:
        #     log.error("QuickMeasure: device address not selected!")
        #     return

        # sourcemeter_channel = self.get("sourcemeter_channel")

        # match device:
        #     case "Keithley 2400":
        #         device = Keithley2400(sourcemeter_address)
        #         device.config_average(self.get("sourcemeter_average"))
        #     case "Keithley 2636":
        #         if sourcemeter_channel == "Channel A":
        #             device = Keithley2636(sourcemeter_address).ChA
        #         else:
        #             device = Keithley2636(sourcemeter_address).ChB
        #     case "Agilent 2912":
        #         if sourcemeter_channel == "Channel A":
        #             device = Agilent2912(sourcemeter_address).ChA
        #         else:
        #             device = Agilent2912(sourcemeter_address).ChB
        #     case _:
        #         log.error("Device not implemented!")
        #         return

        # sourcemeter_source = self.get("sourcemter_source")
        # device.source_mode = sourcemeter_source
        # if sourcemeter_source == "VOLT":
        #     device.current_range = self.get("sourcemeter_limit")
        #     device.compliance_current = self.get("sourcemeter_compliance")
        #     device.source_voltage = self.get("sourcemeter_bias")
        #     device.enable_source()
        #     device.measure_current(self.get("sourcemeter_nplc"), self.get("sourcemeter_limit)"))
        # else:
        #     device.voltage_range = self.get("sourcemeter_limit")
        #     device.compliance_voltage = self.get("sourcemeter_compliance")
        #     device.source_current = self.get("sourcemeter_bias")
        #     device.enable_source()
        #     device.measure_voltage(self.get("sourcemeter_nplc"), self.get("sourcemeter_limit)"))

        # if sourcemeter_source == "VOLT":
        #     if self.get("sourcemeter_bias") != 0:
        #         tmp_voltage = self.get("sourcemeter_bias")
        #     else:
        #         tmp_voltage = 1e-9
        #     tmp_current = device.current
        #     if type(tmp_current) == list:
        #         tmp_current = np.average(tmp_current)
        #     print(tmp_current)
        #     tmp_resistance = tmp_voltage / tmp_current
        # else:
        #     tmp_voltage = device.voltage
        #     if type(tmp_voltage) == list:
        #         tmp_voltage = np.average(tmp_voltage)
        #     print(tmp_voltage)
        #     if self.get("sourcemeter_bias") != 0:
        #         tmp_current = self.get("sourcemeter_bias")
        #     else:
        #         tmp_current = 1e-9
        #     tmp_resistance = tmp_voltage / tmp_current
        
        device = self.get("set_multimeter")
        
        match device:
            case "Agilent 34400": 
                device = Agilent34410A(self.address_multimeter)
            case _:
                log.error("Device not implemented!")
                return
            
        device.resolution = self.get("multimeter_resolution")
        device.range_ = self.get("multimeter_range")
        device.autorange = self.get("self.multimeter_autorange")
        device.function_ = self.get("multimeter_function")
        device.trigger_delay = "MIN"
        device.trigger_count = self.get("multimeter_average")
        device.nplc = self.get("self.multimeter_nplc")
        
        reading = np.average(device.reading)
        
        
        self.volt_le.setText(str(reading))
        self.curr_le.setText(str(reading))
        self.res_le.setText(str(reading))

        # self.volt_le.setText(str(tmp_voltage))
        # self.curr_le.setText(str(tmp_current))
        # self.res_le.setText(str(tmp_resistance))
