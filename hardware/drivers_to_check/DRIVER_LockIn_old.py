import pyvisa
from plotSleep import plotSleep
import numpy as np
import time


class DriverLockIn:
    def __init__(self, address, gain, step, delay, dac) -> None:
        self.address = address
        self.gain = gain
        self.step = step
        self.delay = delay
        self.dac = dac

        self.rm = None
        self.device = None
        self.sen_range = None

        self.range_lut = {
            0: 100e-9,
            1: 300e-9,
            2: 1e-6,
            3: 3e-6,
            4: 10e-6,
            5: 30e-6,
            6: 100e-6,
            7: 300e-6,
            8: 1e-3,
            9: 3e-3,
            10: 10e-3,
            11: 30e-3,
            12: 100e-3,
            13: 300e-3,
            14: 1,
            15: 3
        }

    def __enter__(self):
        self.rm = pyvisa.ResourceManager()
        self.device = self.rm.open_resource(self.address)

        self.device.read_termination = '\r'
        self.device.write_termination = '\r'

        print("lockIN = " + self.query('ID'))
        self.write('DD 44')

        self.input_mode = int(self.query('N'))
        sen_range_code = int(self.query('SEN'))

        self.sen_range = self.range_lut[sen_range_code]

        self.write('D2 0')

        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        print("########### LockIn close method ###########\n"
              " disabling field and closing communication\n"
              "###########################################")

        self.set_field_slow(0)
        self.device.close()
        self.rm.close()

    def write(self, command):
        self.device.write(command)
        start = time.time()
        while not (self.device.read_stb() & (1 << 0)):
            if time.time()-start > 0.1:
                print("!write timout!")
                return
            pass

    def query(self, command):
        return self.device.query(command)

    def read_out(self):
        output_uncal = int(self.query('OUT'))

        output_calib = output_uncal * self.sen_range * pow(10, -5)
        output_calib = output_calib

        return output_calib

    def read_DAC(self, dac):
        if dac == 1:
            b1 = int(self.query('PEEK 65624'))
            b2 = int(self.query('PEEK 65625'))
        else:
            b1 = int(self.query('PEEK 65622'))
            b2 = int(self.query('PEEK 65623'))
        if b2 < 0:
            b2 = b2 + 256
        b2 = b2 / 2
        b1 = b1 / 2
        b1 = b1 * 256
        v = b1 + b2
        v = v / 1000
        return v

    def set_DAC(self, dac, voltage):
        voltage = voltage * 1000
        self.write(f'DAC {dac} {int(voltage)}')

    def get_field(self):
        return self.read_DAC(self.dac) / self.gain

    def set_field(self, field):
        self.set_DAC(self.dac, field * self.gain)

    def set_field_slow(self, field):
        step = self.step
        plotSleep(0.05)
        act_field = self.get_field()
        if abs(act_field - field) > step:
            if act_field > field:
                step = -step
            for f in np.arange(act_field + step, field, step):
                self.set_field(f)
                plotSleep(self.delay)
        self.set_field(field)

    def set_reference(self, n: int):
        """
        Reference channel source control.
        n : selection 0 -> external; 1 -> internal
        """

        self.write(f"IE {n}")
