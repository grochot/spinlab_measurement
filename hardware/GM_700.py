import pyvisa
import time


class GM700:
    def __init__(self, port, read_terminator="\n", write_terminator="\r"):
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


if __name__ == "__main__":
    gm = GM700("ASRL8::INSTR")
    gm.inst.write("")
    time.sleep(1)
    gm.inst.write("*IDN?")
    print(gm.inst.read())
    time.sleep(0.1)
    print(gm.inst.read())
    # gm.inst.close()
