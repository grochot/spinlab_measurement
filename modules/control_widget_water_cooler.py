from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import nidaqmx

class WaterCoolerControl(QtWidgets.QWidget):
    object_name = "water_cooler_control"
    def __init__(self):
        super(WaterCoolerControl, self).__init__()
        self.state = False
        self.name = "Water Cooler Control"

        self.setWindowTitle("Water Cooler Control")

        self.address = "Dev1/ao1"

        self.setStyleSheet("QLabel { font-size: 14pt; } QPushButton { font-size: 14pt; }")
        
        self.layout = QtWidgets.QGridLayout(self)

        self.toggle_btn = QtWidgets.QPushButton("Toggle")
        self.toggle_btn.clicked.connect(self.on_toggle)
        self.layout.addWidget(self.toggle_btn, 1, 1)

        self.label = QtWidgets.QLabel("Cooling?")
        self.layout.addWidget(self.label, 1, 2)

        self.start_btn = QtWidgets.QPushButton("START")
        self.start_btn.clicked.connect(lambda: self.pulse(True))
        self.layout.addWidget(self.start_btn, 2, 1)

        self.stop_btn = QtWidgets.QPushButton("STOP")
        self.stop_btn.clicked.connect(lambda: self.pulse(False))
        self.layout.addWidget(self.stop_btn, 3, 1)

        self.on_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.on_layout, 2, 2)

        self.on_indicator = QtWidgets.QPushButton()
        self.on_indicator.setEnabled(False)
        self.on_indicator.setFixedWidth(40) 
        self.on_indicator.setFixedHeight(33)
        self.on_indicator.setStyleSheet("border: 3px solid gray;")
        self.on_layout.addWidget(self.on_indicator)

        self.on_label = QtWidgets.QLabel("ON")
        self.on_label.setAlignment(QtCore.Qt.AlignCenter)
        self.on_layout.addWidget(self.on_label)

        self.off_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.off_layout, 3, 2)

        self.off_indicator = QtWidgets.QPushButton()
        self.off_indicator.setEnabled(False)
        self.off_indicator.setFixedWidth(40) 
        self.off_indicator.setFixedHeight(33)
        self.off_indicator.setStyleSheet("background: red; border: 3px solid gray;")
        self.off_layout.addWidget(self.off_indicator)

        self.off_label = QtWidgets.QLabel("OFF")
        self.off_label.setAlignment(QtCore.Qt.AlignCenter)
        self.off_layout.addWidget(self.off_label)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.finish_pulse)

        self.loadState()
        self.updateGUI()

    def closeEvent(self, event):
        self.saveState()
        event.accept()

    def updateGUI(self):
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

    def saveState(self):
        with open('water_cooler_state.txt', 'w') as f:
            f.write(str(self.state))

    def loadState(self):
        try:
            with open('water_cooler_state.txt', 'r') as f:
                self.state = bool(f.read())
        except FileNotFoundError:
            pass

    def pulse(self, state):
        self.state = state
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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = WaterCoolerControl()
    widget.show()
    sys.exit(app.exec_())
