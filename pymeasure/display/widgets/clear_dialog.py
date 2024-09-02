from PyQt5 import QtWidgets, QtCore


class ClearDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 150)
        self.setWindowTitle("Clear")

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)

        group_box = QtWidgets.QGroupBox("Select statuses")

        grid_layout = QtWidgets.QGridLayout()
        grid_layout.setSpacing(5)

        self.queued_checkbox = QtWidgets.QCheckBox("Queued")
        self.finished_checkbox = QtWidgets.QCheckBox("Finished")
        self.aborted_checkbox = QtWidgets.QCheckBox("Aborted")
        self.failed_checkbox = QtWidgets.QCheckBox("Failed")

        grid_layout.addWidget(self.queued_checkbox, 0, 0)
        grid_layout.addWidget(self.finished_checkbox, 0, 1)
        grid_layout.addWidget(self.aborted_checkbox, 1, 0)
        grid_layout.addWidget(self.failed_checkbox, 1, 1)

        group_box.setLayout(grid_layout)

        main_layout.addWidget(group_box)

        self.delete_files_checkbox = QtWidgets.QCheckBox("Delete Data Files")

        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addWidget(self.delete_files_checkbox)
        h_layout.addStretch()

        clear_button = QtWidgets.QPushButton("Clear")
        clear_button.setFixedWidth(100)
        clear_button.clicked.connect(self.clear_action)

        h_layout.addWidget(clear_button)

        main_layout.addLayout(h_layout)

    def clear_action(self):
        selected_statuses = (
            self.queued_checkbox.isChecked(),
            self.finished_checkbox.isChecked(),
            self.aborted_checkbox.isChecked(),
            self.failed_checkbox.isChecked(),
        )
        delete_files = self.delete_files_checkbox.isChecked()

        self.parent().clear_by_status(selected_statuses, delete_files)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    dialog = ClearDialog()
    dialog.show()
    app.exec_()
