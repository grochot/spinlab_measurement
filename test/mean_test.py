import pandas as pd 
import numpy as np
from time import sleep
import math
def execute():
    #przygotowanie pomiaru
    
    steps = 5 #ilość uśrednień
    time = 0.01
    tmp_data_time = pd.DataFrame(columns=['time'])
    tmp_data_voltage = pd.DataFrame(columns=['voltage'])
    tmp_frequency = pd.DataFrame(columns=['frequency'])
    tmp_fft = pd.DataFrame(columns=['fft'])
    tmp_data_magnetic_field_x = []
    tmp_data_magnetic_field_y = []
    tmp_data_magnetic_field_z = []


    for i in range(1):
        try:
            tmp_field = [2,2,2]
            tmp_x = tmp_field[0]
            tmp_y = tmp_field[1]
            tmp_z = tmp_field[2]
            
        
            tmp_data_magnetic_field_x.append(float(tmp_x))
            tmp_data_magnetic_field_y.append(float(tmp_y))
            tmp_data_magnetic_field_z.append(float(tmp_z))
            sleep(0.1)


            tmp_data_magnetic_field_x_mean = float(sum(tmp_data_magnetic_field_x)/len(tmp_data_magnetic_field_x))/100
            tmp_data_magnetic_field_y_mean = float(sum(tmp_data_magnetic_field_y)/len(tmp_data_magnetic_field_y))/100
            tmp_data_magnetic_field_z_mean = float(sum(tmp_data_magnetic_field_z)/len(tmp_data_magnetic_field_z))/100
        except: 
            print("error")
        

#Main loop:
        for i in range(steps): #pętla tyle razy ile uśrednień
        
            tmp_time_list = [x for x in range(9)]  #lista czasów z pojedyńczego pomiaru 
            tmp_voltage_list = [x*i for x in range(9)] #lista napięć z pojedyńczego pomiaru
            
        
#FFT Counting:
            smpl_freq = 0.001
            ft_tmp = np.fft.fft(tmp_voltage_list) / len(tmp_voltage_list)  # Normalize amplitude and apply the FFT
            ft_tmp = ft_tmp[range(int(len(tmp_voltage_list)/2))]   # Exclude sampling frequency ---> FFT value
            tp_cnt_tmp = len(tmp_voltage_list)
            val_tmp = np.arange(int(tp_cnt_tmp / 2))
            tm_period_tmp = tp_cnt_tmp / smpl_freq    # oś x pojedyńczy pomiar
            freq_tmp = val_tmp / tm_period_tmp        # częstotliwość pojedyńczy pomiar 
            

            tmp_data_time.insert(i,"time_{}".format(i),pd.Series(tmp_time_list))
            tmp_data_voltage.insert(i,"voltage_{}".format(i),pd.Series(tmp_voltage_list))
            tmp_frequency.insert(i,"frequency_{}".format(i),pd.Series(freq_tmp))
            tmp_fft.insert(i,"fft_{}".format(i),pd.Series(ft_tmp))
            

            
        tmp_data_time["average"] = tmp_data_time.mean(axis=1) #average time
        tmp_data_voltage["average"] = tmp_data_voltage.mean(axis=1) #average voltage
        tmp_fft["average"] = tmp_fft.mean(axis=1) #average fft
        tmp_frequency["average"] = tmp_frequency.mean(axis=1) #average frequency
        print(tmp_fft)

        tmp_data_time_average = tmp_data_time["average"].to_list()
        tmp_data_voltage_average = tmp_data_voltage["average"].to_list()
        tmp_data_fft_average = tmp_fft["average"].to_list()
        tmp_data_frequency_average = tmp_frequency["average"].to_list()
        
    
       
        for ele in range(len(tmp_data_time_average)):
           
            data2 = {
                    # 'frequency (Hz)': tmp_data_frequency_average[ele] if ele < len(tmp_data_frequency_average) else math.nan, 
                    # 'FFT (mV)': abs(tmp_data_fft_average[ele]) if ele < len(tmp_data_frequency_average) else math.nan, 
                    # 'log[frequency] (Hz)': math.log10(tmp_data_frequency_average[ele+1]) if ele < len(tmp_data_frequency_average)-1 else math.nan,
                    # 'log[FFT] (mV)':  math.log10(abs(tmp_data_fft_average[ele+1])) if ele < len(tmp_data_frequency_average)-1 else math.nan,
                    'time (s)': tmp_data_time_average[ele],
                    'Voltage (mV)': tmp_data_voltage_average[ele],
                    'X field (Oe)': tmp_data_magnetic_field_x_mean,
                    'Y field (Oe)': tmp_data_magnetic_field_y_mean,
                    'Z field (Oe)': tmp_data_magnetic_field_z_mean,
                    }
            # print(data2['time (s)'])
            


execute()