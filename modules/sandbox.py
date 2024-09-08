import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QComboBox, QPushButton
from PyQt5.QtCore import QSettings

class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Wybierz ścieżkę do pliku, w którym mają być zapisane ustawienia
        settings_file = 'my_custom_settings.ini'  # Możesz tutaj podać pełną ścieżkę np. '/path/to/my_custom_settings.ini'
        self.settings = QSettings(settings_file, QSettings.IniFormat)

        self.load_settings()
        
        # Tworzenie elementów UI
        self.textbox = QLineEdit(self)
        self.combobox = QComboBox(self)
        self.save_button = QPushButton('Zapisz', self)
        self.load_button = QPushButton('Wczytaj', self)

        # Dodanie opcji do QComboBox
        self.combobox.addItems(['Opcja 1', 'Opcja 2', 'Opcja 3'])

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.textbox)
        layout.addWidget(self.combobox)
        layout.addWidget(self.save_button)
        layout.addWidget(self.load_button)
        self.setLayout(layout)

        # Wczytanie ustawień
        self.load_settings()

        # Połączenie przycisków z metodami
        self.save_button.clicked.connect(self.save_settings)
        self.load_button.clicked.connect(self.load_settings)

        self.setWindowTitle('QSettings Example with Custom Path')
        self.show()

    def save_settings(self):
        # Zapisanie wartości do QSettings
        self.settings.setValue('textbox_text', self.textbox.text())
        self.settings.setValue('combobox_index', self.combobox.currentIndex())

    def load_settings(self):
        # Wczytanie wartości z QSettings
        self.textbox.setText(self.settings.value('textbox_text', ''))
        self.combobox.setCurrentIndex(int(self.settings.value('combobox_index', 0)))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
