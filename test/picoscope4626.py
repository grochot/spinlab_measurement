from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set

import logging
import ctypes
import numpy as np
from picosdk.ps4000 import ps4000 as ps
from picosdk.functions import adc2mV, assert_pico_ok
import time


class PicoScope(): 

    def __init__(self):
        self.chandle = ctypes.c_int16()
        self.status = {}
        self.enabled = 1
        self.status["openunit"] = ps.ps4000OpenUnit(ctypes.byref(self.chandle))
        assert_pico_ok(self.status["openunit"])


    def setChannelA(self, coupling="DC", range="10mV"): 
        if coupling == 'DC':
            self.coupling_type = 1
        else: 
            self.coupling_type = 0
        
        self.range_list = {"10mV":0, "20mV":1, "50mV":2, "100mV":3, "200mV":4, "500mV":5, "1V":6, "2V":7, "5V":8, "10V":9, "20V":10, "50V":11, "100V":12}
        

        self.status["setChA"] = ps.ps4000SetChannel(self.chandle,
                                    ps.PS4000_CHANNEL['PS4000_CHANNEL_A'],
                                    self.enabled,
                                    self.coupling_type,
                                    self.range_list[range])
        assert_pico_ok(self.status["setChA"])


    def setChannelB(self, coupling="DC", range="10mV"): 
        if coupling == 'DC':
            coupling_type = True
        else: 
            coupling_type = False
        
        range_list = {"10mV":0, "20mV":1, "50mV":2, "100mV":3, "200mV":4, "500mV":5, "1V":6, "2V":7, "5V":8, "10V":9, "20V":10, "50V":11, "100V":12}
        

        self.status["setChB"] = ps.ps4000SetChannel(self.chandle,
                                    ps.PS4000_CHANNEL['PS4000_CHANNEL_B'],
                                    self.enabled,
                                    coupling_type,
                                    range_list[range])
        assert_pico_ok(self.status["setChB"])
    
    def setTrigger(self):
        self.status["trigger"] = ps.ps4000SetSimpleTrigger(self.chandle, 1, 0, 1024, 2, 0, 1000)
        assert_pico_ok(self.status["trigger"])

    def set_number_samples(self,no_samples = 1):
        self.preTriggerSamples = round(no_samples/2)
        self.postTriggerSamples = round(no_samples/2)
        self.maxSamples = self.preTriggerSamples + self.postTriggerSamples

    def set_timebase(self, timebase = 1):
        self.timeIntervalns = ctypes.c_float()
        self.returnedMaxSamples = ctypes.c_int32()
        self.timebase = timebase
        self.oversample = ctypes.c_int16(1)
        self.status["getTimebase2"] = ps.ps4000GetTimebase2(self.chandle, self.timebase, self.maxSamples, ctypes.byref(self.timeIntervalns), self.oversample, ctypes.byref(self.returnedMaxSamples), 0)
        assert_pico_ok(self.status["getTimebase2"])

    def run_block_capture(self):
        self.status["runBlock"] = ps.ps4000RunBlock(self.chandle, self.preTriggerSamples, self.postTriggerSamples, self.timebase, self.oversample, None, 0, None, None)
        assert_pico_ok(self.status["runBlock"])

    def check_data_collection(self): 
        ready = ctypes.c_int16(0)
        check = ctypes.c_int16(0)
        while ready.value == check.value:
            self.status["isReady"] = ps.ps4000IsReady(self.chandle, ctypes.byref(ready))

    def create_buffers(self): 
        self.bufferAMax = (ctypes.c_int16 * self.maxSamples)()
        self.bufferAMin = (ctypes.c_int16 * self.maxSamples)() # used for downsampling which isn't in the scope of this example
        self.bufferBMax = (ctypes.c_int16 * self.maxSamples)()
        self.bufferBMin = (ctypes.c_int16 * self.maxSamples)() # used for downsampling which isn't in the scope of this example

    def set_buffer_location(self): 
        self.status["setDataBuffersA"] = ps.ps4000SetDataBuffers(self.chandle, 0, ctypes.byref(self.bufferAMax), ctypes.byref(self.bufferAMin), self.maxSamples)
        assert_pico_ok(self.status["setDataBuffersA"])
        self.status["setDataBuffersB"] = ps.ps4000SetDataBuffers(self.chandle, 1, ctypes.byref(self.bufferBMax), ctypes.byref(self.bufferBMin), self.maxSamples)
        assert_pico_ok(self.status["setDataBuffersB"])
        # create overflow loaction
        self.overflow = ctypes.c_int16()
        # create converted type maxSamples
        self.cmaxSamples = ctypes.c_int32(self.maxSamples)

    def getValuesfromScope(self): 
        self.status["getValues"] = ps.ps4000GetValues(self.chandle, 0, ctypes.byref(self.cmaxSamples), 0, 0, 0, ctypes.byref(self.overflow))
        assert_pico_ok(self.status["getValues"])

    def convert_to_mV(self, range): 
        maxADC = ctypes.c_int16(32767)
        adc2mVChAMax =  adc2mV(self.bufferAMax, self.range_list[range], maxADC)
        return(adc2mVChAMax)

    def create_time(self): 
        time = np.linspace(0, (self.cmaxSamples.value - 1) * self.timeIntervalns.value, self.cmaxSamples.value)
        return(time)

    def stop_scope(self):
        self.status["stop"] = ps.ps4000Stop(self.chandle)
        assert_pico_ok(self.status["stop"])
    
    def disconnect_scope(self): 
        self.status["close"] = ps.ps4000CloseUnit(self.chandle)
        assert_pico_ok(self.status["close"])

       















    # def setSizeCapture(self,sizeOneBuffer=500, noBuffers=10):
    #     sizeOfOneBuffer = sizeOfOneBuffer
    #     numBuffersToCapture = noBuffers
    #     totalSamples = sizeOfOneBuffer * numBuffersToCapture
        
    #     bufferAMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)
    #     bufferBMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)

    #     memory_segment = 0
    #     status["setDataBuffersA"] = ps.ps4000SetDataBuffers(chandle,
    #                                                  ps.PS4000_CHANNEL['PS4000_CHANNEL_A'],
    #                                                  bufferAMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
    #                                                  None,
    #                                                  sizeOfOneBuffer)
    #     assert_pico_ok(status["setDataBuffersA"])

    #     status["setDataBuffersB"] = ps.ps4000SetDataBuffers(chandle,
    #                                                  ps.PS4000_CHANNEL['PS4000_CHANNEL_B'],
    #                                                  bufferBMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
    #                                                  None,
    #                                                  sizeOfOneBuffer)
    #     assert_pico_ok(status["setDataBuffersB"])


    # # def beginStreaming(self): 
    # #     # Begin streaming mode:
    # #     sampleInterval = ctypes.c_int32(250)
    # #     sampleUnits = ps.PS4000_TIME_UNITS['PS4000_US']
    # #     # We are not triggering:
    # #     maxPreTriggerSamples = 0
    # #     autoStopOn = 1
    # #     # No downsampling:
    # #     downsampleRatio = 1
    # #     status["runStreaming"] = ps.ps4000RunStreaming(chandle,
    # #                                                     ctypes.byref(sampleInterval),
    # #                                                     sampleUnits,
    # #                                                     maxPreTriggerSamples,
    # #                                                     totalSamples,
    # #                                                     autoStopOn,
    # #                                                     downsampleRatio,
    # #                                                     sizeOfOneBuffer)
    # #     assert_pico_ok(status["runStreaming"])

    # #     actualSampleInterval = sampleInterval.value
    # #     actualSampleIntervalNs = actualSampleInterval * 1000

    # #     print("Capturing at sample interval %s ns" % actualSampleIntervalNs)

    # #     # We need a big buffer, not registered with the driver, to keep our complete capture in.
    # #     bufferCompleteA = np.zeros(shape=totalSamples, dtype=np.int16)
    # #     bufferCompleteB = np.zeros(shape=totalSamples, dtype=np.int16)
    # #     nextSample = 0
    # #     autoStopOuter = False
    # #     wasCalledBack = False


    

    # #     # Convert the python function into a C function pointer.
    # #     cFuncPtr = ps.StreamingReadyType(streaming_callback)

    # #     # Fetch data from the driver in a loop, copying it out of the registered buffers and into our complete one.
    # #     while nextSample < totalSamples and not autoStopOuter:
    # #         wasCalledBack = False
    # #         status["getStreamingLastestValues"] = ps.ps4000GetStreamingLatestValues(chandle, cFuncPtr, None)
    # #         if not wasCalledBack:
    # #             # If we weren't called back by the driver, this means no data is ready. Sleep for a short while before trying
    # #             # again.
    # #             time.sleep(0.01)

    # #     print("Done grabbing values.")

    # #     # Find maximum ADC count value
    # #     # handle = chandle
    # #     # pointer to value = ctypes.byref(maxADC)
    # #     maxADC = ctypes.c_int16(32767)

    # #     # Convert ADC counts data to mV
    # #     adc2mVChAMax = adc2mV(bufferCompleteA, channel_range, maxADC)
    # #     adc2mVChBMax = adc2mV(bufferCompleteB, channel_range, maxADC)

    # #     # Create time data
    # #     time = np.linspace(0, (totalSamples - 1) * actualSampleIntervalNs, totalSamples)

    # #     # Plot data from channel A and B
    # #     plt.plot(time, adc2mVChAMax[:])
    # #     plt.plot(time, adc2mVChBMax[:])
    # #     plt.xlabel('Time (ns)')
    # #     plt.ylabel('Voltage (mV)')
    # #     plt.show()

    # # def streaming_callback(self,handle, noOfSamples, startIndex, overflow, triggerAt, triggered, autoStop, param):
    # #     global nextSample, autoStopOuter, wasCalledBack
    # #     wasCalledBack = True
    # #     destEnd = nextSample + noOfSamples
    # #     sourceEnd = startIndex + noOfSamples
    # #     bufferCompleteA[nextSample:destEnd] = bufferAMax[startIndex:sourceEnd]
    # #     bufferCompleteB[nextSample:destEnd] = bufferBMax[startIndex:sourceEnd]
    # #     nextSample += noOfSamples
    # #     if autoStop:
    # #         autoStopOuter = True

    # # def stopScope(self):
    # #     # Stop the scope
    # #     # handle = chandle
    # #     status["stop"] = ps.ps4000Stop(chandle)
    # #     assert_pico_ok(status["stop"])

    # # def disconnectScope(self):
    # #     # Disconnect the scope
    # #     # handle = chandle
    # #     status["close"] = ps.ps4000CloseUnit(chandle)
    # #     assert_pico_ok(status["close"])
