from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

from time import sleep

import logging
log = logging.getLogger(__name__) 
log.addHandler(logging.NullHandler())



class Agilent2912(Instrument):
    def __init__(self, resourceName, **kwargs):
        kwargs.setdefault('read_termination', '\n')
        super().__init__(
            resourceName,
            "Agilent 2912",
            includeSCPI=True,
            **kwargs
        )

        
        self.ChA=Channel('1')
        self.ChB=Channel('2')


    def opc(self):
        while self.ask("*OPC?")==1:
            sleep(350/1000)

    def select_channel(self, channel):
        log.error("Not implemented yet")

    def source_mode(self,source_type,channel=1):
        #source_mode=[VOLT,CURR]
        self.opc()
        self.write(':SOUR%s:FUNC:MODE %s'%(channel,source_type))

    def source_voltage_range(self, voltage,channel):
        self.opc()
        self.write(":SOUR%s:VOLT:RANG:AUTO OFF;:SOUR%s:VOLT:RANG %s"%(channel,channel,voltage))

    def compliance_current(self, current,channel=1):
        self.opc()
        self.write(':SENS%s:CURR:PROT %s'%(channel,current))
        
    def enable_source(self):
        self.write(":OUTP ON")
   
    def measure_current(self, nplc=1, current=1.05e-4,channel=1, auto_range=True):
        """ Configures the measurement of current.

        :param nplc: Number of power line cycles (NPLC) from 0.01 to 10
        :param current: Upper limit of current in Amps, from -3.03 A to 3.03 A
        :param auto_range: Enables auto_range if True, else uses the set current
        """
        self.opc()
        self.write(":SENS:FUNC 'CURR';"
                    ":SENS:CURR:NPLC %s;:FORM:ELEM:SENS CURR;" % nplc)
        if auto_range:
            self.opc()
            self.write(":SOUR:CURR:RANG:AUTO ON;")
        else:
            self.opc()
            self.current_range = self.compliance_current(current,channel)
        self.check_errors()
       
    def source_current_range(self, range,channel):
        self.opc()
        self.write(":SOUR%s:CURR:RANG:AUTO OFF;:SOUR%s:CURR:RANG %s"%(channel,channel,range))

    def voltage_nplc(self, nplc):
        log.error("Not implemented yet")
    
    def compliance_voltage(self, voltage,channel=1):
        self.write(':SENS%s:VOLT:PROT %s'%(channel,voltage))
    
    def current_nplc(self, nplc):
        log.error("Not implemented yet")

    def measure_voltage(self, nplc=1, voltage=21.0,channel=1, auto_range=True):
        """ Configures the measurement of voltage.

        :param nplc: Number of power line cycles (NPLC) from 0.01 to 10
        :param voltage: Upper limit of voltage in Volts, from -210 V to 210 V
        :param auto_range: Enables auto_range if True, else uses the set voltage
        """

        self.opc()
        self.write(":SENS%s:FUNC 'VOLT';"
                    ":SENS%s:VOLT:NPLC %s;:FORM:ELEM:SENS%s VOLT;" % (channel,channel,nplc,channel))
        if auto_range:
            self.opc()
            self.write(":SOUR:VOLT:RANG:AUTO ON;")
        else:
            self.opc()
            self.voltage_range = self.source_voltage_range(voltage,channel)
        self.check_errors()
   
    def shutdown(self):
        self.opc()
        self.write(":OUTP OFF")

    def source_voltage(self, voltage,channel):
        self.opc()
        self.write(":SOUR%s:VOLT %g"%(channel,voltage))


    def source_current(self, current,channel):
        self.opc()
        self.write(":SOUR%s:CURR %s"%(channel,current))
   
    def current(self,channel):
        """ Reads the current in Amps, if configured for this reading.
        """
        self.opc()
        return self.ask(":MEAS? (@%s)"%channel)
    
    def voltage(self,channel):
        """ Reads the voltage in Volt, if configured for this reading.
        """
        self.opc()
        return self.ask(":MEAS? (@%s)"%channel)
        
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

    def high_z_source(self,channel=1):
        log.warning("Using exscessed function")
        self.disable_source(channel)

class Channel():

    def __init__(self,channel):
        self.channel=channel

    source_mode = Instrument.control(
        ":SOUR:FUNC?", ":SOUR{}:FUNC %s".format(self.channel),
        """ A string property that controls the source mode, which can
        take the values 'current' or 'voltage'. """,
        validator=strict_discrete_set,
        values={'CURR': 'CURR', 'VOLT': 'VOLT'},
        map_values=True
    )
    
 
#examples they need an instance of class
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


def measure():
    pass





if __name__ == "__main__":
    dev=Agilent2912("GPIB0::23::INSTR")
    dev.ChA.source_mode="CURR"
    #dev.reset()
    #dev.disable(channel=1)
    #dev.compliance_voltage(1e-3,1)
    dev.opc()
    #dev.cls()
    #give_one_pulse(dev)
    #dev.init()
    #dev.trigger()
    #clear_error(dev)

    pass