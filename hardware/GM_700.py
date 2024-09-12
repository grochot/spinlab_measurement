from pymeasure.instruments import Instrument
import pyvisa
import time


class GM700(Instrument):
    def __init__(self, resource_name, **kwargs):
        kwargs.setdefault("baud_rate", 9600)
        kwargs.setdefault("data_bits", 8)
        kwargs.setdefault("parity", pyvisa.constants.Parity.none)
        kwargs.setdefault("stop_bits", pyvisa.constants.StopBits.one)
        kwargs.setdefault("write_termination", "\r")
        kwargs.setdefault("read_termination", "\n")
        super().__init__(resource_name, "GM700", **kwargs)

    def query(self, command):
        """Send command and ignore the echoed command in the response"""
        self.write(command)
        time.sleep(0.1)
        echo = self.read()
        response = self.read()
        return response


if __name__ == "__main__":
    device = GM700("ASRL8::INSTR")
    response = device.query("*IDN?")
    print(f"Response: {response}")
    
    device.shutdown()


