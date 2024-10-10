import logging
from PyQt5 import QtCore, QtGui, QtWidgets

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ParametersWidget(QtWidgets.QWidget):
    sigSetParameter = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._layout()

        self._procedure = None
        self.all_parameters = {}
        self.parameter_names = []

    def _setup_ui(self):
        self.setWindowTitle("Parameters")

        self.search_line_edit = QtWidgets.QLineEdit(self)
        self.search_line_edit.setPlaceholderText("Search parameter names...")

        self.completer = QtWidgets.QCompleter(self)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.completer.setFilterMode(QtCore.Qt.MatchContains)
        self.search_line_edit.setCompleter(self.completer)

        self.search_line_edit.textChanged.connect(self.filter_parameters)

        self.parameters = QtWidgets.QTableWidget(self)
        self.parameters.setColumnCount(2)
        self.parameters.setHorizontalHeaderLabels(["PARAMETER", "VALUE"])
        self.parameters.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.parameters.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.parameters.verticalHeader().hide()
        self.parameters.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.parameters.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.parameters.itemDoubleClicked.connect(self.use_parameter)

        self.setMinimumSize(750, 500)
        self.resize(750, 500)

    def _layout(self):
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self.search_line_edit)
        vbox.addWidget(self.parameters)
        self.setLayout(vbox)

    def clear_parameters(self):
        self.parameters.setRowCount(0)

    def set_parameters(self, parameters):
        self.clear_parameters()
        self.all_parameters = parameters
        self.parameter_names = [param.name for param in parameters.values()]

        self.completer.setModel(QtCore.QStringListModel(self.parameter_names))

        self.parameters.setRowCount(len(parameters))
        for i, (key, param) in enumerate(parameters.items()):
            self.parameters.setItem(i, 0, QtWidgets.QTableWidgetItem(param.name))
            font = QtGui.QFont()
            font.setBold(True)
            self.parameters.item(i, 0).setFont(font)
            self.parameters.setItem(i, 1, QtWidgets.QTableWidgetItem(str(param)))

    def filter_parameters(self, text):
        self.clear_parameters()

        filtered_params = {k: v for k, v in self.all_parameters.items() if text.lower() in v.name.lower()}

        self.parameters.setRowCount(len(filtered_params))
        for i, (key, param) in enumerate(filtered_params.items()):
            self.parameters.setItem(i, 0, QtWidgets.QTableWidgetItem(param.name))
            self.parameters.setItem(i, 1, QtWidgets.QTableWidgetItem(str(param)))

    def use_parameter(self):
        selected = self.parameters.selectedItems()
        if selected:
            name = selected[0].text()
            parameter = None
            parameter_tuple = None
            for key, parameter in self.all_parameters.items():
                if parameter.name == name:
                    parameter_tuple = (key, parameter)
                    break


            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Icon.Question)
            msg.setText(f"Use the parameter: '{name}' with value: {str(parameter)}?")
            msg.setWindowTitle("Use parameter")
            msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            msg.setDefaultButton(QtWidgets.QMessageBox.StandardButton.No)
            ret = msg.exec_()
            if ret == QtWidgets.QMessageBox.StandardButton.Yes:
                self.sigSetParameter.emit(parameter_tuple)

    @property
    def procedure(self):
        return self._procedure

    @procedure.setter
    def procedure(self, procedure):
        self.search_line_edit.clear()
        self.all_parameters = {}
        self.parameter_names = []
        self._procedure = procedure
        self.set_parameters(procedure.parameter_objects())
