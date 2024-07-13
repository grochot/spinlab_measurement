from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import nidaqmx
import nidaqmx.system
import nidaqmx.task

class WaterCoolerControl(QtWidgets.QWidget):
    object_name = "water_cooler_control"
    def __init__(self, address_list):
        super(WaterCoolerControl, self).__init__()
        self.state = False
        self.name = "Water Cooler Control"
        self.address_list = address_list

        self._setup_ui()
        self._layout()

        self.loadState()
        self.updateGUI()

    def _setup_ui(self):
        
        self.setWindowTitle("Water Cooler Control")

        self.setStyleSheet("QLabel { font-size: 14pt; } QPushButton { font-size: 14pt; } QComboBox { font-size: 14pt; }")

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

    def updateGUI(self):
        self.address_cb.setCurrentText(self.address)
        if self.state:
            self.on_indicator.setStyleSheet("background: green; border: 3px solid gray;")
            self.off_indicator.setStyleSheet("border: 3px solid gray;")
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
        else:
            self.on_indicator.setStyleSheet("border: 3px solid gray;")
            self.off_indicator.setStyleSheet("background: red; border: 3px solid gray;")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

    def save_params(self):
        with open('water_cooler_params.txt', 'w') as f:
            f.write(str(self.state)+"\n")
            f.write(self.address)

    def loadState(self):
        try:
            with open('water_cooler_params.txt', 'r') as f:
                state = f.readline()
                self.state = False if state == "False" else True
                address = f.readline()
                self.address = address
        except FileNotFoundError as e:
            pass

    def pulse(self, state):
        self.state = state
        self.save_params()
        if state:
            self.on_indicator.setStyleSheet("background: green; border: 3px solid gray;")
            self.off_indicator.setStyleSheet("border: 3px solid gray;")
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
        else:
            self.on_indicator.setStyleSheet("border: 3px solid gray;")
            self.off_indicator.setStyleSheet("background: red; border: 3px solid gray;")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan(self.address, min_val=0, max_val=5)
            task.write(5)

        self.timer.start(100)

    def finish_pulse(self):
        self.timer.stop()
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan(self.address, min_val=0, max_val=5)
            task.write(0)

    def on_toggle(self):
        self.state = not self.state
        self.save_params()
        if self.state:
            self.on_indicator.setStyleSheet("background: green; border: 3px solid gray;")
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

if __name__ == "__main__":
    found_addreses = ["None"]
    system = nidaqmx.system.System.local()
    for device in system.devices:
        for channel in device.ao_physical_chans:
            found_addreses.append(channel.name)

    app = QtWidgets.QApplication(sys.argv)
    widget = WaterCoolerControl(found_addreses)
    widget.show()
    sys.exit(app.exec_())

    
