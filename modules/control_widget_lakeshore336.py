from pymeasure.display.Qt import QtWidgets, QtCore
import sys
from lakeshore import Model336
from typing import List

class NotConnectedDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connection error")

        retry_button = QtWidgets.QPushButton("Retry")
        cancel_button = QtWidgets.QPushButton("Cancel")

        self.buttonBox = QtWidgets.QDialogButtonBox()
        self.buttonBox.addButton(retry_button, QtWidgets.QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(cancel_button, QtWidgets.QDialogButtonBox.RejectRole)

        retry_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        self.layout = QtWidgets.QVBoxLayout()
        message = QtWidgets.QLabel("Could not connect to Lakeshore 336. Please check the connection and try again.")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class Lakeshore336Control(QtWidgets.QWidget):

    ready_to_meas_signal = QtCore.pyqtSignal()

    def __init__(self, ip_address: str = "192.168.0.12"):
        super().__init__()

        # Constants
        self.HEATER_STATES = ["OFF", "LOW", "MID", "HIGH"]
        self.IP_ADDRESS = ip_address

        # Initialize attributes
        self.lakeshore = None
        self.setpoint_value: float = 0.0
        self.ready_to_meas: bool = False
        self.out1_on: bool = False
        self.out2_on: bool = False
        self.do_update: bool = True
        self.kelvin_readings: List[float] = []
        self.prev_temp_diff: float = 0.0

        self.not_connected_dialog = NotConnectedDialog()

        # Connect to Lakeshore 336
        self.connect_to_lakeshore()

        # GUI setup
        self.setMinimumWidth(550)
        self.setWindowTitle("Lakeshore 336 control")

        self.setStyleSheet("QLabel {font-size: 10pt;} QSpinBox {font-size: 14pt;} QLineEdit {font-size: 14pt;} QPushButton {font-size: 14pt;} QDoubleSpinBox {font-size: 14pt;} QComboBox {font-size: 14pt;}")

        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        grid_layout = QtWidgets.QGridLayout()
        main_layout.addLayout(grid_layout)

        self.status_bar = QtWidgets.QStatusBar()
        self.status_bar.showMessage("Connected!")
        main_layout.addWidget(self.status_bar)

        # Temperature control

        set_temp_l = QtWidgets.QLabel("Temp. setpoint [K]")
        set_temp_l.setAlignment(QtCore.Qt.AlignCenter)
        grid_layout.addWidget(set_temp_l, 1, 1)  

        set_temp_layout = QtWidgets.QHBoxLayout()
        grid_layout.addLayout(set_temp_layout, 2, 1)

        self.set_temp_sb = QtWidgets.QDoubleSpinBox()
        self.set_temp_sb.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.set_temp_sb.setRange(0.0, 600.0)
        self.set_temp_sb.setDecimals(3)
        self.set_temp_sb.setSingleStep(0.001)
        self.set_temp_sb.valueChanged.connect(self.remote_change)
        set_temp_layout.addWidget(self.set_temp_sb)

        self.set_out1_btn = QtWidgets.QPushButton("\u2713")
        self.set_out1_btn.setFixedWidth(40)
        self.set_out1_btn.setFixedHeight(33)
        self.set_out1_btn.clicked.connect(self.setpoint_changed)
        set_temp_layout.addWidget(self.set_out1_btn)

        curr_temp_l = QtWidgets.QLabel("Temp. current [K]")
        curr_temp_l.setAlignment(QtCore.Qt.AlignCenter)
        grid_layout.addWidget(curr_temp_l, 1, 2)

        self.curr_temp_le = QtWidgets.QLineEdit("0")
        self.curr_temp_le.setReadOnly(True)
        self.curr_temp_le.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        grid_layout.addWidget(self.curr_temp_le, 2, 2)

        # Time control

        set_delay_l = QtWidgets.QLabel("Delay [min]")
        set_delay_l.setAlignment(QtCore.Qt.AlignCenter)
        grid_layout.addWidget(set_delay_l, 3, 1)
        
        self.set_delay_sb = QtWidgets.QSpinBox()
        self.set_delay_sb.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.set_delay_sb.setValue(10)
        grid_layout.addWidget(self.set_delay_sb, 4, 1)

        set_timeout_l = QtWidgets.QLabel("Timeout [min]")
        set_timeout_l.setAlignment(QtCore.Qt.AlignCenter)
        grid_layout.addWidget(set_timeout_l, 3, 2)

        self.set_timeout_sb = QtWidgets.QSpinBox()
        self.set_timeout_sb.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.set_timeout_sb.setValue(30)
        grid_layout.addWidget(self.set_timeout_sb, 4, 2)

        # Heater control

        output_layout = QtWidgets.QVBoxLayout()
        grid_layout.addLayout(output_layout, 5, 1)

        output1_layout = QtWidgets.QHBoxLayout()
        output_layout.addLayout(output1_layout)

        output1_l = QtWidgets.QLabel("OUT1")
        output1_l.setAlignment(QtCore.Qt.AlignCenter)
        output1_l.setFixedWidth(45)
        output1_layout.addWidget(output1_l)

        self.out1_cb = QtWidgets.QComboBox()
        self.out1_cb.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        for state in self.HEATER_STATES:
            self.out1_cb.addItem(state)
        self.out1_cb.setFixedWidth(120)
        self.out1_cb.currentTextChanged.connect(self.remote_change)
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
        for state in self.HEATER_STATES:
            self.out2_cb.addItem(state)
        self.out2_cb.setFixedWidth(120)
        self.out2_cb.currentTextChanged.connect(self.remote_change)
        output2_layout.addWidget(self.out2_cb)

        self.set_out2_btn = QtWidgets.QPushButton("\u2713")
        self.set_out2_btn.setFixedWidth(40)
        self.set_out2_btn.setFixedHeight(33)
        self.set_out2_btn.clicked.connect(self.set_out2)
        output2_layout.addWidget(self.set_out2_btn)

        heater_layout = QtWidgets.QHBoxLayout()
        grid_layout.addLayout(heater_layout, 5, 2)

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

        # Timers

        self.refresh_timer = QtCore.QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_tick)
        self.refresh_timer.start(1000)

        self.delay_timer = QtCore.QTimer(self)
        self.delay_timer.timeout.connect(self.set_ready_to_meas)
        self.delay_timer.setSingleShot(True)

        self.timeout_timer = QtCore.QTimer(self)
        self.timeout_timer.timeout.connect(self.timeout_reached)
        self.timeout_timer.setSingleShot(True)

        self.update_gui()
        self.refresh_tick()

    def connect_to_lakeshore(self):
        while True:
            try:
                self.lakeshore = Model336(ip_address=self.IP_ADDRESS)
                break
            except (TimeoutError, ConnectionAbortedError, ConnectionResetError) as e:
                print(e)
                self.not_connected_dialog.exec()
                if self.not_connected_dialog.result() == QtWidgets.QDialog.Rejected:
                    sys.exit()
                else:
                    print("Retrying connection...")

    def remote_change(self):
        self.do_update = False

    def update_gui(self):
        if not self.do_update:
            return

        try:
            setpoint = self.lakeshore.get_control_setpoint(1)
            out1_range = self.lakeshore.get_heater_range(1)
            out2_range = self.lakeshore.get_heater_range(2)
        except (ConnectionResetError, ConnectionAbortedError):
            self.connect_to_lakeshore()

        self.set_temp_sb.setValue(setpoint)
        self.setpoint_value = setpoint

        
        self.out1_cb.setCurrentIndex(out1_range)
        if out1_range > 0:
            self.out1_indicator.setStyleSheet("border: 3px solid gray; background-color: green;")
            self.out1_on = True
        else:
            self.out1_on = False
            self.out1_indicator.setStyleSheet("border: 3px solid gray;")

        
        self.out2_cb.setCurrentIndex(out2_range)
        if out2_range > 0:
            self.out2_indicator.setStyleSheet("border: 3px solid gray; background-color: green;")
            self.out2_on = True
        else:
            self.out2_indicator.setStyleSheet("border: 3px solid gray;")
            self.out2_on = False

        if not (self.out1_on or self.out2_on):
            self.timeout_timer.stop()
            self.delay_timer.stop()
            self.ready_to_meas = False

    def setpoint_changed(self):
        self.do_update = True
        value = float(self.set_temp_sb.value())
        self.setpoint_value = value
        try:
            self.lakeshore.set_control_setpoint(1, value)
        except (ConnectionResetError, ConnectionAbortedError):
            self.connect_to_lakeshore()

    def refresh_tick(self):

        self.update_gui()

        try:
            self.kelvin_readings = self.lakeshore.get_all_kelvin_reading()
        except (ConnectionResetError, ConnectionAbortedError):
            self.connect_to_lakeshore()
        self.curr_temp_le.setText(f"{self.kelvin_readings[0]:.3f}")

        if abs(self.kelvin_readings[0] - self.setpoint_value) < 0.01 and not(self.delay_timer.isActive()) and (self.out1_on or self.out2_on) and not(self.ready_to_meas):
            self.setpoint_reached()

        if (self.out1_on or self.out2_on) and not(self.delay_timer.isActive()) and not(self.ready_to_meas):
            temp_diff = abs(self.kelvin_readings[0] - self.setpoint_value)
            if abs(temp_diff - self.prev_temp_diff) < 1:
                if not self.timeout_timer.isActive():
                    print("Starting timeout timer")
                    self.timeout_timer.start(1000 * 60 * int(self.set_timeout_sb.value()))
            else:
                print("Stopping timeout timer")
                self.timeout_timer.stop()

            self.prev_temp_diff = temp_diff

    def setpoint_reached(self):
            print("Setpoint reached")
            print("\tStarting delay timer")
            print("\tStopping timeout timer")
            self.timeout_timer.stop()
            delay = 60 * 1000 * int(self.set_delay_sb.value())
            self.delay_timer.start(delay)

    def set_ready_to_meas(self):
        print("Ready to measure")
        self.ready_to_meas_signal.emit()
        self.ready_to_meas = True

    def timeout_reached(self):
        print("Timeout reached!!!")
        self.all_off()
        self.ready_to_meas = False

    def all_off(self):
        try:
            self.lakeshore.all_heaters_off()
        except (ConnectionResetError, ConnectionAbortedError):
            self.connect_to_lakeshore()
        self.out1_on = False
        self.out2_on = False

        self.delay_timer.stop()
        self.timeout_timer.stop()

        self.ready_to_meas = False

        self.out1_indicator.setStyleSheet("border: 3px solid gray;")
        self.out2_indicator.setStyleSheet("border: 3px solid gray;")
        self.out1_cb.setCurrentIndex(0)
        self.out2_cb.setCurrentIndex(0)


    def set_out1(self):
        self.do_update = False
        val = self.out1_cb.currentText()
        if val == "OFF":
            try:
                self.lakeshore.set_heater_range(1, 0)
            except (ConnectionResetError, ConnectionAbortedError):
                self.connect_to_lakeshore()
            self.out1_indicator.setStyleSheet("border: 3px solid gray;")
            self.out1_on = False

            if not self.out2_on:
                self.timeout_timer.stop()

            return
        
        self.out1_on = True
        self.out1_indicator.setStyleSheet("border: 3px solid gray; background-color: green;")
        try:
            self.lakeshore.set_heater_range(1, self.HEATER_STATES.index(val))
        except (ConnectionResetError, ConnectionAbortedError):
            self.connect_to_lakeshore()

    def set_out2(self):
        self.do_update = False
        val = self.out2_cb.currentText()
        if val == "OFF":
            try:
                self.lakeshore.set_heater_range(2, 0)
            except (ConnectionResetError, ConnectionAbortedError):
                self.connect_to_lakeshore()
            self.out2_indicator.setStyleSheet("border: 3px solid gray;")
            self.out2_on = False

            if not self.out1_on:
                self.timeout_timer.stop()

            return
        
        self.out2_on = True
        self.out2_indicator.setStyleSheet("border: 3px solid gray; background-color: green;")
        try:       
            self.lakeshore.set_heater_range(2, self.HEATER_STATES.index(val))
        except (ConnectionResetError, ConnectionAbortedError):
            self.connect_to_lakeshore()
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Lakeshore336Control()
    w.show()
    app.exec()
