from pymeasure.display.Qt import QtWidgets, QtCore, QtGui
import sys
from lakeshore import Model336
from typing import List
from logging import WARNING

class DummyLakeshore336:
    def __init__(self):
        self.setpoint = 0.0
        self.heater = {
            1: 0,
            2: 0
        }

    def get_control_setpoint(self, channel):
        return self.setpoint

    def get_heater_range(self, channel):
        return self.heater[channel]

    def get_all_kelvin_reading(self):
        return [300.123]

    def set_control_setpoint(self, channel, value):
        self.setpoint = value

    def all_heaters_off(self):
        pass

    def set_heater_range(self, channel, value):
        self.heater[channel] = value
        
class HeaterControl(QtWidgets.QWidget):
    def __init__(self, label_text):
        super().__init__()
        
        self.HEATER_RANGES = ["OFF", "LOW", "MID", "HIGH"]
        
        self.label_text = label_text
        
        self._setup_ui()
        self._layout()
        
    def _setup_ui(self):
        
        self.label = QtWidgets.QLabel(self.label_text)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.label.setFixedWidth(45)
        
        self.heater_range_cb = QtWidgets.QComboBox()
        self.heater_range_cb.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.setFixedWidth(300)
        for state in self.HEATER_RANGES:
            self.heater_range_cb.addItem(state)
        
        self.set_btn = QtWidgets.QPushButton("\u2713")
        self.set_btn.setFixedWidth(40)
        self.set_btn.setFixedHeight(33)
        
        
    def _layout(self):
        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)
        
        layout.addWidget(self.label)
        layout.addWidget(self.heater_range_cb)
        layout.addWidget(self.set_btn)

class Indicator(QtWidgets.QPushButton):
    def __init__(self, width=40, height=33):
        super().__init__()
        self.setFixedWidth(width)
        self.setFixedHeight(height)
        self.setStyleSheet(f"border: 3px solid gray")
        self.setEnabled(False)
        self.state = 0
        
    def set_color(self, color):
        self.setStyleSheet(f"border: 3px solid gray; background-color: {color};")
        
    def set_on(self):
        self.set_color("green")
        self.state = 1
        
    def set_off(self):
        self.setStyleSheet("border: 3px solid gray;")
        self.state = 0
        
    def set_warning(self):
        self.set_color("yellow")
        self.state = 1
        
    def set_error(self):
        self.set_color("red")
        self.state = 1
        
    def toggle(self, color):
        if self.state == 0:
            self.setStyleSheet(f"border: 3px solid gray; background-color: {color};")
            self.state = 1
        else:
            self.set_off()
            
    def start_blinking(self, color):
        self.setStyleSheet(f"border: 3px solid gray; background-color: {color};")
        self.state = 1
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(lambda: self.toggle(color))
        self.timer.start(500)
        
    def stop_blinking(self):
        try:
            self.timer.stop()
        except AttributeError:
            pass
        self.set_off()

class Lakeshore336Control(QtWidgets.QWidget):

    ready_to_meas_signal = QtCore.pyqtSignal()
    object_name = "lakeshore336_control"

    def __init__(self, ip_address: str = "192.168.0.12"):
        super().__init__()

        # Constants
        self.IP_ADDRESS = ip_address
        self.name = "Lakeshore 336"
        self.icon_path = "modules\icons\Lakeshore336.ico"

        # Initialize attributes
        self.device = None
        self.setpoint_value: float = 0.0
        self.ready_to_meas: bool = False
        self.out1_on: bool = False
        self.out2_on: bool = False
        self.do_update: bool = True
        self.kelvin_readings: List[float] = []
        self.prev_temp_diff: float = 0.0
        self.HEATER_RANGES = ["OFF", "LOW", "MID", "HIGH"]
        
        self._setup_ui()
        self._layout()    

        # Timers
        self.refresh_timer = QtCore.QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_tick)

        self.delay_timer = QtCore.QTimer(self)
        self.delay_timer.timeout.connect(self.set_ready_to_meas)
        self.delay_timer.setSingleShot(True)

        self.timeout_timer = QtCore.QTimer(self)
        self.timeout_timer.timeout.connect(self.timeout_reached)
        self.timeout_timer.setSingleShot(True)
        
        self.connect_to_lakeshore()
        

    def _setup_ui(self):
        self.setMinimumWidth(550)
        self.setWindowTitle("Lakeshore 336")
        self.setWindowIcon(QtGui.QIcon(self.icon_path))
        self.setStyleSheet("QLabel {font-size: 10pt;} QSpinBox {font-size: 14pt;} QLineEdit {font-size: 14pt;} QPushButton {font-size: 14pt;} QDoubleSpinBox {font-size: 14pt;} QComboBox {font-size: 14pt;}")
        
        self.stack = QtWidgets.QStackedWidget(self)
        
        # CONTROL WIDGET
        self.control_widget = QtWidgets.QWidget()
        self.stack.addWidget(self.control_widget)
        # Temperature control
        self.set_temp_l = QtWidgets.QLabel("Setpoint [K]")
        self.set_temp_l.setAlignment(QtCore.Qt.AlignCenter)
        
        self.set_temp_sb = QtWidgets.QDoubleSpinBox()
        self.set_temp_sb.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.set_temp_sb.setRange(0.0, 600.0)
        self.set_temp_sb.setDecimals(3)
        self.set_temp_sb.setSingleStep(0.001)
        self.set_temp_sb.valueChanged.connect(self.remote_change)
        
        self.set_out1_btn = QtWidgets.QPushButton("\u2713")
        self.set_out1_btn.setFixedWidth(40)
        self.set_out1_btn.setFixedHeight(33)
        self.set_out1_btn.clicked.connect(self.setpoint_changed)
        
        self.curr_temp_l = QtWidgets.QLabel("Temperature [K]")
        self.curr_temp_l.setAlignment(QtCore.Qt.AlignCenter)
        
        self.curr_temp_le = QtWidgets.QLineEdit("0")
        self.curr_temp_le.setReadOnly(True)
        self.curr_temp_le.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        
        self.curr_temp_indicator = Indicator()
        
        # Time control
        self.set_delay_l = QtWidgets.QLabel("Delay [min]")
        self.set_delay_l.setAlignment(QtCore.Qt.AlignCenter)
        
        self.set_delay_sb = QtWidgets.QSpinBox()
        self.set_delay_sb.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.set_delay_sb.setValue(10)
        
        self.delay_indicator = Indicator()

        self.set_timeout_l = QtWidgets.QLabel("Timeout [min]")
        self.set_timeout_l.setAlignment(QtCore.Qt.AlignCenter)

        self.set_timeout_sb = QtWidgets.QSpinBox()
        self.set_timeout_sb.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.set_timeout_sb.setValue(30)
        
        self.timeout_indicator = Indicator()
        
        # Heater control
        self.out1_widget = HeaterControl("OUT1")
        self.out1_widget.heater_range_cb.currentTextChanged.connect(self.remote_change)
        self.out1_widget.set_btn.clicked.connect(self.set_out1)
        
        self.out2_widget = HeaterControl("OUT2")
        self.out2_widget.heater_range_cb.currentTextChanged.connect(self.remote_change)
        self.out2_widget.set_btn.clicked.connect(self.set_out2)

        self.out1_indicator = Indicator()

        self.out2_indicator = Indicator()

        self.all_off_btn = QtWidgets.QPushButton("ALL\nOFF")
        self.all_off_btn.setFixedWidth(75)
        self.all_off_btn.clicked.connect(self.all_off)
        
        # NOT CONNECTED WIDGET
        self.not_conn_widget = QtWidgets.QWidget()
        self.stack.addWidget(self.not_conn_widget)
        
        self.not_conn_l = QtWidgets.QLabel("NOT CONNECTED WITH DEVICE")
        self.not_conn_l.setAlignment(QtCore.Qt.AlignCenter)
        self.not_conn_l.setStyleSheet("font-size: 16pt;")
        
        self.retry_btn = QtWidgets.QPushButton("RETRY")
        self.retry_btn.clicked.connect(self.connect_to_lakeshore)
        
        self.stack.setCurrentWidget(self.not_conn_widget)
        
        
    def _layout(self):
        
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)
        
        main_layout.addWidget(self.stack)
        main_layout.addStretch()
        
        control_layout = QtWidgets.QVBoxLayout()
        self.control_widget.setLayout(control_layout)
        
        grid_layout = QtWidgets.QGridLayout()
        control_layout.addLayout(grid_layout)
        
        grid_layout.addWidget(self.set_temp_l, 0, 0)
        
        set_temp_layout = QtWidgets.QHBoxLayout()
        grid_layout.addLayout(set_temp_layout, 1, 0)
        set_temp_layout.addWidget(self.set_temp_sb)
        set_temp_layout.addWidget(self.set_out1_btn)
        
        grid_layout.addWidget(self.curr_temp_l, 0, 1)
        curr_temp_layout = QtWidgets.QHBoxLayout()
        grid_layout.addLayout(curr_temp_layout, 1, 1)
        curr_temp_layout.addWidget(self.curr_temp_le)
        curr_temp_layout.addWidget(self.curr_temp_indicator)
        
        grid_layout.addWidget(self.set_delay_l, 2, 0)
        delay_layout = QtWidgets.QHBoxLayout()
        grid_layout.addLayout(delay_layout, 3, 0)
        delay_layout.addWidget(self.set_delay_sb)
        delay_layout.addWidget(self.delay_indicator)
        
        grid_layout.addWidget(self.set_timeout_l, 2, 1)
        timeout_layout = QtWidgets.QHBoxLayout()
        grid_layout.addLayout(timeout_layout, 3, 1)   
        timeout_layout.addWidget(self.set_timeout_sb)
        timeout_layout.addWidget(self.timeout_indicator)
        
        output_layout = QtWidgets.QVBoxLayout()
        grid_layout.addLayout(output_layout, 4, 0)
        
        output_layout.addWidget(self.out1_widget)
        output_layout.addWidget(self.out2_widget)
        
        heater_layout = QtWidgets.QHBoxLayout()
        grid_layout.addLayout(heater_layout, 4, 1)

        heater_indicator_layout = QtWidgets.QVBoxLayout()
        heater_layout.addLayout(heater_indicator_layout)
        
        heater_indicator_layout.addWidget(self.out1_indicator)
        heater_indicator_layout.addWidget(self.out2_indicator)
        
        heater_layout.addWidget(self.all_off_btn)
        
        for i in range(grid_layout.columnCount()):
            grid_layout.setColumnStretch(i, 1)
            
        not_conn_layout = QtWidgets.QVBoxLayout()
        self.not_conn_widget.setLayout(not_conn_layout)
        
        not_conn_layout.addWidget(self.not_conn_l)
        not_conn_layout.addWidget(self.retry_btn)

    def open_widget(self):
        self.show()
    
    def connect_to_lakeshore(self):
        try:
            # self.device = Model336(ip_address=self.IP_ADDRESS)
            # self.device.logger.setLevel(WARNING)
            self.device = DummyLakeshore336()
        except TimeoutError as e:
            print("!LakeShore336:", e)
            return
        
        if self.device:
            self.stack.setCurrentWidget(self.control_widget)
            self.update_gui()
            self.refresh_tick()
            self.refresh_timer.start(1000)
        
    def lost_connection(self):
        self.device = None
        self.ready_to_meas = False
        self.curr_temp_indicator.set_off()
        self.refresh_timer.stop()
        self.stop_timeout_timer()
        self.stop_delay_timer()
        self.stack.setCurrentWidget(self.not_conn_widget)       

    def remote_change(self):
        self.do_update = False

    def update_gui(self):
        if not self.do_update:
            return

        try:
            setpoint = self.device.get_control_setpoint(1)
            out1_range = self.device.get_heater_range(1)
            out2_range = self.device.get_heater_range(2)
        except ConnectionResetError:
            self.lost_connection()
            return


        self.set_temp_sb.setValue(setpoint)
        self.setpoint_value = setpoint

        
        self.out1_widget.heater_range_cb.setCurrentIndex(out1_range)
        if out1_range > 0:
            self.out1_indicator.set_on()
            self.out1_on = True
        else:
            self.out1_on = False
            self.out1_indicator.set_off()

        
        self.out2_widget.heater_range_cb.setCurrentIndex(out2_range)
        if out2_range > 0:
            self.out2_indicator.set_on()
            self.out2_on = True
        else:
            self.out2_indicator.set_off()
            self.out2_on = False

        if not (self.out1_on or self.out2_on):
            self.timeout_timer.stop()
            self.stop_delay_timer()
            self.ready_to_meas = False

    def setpoint_changed(self):
        self.do_update = True
        value = float(self.set_temp_sb.value())
        self.setpoint_value = value

        try:
            curr_temp = self.device.get_all_kelvin_reading()[0]                
            self.device.set_control_setpoint(1, value)
        except ConnectionResetError:
            self.lost_connection()
            return
        
        # if abs(curr_temp - value) > 0.01:
        #     self.ready_to_meas = False
        #     self.curr_temp_indicator.set_off()
        #     self.stop_delay_timer()

    def refresh_tick(self):

        self.update_gui()
        
        try:
            self.kelvin_readings = self.device.get_all_kelvin_reading()
        except ConnectionResetError:
            self.lost_connection()
            return

        self.curr_temp_le.setText(f"{self.kelvin_readings[0]:.3f}")

        if (self.out1_on or self.out2_on):
            if abs(self.kelvin_readings[0] - self.setpoint_value) < 0.01:
                if not self.ready_to_meas and not(self.delay_timer.isActive()):
                    self.setpoint_reached()
            else:
                self.ready_to_meas = False
                self.curr_temp_indicator.set_off()
                self.stop_delay_timer()
                

        if (self.out1_on or self.out2_on) and not(self.delay_timer.isActive()) and not(self.ready_to_meas):
            temp_diff = abs(self.kelvin_readings[0] - self.setpoint_value)
            if abs(temp_diff - self.prev_temp_diff) < 1:
                if not self.timeout_timer.isActive():
                    print("Starting timeout timer")
                    self.start_timeout_timer()
            else:
                print("Stopping timeout timer")
                self.stop_timeout_timer()

            self.prev_temp_diff = temp_diff

    def setpoint_reached(self):
            print("Setpoint reached")
            print("\tStarting delay timer")
            print("\tStopping timeout timer")
            self.stop_timeout_timer()
            self.start_delay_timer()
            
            self.curr_temp_indicator.set_warning()

    def set_ready_to_meas(self):
        print("Ready to measure")
        self.ready_to_meas_signal.emit()
        self.ready_to_meas = True
        
        self.stop_delay_timer()
        self.curr_temp_indicator.set_on()

    def timeout_reached(self):
        print("Timeout reached!!!")
        self.all_off()
        self.ready_to_meas = False

    def all_off(self):
        try:
            self.device.all_heaters_off()
        except ConnectionResetError:
            self.lost_connection()
            return
        
        self.out1_on = False
        self.out2_on = False

        self.stop_delay_timer()
        self.stop_timeout_timer()

        self.ready_to_meas = False
        self.curr_temp_indicator.set_off()

        self.out1_indicator.set_off()
        self.out2_indicator.set_off()
        self.out1_widget.heater_range_cb.setCurrentIndex(0)
        self.out2_widget.heater_range_cb.setCurrentIndex(0)


    def set_out1(self):
        self.do_update = False
        val = self.out1_widget.heater_range_cb.currentText()
        if val == "OFF":
            try:
                self.device.set_heater_range(1, 0)
            except ConnectionResetError:
                self.lost_connection()
                return

            self.out1_indicator.set_off()
            self.out1_on = False

            if not self.out2_on:
                self.stop_timeout_timer()
                self.stop_delay_timer()
                self.ready_to_meas = False
                self.curr_temp_indicator.set_off()

            return
        
        self.out1_on = True
        self.out1_indicator.setStyleSheet("border: 3px solid gray; background-color: green;")
        
        try:
            self.device.set_heater_range(1, self.HEATER_RANGES.index(val))
        except ConnectionResetError:
            self.lost_connection()
            return

    def set_out2(self):
        self.do_update = False
        val = self.out2_widget.heater_range_cb.currentText()
        if val == "OFF":
            
            try:
                self.device.set_heater_range(2, 0)
            except ConnectionResetError:
                self.lost_connection()
                return
            
            self.out2_indicator.setStyleSheet("border: 3px solid gray;")
            self.out2_on = False

            if not self.out1_on:
                self.stop_timeout_timer()
                self.stop_delay_timer()
                self.ready_to_meas = False
                self.curr_temp_indicator.set_off()

            return
        
        self.out2_on = True
        self.out2_indicator.setStyleSheet("border: 3px solid gray; background-color: green;")
        
        try:
            self.device.set_heater_range(2, self.HEATER_RANGES.index(val))
        except ConnectionResetError:
            self.lost_connection()
            return
        
    def start_delay_timer(self):
        delay = 60 * 1000 * int(self.set_delay_sb.value())
        self.delay_timer.start(delay)
        self.delay_indicator.start_blinking("yellow")
        
    def stop_delay_timer(self):
        self.delay_timer.stop()
        self.delay_indicator.stop_blinking()
        
    def start_timeout_timer(self):
        timeout = 60 * 1000 * int(self.set_timeout_sb.value())
        self.timeout_timer.start(timeout)
        self.timeout_indicator.start_blinking("red")
        
    def stop_timeout_timer(self):
        self.timeout_timer.stop()
        self.timeout_indicator.stop_blinking()

        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Lakeshore336Control()
    w.show()
    app.exec()
