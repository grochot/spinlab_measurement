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

        self.setStyleSheet("QLabel {font-size: 10pt;} QSpinBox {font-size: 14pt;} QLineEdit {font-size: 14pt;} QPushButton {font-size: 14pt;} QDoubleSpinBox {font-size: 14pt;} QComboBox {font-size: 14pt;}")

        locale = QtCore.QLocale(QtCore.QLocale.C)

        # Temperature control

        set_temp_l = QtWidgets.QLabel("Temp. setpoint [K]")
        set_temp_l.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(set_temp_l, 1, 1)  

        self.set_temp_sb = QtWidgets.QDoubleSpinBox()
        self.set_temp_sb.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.set_temp_sb.setRange(0.0, 600.0)
        self.set_temp_sb.setDecimals(3)
        self.set_temp_sb.setSingleStep(0.001)
        self.set_temp_sb.setLocale(locale)
        self.set_temp_sb.valueChanged.connect(self.setpoint_changed)
        main_layout.addWidget(self.set_temp_sb, 2, 1)

        curr_temp_l = QtWidgets.QLabel("Temp. current [K]")
        curr_temp_l.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(curr_temp_l, 1, 2)

        self.curr_temp_le = QtWidgets.QLineEdit("0")
        self.curr_temp_le.setReadOnly(True)
        self.curr_temp_le.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        main_layout.addWidget(self.curr_temp_le, 2, 2)

        # Time control

        set_delay_l = QtWidgets.QLabel("Delay [min]")
        set_delay_l.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(set_delay_l, 3, 1)
        
        self.set_delay_sb = QtWidgets.QSpinBox()
        self.set_delay_sb.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        main_layout.addWidget(self.set_delay_sb, 4, 1)

        set_timeout_l = QtWidgets.QLabel("Timeout [min]")
        set_timeout_l.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(set_timeout_l, 3, 2)

        self.set_timeout_sb = QtWidgets.QSpinBox()
        self.set_timeout_sb.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        main_layout.addWidget(self.set_timeout_sb, 4, 2)

        # Heater control

        output_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(output_layout, 5, 1)

        output1_layout = QtWidgets.QHBoxLayout()
        output_layout.addLayout(output1_layout)

        output1_l = QtWidgets.QLabel("OUT1")
        output1_l.setAlignment(QtCore.Qt.AlignCenter)
        output1_l.setFixedWidth(45)
        output1_layout.addWidget(output1_l)

        self.out1_cb = QtWidgets.QComboBox()
        self.out1_cb.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.out1_cb.addItem("OFF")
        self.out1_cb.addItem("LOW")
        self.out1_cb.addItem("MID")
        self.out1_cb.addItem("HIGH")
        self.out1_cb.setFixedWidth(120)
        output1_layout.addWidget(self.out1_cb)

        self.set_out1_btn = QtWidgets.QPushButton("\u2713")
        self.set_out1_btn.setFixedWidth(40)
        self.set_out1_btn.setFixedHeight(33)
        self.set_out1_btn.clicked.connect(self.set_out1)
        output1_layout.addWidget(self.set_out1_btn)

        output2_layout = QtWidgets.QHBoxLayout()
        output_layout.addLayout(output2_layout)

        output2_l = QtWidgets.QLabel("OUT2")
        output2_l.setAlignment(QtCore.Qt.AlignCenter)
        output2_l.setFixedWidth(45)
        output2_layout.addWidget(output2_l)

        self.out2_cb = QtWidgets.QComboBox()
        self.out2_cb.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.out2_cb.addItem("OFF")
        self.out2_cb.addItem("LOW")
        self.out2_cb.addItem("MID")
        self.out2_cb.addItem("HIGH")
        self.out2_cb.setFixedWidth(120)
        output2_layout.addWidget(self.out2_cb)

        self.set_out2_btn = QtWidgets.QPushButton("\u2713")
        self.set_out2_btn.setFixedWidth(40)
        self.set_out2_btn.setFixedHeight(33)
        self.set_out2_btn.clicked.connect(self.set_out2)
        output2_layout.addWidget(self.set_out2_btn)

        heater_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(heater_layout, 5, 2)

        heater_indicator_layout = QtWidgets.QVBoxLayout()
        heater_layout.addLayout(heater_indicator_layout)

        self.out1_indicator = QtWidgets.QPushButton()
        self.out1_indicator.setFixedWidth(40)
        self.out1_indicator.setFixedHeight(33)
        self.out1_indicator.setStyleSheet("border: 3px solid gray;")
        self.out1_indicator.setEnabled(False)
        heater_indicator_layout.addWidget(self.out1_indicator)

        self.out2_indicator = QtWidgets.QPushButton()
        self.out2_indicator.setFixedWidth(40)
        self.out2_indicator.setFixedHeight(33)
        self.out2_indicator.setEnabled(False)
        self.out2_indicator.setStyleSheet("border: 3px solid gray;")
        heater_indicator_layout.addWidget(self.out2_indicator)

        all_off_btn = QtWidgets.QPushButton("ALL\nOFF")
        all_off_btn.setFixedWidth(75)
        heater_layout.addWidget(all_off_btn)
        all_off_btn.clicked.connect(self.all_off)

        # Initialize attributes

        self.setpoint_value: float = 0.0
        self.ready_to_meas: bool = False
        self.delay_timer_started: bool = False
        self.timout_timer_started: bool = False
        self.timeout_flag: bool = False
        self.out1_on: bool = False
        self.out2_on: bool = False
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
        value = float(self.set_temp_sb.value())
        self.setpoint_value = value
        self.lakeshore.set_control_setpoint(1, value)
   

    def update_temperature(self):
        self.kelvin_readings = self.lakeshore.get_all_kelvin_reading()
        self.curr_temp_le.setText(f"{self.kelvin_readings[0]:.3f}")

        if abs(self.kelvin_readings[0] - self.setpoint_value) < 0.01 and not(self.delay_timer_started) and (self.out1_on or self.out2_on):
            self.setpoint_reached()

        if self.out1_on or self.out2_on:
            temp_diff = abs(self.kelvin_readings[0] - self.setpoint_value)
            if abs(temp_diff - self.prev_temp_diff) < 1:
                if not self.timout_timer_started:
                    print("Starting timeout timer")
                    self.timout_timer.start(1000 * 60 * int(self.set_timeout_sb.value()))
                    self.timout_timer_started = True
            else:
                print("Stopping timeout timer")
                self.timout_timer.stop()
                self.timout_timer_started = False

            self.prev_temp_diff = temp_diff

    def setpoint_reached(self):
            self.delay_timer_started = True
            delay = 60 * 1000 * int(self.set_delay_sb.value())
            self.delay_timer.start(delay)

    def set_ready_to_meas(self):
        print("Ready to measure")
        self.ready_to_meas = True
        self.delay_timer_started = False

    def timeout_reached(self):
        print("Timeout reached!!!")
        self.all_off()
        self.ready_to_meas = False

    def all_off(self):
        self.lakeshore.all_heaters_off()
        self.any_heater_on = False
        self.out1_indicator.setStyleSheet("border: 3px solid gray;")
        self.out2_indicator.setStyleSheet("border: 3px solid gray;")
        self.out1_cb.setCurrentIndex(0)
        self.out2_cb.setCurrentIndex(0)
        self.out1_on = False
        self.out2_on = False
        self.timout_timer.stop()

    def set_out1(self):
        val = self.out1_cb.currentText()
        if val == "OFF":
            self.lakeshore.set_heater_range(1, 0)
            self.out1_indicator.setStyleSheet("border: 3px solid gray;")
            self.out1_on = False

            if not self.out2_on:
                self.timout_timer.stop()

            return
        
        self.out1_on = True
        self.out1_indicator.setStyleSheet("border: 3px solid gray; background-color: green;")

        # start timera
        if val == "LOW":
            self.lakeshore.set_heater_range(1, 1)
            return
        if val == "MID":
            self.lakeshore.set_heater_range(1, 2)
            return
        if val == "HIGH":
            self.lakeshore.set_heater_range(1, 3)
            return

    def set_out2(self):
        val = self.out2_cb.currentText()
        if val == "OFF":
            self.lakeshore.set_heater_range(2, 0)
            self.out2_indicator.setStyleSheet("border: 3px solid gray;")
            self.out2_on = False

            if not self.out1_on:
                self.timout_timer.stop()

            return
        
        self.out2_on = True
        self.out2_indicator.setStyleSheet("border: 3px solid gray; background-color: green;")        
        #start timera


        if val == "LOW":
            self.lakeshore.set_heater_range(2, 1)
            return
        if val == "MID":
            self.lakeshore.set_heater_range(2, 2)
            return
        if val == "HIGH":
            self.lakeshore.set_heater_range(2, 3)
            return
        
        
            
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = LakeshoreControl()
    w.show()
    app.exec()