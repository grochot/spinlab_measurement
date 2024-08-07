from pymeasure.instruments import Instrument
import zhinst.core
from time import sleep, time
from zhinst.toolkit import Session
import numpy as np

class Zurich(Instrument):

    def __init__(self, server):
        #self.daq = zhinst.core.ziDAQServer(server, 8004, 6)
        self.session = Session(server)
        self.device_loc = self.session.connect_device("dev4274")
       
        # self.API_LEVEL = 6
        self.device = 'dev4274'
        # self.ERR_MSG = 'ERR'
        # (self.daq, self.device, _) = zhinst.utils.create_api_session(self.DEVICE_ID,
        #                                                    self.API_LEVEL, required_devtype='.*LI|.*IA',
        #                                                    required_err_msg=self.ERR_MSG)
        # zhinst.utils.api_server_version_check(self.daq)
        # self.daq.setInt(f"/{self.device}/sigouts/0/on", 0)  # disable signal output
        # self.daq.setInt(f"/{self.device}/auxouts/0/outputselect", -1)  # AUX output 1 = manual
        # self.daq.setDouble(f"/{self.device}/auxouts/0/offset", 0.0)  # AUX output 1 offset = 0 V

    ##### SET INPUT SIGNAL #####

    def siginautorange(self, signal:int, auto=1):
        self.device_loc.sigins[signal].autorange(auto)

    def siginrange(self, signal, range=1):
        self.device_loc.sigins[signal].range(range)

    def siginscaling(self, signal, scaling=1):
        self.device_loc.sigins[signal].scaling(scaling)

    def siginac(self, signal, ac=0):
        self.device_loc.sigins[signal].ac(ac)

    def sigindiff(self, signal, diff=0):
        self.device_loc.sigins[signal].diff(diff)

    def siginfloat(self, signal, float=1):
        self.device_loc.sigins[signal].float(float)

    def siginimp50(self, signal, imp50=1):
        self.device_loc.sigins[signal].imp50(imp50)

    ##### SET INPUT CURRENT #####

    def currinautorange(self, signal, auto=1):
        self.device_loc.currins[signal].autorange(auto)

    def currinrange(self, signal, range=1):
        self.device_loc.currins[signal].range(range)

    def currinscaling(self, signal, scaling=1):
        self.device_loc.currins[signal].scaling(scaling)

    def currinfloat(self, signal, float=0):
        self.device_loc.currins[signal].float(float)

    ##### SET SIGNAL OUTPUT #####

    def outputon(self, output, on):
        self.device_loc.sigouts[output].on(on)

    def output50ohm(self, output, ohm):
        self.device_loc.sigouts[output].imp50(ohm)

    def outputdiff(self,output, diff):
        self.device_loc.sigouts[output].diff(diff)

    def outputadd(self, output, add):
        self.device_loc.sigouts[output].add(add)

    def outputrange(self, output, range):
        self.device_loc.sigouts[output].range(range)

    def outputautorange(self, output, auto):
        self.device_loc.sigouts[output].autorange(auto)

    def outputoffset(self, output, offset):
        self.device_loc.sigouts[output].offset(offset)
    
    def aux_set_manual(self, out):
        self.device_loc.auxouts[out].outputselect(-1)
    
    def auxout(self, out, offset = 0): 
        self.device_loc.auxouts[out].offset(offset)

#????????????????????????
    def enableoutput(self, demod, enable):
        self.device_loc.sigouts[0].enables(enable)

    def outputamplitude(self, output, ampli):
        self.device_loc.sigouts[0].amplitudes(ampli) # Vpp
#?????????????????????????


    ##### SET OSCILLATORS #####
    def oscillatorfreq(self, osc_id, freq):
        self.device_loc.oscs[osc_id].freq(freq)

    ##### SET DEMODULATORS #####
    def setosc(self, demod_id, osc_id):
        self.device_loc.demods[demod_id].oscselect(osc_id)  # connect to oscilator

    def setextrefs(self, demod_id, extrefs):
        self.device_loc.extrefs[extrefs].enable(demod_id)  # input select demod
        self.device_loc.extrefs[extrefs].demodselect(demod_id)

    def setharmonic(self, demod_id, harm):
        self.device_loc.demods[demod_id].harmonic(harm)  # select harmonic

    def settimeconst(self, demod_id, timeconst):
        self.device_loc.demods[demod_id].timeconstant(timeconst)  # set timeconstant

    def setadc(self, demod_id, adc):
        if(adc == 10):
            adc = 174
        self.device_loc.demods[demod_id].adcselect(adc)  # input select demod

    def setorder(self, demod_id, order):
        self.device_loc.demods[demod_id].order(order)  # select the filter roll off between 6 and 48 dB/oct

    def enabledemod(self, demod_id, enable):
        self.device_loc.demods[demod_id].enable(enable)  # enable demodulator

    def rate(self, demod_id, rate):
        self.device_loc.demods[demod_id].rate(rate)  # sampling rate 

    def sinc(self, demod_id, sinc):
        self.device_loc.demods[demod_id].sinc(sinc) #sinc filter on



    ##### GET SAMPLE ########

    def getsample(self, demod):
        sample = self.device_loc.demods[demod].sample()
        return sample
    
    ####### LOCKIN SCOPE ###### 


    def scope_init(self, av:int, input_sel:int, rate:float, length:float): 
        with self.device_loc.set_transaction():
            self.device_loc.scopes[0].length(length)
            self.device_loc.scopes[0].channel(1)
            self.device_loc.scopes[0].channels[0].bwlimit(1)
            self.device_loc.scopes[0].channels[0].inputselect(input_sel)
            self.device_loc.scopes[0].time(rate)
            self.device_loc.scopes[0].single(True)
            self.device_loc.scopes[0].trigenable(False)
            self.device_loc.scopes[0].trigholdoff(0.050)
            self.device_loc.scopes[0].segments.enable(False)

        self.scope_module = self.session.modules.scope
        self.scope_module.mode(1)
        self.scope_module.averager.weight(1)
        self.scope_module.historylength(1)
        self.scope_module.fft.window(0)
        self.wave_node = self.device_loc.scopes[0].wave
        self.scope_module.subscribe(self.wave_node)
    

    

    def get_wave(self):
        """Obtain scope records from the device using an instance of the Scope Module."""
        self.scope_module.execute()
        self.device_loc.scopes[0].enable(True)
        self.session.sync()

        start = time()
        timeout = 30 # [s]
        records = 0
        progress = 0
        # Wait until the Scope Module has received and processed
        # the desired number of records.
        while (records < 1):
            sleep(0.5)
            records = self.scope_module.records()
            progress = self.scope_module.progress()
            print(
                f"Scope module has acquired {records} records (requested {1}). "
                f"Progress of current segment {100.0 * progress}%.",
                end="\r",
            )
            if (time() - start) > timeout:
                # Break out of the loop if for some reason we're no longer receiving
                # scope data from thedevice
                print(
                    f"\nScope Module did not return {1} records after {timeout} s - \
                        forcing stop."
                )
                break

        self.device_loc.scopes[0].enable(False)
        # Read out the scope data from the module.
        data = self.scope_module.read()[self.wave_node]
        # Stop the module; to use it again we need to call execute().
        self.scope_module.finish()
        return data[0]
    
    
    def to_timestamp(self,record):
        clockbase = self.device_loc.clockbase()
        totalsamples = record[0]["totalsamples"]
        dt = record[0]["dt"]
        timestamp = record[0]["timestamp"]
        triggertimestamp = record[0]["triggertimestamp"]
        t = np.arange(-totalsamples, 0) * dt + (
            timestamp - triggertimestamp
        ) / float(clockbase)
        return t
        
########################### Test ###########################3

# zur = Zurich('192.168.66.202')

# dd = zur.getsample(0)
# print(dd)

# dd = zur.get_wave()

# print(dd)

# ts = zur.to_timestamp(dd)

# import matplotlib.pyplot as plt 

# plt.plot(ts,dd[0][0]['wave'][0])
# plt.show()