from PyQt5 import QtWidgets, QtCore, QtGui
from app import MeasurementWindow
from analysis import AnalysisWindow
import sys
from os import path


class Button(QtWidgets.QWidget):
    def __init__(self, label, parent=None, icon_path=None):
        super().__init__(parent)
        self.icon_path = icon_path

        self.label_text = label

        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.b = QtWidgets.QPushButton()
        self.b.setText(self.label_text)
        self.b.setFixedSize(130, 80)
        self.b.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(255, 255, 255, 150);
                color: black;
                font-size: 14px;
                border-radius: 10px;
                border: 2px solid black;
            }
            QPushButton:hover {
                background-color: rgba(200, 200, 200, 200);
                color: black;
                font-weight: bold;
            }
        """
        )

    def _layout(self):
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.b, alignment=QtCore.Qt.AlignCenter)
        self.setLayout(layout)


class MasterWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MasterWindow, self).__init__(parent)
        self.setWindowTitle("SpinLabApp")

        self.setFixedSize(800, 500)  # Set window size

        # Set background image using QPalette
        palette = self.palette()
        background_image_path = path.join("Background.png")  # Path to your image
        palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(QtGui.QPixmap(background_image_path)))
        self.setPalette(palette)

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self._setup_ui()
        self._layout()
        self._signals()

    def _setup_ui(self):
        self.meas_module = Button("MEASUREMENT")
        self.analysis_module = Button("ANALYSIS")
        self.camera_module = Button("CAMERA")

    def _layout(self):
        self.layout.addWidget(self.meas_module, alignment=QtCore.Qt.AlignRight)
        self.layout.addWidget(self.analysis_module, alignment=QtCore.Qt.AlignRight)
        self.layout.addWidget(self.camera_module, alignment=QtCore.Qt.AlignRight)

    def _signals(self):
        self.meas_module.b.clicked.connect(self.meas_module_clicked)
        self.analysis_module.b.clicked.connect(self.analysis_module_clicked)
        self.camera_module.b.clicked.connect(self.camera_module_clicked)

    def meas_module_clicked(self):
        self.meas_window = MeasurementWindow()
        self.meas_window.show()

    def analysis_module_clicked(self):
        self.analysis_window = AnalysisWindow()
        self.analysis_window.show()

    def camera_module_clicked(self):
        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MasterWindow()
    window.show()
    sys.exit(app.exec_())
