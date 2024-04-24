class GenerateHeader(): 
    
    
    def set_parameters(self, filename, columns, a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,r,s):
        self.PROCEDURE = '#Procedure: <__main__.NoiseProcedure>'
        self.DATA = "#Data:"
        self.PARAMETERS = """#Parameters:
#\tBias Field Voltage: {0} V
#\tBias Voltage: {1} V
#\tChannel A Coupling Type: {2}
#\tChannel A Range: {3}
#\tDelay: {13} ms
#\tDivide number: {4} mV
#\tHMC8043 adress: {5}
#\tField_sensor: {6}
#\tMode: Mean + Raw
#\tNo Points: {14}
#\tNumber of times: {7}
#\tPeriod of Time: {8} s
#\tReverse voltage: {15}
#\tSample Name: {9}
#\tSampling frequency: {10} Hz
#\tStart: {16}
#\tStop: {17}
#\tTreshold: {11} mV
#\tSIM928 adress: {12}""".format(float(a),b,c,d,e,f,g,int(h),i,j,k,l,m,n,int(o),p,r,s)

        f = open('{}'.format(filename), 'w')

        f.write(self.PROCEDURE + '\n')
        f.write(self.PARAMETERS + '\n')
        f.write(self.DATA + '\n')
        f.writelines(columns)
        f.write('\n')
        f.close()

    def write_data(self, filename2, data):
        f = open('{}'.format(filename2), 'a')
        f.writelines(data)
        f.write('\n')
        f.close()


