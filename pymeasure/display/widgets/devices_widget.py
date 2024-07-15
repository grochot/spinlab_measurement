from ..Qt import QtWidgets, QtCore, QtGui
from .tab_widget import TabWidget

class DeviceWidget(QtWidgets.QWidget):
    def __init__(self, device, parent=None):
        super().__init__(parent)
        self.device = device

        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.setFixedSize(200, 200)
        self.button = QtWidgets.QPushButton()
        self.button.setIcon(QtGui.QIcon(self.device.icon_path))
        self.button.setIconSize(QtCore.QSize(100, 100))
        self.button.setFixedSize(120, 120)
        self.button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.button.clicked.connect(self.device.show)

        self.label = QtWidgets.QLabel(self.device.name)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

    def _layout(self):
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.button, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(self.label, alignment=QtCore.Qt.AlignCenter)
        self.setLayout(layout)


class DevicesWidget(TabWidget, QtWidgets.QWidget):
    def __init__(self, name, devices, parent=None):
        super().__init__(name, parent)
        self.devices = devices
        self.devices_widgets = []
        self.num_cols = 4 

        for device in self.devices:
            setattr(self, device.object_name, device())

        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        for device in self.devices:
            widget = DeviceWidget(getattr(self, device.object_name))
            self.devices_widgets.append(widget)

    def _layout(self):
        layout = QtWidgets.QGridLayout()
        for i in range(len(self.devices_widgets)):
            row = i // self.num_cols
            col = i % self.num_cols
            layout.addWidget(self.devices_widgets[i], row, col)
        self.setLayout(layout)
