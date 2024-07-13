from ..Qt import QtWidgets
from .tab_widget import TabWidget


class DevicesWidget(TabWidget, QtWidgets.QWidget):
    def __init__(self, name, devices, parent=None):
        super().__init__(name, parent)
        self.devices = devices
        self.devices_widgets = []

        for device in self.devices:
            setattr(self, device.object_name, device())

        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        for device in self.devices:
            button = QtWidgets.QPushButton(getattr(self, device.object_name).name)
            button.clicked.connect(getattr(self, device.object_name).show)
            self.devices_widgets.append(button)

    def _layout(self):
        layout = QtWidgets.QVBoxLayout()
        for widget in self.devices_widgets:
            layout.addWidget(widget)
        self.setLayout(layout)
