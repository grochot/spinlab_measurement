from PyQt5 import QtWidgets, QtCore, QtGui
from os.path import basename


class BrowserItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, filename, color, parent=None):
        super().__init__(parent)

        pixelmap = QtGui.QPixmap(24, 24)
        pixelmap.fill(color)
        self.setIcon(0, QtGui.QIcon(pixelmap))
        self.setFlags(self.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
        self.setCheckState(0, QtCore.Qt.CheckState.Checked)
        self.setText(1, basename(filename))


class Browser(QtWidgets.QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        header_labels = ["Graph", "Filename"]
        
        self.setColumnCount(len(header_labels))
        self.setHeaderLabels(header_labels)
        
        for i, width in enumerate([80, 140]):
            self.header().resizeSection(i, width)

    def add(self, filename, color):
        item = BrowserItem(filename, color)
        self.addTopLevelItem(item)
        return item


class BrowserWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.browser = Browser(parent=self)
        self.clear_button = QtWidgets.QPushButton("Clear all", self)
        self.clear_button.setEnabled(False)
        # self.clear_by_status_button = QtWidgets.QPushButton("Clear by status", self)
        # self.clear_by_status_button.setMinimumWidth(120)
        # self.clear_by_status_button.setEnabled(False)
        self.hide_button = QtWidgets.QPushButton("Hide all", self)
        self.hide_button.setEnabled(False)
        self.show_button = QtWidgets.QPushButton("Show all", self)
        self.show_button.setEnabled(False)
        self.open_button = QtWidgets.QPushButton("Open", self)
        self.open_button.setEnabled(True)

    def _layout(self):
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(0)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setSpacing(10)
        hbox.setContentsMargins(-1, 6, -1, 6)
        hbox.addWidget(self.show_button)
        hbox.addWidget(self.hide_button)
        hbox.addWidget(self.clear_button)
        # hbox.addWidget(self.clear_by_status_button)
        hbox.addStretch()
        hbox.addWidget(self.open_button)

        vbox.addLayout(hbox)
        vbox.addWidget(self.browser)
        self.setLayout(vbox)
