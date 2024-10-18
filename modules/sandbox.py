import sys
from PyQt5.QtWidgets import QApplication, QPushButton, QWidget, QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

class Okno(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Tworzenie przycisku
        przycisk = QPushButton("Zatwierdź", self)

        # Ustawienie ikony z ptaszkiem (checkmark) z zasobów systemowych
        przycisk.setIcon(self.style().standardIcon(getattr(self.style(), "SP_DialogApplyButton")))
        
        # Ustawienie rozmiaru ikony
        przycisk.setIconSize(QSize(24, 24))

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(przycisk)
        self.setLayout(layout)

        # Ustawienia okna
        self.setWindowTitle("Przycisk z ptaszkiem")
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    okno = Okno()
    sys.exit(app.exec_())
