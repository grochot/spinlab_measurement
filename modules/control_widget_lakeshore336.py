from pymeasure.display.Qt import QtWidgets, QtCore
import sys
from lakeshore import Model336
from typing import List

class LakeshoreControl(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # GUI setup

        main_layout = QtWidgets.QGridLayout()
        self.setLayout(main_layout)
        self.setMinimumWidth(550)
        self.setWindowTitle("Lakeshore 336 control")

        self.setStyleSheet("QLabel {font-size: 10pt;} QSpinBox {font-size: 14pt;} QLineEdit {font-size: 14pt;} QPushButton {font-size: 14pt;} QDoubleSpinBox {font-size: 14pt;}")

        locale = QtCore.QLocale(QtCore.QLocale.C)

        # Temperature control

        setTemp_l = QtWidgets.QLabel("Temp. setpoint [K]")
        setTemp_l.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(setTemp_l, 1, 1)  

        setTemp_layout = QtWidgets.QHBoxLayout()
        self.setTemp_sb = QtWidgets.QDoubleSpinBox()
        self.setTemp_sb.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.setTemp_sb.setRange(0.0, 600.0)
        self.setTemp_sb.setDecimals(3)
        self.setTemp_sb.setSingleStep(0.001)
        self.setTemp_sb.setLocale(locale)
        self.setTemp_sb.valueChanged.connect(self.setpoint_changed)
        setTemp_layout.addWidget(self.setTemp_sb)

        self.setTemp_btn = QtWidgets.QPushButton("\u2713")
        self.setTemp_btn.setFixedWidth(40)
        self.setTemp_btn.setFixedHeight(33)
        self.setTemp_btn.clicked.connect(self.set_setpoint)
        self.setTemp_btn.setStyleSheet("background-color: red;")

        setTemp_layout.addWidget(self.setTemp_btn)

        main_layout.addLayout(setTemp_layout, 2, 1)

        currTemp_l = QtWidgets.QLabel("Temp. current [K]")
        currTemp_l.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(currTemp_l, 1, 2)

        self.currTemp_le = QtWidgets.QLineEdit("0")
        self.currTemp_le.setReadOnly(True)
        self.currTemp_le.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        main_layout.addWidget(self.currTemp_le, 2, 2)

        # Time control

        setDelay_l = QtWidgets.QLabel("Delay [min]")
        setDelay_l.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(setDelay_l, 3, 1)
        
        self.setDelay_sb = QtWidgets.QSpinBox()
        self.setDelay_sb.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        main_layout.addWidget(self.setDelay_sb, 4, 1)

        setTimeout_l = QtWidgets.QLabel("Timeout [min]")
        setTimeout_l.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(setTimeout_l, 3, 2)

        self.setTimeout_sb = QtWidgets.QSpinBox()
        self.setTimeout_sb.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        main_layout.addWidget(self.setTimeout_sb, 4, 2)

        # Initialize attributes
        self.setpoint_value: float = 0.0
        self.ready_to_meas: bool = False
        self.delay_timer_started: bool = False
        self.timout_timer_started: bool = False
        self.timeout_flag: bool = False
        self.setpoint_set: bool = False
        self.kelvin_readings: List[float] = []
        self.prev_temp_diff: float = 0.0

        # Connect to Lakeshore 336

        self.lakeshore = Model336(ip_address="192.168.0.12")

        # Timers

        refresh_timer = QtCore.QTimer(self)
        refresh_timer.timeout.connect(self.update_temperature)
        refresh_timer.start(1000)

        self.delay_timer = QtCore.QTimer(self)
        self.delay_timer.timeout.connect(self.set_ready_to_meas)
        self.delay_timer.setSingleShot(True)

        self.timout_timer = QtCore.QTimer(self)
        self.timout_timer.timeout.connect(self.timeout_reached)
        self.timout_timer.setSingleShot(True)

        self.update_temperature()

    def setpoint_changed(self):
        value = float(self.setTemp_sb.value())
        if value != self.setpoint_value:
            self.setTemp_btn.setStyleSheet("background-color: red;")
            self.setpoint_set = False
        else:
            self.setTemp_btn.setStyleSheet("background-color: green;")
            

    def update_temperature(self):
        self.kelvin_readings = self.lakeshore.get_all_kelvin_reading()
        self.currTemp_le.setText(f"{self.kelvin_readings[0]}")

        self.setpoint_reached()

        if self.setpoint_set:
            temp_diff = abs(self.kelvin_readings[0] - self.setpoint_value)
            if abs(temp_diff - self.prev_temp_diff) < 1:
                if not self.timout_timer_started:
                    print("Starting timeout timer")
                    self.timout_timer.start(1000 * 60 * int(self.setTimeout_sb.value()))
                    self.timout_timer_started = True
            else:
                print("Stopping timeout timer")
                self.timout_timer.stop()
                self.timout_timer_started = False

            self.prev_temp_diff = temp_diff

    def set_setpoint(self):
        value = float(self.setTemp_sb.value())
        self.setpoint_value = value
        self.temp_diff = abs(self.kelvin_readings[0] - self.setpoint_value)
        self.lakeshore.set_control_setpoint(1, self.setpoint_value)
        self.setpoint_set = True
        self.timout_timer.start(1000 * 60 * int(self.setTimeout_sb.value()))
        self.setTemp_btn.setStyleSheet("background-color: green;")

    def setpoint_reached(self):
        if abs(self.kelvin_readings[0] - self.setpoint_value) < 0.01 and not(self.delay_timer_started):
            self.delay_timer_started = True
            delay = 60 * 1000 * int(self.setDelay_sb.value())
            self.delay_timer.start(delay)

    def set_ready_to_meas(self):
        print("Ready to measure")
        self.ready_to_meas = True
        self.delay_timer_started = False

    def timeout_reached(self):
        print("Timeout reached!!!")
        self.ready_to_meas = False
        
            
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = LakeshoreControl()
    w.show()
    app.exec()