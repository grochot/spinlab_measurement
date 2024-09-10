from pymeasure.display.Qt import QtGui, QtCore, QtWidgets
from pymeasure.experiment.results import Results
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
        # self.setStyleSheet("font-size: 12pt;")

        self.label = QtWidgets.QLabel("Points to delete: 0")
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        self.undo_bttn = QtWidgets.QPushButton("Undo")
        self.undo_bttn.setEnabled(False)
        self.undo_bttn.clicked.connect(self.undo)

        self.undo_all_bttn = QtWidgets.QPushButton("Undo All")
        self.undo_all_bttn.setEnabled(False)
        self.undo_all_bttn.clicked.connect(self.undo_all)

        self.confirm_bttn = QtWidgets.QPushButton("Confirm")
        self.confirm_bttn.setEnabled(False)
        self.confirm_bttn.clicked.connect(self.confirm)

    def _layout(self):
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.label, 0, 0)
        layout.addWidget(self.undo_bttn, 1, 0)
        layout.addWidget(self.undo_all_bttn, 2, 0)
        layout.addWidget(self.confirm_bttn, 3, 0)
        self.setLayout(layout)

    def setMode(self, enabled):
        self.enabled = enabled
        if not enabled:
            self.undo_all()
            self.isConfirmed = False

    def setLabelText(self):
        self.label.setText(f"Points to delete: {self.n_points_deleted}")

    def updateBttns(self):
        if not self.undo_stack:
            self.undo_bttn.setEnabled(False)
            self.undo_all_bttn.setEnabled(False)
            self.confirm_bttn.setEnabled(False)
        else:
            self.undo_bttn.setEnabled(True)
            self.undo_all_bttn.setEnabled(True)
            self.confirm_bttn.setEnabled(True)

    def pointDeleted(self, curve, spot):
        self.isConfirmed = False
        self.inc()
        self.undo_stack.append((curve, spot))
        self.updateBttns()

    def undo(self):
        if self.undo_stack:
            curve, spot = self.undo_stack.pop()
            xdata, ydata = curve.getData()
            idx = spot.index()
            x, y = spot.pos()
            new_xdata = np.insert(xdata, idx, x)
            new_ydata = np.insert(ydata, idx, y)
            curve.setData(new_xdata, new_ydata)
            self.dec()
        self.updateBttns()

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
        self.storeChanges()
        self.isConfirmed = True
        self.n_points_deleted = 0
        self.undo_stack = []
        self.updateBttns()
        self.setLabelText()

    def storeChanges(self):
        to_rewrite = {}

        while self.undo_stack:
            curve, spot = self.undo_stack.pop()

            results: Results = curve.results
            try:
                data = to_rewrite[curve][1]
            except KeyError:
                data = results.data

            x_col, y_col = curve.x, curve.y
            x, y = spot.pos()

            idx = np.where((data[x_col] == x) & (data[y_col] == y))[0]
            if len(idx) > 0:
                idx = idx[0]
                data = data.drop(idx)
                data = data.reset_index(drop=True)
            to_rewrite[curve] = (results, data)

        for results, data in to_rewrite.values():
            with open(results.data_filename, "w") as f:
                f.write(results.header())
                f.write(results.labels())
                for _, row in data.iterrows():
                    f.write(results.format(row.to_dict()) + results.LINE_BREAK)
            results.store_metadata()
            results.reload()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = PointDelWidget()
    widget.show()
    sys.exit(app.exec_())
