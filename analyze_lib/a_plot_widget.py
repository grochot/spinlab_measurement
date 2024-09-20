from PyQt5 import QtWidgets, QtCore


class PlotWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.setStyleSheet("border: 1px solid black;")
        self.label = QtWidgets.QLabel("PLOT", self)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    def _layout(self):
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(0)
        vbox.addWidget(self.label)
        self.setLayout(vbox)
