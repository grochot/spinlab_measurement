from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range, strict_discrete_set
from pymeasure.adapters import Adapter
from time import sleep
import time

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


    #def reset(self):
    #    print("ogolny reset")
    #    self.write("*RST")



    @property
    def error(self):
        """ Returns a tuple of an error code and message from a
        single error. """
        err = self.ask(':SYSTem:ERRor:ALL?')
        err = err.split(',')
        # Keithley Instruments Inc. sometimes on startup
        # if tab delimitated message is greater than one, grab first two as code, message
        # otherwise, assign code & message to returned error
        if len(err) > 1:
            err = (int(float(err[0])), err[1])
            code = err[0]
            message = err[1].replace('"', '')
        else:
            code = message = err[0]
        log.info(f"ERROR {str(code)},{str(message)} - len {str(len(err))}")
        return (code, message)

    def check_errors(self):
        """ Logs any system errors reported by the instrument.
        """
        code, message = self.error
        while code != 0:
            t = time.time()
            log.info("Agilent 2912 reported error: %d, %s" % (code, message))
            code, message = self.error
            if (time.time() - t) > 10:
                log.warning("Timed out for Keithley 2912 error retrieval.")

class Channel:
    def __init__(self, instrument, channel):
        self.instrument = instrument
        self.channel = channel


    def check_errors(self):
        return self.instrument.check_errors()
    

    def prepare_command(self,cmd):
        while self.instrument.ask("*OPC?")==1:
            sleep(450/1000)

        cmd_new=cmd.replace('{ch}',str(self.channel))
        print("AGILENT 2912:",cmd_new)
        return cmd_new

    def ask(self, cmd):
        return self.instrument.ask(self.prepare_command(cmd))

    def write(self, cmd):
        #print("to ten write")
        self.instrument.write(self.prepare_command(cmd))


    def values(self, cmd, **kwargs):
        """ Reads a set of values from the instrument through the adapter,
        passing on any key-word arguments.
        """
        return self.instrument.values(self.prepare_command(cmd))
    
    source_mode = Instrument.control(
        ":SOUR{ch}:FUNC?", ":SOUR{ch}:FUNC:MODE %s",
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
        self.write(":OUTP{ch} ON")
    
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
        ":MEAS? (@{ch})",
        """ Reads the current in Amps, if configured for this reading.
        """
    )
   
    voltage = Instrument.measurement(
        ":MEAS? (@{ch})",
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
def give_one_pulse():
    dev=Agilent2912("GPIB0::23::INSTR")

    ch=dev.ChB

    ch.reset()


    ch.source_mode="VOLT"
    ch.switch_mode="PULSE"
    ch.trigger_source="BUS"

    ch.offset=("VOLT",0)
    ch.amplitude=("VOLT",0.2)
    ch.duration="5e-3"
    
    
    #dev.enable_output()  #OLD
    ch.init()
    ch.trigger()

    sleep(1)
    ch.disable_source()





if __name__ == "__main__":
    dev=Agilent2912("GPIB0::23::INSTR")
    #ch=dev.ChB
    #dev.reset()
    #print(ch.source_mode)
    #dev.ChA.source_mode="CURR"
    give_one_pulse()

    pass