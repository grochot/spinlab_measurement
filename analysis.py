# from pymeasure.display.windows.managed_dock_window import ManagedDockWindow
# from pymeasure.experiment.procedure import Procedure
# from pymeasure.experiment.parameters import FloatParameter, BooleanParameter

# from PyQt5 import QtWidgets, QtCore
from pymeasure.display.Qt import QtWidgets, QtCore
import pyqtgraph as pg
import sys

from analyze_lib.a_browser_widget import BrowserWidget
from analyze_lib.a_plot_widget import PlotWidget
from analyze_lib.a_splitter import Splitter


class AnalysisWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analysis")

        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.test_btn = QtWidgets.QPushButton("Test", self)

        self.plot_widget = PlotWidget(self)

        self.browser_widget = BrowserWidget(self)
        self.browser_widget.open_button.clicked.connect(self.open_experiment)
        self.browser = self.browser_widget.browser

    def _layout(self):
        self.main = QtWidgets.QWidget(self)

        inputs = QtWidgets.QWidget(self)
        inputs_vbox = QtWidgets.QVBoxLayout(self.main)
        inputs_vbox.addWidget(self.test_btn)
        inputs.setLayout(inputs_vbox)
        dock = QtWidgets.QDockWidget("Inputs", self)
        dock.setWidget(inputs)
        dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, dock)

        splitter = Splitter(QtCore.Qt.Orientation.Vertical)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self.plot_widget)
        splitter.addWidget(self.browser_widget)

        vbox = QtWidgets.QVBoxLayout(self.main)
        vbox.setSpacing(0)
        vbox.addWidget(splitter)

        self.main.setLayout(vbox)
        self.setCentralWidget(self.main)
        self.main.show()
        self.resize(800, 600)

    def open_experiment(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFiles)

        if dialog.exec():
            filenames = dialog.selectedFiles()
            for filename in map(str, filenames):
                if filename == "":
                    continue
                else:
                    color = pg.intColor(self.browser.topLevelItemCount() % 10)
                    item = self.browser.add(filename, color)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AnalysisWindow()
    window.show()
    sys.exit(app.exec_())
