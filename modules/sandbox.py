import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # Ustawienie tytułu okna
        self.setWindowTitle("Okienko z pomocą")

        # Tworzenie layoutu
        layout = QVBoxLayout()

        # Tworzenie etykiety
        label = QLabel("Najedź myszką na mnie", self)
        label.setToolTip("To jest pomoc dla tego elementu!")  # Ustawienie podpowiedzi
        
        # Dodanie etykiety do layoutu
        layout.addWidget(label)
        
        # Ustawienie layoutu
        self.setLayout(layout)

# Tworzenie aplikacji
app = QApplication(sys.argv)
window = MainWindow()
window.show()

# Uruchomienie aplikacji
sys.exit(app.exec_())
