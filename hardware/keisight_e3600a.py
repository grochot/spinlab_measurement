from pymeasure.instruments import Instrument 
import pyvisa 
from time import sleep
import numpy as np

class E3600a(Instrument):
    def __init__(self, adapter, read_termination="\n", **kwargs):
        super().__init__(
            adapter,
            "Keysight E3600a" ,
            read_termination=read_termination,
            **kwargs
        )

    def enabled(self):
        self.write(':OUTput ON')
    
    def remote(self):
        self.write(':SYSTem:REMote')    
    
    def outputselect(self,channel=1):
        self.write(':INSTrument:NSELect %G' % channel)
        
    def shutdown(self, vol=0):
        self.vec = np.linspace(vol,0,5)
        for i in self.vec:  
            print(i)
            self.write(":APPLy 8.0, %G" % i)
            sleep(0.4)
        self.write(":APPLy 0.0, 0.0")
        self.write(':OUTput OFF')
    
    def set_field(self, vol = 0): 
        if vol < 0:
            
            self.write(':INSTrument:NSELect 1')
            self.write(':APPLy 0, 0')
            self.write(':OUTput OFF')
            self.write(':INSTrument:NSELect 2')
            self.write(':APPLy 8, %G' % abs(vol))
            self.write(':OUTput ON')
        else: 
            self.write(':INSTrument:NSELect 2')
            self.write(':APPLy 0, 0')
            self.write(':OUTput OFF')
            self.write(':INSTrument:NSELect 1')
            self.write(':APPLy 8, %G' % abs(vol))
            self.write(':OUTput ON')
    
    def disable_now(self):
        self.write(':OUTput OFF')

    def reset(self):
        self.write("*CLS")
    


# from pymeasure.instruments import Instrument 
# import pyvisa 
# from time import sleep
# import numpy as np

# class E3600a(Instrument):
#     def __init__(self, adapter, read_termination="\n", **kwargs):
#         super().__init__(
#             adapter,
#             "Keysight E3600a" ,
#             read_termination=read_termination,
#             **kwargs
#         )

#     def enabled(self):
#         self.write(':OUTput ON')
    
#     def remote(self):
#         self.write(':SYSTem:REMote')    
    
#     def outputselect(self,channel=1):
#         self.write(':INSTrument:NSELect %G' % channel)
    
#     def disabled(self, vol):
#         self.vec = np.linspace(vol,0,5)
#         for i in self.vec:  
#             self.write(":APPLy 8.0, %G" % i)
#             sleep(0.4)
#         self.write(":APPLy 0.0, 0.0")
#         self.write(':OUTput OFF')
    
#     def current(self, curr = 0): 
#         self.write(":APPLy 8.0, %G" % curr)
    
#     def disable_now(self):
#         self.write(":APPLy 0.0, 0.0")
#         self.write(':OUTput OFF')
    
#     def reset(self):
#         self.write('*CLS')
    
#     def get_current(self):
#         self.write("*IDN?")
#         sleep(0.3)
#         answer = self.read()
#         return answer 
#     def test(self):
#         self.write(":INSTrument:SELect OUT1")
#         # self.write(":VOLTage:TRIGgered 8")
#         # self.write(":CURRent:TRIGgered 0.013")
#         # # self.write("INST:SEL OUT2")
#         # # self.write("VOLT TRIG 0")
#         # # self.write("CURR TRIG 0")
#         # #self.write(":INSTrument:COUPle:TRIGger ON")
#         # self.write(":TRIGger:SOURce IMM")
#         # self.write(":INITiate")
#         self.write("APPLy 0.0, 0.000")
#         # self.write(":OUTput OFF")



    
   
# # field = E3600a('ASRL/dev/ttyUSB0::INSTR')    
# # field.remote()
# # #field.test()
# # field.outputselect(2)
# # field.current(0.002)
# # sleep(1)
# # #field.disable_now()
# # field.enabled()


# #field.get_current()