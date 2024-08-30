from ..Qt import QtCore, QtWidgets, QtGui
import numpy as np
from logic.vector import Vector


class VectorTableWidget(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["Index", "Value"])
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.verticalHeader().hide()
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setAlternatingRowColors(True)

    def set_vector(self, vector: np.ndarray):
        self.setRowCount(len(vector))
        for i, value in enumerate(vector):
            index = QtWidgets.QTableWidgetItem(str(i))
            index.setTextAlignment(QtCore.Qt.AlignCenter)
            self.setItem(i, 0, index)

            item = QtWidgets.QTableWidgetItem(format_number(value))
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.setItem(i, 1, item)

    def clear(self):
        self.setRowCount(0)


class VectorPreviewDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vector Preview")
        # self.setFixedSize(200, 300)

        main_layout = QtWidgets.QVBoxLayout()

        self.vector_table = VectorTableWidget()
        main_layout.addWidget(self.vector_table)

        self.ok_button = QtWidgets.QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        main_layout.addWidget(self.ok_button)

        self.setLayout(main_layout)

    def set_vector(self, vector: np.ndarray):
        self.vector_table.set_vector(vector)

    def clear(self):
        self.vector_table.clear()


class HorizontalLine(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class CreatorWindow(QtWidgets.QDialog):
    VECTOR_PREVIEW_LIMIT = 50
    MAX_VECTOR_LENGTH = 100

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Creator Window")
        self.setFixedSize(425, 475)

        self.vector = None

        self.setStyleSheet("font-size: 11pt;")

        main_layout = QtWidgets.QVBoxLayout()

        self.tab_widget = QtWidgets.QTabWidget()
        main_layout.addWidget(self.tab_widget)

        self.numpy_tab = QtWidgets.QWidget()
        self.tab_widget.addTab(self.numpy_tab, "NumPy")

        numpy_layout = QtWidgets.QVBoxLayout()

        input_group = QtWidgets.QGroupBox("Input Parameters")
        input_layout = QtWidgets.QGridLayout()

        self.start_label = QtWidgets.QLabel("Start")
        self.start_input = QtWidgets.QLineEdit(self)
        self.start_input.setValidator(QtGui.QDoubleValidator())
        self.start_input.setAlignment(QtCore.Qt.AlignCenter)
        input_layout.addWidget(self.start_label, 0, 0)
        input_layout.addWidget(self.start_input, 0, 1)

        self.end_label = QtWidgets.QLabel("End")
        self.end_input = QtWidgets.QLineEdit(self)
        self.end_input.setValidator(QtGui.QDoubleValidator())
        self.end_input.setAlignment(QtCore.Qt.AlignCenter)
        input_layout.addWidget(self.end_label, 1, 0)
        input_layout.addWidget(self.end_input, 1, 1)

        input_layout.addWidget(HorizontalLine(), 2, 0, 1, 2)

        self.step_radio = QtWidgets.QRadioButton("Step")
        self.points_radio = QtWidgets.QRadioButton("Number of Points")
        self.step_radio.setChecked(True)

        input_layout.addWidget(self.step_radio, 3, 0)
        input_layout.addWidget(self.points_radio, 4, 0)

        self.step_input = QtWidgets.QLineEdit(self)
        self.step_input.setValidator(QtGui.QDoubleValidator())
        self.step_input.setAlignment(QtCore.Qt.AlignCenter)
        input_layout.addWidget(self.step_input, 3, 1, 2, 1)

        input_group.setLayout(input_layout)
        numpy_layout.addWidget(input_group)

        self.preview_label = QtWidgets.QLabel("Command Preview:")
        self.preview_text = QtWidgets.QLineEdit("")
        self.preview_text.setAlignment(QtCore.Qt.AlignCenter)
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet("font-weight: bold; color: blue;")
        numpy_layout.addWidget(self.preview_label)
        numpy_layout.addWidget(self.preview_text)
        self.numpy_tab.setLayout(numpy_layout)

        vector_tab = QtWidgets.QWidget()
        self.tab_widget.addTab(vector_tab, "Vector")
        vector_layout = QtWidgets.QVBoxLayout()
        vector_layout.addStretch()

        self.vector_input_label = QtWidgets.QLabel("Vector Input:")
        vector_layout.addWidget(self.vector_input_label)
        self.vector_input = QtWidgets.QLineEdit()
        self.vector_input.setAlignment(QtCore.Qt.AlignCenter)
        vector_layout.addWidget(self.vector_input)
        vector_layout.addStretch()

        vector_tab.setLayout(vector_layout)

        h_layout = QtWidgets.QHBoxLayout()
        self.vector_preview_label = QtWidgets.QLabel("Vector Preview:")
        h_layout.addWidget(self.vector_preview_label)

        self.vector_length_label = QtWidgets.QLabel("Vector Length: X")
        self.vector_length_label.setAlignment(QtCore.Qt.AlignRight)
        h_layout.addWidget(self.vector_length_label)
        main_layout.addLayout(h_layout)

        self.vector_preview_text = QtWidgets.QPushButton()
        self.vector_preview_text.setEnabled(False)
        main_layout.addWidget(self.vector_preview_text)

        main_layout.addStretch()

        self.ok_button = QtWidgets.QPushButton("OK", self)
        self.ok_button.clicked.connect(self.on_ok_clicked)
        main_layout.addWidget(self.ok_button)

        self.setLayout(main_layout)
        self.update_preview()

        self.start_input.textChanged.connect(self.update_preview)
        self.end_input.textChanged.connect(self.update_preview)
        self.step_input.textChanged.connect(self.update_preview)
        self.step_radio.toggled.connect(self.update_preview)
        self.points_radio.toggled.connect(self.update_preview)
        self.vector_preview_text.clicked.connect(self.show_vector_preview)

        self.vector_input.textChanged.connect(self.update_preview)

    def show_vector_preview(self):
        dialog = VectorPreviewDialog(self)
        dialog.set_vector(self.get_vector())
        dialog.exec_()

    def get_vector(self) -> np.ndarray:
        return self.vector

    def on_ok_clicked(self):
        if self.tab_widget.currentIndex() == 0:
            if self.validate_input():
                self.accept()
        else:
            if self.vector:
                self.accept()
            else:
                QtWidgets.QMessageBox.warning(self, "Invalid Input", "Invalid Vector Input.")

    def validate_input(self) -> bool:
        try:
            start = float(self.start_input.text())
            end = float(self.end_input.text())
            step_or_points = float(self.step_input.text())

            if start >= end:
                raise ValueError("Start must be less than End.")

            if self.step_radio.isChecked():
                self.validate_step_input(start, end, step_or_points)
            else:
                self.validate_points_input(step_or_points)

            return True
        except ValueError as e:
            QtWidgets.QMessageBox.warning(self, "Invalid Input", str(e))
            return False

    def validate_step_input(self, start: float, end: float, step: float):
        if step <= 0:
            raise ValueError("Step must be a positive number.")
        if step > (end - start):
            raise ValueError("Step must be less than End - Start.")
        if (end - start) / step > self.MAX_VECTOR_LENGTH:
            raise ValueError(f"Vector length exceeds maximum of {self.MAX_VECTOR_LENGTH}.")

    def validate_points_input(self, points: float):
        try:
            points = int(points)
        except ValueError:
            raise ValueError("Number of Points must be an integer.")
        if points <= 0:
            raise ValueError("Number of Points must be a positive integer.")
        if points > self.MAX_VECTOR_LENGTH:
            raise ValueError(f"Vector length exceeds maximum of {self.MAX_VECTOR_LENGTH}.")

    def update_preview(self):
        if self.tab_widget.currentIndex() == 0:
            self.update_numpy_preview()
        else:
            self.update_vector_preview()

    def update_numpy_preview(self):
        try:
            start = float(self.start_input.text())
            end = float(self.end_input.text())
            step_or_points = float(self.step_input.text())
        except ValueError:
            self.vector = None
            self.preview_text.setStyleSheet("color: red;")
            self.preview_text.setText("Invalid input")
            self.vector_preview_text.setText("")
            self.vector_preview_text.setEnabled(False)
            self.vector_length_label.setText("Vector Length: X")
            return

        try:
            if start >= end:
                raise ValueError("Start must be less than End.")

            if self.step_radio.isChecked():
                self.validate_step_input(start, end, step_or_points)
                numpy_command = f"arange({format_number(start)}, {format_number(end)}, {format_number(step_or_points)})"
                self.vector = np.arange(start, end, step_or_points)
            else:
                step_or_points = int(step_or_points)
                self.validate_points_input(step_or_points)
                numpy_command = f"linspace({format_number(start)}, {format_number(end)}, {step_or_points})"
                self.vector = np.linspace(start, end, step_or_points)

            self.preview_text.setStyleSheet("color: blue;")
            self.preview_text.setText(numpy_command)

            self.vector_preview_text.setText(self.format_vector_preview(self.vector))
            self.vector_preview_text.setEnabled(True)

            self.vector_length_label.setText(f"Vector Length: {len(self.vector)}")
        except ValueError as e:
            self.vector = None
            self.preview_text.setStyleSheet("color: red;")
            self.preview_text.setText(str(e))
            self.vector_preview_text.setText("")
            self.vector_preview_text.setEnabled(False)
            self.vector_length_label.setText("Vector Length: X")

    def update_vector_preview(self):
        self.vector = None
        try:
            self.vector = Vector().generate_vector(self.vector_input.text())
        except ValueError:
            pass

        if self.vector:
            self.vector_preview_text.setText(self.format_vector_preview(np.array(self.vector)))
            self.vector_preview_text.setEnabled(True)
            self.vector_length_label.setText(f"Vector Length: {len(self.vector)}")
        else:
            self.vector_preview_text.setText("")
            self.vector_preview_text.setEnabled(False)
            self.vector_length_label.setText("Vector Length: X")

    def format_vector_preview(self, vector: np.ndarray) -> str:
        sep = ", "
        filler = ", ..., "
        est1 = len(np.array2string(vector[0:1], precision=2, separator=""))
        est2 = len(np.array2string(vector[-1:], precision=2, separator=""))
        est3 = len(np.array2string(vector[len(vector)//2:len(vector)//2+1], precision=2, separator=""))
        amount1 = int(np.ceil((self.VECTOR_PREVIEW_LIMIT - 4) * 2 / (est1 + est2 + est3*2)))
        amount2 = amount1
        if len(np.array2string(vector, precision=2, separator=", ")) <= self.VECTOR_PREVIEW_LIMIT:
            return np.array2string(vector, precision=2, separator=", ")
        flicker = True
        while amount1 * est1 + amount2 * est2 > self.VECTOR_PREVIEW_LIMIT:
            if flicker:
                amount2 -= 1
            else:
                amount1 -= 1
            flicker = not flicker
        first_half = np.array2string(vector[:amount1], precision=2, separator=sep)
        second_half = np.array2string(vector[-amount2:], precision=2, separator=sep)
        while len(first_half) + len(second_half) + len(filler) - 2 > self.VECTOR_PREVIEW_LIMIT:
            if flicker:
                amount2 -= 1
                second_half = np.array2string(vector[-amount2:], precision=2, separator=sep)
            else:
                amount1 -= 1
                first_half = np.array2string(vector[:amount1], precision=2, separator=sep)
            flicker = not flicker
        return f"{first_half[:-1]}, ..., {second_half[1:]}"

    def get_command(self) -> str:
        return self.preview_text.text() if self.tab_widget.currentIndex() == 0 else np.array2string(np.array(self.vector), separator=", ")


def format_number(x: float) -> str:
    return f"{x}" if 1e-3 < x < 1e3 else f"{x:.2e}"


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = CreatorWindow()
    window.show()
    app.exec_()
    print(window.get_command())
