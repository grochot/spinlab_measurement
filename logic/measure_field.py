from time import sleep 
def measure_field(averaging, field, stop):
     tmp_data_magnetic_field_x = []
     tmp_data_magnetic_field_y = []
     tmp_data_magnetic_field_z = []
     for i in range(averaging):
                try:
                    tmp_field = field.read_field()
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
                    return tmp_data_magnetic_field_x_mean, tmp_data_magnetic_field_y_mean, tmp_data_magnetic_field_z_mean
                except Exception as e:
                    print(e)
                    stop