from PyQt5 import QtWidgets, QtCore, QtGui
import sys
from app import MainWindow


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

        if self.icon_path:
            self.b.setIcon(QtGui.QIcon(self.icon_path))
            self.b.setIconSize(QtCore.QSize(75, 75))
        else:
            self.b.setText("OPEN")

        self.b.setFixedSize(90, 90)

        self.label = QtWidgets.QLabel(self.label_text)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

    def _layout(self):
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.b, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(self.label, alignment=QtCore.Qt.AlignCenter)
        self.setLayout(layout)


class MasterWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MasterWindow, self).__init__(parent)
        self.setWindowTitle("SpinLabAPP")
        # self.setGeometry(100, 100, 800, 600)
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.meas_module = Button("Measurement")
        self.analysis_module = Button("Analysis")
        self.camera_module = Button("Camera")

    def create_layout(self):
        self.layout.addWidget(self.meas_module, alignment=QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.analysis_module, alignment=QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.camera_module, alignment=QtCore.Qt.AlignCenter)

    def create_connections(self):
        self.meas_module.b.clicked.connect(self.meas_module_clicked)
        self.analysis_module.b.clicked.connect(self.analysis_module_clicked)
        self.camera_module.b.clicked.connect(self.camera_module_clicked)

    def meas_module_clicked(self):
        self.main_window = MainWindow()
        self.main_window.show()

    def analysis_module_clicked(self):
        pass

    def camera_module_clicked(self):
        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MasterWindow()
    window.show()
    sys.exit(app.exec_())
