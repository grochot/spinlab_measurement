from pymeasure.display.Qt import QtWidgets, QtCore, QtGui
import sys
import os
from lakeshore import Model336
import json
from threading import Lock
from abc import ABC, abstractmethod


def format_time(time):
    minutes = time // 60
    seconds = time % 60
    return f"{minutes:02d}:{seconds:02d}"


class DummyModel336:
    def __init__(self):
        self.setpoint = 0.0
        self.heater = {1: 0, 2: 0}
        self.kelwin_reading = 0

    def get_control_setpoint(self, channel):
        return self.setpoint

    def get_heater_range(self, channel):
        return self.heater[channel]

    def get_all_kelvin_reading(self):
        tmp = self.kelwin_reading
        if self.kelwin_reading < self.setpoint:
            self.kelwin_reading += 0.1
        return [tmp]

    def set_control_setpoint(self, channel, value):
        self.setpoint = value
        self.kelwin_reading = value - 2
        print(f"Set control setpoint {channel} to {value}")

    def all_heaters_off(self):
        for channel in self.heater:
            self.heater[channel] = 0
        print("All heaters off")

    def set_heater_range(self, channel, value):
        self.heater[channel] = value
        print(f"Set heater range {channel} to {value}")

    def get_heater_output(self, channel):
        return 0

    def disconnect_tcp(self):
        pass


class State(ABC):
    @abstractmethod
    def on_entry(self, context: "Lakeshore336Control"):
        pass

    @abstractmethod
    def on_tick(self, context: "Lakeshore336Control"):
        pass

    @abstractmethod
    def on_exit(self, context: "Lakeshore336Control"):
        pass


class NotConnectedState(State):
    def on_entry(self, context):
        context.set_ready(False)
        if context.tick_timer.isActive():
            context.tick_timer.stop()

        context.stacked_widget.setCurrentIndex(1)
        context.settings_win.connect_btn.setEnabled(True)
        context.settings_win.disconnect_btn.setEnabled(False)

    def on_tick(self, context):
        pass

    def on_exit(self, context):
        pass


class ConnectedState(State):
    def on_entry(self, context):
        context.query_device()
        context.tick_timer.start(context.settings_win.refresh_interval)

        context.settings_win.connect_btn.setEnabled(False)
        context.settings_win.disconnect_btn.setEnabled(True)
        context.stacked_widget.setCurrentIndex(0)

    def on_tick(self, context):
        if any([heater.is_on for heater in context.outputs]):
            context.change_state(context.heaterOnState)

    def on_exit(self, context):
        pass


class HeaterOnState(State):
    def on_entry(self, context):
        pass

    def on_tick(self, context):
        if not any([heater.is_on for heater in context.outputs]):
            context.change_state(context.connectedState)

        if context.is_setpoint_reached():
            context.change_state(context.delayState)
            return

        context.time_delta -= context.settings_win.refresh_interval
        if context.time_delta > 0:
            return

        if context.is_error_not_changing():
            context.change_state(context.timeoutState)
            return

    def on_exit(self, context):
        pass


class DelayState(State):
    def on_entry(self, context):
        self.delay_duration = float(context.settings_win.delay_duration)
        self.delay_duration = int(self.delay_duration * 60 * 1000)
        context.single_shot_timer.timeout.connect(
            lambda: context.change_state(context.readyState)
        )
        context.single_shot_timer.start(self.delay_duration)
        context.delay_timer_label.setText(
            f"DELAY: {format_time(self.delay_duration // 1000)}"
        )
        context.delay_timer_indicator.start_blink("green", 500)

    def on_tick(self, context):
        self.delay_duration -= context.settings_win.refresh_interval
        context.delay_timer_label.setText(
            f"DELAY: {format_time(self.delay_duration // 1000)}"
        )

        if not any([heater.is_on for heater in context.outputs]):
            context.change_state(context.connectedState)
            return

        if not context.is_setpoint_reached():
            context.change_state(context.heaterOnState)
            return

    def on_exit(self, context):
        context.single_shot_timer.stop()
        context.single_shot_timer.disconnect()
        context.delay_timer_indicator.stop_blink()
        context.delay_timer_label.setText("Delay")


class TimeoutState(State):
    def on_entry(self, context):
        self.timeout_duration = float(context.settings_win.timeout_duration)
        self.timeout_duration = int(self.timeout_duration * 60 * 1000)
        context.single_shot_timer.timeout.connect(
            lambda: context.change_state(context.timeoutErrorState)
        )

        context.single_shot_timer.start(self.timeout_duration)
        context.timeout_timer_indicator.start_blink("red", 500)
        context.timeout_timer_label.setText(
            f"TIMEOUT: {format_time(self.timeout_duration // 1000)}"
        )

    def on_tick(self, context):
        self.timeout_duration -= context.settings_win.refresh_interval
        context.timeout_timer_label.setText(
            f"TIMEOUT: {format_time(self.timeout_duration // 1000)}"
        )

        if not any([heater.is_on for heater in context.outputs]):
            context.change_state(context.connectedState)
            return

        if context.is_setpoint_reached():
            context.change_state(context.delayState)
            return

        context.time_delta -= context.settings_win.refresh_interval
        if context.time_delta > 0:
            return

        if not context.is_error_not_changing():
            context.change_state(context.heaterOnState)
            return

    def on_exit(self, context):
        context.single_shot_timer.stop()
        context.single_shot_timer.disconnect()
        context.timeout_timer_indicator.stop_blink()
        context.timeout_timer_label.setText("Timeout")


class ReadyState(State):
    def on_entry(self, context):
        context.set_ready(True)
        context.ready_label.setText("READY")

    def on_tick(self, context):
        if not any([heater.is_on for heater in context.outputs]):
            context.change_state(context.connectedState)

    def on_exit(self, context):
        context.set_ready(False)
        context.ready_label.setText("Ready")


class TimeoutErrorState(State):
    def on_entry(self, context):
        context.timeout_timer_indicator.set_error()

    def on_tick(self, context):
        if not any([heater.is_on for heater in context.outputs]):
            context.change_state(context.connectedState)

    def on_exit(self, context):
        context.timeout_timer_indicator.set_off()


class Lakeshore336Control(QtWidgets.QWidget):
    object_name = "lakeshore336_control"
    sigReady = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(Lakeshore336Control, self).__init__(parent)
        self.name = "Lakeshore 336"
        self.icon_path = os.path.join("modules", "icons", "LakeShore336.ico")

        self.lock = Lock()

        self.settings_win = SettingsWindow(self.lock)
        self.settings_win.load_settings()
        self.settings_win.connect_btn.clicked.connect(self.on_connect_btn_clicked)
        self.settings_win.disconnect_btn.clicked.connect(self.on_disconnect_btn_clicked)
        self.settings_win.refresh_int_btn.clicked.connect(
            lambda: self.on_timer_btn_clicked("refresh")
        )
        self.settings_win.delay_btn.clicked.connect(
            lambda: self.on_timer_btn_clicked("delay")
        )
        self.settings_win.timeout_cond_btn.clicked.connect(
            lambda: self.on_timer_btn_clicked("timeout")
        )

        self.notConnectedState = NotConnectedState()
        self.connectedState = ConnectedState()
        self.heaterOnState = HeaterOnState()
        self.delayState = DelayState()
        self.timeoutState = TimeoutState()
        self.readyState = ReadyState()
        self.timeoutErrorState = TimeoutErrorState()

        self.ready: bool = False
        self.current_state: State = self.notConnectedState
        self.device: Model336 = None

        self.setpoint = 0.0
        self.is_setpoint_set: bool = True
        self.prev_temp: float = 0.0
        self.time_delta: int = self.settings_win.dt * 1000

        self.tick_timer = QtCore.QTimer()
        self.tick_timer.timeout.connect(self.on_tick)

        self.single_shot_timer = QtCore.QTimer()
        self.single_shot_timer.setSingleShot(True)

        self._setup_ui()
        self._layout()
        self.all_off_btn.setFocus()
        self.connect_with_device()

    def _setup_ui(self):
        self.setWindowTitle(self.name)
        self.setWindowIcon(QtGui.QIcon(self.icon_path))

        self.setStyleSheet("font-size: 12pt;")

        self.stacked_widget = QtWidgets.QStackedWidget()

        # CONTROL WIDGET
        self.control_widget = QtWidgets.QWidget()
        self.stacked_widget.addWidget(self.control_widget)

        self.settings_btn = QtWidgets.QPushButton("Settings")
        self.settings_btn.clicked.connect(self.on_settings_btn_clicked)

        self.setpoint_l = QtWidgets.QLabel("Setpoint [K]")
        self.setpoint_l.setAlignment(QtCore.Qt.AlignCenter)
        self.setpoint_le = QtWidgets.QLineEdit("-")
        self.setpoint_le.setAlignment(QtCore.Qt.AlignCenter)
        validator = QtGui.QDoubleValidator(bottom=0, decimals=3)
        validator.setLocale(QtCore.QLocale(QtCore.QLocale.English))
        self.setpoint_le.setValidator(validator)
        self.setpoint_le.textChanged.connect(self.on_setpoint_changed)
        self.setpoint_le.returnPressed.connect(self.on_setpoint_set_clicked)

        self.setpoint_btn = QtWidgets.QPushButton("SET")
        self.setpoint_btn.setFixedWidth(45)
        self.setpoint_btn.clicked.connect(self.on_setpoint_set_clicked)

        self.curr_temp_l = QtWidgets.QLabel("Temperature [K]")
        self.curr_temp_l.setAlignment(QtCore.Qt.AlignCenter)
        self.curr_temp_le = QtWidgets.QLineEdit("-")
        self.curr_temp_le.setAlignment(QtCore.Qt.AlignCenter)
        self.curr_temp_le.setReadOnly(True)

        self.outputs: list[HeaterWidget] = []

        self.output_1 = HeaterWidget("OUT 1")
        self.output_1.btn.clicked.connect(lambda: self.on_output_set_clicked(1))
        self.outputs.append(self.output_1)

        self.all_off_btn = QtWidgets.QPushButton("ALL OFF")
        self.all_off_btn.clicked.connect(self.on_all_off_btn_clicked)

        self.delay_timer_label = QtWidgets.QLabel("Delay")
        self.delay_timer_indicator = Indicator()

        self.timeout_timer_label = QtWidgets.QLabel("Timeout")
        self.timeout_timer_indicator = Indicator()

        self.ready_label = QtWidgets.QLabel("Ready")
        self.ready_indicator = Indicator()

        # NOT CONNECTED WIDGET
        self.not_connected_widget = QtWidgets.QWidget()
        self.stacked_widget.addWidget(self.not_connected_widget)

        self.not_connected_label = QtWidgets.QLabel("Not connected")
        self.not_connected_label.setAlignment(QtCore.Qt.AlignCenter)

        self.stacked_widget.setCurrentIndex(1)

    def _layout(self):
        layout = QtWidgets.QVBoxLayout()

        layout.addStretch()

        layout.addWidget(self.settings_btn)

        layout.addWidget(HorizontalDivider())
        layout.addWidget(self.stacked_widget)

        control_layout = QtWidgets.QVBoxLayout()

        row_0_layout = QtWidgets.QHBoxLayout()

        widget = QtWidgets.QWidget()
        grid_layout = QtWidgets.QGridLayout()
        grid_layout.addWidget(self.setpoint_l, 0, 0)
        grid_layout.addWidget(self.setpoint_le, 1, 0)
        grid_layout.addWidget(self.setpoint_btn, 1, 1)
        widget.setLayout(grid_layout)
        row_0_layout.addWidget(widget)

        widget = QtWidgets.QWidget()
        grid_layout = QtWidgets.QGridLayout()
        grid_layout.addWidget(self.curr_temp_l, 0, 0)
        grid_layout.addWidget(self.curr_temp_le, 1, 0)
        widget.setLayout(grid_layout)
        row_0_layout.addWidget(widget)

        control_layout.addLayout(row_0_layout)

        control_layout.addWidget(HorizontalDivider())

        control_layout.addWidget(self.output_1)

        control_layout.addWidget(self.all_off_btn)

        control_layout.addWidget(HorizontalDivider())

        row_2_layout = QtWidgets.QHBoxLayout()
        row_2_layout.addStretch()
        row_2_layout.addWidget(self.delay_timer_label)
        row_2_layout.addWidget(self.delay_timer_indicator)
        row_2_layout.addStretch()
        row_2_layout.addWidget(VerticalDivider())
        row_2_layout.addStretch()
        row_2_layout.addWidget(self.timeout_timer_label)
        row_2_layout.addWidget(self.timeout_timer_indicator)
        row_2_layout.addStretch()
        row_2_layout.addWidget(VerticalDivider())
        row_2_layout.addStretch()
        row_2_layout.addWidget(self.ready_label)
        row_2_layout.addWidget(self.ready_indicator)
        row_2_layout.addStretch()

        control_layout.addLayout(row_2_layout)

        self.control_widget.setLayout(control_layout)

        # NOT CONNECTED LAYOUT
        not_connected_layout = QtWidgets.QVBoxLayout()
        not_connected_layout.addWidget(self.not_connected_label)
        self.not_connected_widget.setLayout(not_connected_layout)

        layout.addStretch()
        self.setLayout(layout)

    @QtCore.pyqtSlot()
    def change_state(self, state: State):
        with self.lock:
            self.current_state.on_exit(self)
            self.current_state = state
            self.current_state.on_entry(self)

    def on_connect_btn_clicked(self):
        self.connect_with_device()

    def on_disconnect_btn_clicked(self):
        self.disconnect_from_device()

    def connect_with_device(self):
        try:
            if self.settings_win.ip_le.text() == "":
                raise ValueError("IP address is empty")
            # self.device = Model336(ip_address=self.settings_win.ip_le.text())
            # self.device.logger.setLevel("WARNING")
            self.device = DummyModel336()
            self.change_state(self.connectedState)
        except Exception as e:
            self.change_state(self.notConnectedState)
            print(e)
            return

    def disconnect_from_device(self):
        if self.device:
            self.device.disconnect_tcp()
            self.device = None
            self.change_state(self.notConnectedState)

    def on_timer_btn_clicked(self, timer: str):
        match timer:
            case "refresh":
                if self.tick_timer.isActive():
                    self.tick_timer.stop()
                self.tick_timer.start(self.settings_win.refresh_interval)
            case "delay":
                if self.current_state == self.delayState:
                    dialog = RestartTimerDialog()
                    if dialog.exec():
                        self.change_state(self.delayState)

            case "timeout":
                if self.current_state == self.timeoutState:
                    dialog = RestartTimerDialog()
                    if dialog.exec():
                        self.change_state(self.timeoutState)

    def set_ready(self, ready: bool):
        self.ready = ready
        if ready:
            self.sigReady.emit()
            self.ready_indicator.set_on()
        else:
            self.ready_indicator.set_off()

    @QtCore.pyqtSlot()
    def on_tick(self):
        self.query_device()
        self.current_state.on_tick(self)

    def query_device(self):
        try:
            setpoint = self.device.get_control_setpoint(1)
            self.setpoint = setpoint
            if self.is_setpoint_set:
                self.setpoint_le.blockSignals(True)
                self.setpoint_le.setText(f"{setpoint:.3f}")
                self.setpoint_le.blockSignals(False)

            curr_temp = self.device.get_all_kelvin_reading()
            self.curr_temp_le.setText(f"{curr_temp[0]:.3f}")

            for i in range(len(self.outputs)):
                heater_range = self.device.get_heater_range(i + 1)

                if self.outputs[i].is_heater_set:
                    self.outputs[i]._set_range(heater_range)

                heater_output = self.device.get_heater_output(i + 1)
                self.outputs[i].percent_le.setText(f"{heater_output:.2f}%")
        except Exception as e:
            print(e)
            self.change_state(self.notConnectedState)

        if heater_range == 0:
            self.outputs[0].indicator.set_off()
        else:
            self.outputs[0].indicator.set_on()

    def is_setpoint_reached(self):
        with self.lock:
            setpoint = self.setpoint
        curr_temp = float(self.curr_temp_le.text())

        match self.settings_win.ready_condition:
            case "absolute error":
                error = abs(setpoint - curr_temp)
            case "relative error":
                error = abs(setpoint - curr_temp) / setpoint * 100

        error_threshold = self.settings_win.error_threshold

        if error < error_threshold:
            return True
        else:
            return False

    def is_error_not_changing(self):
        self.time_delta = self.settings_win.dt * 1000

        curr_temp = float(self.curr_temp_le.text())

        tmp = self.prev_temp
        self.prev_temp = float(self.curr_temp_le.text())

        if abs(curr_temp - tmp) < self.settings_win.dT:
            return True
        else:
            return False

    def on_settings_btn_clicked(self):
        self.settings_win.exec()

    def on_setpoint_changed(self, text):
        self.is_setpoint_set = False
        if text == "":
            self.setpoint_btn.setStyleSheet("color: RED;")
            return
        if float(text) != self.setpoint:
            self.setpoint_btn.setStyleSheet("color: RED;")
        else:
            self.setpoint_btn.setStyleSheet("")

    def on_setpoint_set_clicked(self):
        if self.current_state in [self.delayState, self.readyState, self.timeoutState]:
            self.change_state(self.connectedState)
        with self.lock:
            self.setpoint_btn.setFocus()
            self.is_setpoint_set = True
            self.setpoint_btn.setStyleSheet("")
            setpoint = (
                float(self.setpoint_le.text())
                if self.setpoint_le.text() != ""
                else self.setpoint
            )
            self.setpoint = setpoint
            try:
                self.device.set_control_setpoint(1, self.setpoint)
            except Exception as e:
                print(e)
                self.change_state(self.notConnectedState)

    def on_output_set_clicked(self, output: int):
        with self.lock:
            heater_range = self.outputs[output - 1].range_cb.currentIndex()
            self.outputs[output - 1]._set_range(heater_range)
            try:
                self.device.set_heater_range(output, heater_range)
            except Exception as e:
                print(e)
                self.change_state(self.notConnectedState)

    def on_all_off_btn_clicked(self):
        with self.lock:
            try:
                self.device.all_heaters_off()
                for output in self.outputs:
                    output._set_range(0)
            except Exception as e:
                print(e)
                self.change_state(self.notConnectedState)

    def closeEvent(self, event):
        if self.tick_timer.isActive():
            self.tick_timer.stop()
        if self.single_shot_timer.isActive():
            self.single_shot_timer.stop()
        self.disconnect_from_device()

        self.settings_win.close()
        event.accept()


class HeaterWidget(QtWidgets.QWidget):
    def __init__(self, label_text, parent=None):
        super(HeaterWidget, self).__init__(parent)
        self._label_text = label_text

        self.HEATER_RANGE = {0: "OFF", 1: "LOW", 2: "MID", 3: "HIGH"}
        self.prev_heater_range: int = 0
        self.is_heater_set: bool = True
        self.is_on: bool = False

        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.label = QtWidgets.QLabel(self._label_text)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        self.percent_le = QtWidgets.QLineEdit(f"0.00%")
        self.percent_le.setAlignment(QtCore.Qt.AlignCenter)
        self.percent_le.setReadOnly(True)
        self.percent_le.setFixedWidth(100)

        self.range_cb = QtWidgets.QComboBox()
        self.range_cb.addItems(list(self.HEATER_RANGE.values()))
        self.range_cb.currentIndexChanged.connect(self.on_range_cb_changed)

        self.btn = QtWidgets.QPushButton("SET")
        self.btn.setFixedWidth(45)
        self.btn.clicked.connect(self.on_btn_clicked)

        self.indicator = Indicator()

    def _layout(self):
        layout = QtWidgets.QHBoxLayout()
        layout.addStretch()
        layout.addWidget(self.label)
        layout.addWidget(self.percent_le)
        layout.addWidget(self.range_cb)
        layout.addWidget(self.btn)
        layout.addWidget(self.indicator)
        layout.addStretch()
        self.setLayout(layout)

    def _set_range(self, range: int):
        if range == 0:
            self.indicator.set_off()
            self.is_on = False
        else:
            self.indicator.set_on()
            self.is_on = True
        self.range_cb.blockSignals(True)
        self.range_cb.setCurrentIndex(range)
        self.range_cb.blockSignals(False)

    def on_range_cb_changed(self, index):
        self.is_heater_set = False
        if index != self.prev_heater_range:
            self.btn.setStyleSheet("color: RED;")
        else:
            self.btn.setStyleSheet("")

    def on_btn_clicked(self):
        self.prev_heater_range = self.range_cb.currentIndex()
        self.is_heater_set = True
        self.btn.setStyleSheet("")


class Indicator(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(Indicator, self).__init__(parent)
        self.setFixedSize(25, 25)
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setStyleSheet(
            "border-radius: 4px; border: 2px solid black; background-color: white;"
        )

        self.state = 0
        self.timer = QtCore.QTimer()

    def set_color(self, color):
        self.setStyleSheet(
            f"background-color: {color}; border-radius: 4px; border: 2px solid black;"
        )
        self.state = 1

    def set_on(self):
        self.set_color("green")
        self.state = 1

    def set_off(self):
        self.setStyleSheet(
            "border-radius: 4px; border: 2px solid black; background-color: white;"
        )
        self.state = 0

    def set_warning(self):
        self.set_color("yellow")
        self.state = 1

    def set_error(self):
        self.set_color("red")
        self.state = 1

    def toggle(self, color):
        if self.state == 0:
            self.set_color(color)
        else:
            self.set_off()

    def start_blink(self, color: str, interval: int):
        if self.timer.isActive():
            self.timer.stop()
            self.timer.disconnect()

        self.set_color(color)
        self.timer.timeout.connect(lambda: self.toggle(color))
        self.timer.start(interval)

    def stop_blink(self):
        self.timer.stop()
        self.timer.disconnect()
        self.set_off()


class SettingsWindow(QtWidgets.QDialog):
    def __init__(self, lock: Lock, parent=None):
        super(SettingsWindow, self).__init__(parent)
        self.save_path = os.path.join("LakeShore336_parameters.json")

        self.lock = lock

        self.refresh_interval: int = 500
        self.delay_duration: float = 10
        self.timeout_duration: float = 30

        self.ready_condition: str = "absolute error"
        self.error_threshold: float = "1"

        self.dT: float = 1
        self.dt: float = 5 * 60

        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.setWindowTitle("LakeShore 336 - Settings")
        icon_path = os.path.join("modules", "icons", "LakeShore336.ico")
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.setStyleSheet("font-size: 12pt;")

        self.ip_le = QtWidgets.QLineEdit()
        self.ip_le.setAlignment(QtCore.Qt.AlignCenter)
        ipRegex = QtCore.QRegExp(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
        ipValidator = QtGui.QRegExpValidator(ipRegex)
        self.ip_le.setValidator(ipValidator)

        self.connect_btn = QtWidgets.QPushButton("Connect")
        self.disconnect_btn = QtWidgets.QPushButton("Disconnect")
        self.disconnect_btn.setEnabled(False)

        self.refresh_int_le = QtWidgets.QLineEdit(str(self.refresh_interval))
        self.refresh_int_le.setAlignment(QtCore.Qt.AlignCenter)
        validator = QtGui.QIntValidator(bottom=100)
        validator.setLocale(QtCore.QLocale(QtCore.QLocale.English))
        self.refresh_int_le.setValidator(validator)
        self.refresh_int_le.textChanged.connect(
            lambda text: self.time_le_changed(
                text, self.refresh_interval, self.refresh_int_btn
            )
        )
        self.refresh_int_le.returnPressed.connect(self.on_refresh_btn_clicked)

        self.refresh_int_btn = QtWidgets.QPushButton("SET")
        self.refresh_int_btn.setFixedWidth(45)
        self.refresh_int_btn.clicked.connect(self.on_refresh_btn_clicked)

        self.delay_le = QtWidgets.QLineEdit(str(self.delay_duration))
        self.delay_le.setAlignment(QtCore.Qt.AlignCenter)
        validator = QtGui.QDoubleValidator(bottom=0)
        validator.setLocale(QtCore.QLocale(QtCore.QLocale.English))
        self.delay_le.setValidator(validator)
        self.delay_le.textChanged.connect(
            lambda text: self.time_le_changed(text, self.delay_duration, self.delay_btn)
        )
        self.delay_le.returnPressed.connect(self.on_delay_btn_clicked)

        self.delay_btn = QtWidgets.QPushButton("SET")
        self.delay_btn.setFixedWidth(45)
        self.delay_btn.clicked.connect(self.on_delay_btn_clicked)

        self.timeout_le = QtWidgets.QLineEdit(str(self.timeout_duration))
        self.timeout_le.setAlignment(QtCore.Qt.AlignCenter)
        validator = QtGui.QDoubleValidator(bottom=0)
        validator.setLocale(QtCore.QLocale(QtCore.QLocale.English))
        self.timeout_le.setValidator(validator)
        self.timeout_le.textChanged.connect(
            lambda text: self.time_le_changed(
                text, self.timeout_duration, self.timeout_cond_btn
            )
        )
        self.timeout_le.returnPressed.connect(self.on_timeout_btn_clicked)

        self.timeout_btn = QtWidgets.QPushButton("SET")
        self.timeout_btn.setFixedWidth(45)
        self.timeout_btn.clicked.connect(self.on_timeout_btn_clicked)

        self.ready_cond_l = QtWidgets.QLabel("Ready condition:")
        self.ready_condition_cb = QtWidgets.QComboBox()
        self.ready_condition_cb.addItems(["absolute error", "relative error"])
        self.ready_condition_cb.currentIndexChanged.connect(
            self.on_ready_condition_changed
        )
        self.value_l = QtWidgets.QLabel("[K] <")
        self.value_le = QtWidgets.QLineEdit("0.1")
        self.value_le.setAlignment(QtCore.Qt.AlignCenter)
        validator = QtGui.QDoubleValidator(bottom=0.001)
        validator.setLocale(QtCore.QLocale(QtCore.QLocale.English))
        self.value_le.setValidator(validator)
        self.value_le.textChanged.connect(self.on_value_changed)
        self.value_le.returnPressed.connect(self.on_value_btn_clicked)

        self.value_btn = QtWidgets.QPushButton("SET")
        self.value_btn.setFixedWidth(45)
        self.value_btn.clicked.connect(self.on_value_btn_clicked)

        self.timeout_cond_l = QtWidgets.QLabel("Timeout condition:")
        self.timeout_cond_dT_l = QtWidgets.QLabel("\u0394T <")
        self.timeout_cond_dT_le = QtWidgets.QLineEdit(str(self.dT))
        self.timeout_cond_dT_le.setAlignment(QtCore.Qt.AlignCenter)
        validator = QtGui.QDoubleValidator(bottom=0.001)
        validator.setLocale(QtCore.QLocale(QtCore.QLocale.English))
        self.timeout_cond_dT_le.setValidator(validator)
        self.timeout_cond_dT_le.textChanged.connect(self.on_timeout_cond_changed)
        self.timeout_cond_dT_le.returnPressed.connect(self.on_timeout_btn_clicked)
        # self.timeout_cond_dT_le.setFixedWidth(130)

        self.timeout_cond_dt_l = QtWidgets.QLabel("[K] /")
        self.timeout_cond_dt_le = QtWidgets.QLineEdit(str(self.dt))
        self.timeout_cond_dt_le.setAlignment(QtCore.Qt.AlignCenter)
        validator = QtGui.QDoubleValidator(bottom=0.001)
        validator.setLocale(QtCore.QLocale(QtCore.QLocale.English))
        self.timeout_cond_dt_le.setValidator(validator)
        self.timeout_cond_dt_le.textChanged.connect(self.on_timeout_cond_changed)
        self.timeout_cond_dt_le.returnPressed.connect(self.on_timeout_btn_clicked)
        # self.timeout_cond_dt_le.setFixedWidth(130)

        self.timeout_cond_btn = QtWidgets.QPushButton("SET")
        self.timeout_cond_btn.setFixedWidth(45)
        self.timeout_cond_btn.clicked.connect(self.on_timeout_btn_clicked)

        self.timeout_cond_unit_l = QtWidgets.QLabel("[s]")

    def _layout(self):
        layout = QtWidgets.QFormLayout()
        layout.addRow("IP address", self.ip_le)
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.connect_btn)
        btn_layout.addWidget(self.disconnect_btn)
        layout.addRow(btn_layout)

        layout.addRow(HorizontalDivider())

        refresh_layout = QtWidgets.QHBoxLayout()
        refresh_layout.addWidget(self.refresh_int_le)
        refresh_layout.addWidget(self.refresh_int_btn)
        layout.addRow("Refresh [ms]", refresh_layout)

        delay_layout = QtWidgets.QHBoxLayout()
        delay_layout.addWidget(self.delay_le)
        delay_layout.addWidget(self.delay_btn)

        layout.addRow("Delay [min]", delay_layout)

        timeout_layout = QtWidgets.QHBoxLayout()
        timeout_layout.addWidget(self.timeout_le)
        timeout_layout.addWidget(self.timeout_btn)
        layout.addRow("Timeout [min]", timeout_layout)

        layout.addRow(HorizontalDivider())
        layout.addRow(self.ready_cond_l)
        ready_cond_layout = QtWidgets.QHBoxLayout()
        ready_cond_layout.addWidget(self.ready_condition_cb, stretch=1)
        ready_cond_layout.addWidget(self.value_l)
        ready_cond_layout.addWidget(self.value_le, stretch=1)
        ready_cond_layout.addWidget(self.value_btn)
        layout.addRow(ready_cond_layout)

        layout.addRow(self.timeout_cond_l)
        timeout_cond_layout = QtWidgets.QHBoxLayout()
        timeout_cond_layout.addWidget(self.timeout_cond_dT_l)
        timeout_cond_layout.addWidget(self.timeout_cond_dT_le, stretch=1)
        timeout_cond_layout.addWidget(self.timeout_cond_dt_l)
        timeout_cond_layout.addWidget(self.timeout_cond_dt_le, stretch=1)
        timeout_cond_layout.addWidget(self.timeout_cond_unit_l)
        timeout_cond_layout.addWidget(self.timeout_cond_btn)
        layout.addRow(timeout_cond_layout)

        self.setLayout(layout)

    def on_ready_condition_changed(self, index):
        if index == 0 or self.value_le.text() == "":
            self.value_l.setText("[K] <")
        else:
            self.value_l.setText("[%] <")

        if (
            self.ready_condition_cb.currentText() != self.ready_condition
            or float(self.value_le.text()) != self.error_threshold
        ):
            self.value_btn.setStyleSheet("color: RED;")
        else:
            self.value_btn.setStyleSheet("")

    def time_le_changed(self, text, param, btn):
        if text == "":
            btn.setStyleSheet("color: RED;")
            return

        if float(text) != float(param):
            btn.setStyleSheet("color: RED;")
        else:
            btn.setStyleSheet("")

    def on_refresh_btn_clicked(self):
        self.refresh_int_btn.setStyleSheet("")

        with self.lock:
            self.refresh_interval = (
                int(self.refresh_int_le.text())
                if self.refresh_int_le.text() != ""
                else self.refresh_interval
            )
            self.refresh_int_le.setText(str(self.refresh_interval))

    def on_delay_btn_clicked(self):
        self.delay_btn.setStyleSheet("")
        with self.lock:
            self.delay_duration = (
                float(self.delay_le.text())
                if self.delay_le.text() != ""
                else self.delay_duration
            )
            self.delay_le.setText(str(self.delay_duration))

    def on_timeout_btn_clicked(self):
        self.timeout_cond_btn.setStyleSheet("")
        with self.lock:
            self.timeout_duration = (
                float(self.timeout_le.text())
                if self.timeout_le.text() != ""
                else self.timeout_duration
            )
            self.timeout_le.setText(str(self.timeout_duration))

    def on_value_changed(self, text):
        if text == "":
            self.value_btn.setStyleSheet("color: RED;")
            return

        if (
            float(text) != float(self.error_threshold)
            or self.ready_condition != self.ready_condition_cb.currentText()
        ):
            self.value_btn.setStyleSheet("color: RED;")
        else:
            self.value_btn.setStyleSheet("")

    def on_value_btn_clicked(self):
        self.value_btn.setStyleSheet("")
        with self.lock:
            self.error_threshold = (
                float(self.value_le.text())
                if self.value_le.text() != ""
                else self.error_threshold
            )
            self.value_le.setText(str(self.error_threshold))
            self.ready_condition = self.ready_condition_cb.currentText()

    def on_timeout_cond_changed(self, text):
        if text == "":
            self.timeout_cond_btn.setStyleSheet("color: RED;")
            return

        if self.dT != float(self.timeout_cond_dT_le.text()) or self.dt != float(
            self.timeout_cond_dt_le.text()
        ):
            self.timeout_cond_btn.setStyleSheet("color: RED;")
        else:
            self.timeout_cond_btn.setStyleSheet("")

    def on_timeout_btn_clicked(self):
        self.timeout_cond_btn.setStyleSheet("")
        with self.lock:
            self.dT = (
                float(self.timeout_cond_dT_le.text())
                if self.timeout_cond_dT_le.text() != ""
                else self.dT
            )
            self.timeout_cond_dT_le.setText(str(self.dT))

            self.dt = (
                float(self.timeout_cond_dt_le.text())
                if self.timeout_cond_dt_le.text() != ""
                else self.dt
            )
            self.timeout_cond_dt_le.setText(str(self.dt))

    def save_settings(self):
        settings_dict = {
            "ip": self.ip_le.text(),
            "refresh": str(self.refresh_interval),
            "delay": str(self.delay_duration),
            "timeout": str(self.timeout_duration),
            "ready_condition": self.ready_condition,
            "error_threshold": str(self.error_threshold),
            "dT": str(self.dT),
            "dt": str(self.dt),
        }
        try:
            with open(self.save_path, "w") as f:
                json.dump(settings_dict, f)
        except Exception as e:
            print(e)

    def load_settings(self):
        try:
            with open(self.save_path, "r") as f:
                self.refresh_int_le.blockSignals(True)
                self.delay_le.blockSignals(True)
                self.timeout_le.blockSignals(True)
                self.ready_condition_cb.blockSignals(True)
                self.value_le.blockSignals(True)
                self.timeout_cond_dT_le.blockSignals(True)
                self.timeout_cond_dt_le.blockSignals(True)

                settings_dict = json.load(f)
                self.ip_le.setText(settings_dict["ip"])

                self.refresh_int_le.setText(settings_dict["refresh"])
                self.refresh_interval = int(settings_dict["refresh"])

                self.delay_le.setText(settings_dict["delay"])
                self.delay_duration = float(settings_dict["delay"])

                self.timeout_le.setText(settings_dict["timeout"])
                self.timeout_duration = float(settings_dict["timeout"])

                self.ready_condition_cb.setCurrentText(settings_dict["ready_condition"])
                self.ready_condition = settings_dict["ready_condition"]

                self.value_le.setText(settings_dict["error_threshold"])
                self.error_threshold = float(settings_dict["error_threshold"])

                self.timeout_cond_dT_le.setText(settings_dict["dT"])
                self.dT = float(settings_dict["dT"])

                self.timeout_cond_dt_le.setText(settings_dict["dt"])
                self.dt = float(settings_dict["dt"])

                self.refresh_int_le.blockSignals(False)
                self.delay_le.blockSignals(False)
                self.timeout_le.blockSignals(False)
                self.ready_condition_cb.blockSignals(False)
                self.value_le.blockSignals(False)
                self.timeout_cond_dT_le.blockSignals(False)
                self.timeout_cond_dt_le.blockSignals(False)
        except FileNotFoundError:
            pass
        except Exception as e:
            print(e)

    def closeEvent(self, event):
        self.save_settings()
        event.accept()


class RestartTimerDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(RestartTimerDialog, self).__init__(parent)
        self.setWindowTitle("Restart timer")
        self.setStyleSheet("font-size: 12pt;")

        self.label = QtWidgets.QLabel("Timer is already running! Restart?")
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel

        self.dialogBtns = QtWidgets.QDialogButtonBox(QBtn)
        self.dialogBtns.accepted.connect(self.accept)
        self.dialogBtns.rejected.connect(self.reject)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.dialogBtns)
        self.setLayout(layout)


class HorizontalDivider(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(HorizontalDivider, self).__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class VerticalDivider(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(VerticalDivider, self).__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.VLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Lakeshore336Control()
    window.show()
    app.exec()
