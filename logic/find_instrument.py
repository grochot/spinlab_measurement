import pyvisa
import os


class FindInstrument(): 
    def __init__(self): 
        self.rm = pyvisa.ResourceManager() 
        self.hardware = {}
   
    def find_instrument(self):
        for i in self.rm.list_resources(): 
            try:
                inst = self.rm.open_resource(i)  
                self.hardware[inst.query('*IDN?')] = i
                inst.close()
            except:
                
                self.hardware[i] = i
        self.isExist = os.path.exists("finded_instruments.txt")
        if self.isExist == True:
            self.file = open("finded_instruments.txt", "r")
        else: 
            self.file = open("finded_instruments.txt",'w+')    
        self.content = self.file.read()
        self.file.close()
        self.content_tab = self.content.split(",") 
        for k in self.hardware.keys(): 
            if k in self.content_tab: 
                pass 
            else: 
                if k != '':
                    self.file = open("finded_instruments.txt", 'a')
                    self.save_data =   ","+k  
                    self.file.write(self.save_data)
                    self.file.close()

        self.file = open("finded_instruments.txt", 'r') 
        self.instruments = self.file.read().split(',')[1:]

        return self.instruments

    
    def show_instrument(self): 
    	return self.rm.list_resources()
