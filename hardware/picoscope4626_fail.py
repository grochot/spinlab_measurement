
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set

import logging
import ctypes
import numpy as np
import time


class PicoScope(): 

    def setChannelA(self, coupling="DC", range="10mV"): 
       pass

    def setChannelB(self, coupling="DC", range="10mV"): 
        pass
    
    def setTrigger(self, source = 0):
        pass

    def set_number_samples(self,no_samples = 1):
       pass

    def set_timebase(self, timebase = 1):
        pass

    def run_block_capture(self):
        pass

    def check_data_collection(self): 
        pass

    def create_buffers(self): 
        pass
    def set_buffer_location(self): 
        pass

    def getValuesfromScope(self): 
       pass

    def convert_to_mV(self): 
        adc2mVChAMax =  1
        return(adc2mVChAMax)

    def create_time(self): 
        time = 1
        return(time)

    def stop_scope(self):
        pass
    
    def disconnect_scope(self): 
        pass
       















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
