from ..Qt import QtWidgets, QtCore, QtGui
from .tab_widget import TabWidget
from typing import Dict


class QuickMeasureWidget(TabWidget, QtWidgets.QWidget):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        
        self.inputs = None
        
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

        self.result_le = QtWidgets.QLineEdit("RESULT")
        self.result_le.setReadOnly(True)
        self.result_le.setAlignment(QtCore.Qt.AlignCenter)
        # self.result_le.setStyleSheet("font-size: 20pt; font-weight: bold; border: 2px solid black;")
        self.result_le.setFixedHeight(100)

    def _layout(self):
        main_layout = QtWidgets.QVBoxLayout()

        # v_layout = QtWidgets.QVBoxLayout()
        # v_layout.addStretch()
        # v_layout.addWidget(self.device_cb)
        # v_layout.addWidget(self.measure_btn)
        # v_layout.addStretch()
        # main_layout.addLayout(v_layout, stretch=1)
        main_layout.addStretch()
        main_layout.addWidget(self.result_le, stretch=2)
        main_layout.addWidget(self.measure_btn, stretch=1)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        
    def measure(self):
        self.result_le.setText(self.inputs.set_sourcemeter.value())
