from pymeasure.display.Qt import QtGui, QtCore, QtWidgets
import sys


class PointDelWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PointDelWidget, self).__init__(parent)

        self.n_points_deleted = 0

        self.deleted_points_lifo = []

        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.setWindowTitle(" ")
        self.setStyleSheet("font-size: 12pt;")
        self.setFixedSize(200, 160)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        self.label = QtWidgets.QLabel("Points deleted: 0")
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        self.undo_bttn = QtWidgets.QPushButton("Undo")
        self.redo_bttn = QtWidgets.QPushButton("Redo")

        self.undo_all_bttn = QtWidgets.QPushButton("Undo All")
        self.confirm_bttn = QtWidgets.QPushButton("Confirm")

    def _layout(self):
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.label, 0, 0, 1, 2)
        layout.addWidget(self.undo_bttn, 1, 0)
        layout.addWidget(self.redo_bttn, 1, 1)
        layout.addWidget(self.undo_all_bttn, 2, 0, 1, 2)
        layout.addWidget(self.confirm_bttn, 3, 0, 1, 2)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = PointDelWidget()
    widget.show()
    sys.exit(app.exec_())
