from ..Qt import QtCore, QtWidgets, QtGui

class CreatorWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Creator Window")
        self.setFixedSize(300, 300)

        layout = QtWidgets.QVBoxLayout()

        # Starting point input
        self.start_label = QtWidgets.QLabel("Start:")
        self.start_input = QtWidgets.QLineEdit(self)
        layout.addWidget(self.start_label)
        layout.addWidget(self.start_input)

        # Ending point input
        self.end_label = QtWidgets.QLabel("End:")
        self.end_input = QtWidgets.QLineEdit(self)
        layout.addWidget(self.end_label)
        layout.addWidget(self.end_input)

        # Step or number of points input
        self.step_label = QtWidgets.QLabel("Step / Number of Points:")
        self.step_input = QtWidgets.QLineEdit(self)
        layout.addWidget(self.step_label)
        layout.addWidget(self.step_input)

        # Radio buttons to choose between step or number of points
        self.step_radio = QtWidgets.QRadioButton("Use Step")
        self.points_radio = QtWidgets.QRadioButton("Use Number of Points")
        self.step_radio.setChecked(True)  # Default selection
        layout.addWidget(self.step_radio)
        layout.addWidget(self.points_radio)

        # OK button
        self.ok_button = QtWidgets.QPushButton("OK", self)
        self.ok_button.clicked.connect(self.on_ok_clicked)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

    def on_ok_clicked(self):
        # Validate input
        if self.validate_input():
            self.accept()

    def validate_input(self):
        try:
            start = float(self.start_input.text())
            end = float(self.end_input.text())
            step_or_points = float(self.step_input.text())

            if self.step_radio.isChecked():
                if step_or_points <= 0:
                    raise ValueError("Step must be a positive number.")
                if start >= end:
                    raise ValueError("Start must be less than End when using Step.")
                if step_or_points > (end - start):
                    raise ValueError("Step must be less than End - Start.")
            else:
                if step_or_points <= 0 or not step_or_points.is_integer():
                    raise ValueError("Number of Points must be a positive integer.")
            
            return True
        except ValueError as e:
            QtWidgets.QMessageBox.warning(self, "Invalid Input", str(e))
            return False

    def getInput(self):
        start = float(self.start_input.text())
        end = float(self.end_input.text())
        step_or_points = float(self.step_input.text())

        if self.step_radio.isChecked():
            numpy_command = f"arange({start}, {end}, {step_or_points})"
        else:
            step_or_points = int(step_or_points)
            numpy_command = f"linspace({start}, {end}, {step_or_points})"

        return numpy_command