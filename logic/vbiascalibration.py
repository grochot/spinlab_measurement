import numpy as np 
from scipy.optimize import curve_fit

def func(x, a, b, c):
    return (1/(a*x+b))+c
def linear_func(x,a,b):
    return a*x+b

def vbiascalibration(vbias_list, vs_list, typ="linear"):
    if typ == "1/x":
        popt, pcov = curve_fit(func, vbias_list, vs_list)
    elif typ == "linear":
        popt, pcov = curve_fit(linear_func, vbias_list, vs_list )
    return popt

def calculationbias(vin, a,b,c=0, typ="linear"):
    if typ == "1/x":
        return (1-float(vin)*b+c*b)/(float(vin)*a-c*a)
    elif typ == "linear":
        return (float(vin)-b)/a


# wynik = calculationbias(0.1, -1439.5638741955333, 235.0248602114991, 246.80517253562815)
# print(wynik)