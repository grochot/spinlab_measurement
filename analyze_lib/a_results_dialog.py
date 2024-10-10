import os

from pymeasure.display.Qt import QtWidgets, QtCore
from a_results import Results

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ResultsDialog(QtWidgets.QFileDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOption(QtWidgets.QFileDialog.Option.DontUseNativeDialog, True)
        self._setup_ui()

    def _setup_ui(self):
        preview_tab = QtWidgets.QTabWidget()
        param_vbox = QtWidgets.QVBoxLayout()
        metadata_vbox = QtWidgets.QVBoxLayout()
        param_vbox_widget = QtWidgets.QWidget()
        metadata_vbox_widget = QtWidgets.QWidget()

        self.preview_param = QtWidgets.QTreeWidget()
        param_header = QtWidgets.QTreeWidgetItem(["Name", "Value"])
        self.preview_param.setHeaderItem(param_header)
        self.preview_param.setColumnWidth(0, 150)
        self.preview_param.setAlternatingRowColors(True)

        self.preview_metadata = QtWidgets.QTreeWidget()
        param_header = QtWidgets.QTreeWidgetItem(["Name", "Value"])
        self.preview_metadata.setHeaderItem(param_header)
        self.preview_metadata.setColumnWidth(0, 150)
        self.preview_metadata.setAlternatingRowColors(True)

        param_vbox.addWidget(self.preview_param)
        metadata_vbox.addWidget(self.preview_metadata)

        param_vbox_widget.setLayout(param_vbox)
        metadata_vbox_widget.setLayout(metadata_vbox)

        preview_tab.addTab(param_vbox_widget, "Parameters")
        preview_tab.addTab(metadata_vbox_widget, "Metadata")

        self.layout().addWidget(preview_tab, 0, 5, 4, 1)
        self.layout().setColumnStretch(5, 1)
        self.setMinimumSize(900, 500)
        self.resize(900, 500)

        self.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFiles)
        self.currentChanged.connect(self.update_preview)

    def update_preview(self, filename):
        if not os.path.isdir(filename) and filename != "":
            try:
                results = Results.load(str(filename))
            except ValueError:
                return
            except Exception as e:
                raise e

        self.preview_param.clear()
