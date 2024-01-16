import pyvisa 
from time import sleep
from pyvisa.constants import StopBits, Parity
from pyvisa import constants
rm = pyvisa.ResourceManager() 
print(rm.list_resources()) 
# inst = rm.open_resource('USB0::2733::309::032163928::0::INSTR')  

#inst = rm.open_resource('GPIB0::24::INSTR')
# inst.timeout = 2000

# sleep(2)
# inst.write('*VOLT?')
# sleep(2)
# print(inst.read())
# # inst.write('*RST')
# #sleep(2)
# inst.write('VOLT 4')
# sleep(2)
# # inst.write('OPON 1')
# # sleep(2)
# inst.write("VOLT?")
# sleep(2)
# print(inst.read())
# # sleep(2)
# # #print(inst.read())

# print(inst.query('*IDN?'))
# inst.close()
