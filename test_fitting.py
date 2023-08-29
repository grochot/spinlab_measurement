import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt

from logic.fit_parameters_to_file import fit_parameters_to_file, fit_parameters_from_file
from logic.vbiascalibration import vbiascalibration, calculationbias, func

def generate_data():
    xdata = np.linspace(0, 4, 50) 
    y = func(xdata, 2.5, 1.3, 0.5)
    rng = np.random.default_rng()
    y_noise = 0.2 * rng.normal(size=xdata.size)
    ydata = y + y_noise
    return xdata, ydata


xdata, ydata = generate_data()

popt = vbiascalibration(xdata, ydata)
print(popt)

fit_parameters_to_file(popt)

popt_wczytane= fit_parameters_from_file()

print(popt_wczytane)

point_test = 0.5
ydata_fit = calculationbias(point_test, popt_wczytane)
print(ydata_fit) 

plt.plot(xdata, ydata, 'b-', label='data')
plt.plot(point_test, ydata_fit, 'ro', label='fit')
plt.legend()
plt.show()