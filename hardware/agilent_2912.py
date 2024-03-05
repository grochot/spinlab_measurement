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

    def source_mode(self,source_type,channel=1):
        #source_mode=[VOLT,CURR]
        self.opc()
        self.write(':SOUR%s:FUNC:MODE %s'%(channel,source_type))

    def source_voltage_range(self, voltage):
        pass

    def compliance_current(self, current,channel=1):
        self.write(':SENS%s:CURR:PROT %s'%(channel,current))
        
    def enable_source(self):
        pass
   
    def measure_current(self):
        pass
       
    def source_current_range(self, range):
        pass
    def voltage_nplc(self, nplc):
        pass
    
    def compliance_voltage(self, voltage,channel=1):
        self.write(':SENS%s:VOLT:PROT %s'%(channel,voltage))
    
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
    def opc(self):
        while self.ask("*OPC?")==1:
            sleep(350/1000)
        
    def duration(self,time,channel=1):
        self.opc()
        self.write(":SOUR%s:PULS:WIDT %s"%(channel,time))

    def switch_mode(self,shape,channel=1):
        #shape=["DC","PULSE"]
        self.opc()
        self.write(":SOUR%s:FUNC:SHAP %s"%(channel,shape))



    def offset(self,amplitude,source_mode,channel=1):
        #source_mode=[VOLT,CURR]
        self.opc()
        self.write(":SOUR%s:%s:IMM %s"%(channel,source_mode,amplitude))

    def amplitude(self,amplitude,channel=1):
        self.opc()
        self.write("SOUR%s:VOLT:TRIG %s"%(channel,amplitude))

    def trigger(self):
        self.opc()
        self.write("*TRG")

    def reset(self):
        self.opc()
        self.write("*RST")

    def trigger_source(self,trigger_source):
        self.opc()
        self.write(':TRIG:SOUR %s'%trigger_source)

    '''def arm_source(self,arm_source):
        self.write(':ARM:SOUR %s'%arm_source)'''

    def init(self,channel=1):
        #you can pass list like 2:1
        self.opc()
        self.write(':INIT:TRAN (@%s)'%channel)

    def enable_source(self,channel=1):
        self.opc()
        self.write(":OUTP%s ON"%(channel))

    def disable_source(self,channel=1):
        self.opc()
        self.write(":OUTP%s OFF"%channel)

    def cls(self):
        self.opc()
        self.write("*CLS")



#examples
def give_one_pulse(dev):
    #dev=Agilent2912("GPIB0::23::INSTR")
    dev.reset()


    dev.source_mode("VOLT",channel=2)
    dev.switch_mode("PULSE",channel=2)
    dev.trigger_source("BUS")

    dev.offset(0,"VOLT",channel=2)
    dev.amplitude(4,channel=2)
    dev.duration("5e-3",channel=2)
    
    
    #dev.enable_output() 
    dev.init(channel=2)
    dev.trigger()

    sleep(1)
    dev.disable_source(channel=2)

def clear_error(dev):
    #dev=Agilent2912("GPIB0::23::INSTR")
    dev.cls()


if __name__ == "__main__":
    dev=Agilent2912("GPIB0::23::INSTR")
    #dev.reset()
    #dev.disable(channel=1)
    dev.compliance_voltage(1e-3,1)
    #dev.opc()
    #dev.cls()
    #give_one_pulse(dev)
    #dev.init()
    #dev.trigger()
    #clear_error(dev)

    pass