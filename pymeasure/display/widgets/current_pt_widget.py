from ..Qt import QtWidgets, QtCore


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
        self.line_edit.setText(str(point))