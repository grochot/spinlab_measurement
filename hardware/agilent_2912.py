from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range, strict_discrete_set
from pymeasure.adapters import Adapter
from time import sleep

import logging
log = logging.getLogger(__name__) 
log.addHandler(logging.NullHandler())



class Agilent2912(Instrument):
    def __init__(self, adapter, name="Agilent 2912 SourceMeter", **kwargs):
        kwargs.setdefault('read_termination', '\n')
        super().__init__(
            adapter,
            name,
            **kwargs
        )

        
        self.ChA=Channel(self,'1')
        self.ChB=Channel(self,'2')



    #errors itp

'''    def opc(self):
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
        self.write(':SENS{ch}%s:CURR:PROT %s'%(channel,current))
        
    def enable_source(self):
        self.write(":OUTP ON")
   
    def measure_current(self, nplc=1, current=1.05e-4,channel=1, auto_range=True):
        """ Configures the measurement of current.

        :param nplc: Number of power line cycles (NPLC) from 0.01 to 10
        :param current: Upper limit of current in Amps, from -3.03 A to 3.03 A
        :param auto_range: Enables auto_range if True, else uses the set current
        """
        self.opc()
        self.write(":SENS{ch}:FUNC 'CURR';"
                    ":SENS{ch}:CURR:NPLC %s;:FORM:ELEM:SENS{ch} CURR;" % nplc)
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
        self.write(':SENS{ch}%s:VOLT:PROT %s'%(channel,voltage))
    
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

    def arm_source(self,arm_source):
        self.write(':ARM:SOUR %s'%arm_source)

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
        self.disable_source(channel)'''


class Channel:
    def __init__(self, instrument, channel):
        self.instrument = instrument
        self.channel = channel

    def prepare_command(self,cmd):
        while self.instrument.ask("*OPC?")==1:
            sleep(350/1000)
        return cmd.replace('{ch}',str(self.channel))

    def ask(self, cmd):
        return self.instrument.ask(self.prepare_command(cmd))

    def write(self, cmd):
        print("to ten write")
        self.instrument.write(self.prepare_command(cmd))
    
    source_mode = Instrument.control(
        ":SOUR{ch}:FUNC?", ":SOUR{ch}:FUNC %s",
        """ A string property that controls the source mode, which can
        take the values 'current' or 'voltage'. """,
        validator=strict_discrete_set,
        values={'CURR': 'CURR', 'VOLT': 'VOLT'},
        map_values=True
    )
    voltage_range = Instrument.control(
        ":SOUR{ch}:VOLT:RANG?", ":SOUR{ch}:VOLT:RANG:AUTO OFF;:SOUR{ch}:VOLT:RANG %g",
        """ A floating point property that controls the measurement voltage
        range in Volts, which can take values from -210 to 210 V.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[-210, 210]
    )
    compliance_current = Instrument.control(
        ":SENS{ch}:CURR:PROT?", ":SENS{ch}:CURR:PROT %g",
        """ A floating point property that controls the compliance current
        in Amps. """,
        validator=truncated_range,
        values=[-3.03, 3.03]
    )

    def enable_source(self):
        self.write(":OUTP ON")
    
    def measure_current(self, nplc=1, current=1.05e-4, auto_range=True):
        """ Configures the measurement of current.

        :param nplc: Number of power line cycles (NPLC) from 0.01 to 10
        :param current: Upper limit of current in Amps, from -3.03 A to 3.03 A
        :param auto_range: Enables auto_range if True, else uses the set current
        """
       
        self.write(":SENS{ch}:FUNC 'CURR';"
                    ":SENS{ch}:CURR:NPLC %f;:FORM:ELEM:SENS{ch} CURR;" % nplc)
        if auto_range:
            self.write(":SOUR{ch}:CURR:RANG:AUTO ON;")
        else:
            self.current_range = current
        self.check_errors()

    current_range = Instrument.control(
        ":SOUR{ch}:CURR:RANG?", ":SOUR{ch}:CURR:RANG:AUTO OFF;:SOUR{ch}:CURR:RANG %g",
        """ A floating point property that controls the measurement current
        range in Amps, which can take values between -3.03 and +3.03 A.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[-3.03, 3.03]
    )   
    compliance_voltage = Instrument.control(
        ":SENS{ch}:VOLT:PROT?", ":SENS{ch}:VOLT:PROT %g",
        """ A floating point property that controls the compliance voltage
        in Volts. """,
        validator=truncated_range,
        values=[-210, 210]
    ) 
    def measure_voltage(self, nplc=1, voltage=21.0, auto_range=True):
        """ Configures the measurement of voltage.

        :param nplc: Number of power line cycles (NPLC) from 0.01 to 10
        :param voltage: Upper limit of voltage in Volts, from -210 V to 210 V
        :param auto_range: Enables auto_range if True, else uses the set voltage
        """
        self.write(":SENS{ch}:FUNC 'VOLT';"
                    ":SENS{ch}:VOLT:NPLC %f;:FORM:ELEM:SENS{ch} VOLT;" % nplc)
        if auto_range:
            self.write(":SOUR{ch}:VOLT:RANG:AUTO ON;")
        else:
            self.voltage_range = voltage
        self.check_errors()
    
    def shutdown(self):
        self.write(":OUTP OFF")

    def config_average(self, average):
        # self.write(":SENS{ch}e:AVERage:TCONtrol REP")
        # self.write(":SENS{ch}e:AVERage:COUNt {}".format(average))
        self.write(":TRIG:COUN {}".format(average))
    
    source_voltage = Instrument.control(
        ":SOUR{ch}:VOLT?", ":SOUR{ch}:VOLT %g",
        """ A floating point property that controls the source voltage
        in Volts. """
    )
    
    source_current = Instrument.control(
        ":SOUR{ch}:CURR?", ":SOUR{ch}:CURR %g",
        """ A floating point property that controls the source current
        in Amps. """,
        validator=truncated_range,
        values=[-1.05, 1.05]
    )

    current = Instrument.measurement(
        ":MEAS?",
        """ Reads the current in Amps, if configured for this reading.
        """
    )
   
    voltage = Instrument.measurement(
        ":MEAS?",
        """ Reads the voltage in Volt, if configured for this reading.
        """
    )


    #pulsegen

    switch_mode = Instrument.control(
        ":SOUR{ch}:FUNC:SHAP?", ":SOUR{ch}:FUNC:SHAP %s",
        """ Selects the source output shape of the specified channel. """
    )

    trigger_source = Instrument.control(
        ":TRIG:SOUR?", ":TRIG:SOUR %s",
        """ Selects the trigger source for the specified device action. """
    )

    offset = Instrument.control(
        ":SOUR{ch}:%s:IMM?", ":SOUR{ch}:%s:IMM %s",
        """ Changes the output level of the specified source channel immediately. """
    )

    amplitude = Instrument.control(
        ":SOUR{ch}:%s:TRIG?", ":SOUR{ch}:%s:TRIG %s",
        """ Changes the output level of the specified source channel immediately by receiving a trigger from the trigger source """
    )

    duration=Instrument.control(
        ":SOUR{ch}:PULS:WIDT?", ":SOUR{ch}:PULS:WIDT %s",
        """ Changes the output level of the specified source channel immediately by receiving a trigger from the trigger source """
    )

    def init(self):
        #you can pass list like 2:1
        self.write(':INIT:TRAN (@{ch})')

    def trigger(self):
        self.write("*TRG")

    def reset(self):
        self.write("*RST")


    def disable_source(self):
        self.write(":OUTP{ch} OFF")

    
 
#examples they need an instance of class
def give_one_pulse(dev):
    dev=Agilent2912("GPIB0::23::INSTR")

    ch=dev.ChA

    ch.reset()


    ch.source_mode="VOLT"
    ch.switch_mode="PULSE"
    ch.trigger_source="BUS"

    ch.offset=(0,"VOLT")
    ch.amplitude=4
    ch.duration="5e-3"
    
    
    #dev.enable_output() 
    ch.init()
    ch.trigger()

    sleep(1)
    ch.disable_source(channel=2)


def measure():
    pass





if __name__ == "__main__":
    dev=Agilent2912("GPIB0::23::INSTR")
    dev.ChA.source_mode="CURR"
    #dev.source_mode="CURR"
    #ch.insert_id(dev,'1')

    #dev.ChA.source_mode="CURR"
    #dev.ChA.source_mode2("COS")
    #dev.reset()
    #dev.disable(channel=1)
    #dev.compliance_voltage(1e-3,1)
    #dev.opc()
    #dev.cls()
    #give_one_pulse(dev)
    #dev.init()
    #dev.trigger()
    #clear_error(dev)

    pass