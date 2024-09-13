import serial
import time


class GM700():
    def __init__(self, port, read_term='\n', write_term='\r'):
        self.port = port
        self.ser = serial.Serial(port, baudrate=9600, timeout=1)
        self.read_term = read_term
        self.write_term = write_term
        
    def query(self, command, query_delay=0.1):
        self.ser.write(command.encode())
        time.sleep(query_delay)
        echo = self.ser.readline().decode().strip()
        response = self.ser.readline().decode().strip()
        return response
    
    def shutdown(self):
        self.ser.close()
        print("Connection closed")


if __name__ == "__main__":
    gm = GM700("COM8")
    print(gm.query("*IDN?\n"))
    gm.shutdown()


