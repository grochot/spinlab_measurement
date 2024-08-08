from ..Qt import QtWidgets, QtCore
from math import floor, log10


def round_sig(x, sig=6):
    if x == 0:
        return 0
    return round(x, sig - int(floor(log10(abs(x)))) - 1)


class CurrentPointWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.setStyleSheet("font-size: 12pt;")
        self.line_edit = QtWidgets.QLineEdit(self)
        self.line_edit.setReadOnly(True)
        self.line_edit.setAlignment(QtCore.Qt.AlignCenter)

    def _layout(self):
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self.line_edit)
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)

    def set_current_point(self, point):
        self.line_edit.setText(str(round_sig(point, 4)))
