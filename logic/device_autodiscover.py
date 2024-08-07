import pyvisa
import threading
import time

class DeviceScanner:
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.devices = []
        self.stop_scanning = threading.Event()
        self.lock = threading.Lock()

    def scan_devices(self):
        while not self.stop_scanning.is_set():
            with self.lock:
                self.devices = self.rm.list_resources()
            time.sleep(2)

    def start_scanning(self):
        self.scanning_thread = threading.Thread(target=self.scan_devices)
        self.scanning_thread.start()

    def stop_scanning(self):
        self.stop_scanning.set()
        self.scanning_thread.join()

    def get_devices(self):
        with self.lock:
            return list(self.devices)

# Przykład użycia
if __name__ == "__main__":
    scanner = DeviceScanner()
    scanner.start_scanning()
    
    try:
        while True:
            devices = scanner.get_devices()
            print("Podłączone urządzenia:", devices)
            time.sleep(2)
    except KeyboardInterrupt:
        scanner.stop_scanning()
        print("Zatrzymano skanowanie.")
