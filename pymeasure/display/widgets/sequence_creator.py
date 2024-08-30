# from ..Qt import QtCore, QtWidgets, QtGui
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui


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
        self.setFixedSize(400, 380)
        
        self.setStyleSheet("font-size: 11pt;")

        main_layout = QtWidgets.QVBoxLayout()

        input_group = QtWidgets.QGroupBox("Input Parameters")
        input_layout = QtWidgets.QGridLayout()

        self.start_label = QtWidgets.QLabel("Start")
        self.start_input = QtWidgets.QLineEdit(self)
        self.start_input.setValidator(QtGui.QDoubleValidator())
        input_layout.addWidget(self.start_label, 0, 0)
        input_layout.addWidget(self.start_input, 0, 1)

        self.end_label = QtWidgets.QLabel("End")
        self.end_input = QtWidgets.QLineEdit(self)
        self.end_input.setValidator(QtGui.QDoubleValidator())
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
        input_layout.addWidget(self.step_input, 3, 1, 2, 1)

        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        self.preview_label = QtWidgets.QLabel("Command Preview:")
        self.preview_text = QtWidgets.QLineEdit("")
        self.preview_text.setAlignment(QtCore.Qt.AlignCenter)
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet("font-weight: bold; color: blue;")
        main_layout.addWidget(self.preview_label)
        main_layout.addWidget(self.preview_text)

        self.vector_preview_label = QtWidgets.QLabel("Vector Preview:")
        self.vector_preview_text = QtWidgets.QLineEdit()
        self.vector_preview_text.setReadOnly(True)
        self.vector_preview_text.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(self.vector_preview_label)
        main_layout.addWidget(self.vector_preview_text)

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

    def on_ok_clicked(self):
        if self.validate_input():
            self.accept()

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
            self.show_error("Step must be a positive number.")
            raise ValueError("Step must be a positive number.")
        if step > (end - start):
            self.show_error("Step must be less than End - Start.")
            raise ValueError("Step must be less than End - Start.")
        if (end - start) / step > self.MAX_VECTOR_LENGTH:
            self.show_error(f"Vector length exceeds maximum of {self.MAX_VECTOR_LENGTH}.")
            raise ValueError(f"Vector length exceeds maximum of {self.MAX_VECTOR_LENGTH}.")

    def validate_points_input(self, points: float):
        try:
            points = int(points)
        except ValueError:
            self.show_error("Number of Points must be an integer.")
            raise ValueError("Number of Points must be an integer.")
        if points <= 0:
            self.show_error("Number of Points must be a positive integer.")
            raise ValueError("Number of Points must be a positive integer.")
        if points > self.MAX_VECTOR_LENGTH:
            self.show_error(f"Vector length exceeds maximum of {self.MAX_VECTOR_LENGTH}.")
            raise ValueError(f"Vector length exceeds maximum of {self.MAX_VECTOR_LENGTH}.")

    def update_preview(self):
        try:
            start = float(self.start_input.text())
            end = float(self.end_input.text())
            step_or_points = float(self.step_input.text())

            if start >= end:
                self.show_error("Start must be less than End.")
                raise ValueError("Start must be less than End.")

            if self.step_radio.isChecked():
                self.validate_step_input(start, end, step_or_points)
                numpy_command = f"arange({format_number(start)}, {format_number(end)}, {format_number(step_or_points)})"
                vector = np.arange(start, end, step_or_points)
            else:
                step_or_points = int(step_or_points)
                self.validate_points_input(step_or_points)
                numpy_command = f"linspace({format_number(start)}, {format_number(end)}, {step_or_points})"
                vector = np.linspace(start, end, step_or_points)

            self.preview_text.setStyleSheet("color: blue;")
            self.preview_text.setText(numpy_command)
            self.vector_preview_text.setText(self.format_vector_preview(vector))
        except ValueError:
            self.vector_preview_text.clear()

    def format_vector_preview(self, vector: np.ndarray) -> str:
        sep = ", "
        filler = ", ..., "
        est1 = len(np.array2string(vector[0:1], precision=2, separator=""))
        est2 = len(np.array2string(vector[-1:], precision=2, separator=""))
        amount1 = int(np.ceil((self.VECTOR_PREVIEW_LIMIT - 4) / (est1 + est2)))
        amount2 = amount1
        if amount1 * 2 >= len(vector):
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

    def show_error(self, message: str):
        self.preview_text.setStyleSheet("color: red;")
        self.preview_text.setText(message)

    def get_command(self) -> str:
        return self.preview_text.text()


def format_number(x: float) -> str:
    return f"{x}" if 1e-3 < x < 1e3 else f"{x:.2e}"


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = CreatorWindow()
    window.show()
    app.exec_()
    print(window.get_command_input())
