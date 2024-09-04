from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QMessageBox
import os
import requests
import subprocess
import sys
class UpdateChecker(QWidget):

    def __init__(self):
        super().__init__()
        self.current_version = '3.0.0'
        self.initUI()
        self.check_for_updates()

    def initUI(self):
        self.setWindowTitle('Sprawdzanie aktualizacji')
        self.setGeometry(300, 300, 300, 150)

        self.layout = QVBoxLayout()
        self.label = QLabel('Sprawdzanie aktualizacji...', self)
        self.layout.addWidget(self.label)

        self.setLayout(self.layout)
    
    def check_for_updates(self):
        try:
            latest_version = self.get_latest_version_info()
            if latest_version != self.current_version:
                reply = QMessageBox.question(
                    self, 'Aktualizacja dostępna',
                    f'Nowa wersja {latest_version} jest dostępna. Czy chcesz zaktualizować?',
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.download_and_install_update()
                else:
                   
                    self.run_main_application()
            else:
                self.label.setText('Masz już najnowszą wersję.')
                self.run_main_application()
        except Exception as e:
            self.label.setText(f'Błąd podczas sprawdzania aktualizacji: {e}')
            self.run_main_application()

    def get_latest_version_info(self):
        url = 'http://update-test.cytr.us/latest_version.txt'
        response = requests.get(url)
        response.raise_for_status()
        return response.text.strip()

    def download_and_install_update(self):
        try:
            download_url = 'http://update-test.cytr.us/SpinLabAPP.exe'
            output_path = os.path.join(os.path.dirname(__file__), 'SpinLabAPP.exe')
            self.download_new_installer(download_url, output_path)
            self.label.setText('Pobrano nowy instalator. Uruchamianie aktualizacji...')
            self.run_installer(output_path)
        except Exception as e:
            self.label.setText(f'Błąd podczas pobierania aktualizacji: {e}')
            #self.run_main_application()

    def download_new_installer(self, download_url, output_path):
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        with open(output_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

    def run_installer(self, installer_path):
        try:

            # if sys.platform == 'win32':
            #     os.startfile(installer_path)
            # else:
            #     subprocess.run(['open', installer_path], check=True)  # dla macOS
            QApplication.instance().quit()  # Zamknięcie aplikacji
            subprocess.run([installer_path], check=True)
            exit()
        except Exception as e:
            self.label.setText(f'Błąd podczas uruchamiania instalatora: {e}')
            self.run_main_application()



    def run_main_application(self):
        script_directory = os.path.dirname(os.path.abspath(__file__))
        DETACHED_PROCESS = 0x000000
        CREATE_NEW_CONSOLE = subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
        python_interpreter = sys.executable
        process = subprocess.Popen([python_interpreter, 'app.py'], creationflags=DETACHED_PROCESS)
        QApplication.instance().quit()
        exit()
        # try:
        #     main_app_path = os.path.join(os.path.dirname(__file__), 'main_app.py')  # Zmień na właściwą nazwę swojej aplikacji
        #     self.close()  # Zamknięcie okna aktualizacji
        #     subprocess.run([sys.executable, main_app_path], check=True)
        #     QApplication.instance().quit()
        # except Exception as e:
        #     self.label.setText(f'Błąd podczas uruchamiania aplikacji: {e}')
        # window = MainWindow()
        # window.show()
        # sys.exit(app.exec())

    def main():
        # app = QApplication(sys.argv)
        ex = UpdateChecker()
        ex.show()
        sys.exit(app.exec_())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    UpdateChecker.main()