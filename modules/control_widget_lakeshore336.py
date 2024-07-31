from pymeasure.display.Qt import QtWidgets, QtCore, QtGui
import sys
import os
from lakeshore import Model336
import json


class DummyModel336:
    def __init__(self):
        self.setpoint = 0.0
        self.heater = {1: 1, 2: 0}

    def get_control_setpoint(self, channel):
        return self.setpoint

    def get_heater_range(self, channel):
        return self.heater[channel]

    def get_all_kelvin_reading(self):
        return [300.123]

    def set_control_setpoint(self, channel, value):
        self.setpoint = value
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


class State:
    def on_entry(self, context: "Lakeshore336Control"):
        pass

    def on_tick(self, context: "Lakeshore336Control"):
        pass

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


class ConnectedState(State):
    def on_entry(self, context):
        context.query_device()
        context.tick_timer.start(400)

        context.settings_win.connect_btn.setEnabled(False)
        context.settings_win.disconnect_btn.setEnabled(True)
        context.stacked_widget.setCurrentIndex(0)

    def on_tick(self, context):
        if any([heater.is_on for heater in context.outputs]):
            context.change_state(context.heaterOnState)


class HeaterOnState(State):
    def on_tick(self, context):
        if not any([heater.is_on for heater in context.outputs]):
            context.change_state(context.connectedState)

        if context.is_setpoint_reached():
            context.change_state(context.delayState)

        if context.is_error_not_changing():
            context.change_state(context.timeoutState)


class DelayState(State):
    def on_entry(self, context):
        delay_duration = float(context.settings_win.delay_le.text())
        delay_duration = int(delay_duration * 60 * 1000)
        context.single_shot_timer.timeout.connect(
            lambda: context.change_state(context.readyState)
        )
        context.single_shot_timer.start(delay_duration)
        context.delay_timer_indicator.start_blink("green", 500)

    def on_tick(self, context):
        if not any([heater.is_on for heater in context.outputs]):
            context.change_state(context.connectedState)

        if not context.is_setpoint_reached():
            context.change_state(context.heaterOnState)

    def on_exit(self, context):
        context.single_shot_timer.stop()
        context.single_shot_timer.disconnect()
        context.delay_timer_indicator.stop_blink()


class TimeoutState(State):
    def on_entry(self, context):
        timeout_duration = float(context.settings_win.timeout_le.text())
        timeout_duration = int(timeout_duration * 60 * 1000)
        context.single_shot_timer.timeout.connect(
            lambda: context.change_state(context.timeoutErrorState)
        )
        context.single_shot_timer.start(timeout_duration)
        context.timeout_timer_indicator.start_blink("red", 500)

    def on_tick(self, context):
        if not any([heater.is_on for heater in context.outputs]):
            context.change_state(context.connectedState)

        if not context.is_error_not_changing():
            context.change_state(context.heaterOnState)

    def on_exit(self, context):
        context.single_shot_timer.stop()
        context.single_shot_timer.disconnect()
        context.timeout_timer_indicator.stop_blink()


class ReadyState(State):
    def on_entry(self, context):
        context.set_ready(True)

    def on_tick(self, context):
        if not any([heater.is_on for heater in context.outputs]):
            context.change_state(context.connectedState)

    def on_exit(self, context):
        context.set_ready(False)


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
        
        self.settings_win = SettingsWindow()
        self.settings_win.load_settings()
        self.settings_win.connect_btn.clicked.connect(self.on_connect_btn_clicked)
        self.settings_win.disconnect_btn.clicked.connect(self.on_disconnect_btn_clicked)

        self.notConnectedState = NotConnectedState()
        self.connectedState = ConnectedState()
        self.heaterOnState = HeaterOnState()
        self.delayState = DelayState()
        self.timeoutState = TimeoutState()
        self.readyState = ReadyState()
        self.timeoutErrorState = TimeoutErrorState()

        self.ready: bool = False
        self.current_state = self.notConnectedState
        self.device: Model336 = None

        self.is_setpoint_set: bool = True
        self.prev_temp_diff: float = 0.0

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
        self.setpoint_btn.setFixedWidth(40)
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

        self.delay_timer_label = QtWidgets.QLabel("Delay Timer")
        self.delay_timer_indicator = Indicator()

        self.timeout_timer_label = QtWidgets.QLabel("Timeout Timer")
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

    def change_state(self, state: State):
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
            self.device = Model336(ip_address=self.settings_win.ip_le.text())
            self.device.logger.setLevel("WARNING")
            # self.device = DummyModel336()
            self.change_state(self.connectedState)
        except Exception as e:
            self.change_state(self.notConnectedState)
            print(e)
            return

    def disconnect_from_device(self):
        self.device.disconnect_tcp()
        self.device = None
        self.change_state(self.notConnectedState)

    def set_ready(self, ready: bool):
        self.ready = ready
        if ready:
            self.sigReady.emit()
            self.ready_indicator.set_on()
        else:
            self.ready_indicator.set_off()

    def on_tick(self):
        self.query_device()
        self.current_state.on_tick(self)

    def query_device(self):
        try:
            setpoint = self.device.get_control_setpoint(1)
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
        try:
            setpoint = self.device.get_control_setpoint(1)
            curr_temp = self.device.get_all_kelvin_reading()[0]
        except Exception as e:
            print(e)
            self.change_state(self.notConnectedState)

        match self.settings_win.ready_condition.currentText():
            case "absolute error":
                error = abs(setpoint - curr_temp)
            case "relative error":
                error = abs(setpoint - curr_temp) / setpoint * 100

        error_threshold = float(self.settings_win.value_le.text())

        if error < error_threshold:
            return True
        else:
            return False

    def is_error_not_changing(self):
        try:
            curr_temp = self.device.get_all_kelvin_reading()[0]
        except Exception as e:
            print(e)
            self.change_state(self.notConnectedState)

        error = abs(self.device.get_control_setpoint(1) - curr_temp)
        tmp = self.prev_temp_diff
        self.prev_temp_diff = error

        if abs(error - tmp) < 0.01:
            return True
        else:
            return False

    def on_settings_btn_clicked(self):
        self.settings_win.exec()

    def on_setpoint_changed(self, text):
        self.is_setpoint_set = False
        self.setpoint_btn.setStyleSheet("color: RED;")

    def on_setpoint_set_clicked(self):
        self.setpoint_btn.setFocus()
        self.is_setpoint_set = True
        self.setpoint_btn.setStyleSheet("")
        setpoint = self.setpoint_le.text()
        try:
            setpoint = float(setpoint.replace(",", "."))
            self.device.set_control_setpoint(1, setpoint)
        except Exception as e:
            print(e)
            self.change_state(self.notConnectedState)

    def on_output_set_clicked(self, output: int):
        heater_range = self.outputs[output - 1].range_cb.currentIndex()
        self.outputs[output - 1]._set_range(heater_range)
        try:
            self.device.set_heater_range(output, heater_range)
        except Exception as e:
            print(e)
            self.change_state(self.notConnectedState)

    def on_all_off_btn_clicked(self):
        try:
            self.device.all_heaters_off()
        except Exception as e:
            print(e)
            self.change_state(self.notConnectedState)


class HeaterWidget(QtWidgets.QWidget):
    def __init__(self, label_text, parent=None):
        super(HeaterWidget, self).__init__(parent)
        self._label_text = label_text

        self.HEATER_RANGE = {0: "OFF", 1: "LOW", 2: "MID", 3: "HIGH"}
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
        self.btn.setFixedWidth(40)
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
        self.btn.setStyleSheet("color: RED;")

    def on_btn_clicked(self):
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
    def __init__(self, parent=None):
        super(SettingsWindow, self).__init__(parent)

        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.setWindowTitle("LakeShore 336 - Settings")
        self.setWindowIcon(QtGui.QIcon("modules/icons/LakeShore336.ico"))
        self.setStyleSheet("font-size: 12pt;")

        self.ip_le = QtWidgets.QLineEdit()
        self.ip_le.setAlignment(QtCore.Qt.AlignCenter)
        ipRegex = QtCore.QRegExp(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
        ipValidator = QtGui.QRegExpValidator(ipRegex)
        self.ip_le.setValidator(ipValidator)

        self.connect_btn = QtWidgets.QPushButton("Connect")
        self.disconnect_btn = QtWidgets.QPushButton("Disconnect")
        self.disconnect_btn.setEnabled(False)

        self.delay_le = QtWidgets.QLineEdit("1")
        self.delay_le.setAlignment(QtCore.Qt.AlignCenter)
        validator = QtGui.QDoubleValidator(bottom=0)
        validator.setLocale(QtCore.QLocale(QtCore.QLocale.English))
        self.delay_le.setValidator(validator)

        self.timeout_le = QtWidgets.QLineEdit("10")
        self.timeout_le.setAlignment(QtCore.Qt.AlignCenter)
        validator = QtGui.QDoubleValidator(bottom=0)
        validator.setLocale(QtCore.QLocale(QtCore.QLocale.English))
        self.timeout_le.setValidator(validator)

        self.ready_condition = QtWidgets.QComboBox()
        self.ready_condition.addItems(["absolute error", "relative error"])
        self.ready_condition.currentIndexChanged.connect(
            self.on_ready_condition_changed
        )

        self.value_l = QtWidgets.QLabel("error [K] < ")
        self.value_le = QtWidgets.QLineEdit("0.1")

    def _layout(self):
        layout = QtWidgets.QFormLayout()
        layout.addRow("IP address", self.ip_le)
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.connect_btn)
        btn_layout.addWidget(self.disconnect_btn)
        layout.addRow(btn_layout)
        layout.addRow(HorizontalDivider())
        layout.addRow("Delay [min]", self.delay_le)
        layout.addRow("Timeout [min]", self.timeout_le)
        layout.addRow(HorizontalDivider())
        layout.addRow("Ready condition", self.ready_condition)
        layout.addRow(self.value_l, self.value_le)

        self.setLayout(layout)

    def on_ready_condition_changed(self, index):
        if index == 0:
            self.value_l.setText("error [K] <")
        else:
            self.value_l.setText("error [%] <")

    def save_settings(self):
        settings_dict = {
            "ip": self.ip_le.text(),
            "delay": self.delay_le.text(),
            "timeout": self.timeout_le.text(),
            "ready_condition": self.ready_condition.currentText(),
            "value": self.value_le.text(),
        }
        try:
            with open("LakeShore336_parameters.json", "w") as f:
                json.dump(settings_dict, f)
        except Exception as e:
            print(e)

    def load_settings(self):
        try:
            with open("LakeShore336_parameters.json", "r") as f:
                settings_dict = json.load(f)
                self.ip_le.setText(settings_dict["ip"])
                self.delay_le.setText(settings_dict["delay"])
                self.timeout_le.setText(settings_dict["timeout"])
                self.ready_condition.setCurrentText(settings_dict["ready_condition"])
                self.value_le.setText(settings_dict["value"])
        except FileNotFoundError:
            pass
        except Exception as e:
            print(e)

    def closeEvent(self, event):
        self.save_settings()
        event.accept()


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
