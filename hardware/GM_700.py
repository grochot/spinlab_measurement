import pyvisa
from time import sleep


class GM700:
    def __init__(self, port, read_terminator="\n", write_terminator="\r", delay=0.1):
        self.port = port
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource(
            port,
            baud_rate=9600,
            timeout=3000,
            parity=pyvisa.constants.Parity.none,
            data_bits=8,
            stop_bits=pyvisa.constants.StopBits.one,
            read_termination=read_terminator,
            write_termination=write_terminator,
        )
        self.delay = delay
        self.units = ["T", "mT", "G", "kG"]
        self.modes = ["Relative", "Absolute"]

    def write(self, command):
        self.inst.write(command)
        sleep(self.delay)
        echo = self.inst.read()
        return echo

    def query(self, command, query_delay=None):
        if not query_delay:
            query_delay = self.delay
        self.inst.write(command)
        sleep(query_delay)
        echo = self.inst.read()
        sleep(query_delay)
        response = self.inst.read()
        return response

    def measure(self):
        self.write("MEAS")
        status = int(self.query("*STB?"))
        while not (status & 1):
            sleep(self.delay)
            status = int(self.query("*STB?"))
        field = self.query("MEAS?")
        return field

    def set_unit(self, unit: str):
        if unit not in self.units:
            raise Exception(f"Provided unit: '{unit}' is not supported. Supported units: {self.units}!")

        self.write(f"UNITS {unit}")

    def get_unit(self):
        return self.query("UNITS?")

    def set_mode(self, mode: str):
        if mode not in self.modes:
            raise Exception(f"Provided mode: '{mode}' is not supported. Supported modes: {self.modes}!")

        self.write(f"MODE {mode}")

    def get_mode(self):
        return self.query("MODE?")

    def set_reference(self, reference: float):
        self.write(f"REF {reference}")

    def get_reference(self):
        return self.query("REF?")
    
    def reset(self):
        self.write("*RST")

    def close(self):
        self.inst.close()
        self.rm.close()


if __name__ == "__main__":
    gm = GM700("ASRL3::INSTR")
    print(gm.set_unit("G"))
    sleep(1)
    print(gm.measure())
    gm.close()
