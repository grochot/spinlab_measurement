# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import logging
import time
import numpy as np
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

# Setup logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Keithley2636(Instrument):
    """Represents the Keithley 2600 series (channel A and B) SourceMeter"""

    def __init__(self, adapter, name="Keithley 2600 SourceMeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
        self.ChA=Channel(self, 'a')
        self.ChB = Channel(self, 'b')
        #self.reset()


    @property
    def error(self):
        """ Returns a tuple of an error code and message from a
        single error. """
        err = self.ask('print(errorqueue.next())')
        err = err.split('\t')
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
            log.info("Keithley 2636 reported error: %d, %s" % (code, message))
            code, message = self.error
            if (time.time() - t) > 10:
                log.warning("Timed out for Keithley 2636 error retrieval.")

    def opc(self): 
        kk= self.ask("*OPC?")
        return kk
    


class Channel:

    def __init__(self, instrument, channel):
        self.instrument = instrument
        self.channel = channel


    def check_errors(self):
        return self.instrument.check_errors()
    

    def prepare_command(self,cmd):
        while self.instrument.ask("*OPC?")=="1":
            time.sleep(350/1000)
        cmd_new=cmd.replace('{ch}',str(self.channel))
        print("KEITHLEY 2636:",cmd_new)
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
        return self.instrument.values('print(%s)'%self.prepare_command(cmd))


    '''def ask(self, cmd):
        return float(self.instrument.ask(f'print(smu{self.channel}.{cmd})'))
    
    def askall(self, cmd):
        return self.instrument.ask(f'print({cmd})')

    def write(self, cmd):
        self.instrument.write(f'smu{self.channel}.{cmd}')
    
    def writeall(self, cmd):
        self.instrument.write(f'{cmd}')

    def values(self, cmd, **kwargs):
        """ Reads a set of values from the instrument through the adapter,
        passing on any key-word arguments.
        """
        return self.instrument.values(f'print(smu{self.channel}.{cmd})')

    def binary_values(self, cmd, header_bytes=0, dtype=np.float32):
        return self.instrument.binary_values('print(smu%s.%s)' %
                                             (self.channel, cmd,), header_bytes, dtype)

    def check_errors(self):
        return self.instrument.check_errors()'''

    source_output = Instrument.control(
        'smu{ch}.source.output', 'smu{ch}.source.output=%d',
        """Property controlling the channel output state (ON of OFF)
        """,
        validator=strict_discrete_set,
        values={'OFF': 0, 'ON': 1, 'HIGH_Z':2},
        map_values=True
    )


    source_mode = Instrument.control(
        'smu{ch}.source.func', 'smu{ch}.source.func=%d',
        """Property controlling the channel soource function (Voltage or Current)
        """,
        validator=strict_discrete_set,
        values={'voltage': 1, 'current': 0,'VOLT':1,'CURR':0},
        map_values=True
    )

    measure_nplc = Instrument.control(
        'smu{ch}.measure.nplc', 'smu{ch}.measure.nplc=%f',
        """ Property controlling the nplc value """,
    )

    ###############
    # Current (A) #
    ###############
    current = Instrument.measurement(
        'smu{ch}.measure.i()',
        """ Reads the current in Amps """
    )

    source_current = Instrument.control(
        'smu{ch}.source.leveli', 'smu{ch}.source.leveli=%f',
        """ Property controlling the applied source current """,
        validator=truncated_range,
        values=[-1.5, 1.5]
    )

    compliance_current = Instrument.control(
        'smu{ch}.source.limiti', 'smu{ch}.source.limiti=%f',
        """ Property controlling the source compliance current """,
        validator=truncated_range,
        values=[-1.5, 1.5]
    )

    source_current_range = Instrument.control(
        'smu{ch}.source.rangei', 'smu{ch}.source.rangei=%f',
        """Property controlling the source current range """,
        validator=truncated_range,
        values=[-1.5, 1.5]
    )

    current_range = Instrument.control(
        'smu{ch}.measure.rangei', 'smu{ch}.measure.rangei=%f',
        """Property controlling the measurement current range """,
        validator=truncated_range,
        values=[-1.5, 1.5]
    )

    ###############
    # Voltage (V) #
    ###############
    voltage = Instrument.measurement(
        'smu{ch}.measure.v()',
        """ Reads the voltage in Volts """
    )

    opc = Instrument.measurement(
        'opc()',
        """ Reads the voltage in Volts """
    )


    source_voltage = Instrument.control(
        'smu{ch}.source.levelv', 'smu{ch}.source.levelv=%f',
        """ Property controlling the applied source voltage """,
        validator=truncated_range,
        values=[-200, 200]
    )

    offset=Instrument.control(
        'smu{ch}.source.level%s', 'smu{ch}.source.level%s=%s',
        """ Property controlling the applied source voltage """,
        set_process=lambda v:(v[0].replace("VOLT",'v').replace("CURR",'i'),v[1])
        #validator=truncated_range,
        #values=[-200, 200]
    )

    compliance_voltage = Instrument.control(
        'smu{ch}.source.limitv', 'smu{ch}.source.limitv=%f',
        """ Property controlling the source compliance voltage """,
        validator=truncated_range,
        values=[-200, 200]
    )

    source_voltage_range = Instrument.control(
        'smu{ch}.source.rangev', 'smu{ch}.source.rangev=%f',
        """Property controlling the source current range """,
        validator=truncated_range,
        values=[-200, 200]
    )

    voltage_range = Instrument.control(
        'smu{ch}.measure.rangev', 'smu{ch}.measure.rangev=%f',
        """Property controlling the measurement voltage range """,
        validator=truncated_range,
        values=[-200, 200]
    )

    ####################
    # Resistance (Ohm) #
    ####################
    resistance = Instrument.measurement(
        'smu{ch}.measure.r()',
        """ Reads the resistance in Ohms """
    )

    wires_mode = Instrument.control(
        'smu{ch}.sense', 'smu{ch}.sense=%d',
        """Property controlling the resistance measurement mode: 4 wires or 2 wires""",
        validator=strict_discrete_set,
        values={'4': 1, '2': 0},
        map_values=True
    )


    #######################
    # Measurement Methods #
    #######################

    def measure_voltage(self, nplc=1, voltage=21.0, auto_range=True):
        """ Configures the measurement of voltage.
        :param nplc: Number of power line cycles (NPLC) from 0.001 to 25
        :param voltage: Upper limit of voltage in Volts, from -200 V to 200 V
        :param auto_range: Enables auto_range if True, else uses the set voltage
        """
        log.info("%s is measuring voltage." % self.channel)
        self.write('smu{ch}.measure.v()')
        self.write('smu{ch}.measure.nplc=%f' % nplc)
        if auto_range:
            self.write('smu{ch}.measure.autorangev=1')
        else:
            self.voltage_range = voltage
        

    def measure_current(self, nplc=1, current=1.5, auto_range=True):
        """ Configures the measurement of current.
        :param nplc: Number of power line cycles (NPLC) from 0.001 to 25
        :param current: Upper limit of current in Amps, from -1.5 A to 1.5 A
        :param auto_range: Enables auto_range if True, else uses the set current
        """
        log.info("%s is measuring current." % self.channel)
        self.write('smu{ch}.measure.i()')
        self.write('smu{ch}.measure.nplc=%f' % nplc)
        if auto_range:
            self.write('smu{ch}.measure.autorangei=1')
        else:
            self.current_range = current
       
    
    def single_pulse_prepare(self):
        log.info("generate pulse")
        #self.write('trigger.source.listv({%f})' %voltage )
        self.write('smu{ch}.trigger.source.action = smu%s.ENABLE '%self.channel)
        self.write('smu{ch}.trigger.measure.action = smu%s.DISABLE '%self.channel)
        self.write('smu{ch}.trigger.source.limiti = 0.0001') #!!!!!!!!! COMPILANCE !!!!!!!!!!!!!!!!!!!!!!
        #self.write('source.rangev = %f' %range)
        #self.writeall('trigger.timer[1].delay = %f' %time)
        self.write('trigger.timer[1].count = 1 ')
        self.write('trigger.timer[1].passthrough = false ')
        self.write('trigger.timer[1].stimulus = smu%s.trigger.ARMED_EVENT_ID '%self.channel)
        self.write('smu{ch}.trigger.source.stimulus = 0')
        self.write('smu{ch}.trigger.endpulse.action = smu%s.SOURCE_IDLE '%self.channel)
        self.write('smu{ch}.trigger.endpulse.stimulus = trigger.timer[1].EVENT_ID ')
        self.write('smu{ch}.trigger.count = 1')
        self.write('smu{ch}.trigger.arm.count = 1 ')
        self.write('smu{ch}.source.output = smu%s.OUTPUT_ON'%self.channel)


    amplitude = Instrument.control(
        "", "smu{ch}.trigger.source.list%s({%s})",
        """ Set pulse amplitude in volts""",
        #validator=strict_discrete_set,
        #values=[],
        #map_values=True,
        set_process=lambda v:(v[0].replace("VOLT",'v').replace("CURR",'i'),v[1])
    )

    generator_compliance_current=Instrument.control(
        "", "smu{ch}.trigger.source.limiti = %s",
        """ Set pulse amplitude in volts""",
    )

    
    generator_compliance_voltage=Instrument.control(
        "", "smu{ch}.trigger.source.limitv = %s",
        """ Set pulse amplitude in volts""",
    )
    
    source_range= Instrument.control(
        "", "smu{ch}.source.range%s = %f",
        """ Set pulse range in volts""",
        #validator=strict_discrete_set,
        #values={'CURR': 'i', 'VOLT': 'v'},
        #map_values=True
        set_process=lambda v:(v[0].replace("VOLT",'v').replace("CURR",'i'),v[1])
    )

    duration= Instrument.control(
        "", "trigger.timer[1].delay = %s",
        """ Set pulse range in volts""",
        #validator=strict_discrete_set,
        #values={'CURR': 'CURR', 'VOLT': 'VOLT'},
        #map_values=True
    )


    def trigger(self):
        self.single_pulse_run()

    def init(self):
        pass
        #log.info("Using excessed function init() for Keithley2636")
        
    def single_pulse_run(self):
        self.write('smu{ch}.trigger.initiate()')
        self.write('waitcomplete()')
        #self.write('smu{ch}.source.output = smub.OUTPUT_OFF')


    def pulse_script_v(self, bias, level, ton, toff, points, limiti): 
        self.write('smu{ch}.source.limiti = %s' %limiti)
        self.write('PulseVMeasureI(smub,{}, {}, {}, {}, {})'.format(bias, level, ton, toff, points)) #PulseVMeasureI(smu, bias, level, ton, toff, points) 
    
    def pulse_script_i(self): 
        self.write('smu{ch}.reset()')
        self.write('smu{ch}.source.limitv = 1')
        self.write('PulseIMeasureV(smub, 0, 10e-3, 20e-3, 50e-3, 10)') #PulseIMeasureV(smu, bias, level, ton, toff, points) 
   
    def pulse_script_read_i(self):
        self.ask('printbuffer(1, 2, smub.nvbuffer1.readings)')
    
    def pulse_script_read_v(self):
        self.ask('printbuffer(1, 2, smub.nvbuffer1.readings)')

    def config_pulse_v(self):
        self.write('smu{ch}.reset()')
        self.write('ConfigPulseVMeasureI(smub, 0, 0.1, 1, 0.800, 0.800, 10, smub.nvbuffer1, 2)') #ConfigPulseVMeasureI(smu, bias, level, limit, ton, toff, points, buffer,tag) 


    def config_pulse_i(self):
        self.write('rbi = smua.makebuffer(10)')
        self.write('rbv = smua.makebuffer(10)')
        self.write('rbi.appendmode = 1')
        self.write('rbv.appendmode = 1')
        self.write('rbs = { i = rbi, v = rbv }')
        self.write('ConfigPulseIMeasureV(smua, 0, 5, 10, 0.001, 0.080, 1, smub.nvbuffer1, 1)' ) # f, msg = ConfigPulseIMeasureV(smu, bias, level, limit, ton, toff, points, buffer (if nil no measurements),ag) 


    def start_pulse(self):
        
        self.ask('InitiatePulseTest(1)')
    
    def reset_buffer(self):
        self.write('smub.nvbuffer1.clear()')
        self.write('smub.nvbuffer1.appendmode = 1')

    def reset_smu(self):
        self.write('smub.reset()')

    def auto_range_source(self, source_mode):
        """ Configures the source to use an automatic range.
        """
        if source_mode == 'current':
            self.write('smu{ch}.source.autorangei=1')
        else:
            self.write('smu{ch}.source.autorangev=1')

    def apply_current(self, current_range=None, compliance_voltage=0.1):
        """ Configures the instrument to apply a source current, and
        uses an auto range unless a current range is specified.
        The compliance voltage is also set.
        :param compliance_voltage: A float in the correct range for a
                                   :attr:`~.Keithley2600.compliance_voltage`
        :param current_range: A :attr:`~.Keithley2600.current_range` value or None
        """
        log.info("%s is sourcing current." % self.channel)
        self.source_mode = 'current'
        if current_range is None:
            self.auto_range_source()
        else:
            self.source_current_range = current_range
        self.compliance_voltage = compliance_voltage
        #self.check_errors()

    def apply_voltage(self, voltage_range=None,
                      compliance_current=0.1):
        """ Configures the instrument to apply a source voltage, and
        uses an auto range unless a voltage range is specified.
        The compliance current is also set.
        :param compliance_current: A float in the correct range for a
                                   :attr:`~.Keithley2600.compliance_current`
        :param voltage_range: A :attr:`~.Keithley2600.voltage_range` value or None
        """
        log.info("%s is sourcing voltage." % self.channel)
        self.source_mode = 'voltage'
        if voltage_range is None:
            self.auto_range_source()
        else:
            self.source_voltage_range = voltage_range
        self.compliance_current = compliance_current
        self.check_errors()

    def ramp_to_voltage(self, target_voltage, steps=30, pause=0.1):
        """ Ramps to a target voltage from the set voltage value over
        a certain number of linear steps, each separated by a pause duration.
        :param target_voltage: A voltage in Amps
        :param steps: An integer number of steps
        :param pause: A pause duration in seconds to wait between steps """
        voltages = np.linspace(self.source_voltage, target_voltage, steps)
        for voltage in voltages:
            self.source_voltage = voltage
            time.sleep(pause)

    def ramp_to_current(self, target_current, steps=30, pause=0.1):
        """ Ramps to a target current from the set current value over
        a certain number of linear steps, each separated by a pause duration.
        :param target_current: A current in Amps
        :param steps: An integer number of steps
        :param pause: A pause duration in seconds to wait between steps """
        currents = np.linspace(self.source_current, target_current, steps)
        for current in currents:
            self.source_current = current
            time.sleep(pause)

    def shutdown(self):
        """ Ensures that the current or voltage is turned to zero
        and disables the output. """
        log.info("Shutting down channel %s." % self.channel)
        # if self.source_mode == 'current':
        #     self.ramp_to_current(0.0)
        # else:
        #     self.ramp_to_voltage(0.0)
        self.source_output = 'OFF'

    #def read_current(self): 
    #    return self.ask('measure.i()')
    
    def enable_source(self):
        self.source_output="ON"

    def disable_source(self):
        self.source_output="HIGH_Z"

    

if __name__ == "__main__":
#from time import sleep
    k = Keithley2636('GPIB0::26::INSTR', timeout=50000)
    ch=k.ChA
    ch.amplitude=("VOLT",2)
    ch.single_pulse_prepare()
    
    
    ch.duration=1e-3
    ch.source_range=("VOLT",5)
    
    while True:
        ch.trigger()
        time.sleep(1)
    #time.sleep(1)
    #ch.disable_source()
    #ch.trigger()

    #k.ChB.enable_source()
    #time.sleep(5)
    #k.ChB.shutdown()
   #k.reset()
    #k.ChA.source_output="ON"
    #k.ChA.single_pulse_prepare(4,1e-6,5)
    #k.ChA.single_pulse_run()
    #k.ChA.measure_current()
    #k.ChA.shutdown()

# #print(k.opc())
# # k.reset()
#k.ChB.pulse_script_v(0, 0.1, 2,2, 2, 0.001)
# flag = True
# pp = k.opc()
# # while flag:
#     try: 
#         if pp == 1: 
#             sleep(0.3)
#             flag = False
#     except:
#         flag = True
#         sleep(0.2)

# print(k.opc())
# flag = True 
# while flag: 
#     try:
#     print(k.opc)
# print(k.ChB.read_current() ) 
# time.sleep(0.3)
# k.reset()
# time.sleep(0.3)
# k.ChB.measure_current(1, 3,1)
# k.ChB.source_mode = "voltage"
# k.ChB.compliance_current = 0.01
# k.ChB.source_voltage = 0.1
# k.ChB.source_output = 'ON'
# time.sleep(0.4)
# flag = True
# while flag:
#     try:
#         current_sense = k.ChB.current   
#         flag = False
#     except:
#         k.reset()
#         print("error")
#         time.sleep(0.5)
#         flag = True
# print(current_sense)
# k.ChB.source_output = 'OFF'
