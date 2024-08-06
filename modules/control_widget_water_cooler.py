from pymeasure.display.Qt import QtCore, QtWidgets, QtGui
import sys
import nidaqmx
import nidaqmx.system
import nidaqmx.task
import os
import json
import logging

logger = logging.getLogger(__name__)


class WaterCoolerControl(QtWidgets.QWidget):
    object_name = "water_cooler_control"

    def __init__(self):
        super(WaterCoolerControl, self).__init__()
        self.state = False
        self.name = "Water Cooler"
        self.icon_path = os.path.join("modules", "icons", "WaterCooler.ico")
        self.save_path = os.path.join("WaterCoolerControl_parameters.json")

        self.address_list = ["None"]
        self.address = "None"

        self.loadState()
        self._setup_ui()
        self._layout()

    def open_widget(self):
        self.get_available_addresses()
        self.updateGUI()
        self.show()

    def _setup_ui(self):

        self.setWindowTitle("Water Cooler Control")
        self.setWindowIcon(QtGui.QIcon(self.icon_path))

        self.setStyleSheet(
            "QLabel { font-size: 14pt; } QPushButton { font-size: 14pt; } QComboBox { font-size: 14pt; }"
        )

        self.address_cb = QtWidgets.QComboBox()
        for address in self.address_list:
            self.address_cb.addItem(address)
        self.address_cb.currentIndexChanged.connect(self.on_address_change)

        self.stack = QtWidgets.QStackedWidget(self)

        self.control_widget = QtWidgets.QWidget()
        self.stack.addWidget(self.control_widget)

        self.toggle_btn = QtWidgets.QPushButton("Toggle")
        self.toggle_btn.setStyleSheet("font-size: 10pt")
        self.toggle_btn.clicked.connect(self.on_toggle)

        self.start_btn = QtWidgets.QPushButton("START")
        self.start_btn.clicked.connect(lambda: self.pulse(True))

        self.stop_btn = QtWidgets.QPushButton("STOP")
        self.stop_btn.clicked.connect(lambda: self.pulse(False))

        self.on_indicator = QtWidgets.QPushButton()
        self.on_indicator.setEnabled(False)
        self.on_indicator.setFixedWidth(40)
        self.on_indicator.setFixedHeight(33)
        self.on_indicator.setStyleSheet("border: 3px solid gray;")

        self.on_label = QtWidgets.QLabel("ON")
        self.on_label.setAlignment(QtCore.Qt.AlignCenter)

        self.off_indicator = QtWidgets.QPushButton()
        self.off_indicator.setEnabled(False)
        self.off_indicator.setFixedWidth(40)
        self.off_indicator.setFixedHeight(33)
        self.off_indicator.setStyleSheet("background: red; border: 3px solid gray;")

        self.off_label = QtWidgets.QLabel("OFF")
        self.off_label.setAlignment(QtCore.Qt.AlignCenter)

        self.not_connected_widget = QtWidgets.QWidget()
        self.stack.addWidget(self.not_connected_widget)
        self.stack.setCurrentIndex(1)

        self.not_connected_l = QtWidgets.QLabel("DEVICE NOT CONNECTED!")
        self.not_connected_l.setAlignment(QtCore.Qt.AlignCenter)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.finish_pulse)

    def _layout(self):
        self.layout = QtWidgets.QVBoxLayout(self)

        self.layout.addWidget(self.address_cb)
        self.layout.addWidget(self.stack)

        self.control_layout = QtWidgets.QVBoxLayout()
        self.control_widget.setLayout(self.control_layout)
        self.control_layout.addWidget(self.toggle_btn)

        self.grid_layout = QtWidgets.QGridLayout()
        self.control_layout.addLayout(self.grid_layout)

        self.grid_layout.addWidget(self.start_btn, 2, 1)
        self.grid_layout.addWidget(self.stop_btn, 3, 1)

        self.on_layout = QtWidgets.QHBoxLayout()
        self.grid_layout.addLayout(self.on_layout, 2, 2)
        self.on_layout.addWidget(self.on_indicator)
        self.on_layout.addWidget(self.on_label)

        self.off_layout = QtWidgets.QHBoxLayout()
        self.grid_layout.addLayout(self.off_layout, 3, 2)
        self.off_layout.addWidget(self.off_indicator)
        self.off_layout.addWidget(self.off_label)

        self.not_connected_layout = QtWidgets.QVBoxLayout()
        self.not_connected_widget.setLayout(self.not_connected_layout)
        self.not_connected_layout.addWidget(self.not_connected_l)

    def get_available_addresses(self):
        self.address_list = ["None"]
        system = nidaqmx.system.System.local()
        for device in system.devices:
            for channel in device.ao_physical_chans:
                self.address_list.append(channel.name)

    def updateGUI(self):
        self.address_cb.currentIndexChanged.disconnect()
        self.address_cb.clear()

        for address in self.address_list:
            self.address_cb.addItem(address)

        if self.address not in self.address_list:
            self.address = "None"

        if len(self.address_list) > 1:
            self.not_connected_l.setText("Select device address")
        else:
            self.not_connected_l.setText("DEVICE NOT CONNECTED!")

        self.display()
        self.address_cb.setCurrentText(self.address)
        self.address_cb.currentIndexChanged.connect(self.on_address_change)
        if self.state:
            self.on_indicator.setStyleSheet(
                "background: green; border: 3px solid gray;"
            )
            self.off_indicator.setStyleSheet("border: 3px solid gray;")
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
        else:
            self.on_indicator.setStyleSheet("border: 3px solid gray;")
            self.off_indicator.setStyleSheet("background: red; border: 3px solid gray;")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

    def save_params(self):
        dict = {"state": self.state, "address": self.address}
        try:
            with open(self.save_path, "w") as f:
                json.dump(dict, f)
        except Exception as e:
            logger.exception(e)

    def loadState(self):
        try:
            with open(self.save_path, "r") as f:
                json_dict = json.load(f)
                self.state = json_dict["state"]
                self.address = json_dict["address"]
        except FileNotFoundError as e:
            pass
        except Exception as e:
            logger.exception(e)
            self.state = False
            self.address = "None"

    def pulse(self, state):
        try:
            with nidaqmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan(self.address, min_val=0, max_val=5)
                task.write(3.3)
        except Exception as e:
            logger.exception(e)
            self.connection_lost()
            return

        self.state = state
        self.save_params()
        if state:
            self.on_indicator.setStyleSheet(
                "background: green; border: 3px solid gray;"
            )
            self.off_indicator.setStyleSheet("border: 3px solid gray;")
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
        else:
            self.on_indicator.setStyleSheet("border: 3px solid gray;")
            self.off_indicator.setStyleSheet("background: red; border: 3px solid gray;")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

        self.timer.start(500)

    def finish_pulse(self):
        self.timer.stop()
        try:
            with nidaqmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan(self.address, min_val=0, max_val=5)
                task.write(0)
        except Exception as e:
            logger.exception(e)
            self.connection_lost()

    def on_toggle(self):
        self.state = not self.state
        self.save_params()
        if self.state:
            self.on_indicator.setStyleSheet(
                "background: green; border: 3px solid gray;"
            )
            self.off_indicator.setStyleSheet("border: 3px solid gray;")
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
        else:
            self.on_indicator.setStyleSheet("border: 3px solid gray;")
            self.off_indicator.setStyleSheet("background: red; border: 3px solid gray;")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

    def on_address_change(self, idx):
        self.address = self.address_list[idx]
        self.display()
        self.save_params()

    def display(self):
        if self.address == "None":
            self.stack.setCurrentIndex(1)
            return
        self.stack.setCurrentIndex(0)

    def connection_lost(self):
        self.address_list = ["None"]
        self.updateGUI()
        self.display()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = WaterCoolerControl()
    widget.show()
    sys.exit(app.exec_())
