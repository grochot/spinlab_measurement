import pyvisa
import time
import random
import matplotlib.pyplot as plt
import pandas as pd
import os

from hardware.fgen import *
from SourceMeterDriver import *
from hardware.stepper import *
from FieldDriverLockIn import *
from GaussmeterDriver import *
from SpectrumDriver import *
from DataStorage import *

from scipy.optimize import curve_fit


def calF(x, a, b):
    return x * a + b


if __name__ == "__main__":
    field = FieldDriverLockIn('GPIB0::13::INSTR', 1, 50, 0.5, 2)
    gauss = GaussmeterDriver('GPIB0::12::INSTR')

    voltages = list(np.arange(0, 2.2, 0.2))
    fields = []

    for v in voltages:
        field.setRAW(v)
        time.sleep(1)
        H = gauss.read()
        fields.append(H)
        print("V = {:2.2f} => H = {:4.2f}".format(v, H))

    plt.plot(voltages, fields, '*r')
    plt.xlabel('Voltage [V]')
    plt.ylabel('Field [Oe]')

    #const = voltages[-1]/fields[-1]

    popt, pcov = curve_fit(calF, fields, voltages)
    const = popt[0]
    print("Const = {:.10f}".format(const))

    plt.plot(voltages, np.array(voltages) / const, '--g')
    plt.show()

    field.setGain(const)

    fieldsSet = np.linspace(0, abs(fields[-1]), 10)
    fields = []

    for H in fieldsSet:
        field.setFieldSlow(H)
        time.sleep(1)
        Hr = gauss.read()
        fields.append(Hr)
        print("H_set = {:4.2f} => H = {:4.2f}".format(H, Hr))

    plt.plot(fieldsSet, fields, '*r')
    plt.xlabel('Field set [Oe]')
    plt.ylabel('Field [Oe]')

    plt.plot(fieldsSet, fieldsSet, '--g')
    plt.show()
    print("Const = {:.10f}".format(const))



