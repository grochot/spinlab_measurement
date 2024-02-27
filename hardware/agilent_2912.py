from pymeasure.instruments import Instrument
from time import sleep

######## TO DO #########
class Agilent2912(Instrument):
    def __init__(self, resourceName, **kwargs):
        kwargs.setdefault('read_termination', '\n')
        super().__init__(
            resourceName,
            "Agilent 2912",
            includeSCPI=True,
            **kwargs
        )

    def select_channel(self, channel):
       pass

    def source_mode(self, source_type):
       pass

    def source_voltage_range(self, voltage):
        pass

    def compliance_current(self, current):
        pass
        
    def enable_source(self):
        pass
   
    def measure_current(self):
        pass
       
    def source_current_range(self, range):
        pass
    def voltage_nplc(self, nplc):
        pass
    def compliance_voltage(self, voltage):
        pass
    
    def current_nplc(self, nplc):
        pass

    def measure_voltage(self):
        pass
   
    def shutdown(self):
        pass

    def source_voltage(self, voltage):
        pass
    def source_current(self, current):
        pass
   
    def current(self):
        pass
    
    def voltage(self):
        pass



#Mariusz
    def WAI(self):
        #pozwala zaczekać aż dana procedura się zakończy
        while self.qr("*OPC?")==1:
        	time.sleep(50/1000)
        #return self.write("*WAI")

    #[:SOURce]:PULSe:WIDTh #czas trwania

    #pewnie sie nie przyda [:SOURce]:FUNCtion:MODE #przelaczenie trybu 

    #[:SOURce]:FUNCtion[:SHAPe] #przelaczanie trybu

    #[:SOURce]:<CURRent|VOLTage>[:LEVel][:IMMediate][:AMPLitude] #amplituda

    
    #[:SOURce]:TOUTput:SIGNal ustawia trigger (tym triggerem potem strzela sie impulsem)