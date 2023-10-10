#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from pymeasure.instruments import Instrument


class Agilent34410A(Instrument):
    def __init__(self, adapter, name="HP/Agilent/Keysight 34410A Multimeter", **kwargs):
        super().__init__(
            adapter, name, **kwargs
        )
    def resolution(self, resolution):
        pass
    def range(self, range):
        self.write("CONF:%s\n" % range)
    def autorange(self, autorange):
        pass
    def function(self, function):
        pass
    def average(self, average):
        pass
    
    def current_dc(self):
        current_dc = Instrument.measurement("MEAS:CURR:DC? DEF,DEF", "DC current, in Amps")
        return current_dc
    def voltage_dc(self):
        voltage_dc = Instrument.measurement("MEAS:VOLT:DC? DEF,DEF", "DC voltage, in Volts")
        return voltage_dc

