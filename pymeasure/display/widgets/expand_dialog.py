from ..Qt import QtWidgets


class ExpandDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, procedure_class=None):
        super().__init__(parent)
        _procedure = procedure_class()
        self.params = [param.name for param in _procedure.placeholder_objects().values()]
        self.params.sort()

        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.setWindowTitle("Expand")
        self.setFixedSize(300, 150)

        self.label = QtWidgets.QLabel("Select parameter:")

        self.combo = QtWidgets.QComboBox()
        self.combo.setEditable(True)
        self.combo.addItems(self.params)

        completer = QtWidgets.QCompleter(self.params)
        completer.setCaseSensitivity(0)
        self.combo.setCompleter(completer)

        self.ok_button = QtWidgets.QPushButton("OK")
        self.cancel_button = QtWidgets.QPushButton("Cancel")

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def _layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        main_layout.addWidget(self.label)
        main_layout.addWidget(self.combo)

        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addWidget(self.ok_button)
        h_layout.addWidget(self.cancel_button)

        main_layout.addLayout(h_layout)

        self.setLayout(main_layout)

    def validate(self):
        self.combo.setCurrentText(self.combo.currentText().strip())
        if not self.combo.currentText() in self.params:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Invalid parameter")
            msg.setWindowTitle("Error")
            msg.exec_()
            return False
        return True

    def accept(self):
        if self.validate():
            super().accept()
