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

    #[:SOURce]:PULSe:WIDTh #czas trwania -ok

    #pewnie sie nie przyda [:SOURce]:FUNCtion:MODE #przelaczenie trybu -ok

    #[:SOURce]:FUNCtion[:SHAPe] #przelaczanie trybu -ok

    #[:SOURce]:<CURRent|VOLTage>[:LEVel][:IMMediate][:AMPLitude] #amplituda

    
    #[:SOURce]:TOUTput:SIGNal ustawia trigger (tym triggerem potem strzela sie impulsem)
            

    def duration(self,time,channel=1):
        self.write(":SOUR%s:PULS:WIDTh %s"%(channel,time))

    def switch_mode(self,shape,channel=1):
        #shape=["DC","PULSE"]
        self.write(":SOUR%s:FUNC:SHAP %s"%(channel,shape))

    def amplitude(self,amplitude,channel=1):
        self.write(":SOUR%s:VOLT:IMM:AMPL %s"%(channel,amplitude))

    def give_one_pulse():
        pass






    def test_command(self):
        print(self.ask(":SOUR1:PULS:WIDTh?"))

    def test_command2(self):
        self.write(":ARM:TRAN:IMMediate @1")

    def test_command3(self):
        self.write(":PULS:WIDT 2E-2")
            

if __name__:
    
    dev=Agilent2912("GPIB0::23::INSTR")
    dev.switch_mode("PULSE","1")
    dev.duration("1E-4")
    dev.amplitude(1)
    dev.test_command()
    #dev.test_command3()
    dev.test_command2()
    print("dziala")