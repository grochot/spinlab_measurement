from pymeasure.display.Qt import QtGui, QtCore, QtWidgets
import numpy as np
import sys


class PointDelWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PointDelWidget, self).__init__(parent)

        self.enabled = False
        self.isConfirmed = False

        self.n_points_deleted = 0

        self.undo_stack = []

        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.setWindowTitle(" ")
        self.setStyleSheet("font-size: 12pt;")
        self.setFixedSize(250, 160)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        self.label = QtWidgets.QLabel("Points to delete: 0")
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        self.undo_bttn = QtWidgets.QPushButton("Undo")
        self.undo_bttn.setEnabled(False)
        self.undo_bttn.clicked.connect(self.undo)

        self.undo_all_bttn = QtWidgets.QPushButton("Undo All")
        self.undo_all_bttn.setEnabled(False)
        self.undo_all_bttn.clicked.connect(self.undo_all)

        self.confirm_bttn = QtWidgets.QPushButton("Confirm")
        self.confirm_bttn.clicked.connect(self.confirm)

    def _layout(self):
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.label, 0, 0)
        layout.addWidget(self.undo_bttn, 1, 0)
        layout.addWidget(self.undo_all_bttn, 2, 0)
        layout.addWidget(self.confirm_bttn, 3, 0)
        self.setLayout(layout)

    def setLabelText(self):
        self.label.setText(f"Points to delete: {self.n_points_deleted}")

    def updateUndoBttnsState(self):
        if not self.undo_stack:
            self.undo_bttn.setEnabled(False)
            self.undo_all_bttn.setEnabled(False)
        else:
            self.undo_bttn.setEnabled(True)
            self.undo_all_bttn.setEnabled(True)


    def pointDeleted(self, curve, idx: int, spot):
        self.isConfirmed = False
        self.inc()
        self.undo_stack.append((curve, idx, spot))

        self.updateUndoBttnsState()

    def undo(self):
        if self.undo_stack:
            curve, idx, spot = self.undo_stack.pop()

            xdata, ydata = curve.getData()
            x, y = spot.pos()
            new_xdata = np.insert(xdata, idx, x)
            new_ydata = np.insert(ydata, idx, y)
            curve.setData(new_xdata, new_ydata)
            self.dec()

        self.updateUndoBttnsState()

    def undo_all(self):
        while self.undo_stack:
            self.undo()

    def inc(self):
        self.n_points_deleted += 1
        self.setLabelText()

    def dec(self):
        self.n_points_deleted -= 1
        self.setLabelText()

    def confirm(self):
        self.isConfirmed = True
        self.n_points_deleted = 0
        self.undo_stack = []
        self.updateUndoBttnsState()
        self.setLabelText()

    def closeEvent(self, ev):
        if not self.isConfirmed:
            self.undo_all()
        self.isConfirmed = False
        self.enabled = False
        ev.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = PointDelWidget()
    widget.show()
    sys.exit(app.exec_())
