import numpy as np 
from scipy.optimize import curve_fit
from time import sleep
from matplotlib import pyplot as plt
from hardware.daq import DAQ
from hardware.lakeshore import Lakeshore

start = 0
stop = 1
points = 5

delay = 1

address_daq= "Dev4/ao0"
address_gaussmeter = "GPIB1::12::INSTR"

daq = DAQ(address_daq)
gaussmeter = Lakeshore(address_gaussmeter)

def linear_func(x,a,b):
    return a*x+b

voltages = np.linspace(start, stop, points)
fields = []

plt.ion()  # Turn on interactive mode

fig, ax = plt.subplots()
line, = ax.plot(voltages, fields, 'b-', label='data')
fit_line, = ax.plot(voltages, voltages * 0, 'r-', label='fit: a=0, b=0')
ax.set_xlabel('Voltage')
ax.set_ylabel('Field')
ax.legend()

for i in voltages:
    daq.set_field(i)
    sleep(delay)
    
    result = gaussmeter.measure()
    
    if type(result) != int and type(result) != float:
        result = 0
    
    fields.append(result)
    
    # Update the plot with new data
    line.set_ydata(fields)
    popt, pcov = curve_fit(linear_func, voltages, fields)
    fit_line.set_ydata(linear_func(voltages, *popt))
    fit_line.set_label('fit: a=%5.3f, b=%5.3f' % tuple(popt))
    ax.legend()
    plt.draw()
    plt.pause(0.1)

plt.ioff()  # Turn off interactive mode at the end
plt.show()
