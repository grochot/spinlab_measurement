import pyvisa as visa
from pymeasure.display.Qt import QtCore, QtWidgets, QtGui
import sys
#sys.path.append("/home/mariusz/moje_pliki/programowanie/python/spinlab_measurement/")
sys.path.append("C:\\Users\\IE\\git\\spinlab_measurement")
from logic.find_instrument import FindInstrument
from hardware.dummy_motion_driver import DummyMotionDriver
from hardware.esp300_simple import Esp300
from hardware.keithley2400 import Keithley2400
from functools import partial
from PyQt5.QtCore import Qt
from logic.map_generator import generate_coord


class AutomaticStationGenerator(QtWidgets.QWidget):
    object_name = "automatic_station_generator"


    def __init__(self):
        super(AutomaticStationGenerator, self).__init__()
        self.state = False
        self.name = "Automatic Station Generator"
        self.icon_path = "modules\icons\AutomaticStationGenerator.ico"
        self.address_list = ["None"]
        self.address = "None"
        self.get_available_addresses()
        #self.make_connection_with_devices()

        #self.loadState()
        self._setup_ui()
        self._layout()


    def open_widget(self):
        self.get_available_addresses()
        #self.updateGUI()
        self.show()


    def get_available_addresses(self):
        find_instruments=FindInstrument()
        self.address_list=find_instruments.show_instrument()
        print(self.address_list)


    def go(self):
        self.MotionDriver.goTo_2(self.go_x_textbox.text())
        self.MotionDriver.goTo_3(self.go_y_textbox.text())
        self.MotionDriver.goTo_1(self.go_z_textbox.text())


    def _setup_ui(self):
        self.MotionDriver=DummyMotionDriver("trash")
        self.z_pos=self.MotionDriver.pos_1()
        print(self.z_pos)
        

        self.setWindowTitle("Automatic station generator")
        self.setWindowIcon(QtGui.QIcon(self.icon_path))

        #first part of widget
        self.drive_motion_adresses_combo=QtWidgets.QComboBox()
        self.drive_motion_adresses_combo.addItems(self.address_list) #dodaj prawdziwe
        self.drive_motion_adresses_label=QtWidgets.QLabel('Driver motion address')

        '''self.sourcemeter_adresses_combo=QtWidgets.QComboBox()
        self.sourcemeter_adresses_combo.addItems(self.address_list)
        self.sourcemeter_adresses_combo_label = QtWidgets.QLabel('Sourcemeter address')

        self.choice_sourcemeter_label=QtWidgets.QLabel('Sourcemeter type')
        self.choice_sourcemeter_label_combo=QtWidgets.QComboBox()
        self.choice_sourcemeter_label_combo.addItems(["Keithley 2400","Keithley 2636","Agilent 2912"])'''

        self.make_connection_with_devices_label=QtWidgets.QLabel('Make connection with devices')
        self.make_connection_with_devices_button=QtWidgets.QPushButton("connect")
        

        '''self.resistance_label=QtWidgets.QLabel('Resistance: ')
        #self.resistance_label.setFixedSize(10,20)
        self.resistance_read_button=QtWidgets.QPushButton('Read', self)'''

        self.make_connection_label=QtWidgets.QLabel('connect distance [mm]')
        self.make_connection_textbox=QtWidgets.QLineEdit(self)
        self.make_connection_textbox.setText("0")
        self.make_connection_textbox.setFixedSize(100,20)
        self.make_connection_textbox.setAlignment(Qt.AlignLeft)

        self.connect_checkable_button=self.checkable_button = QtWidgets.QPushButton("disconnect")
        self.connect_checkable_button.setCheckable(True)
        self.led_indicator_label=QtWidgets.QLabel()
        self.led_indicator_label.setFixedSize(35,35)
        self.led_indicator_label.setAlignment(Qt.AlignCenter)
        self.update_led_indicator(False)
        self.connect_checkable_button.toggled.connect(self.update_led_indicator)

        self.enable_motors_checkable_button= QtWidgets.QPushButton("Disabled")
        self.enable_motors_checkable_button.setCheckable(True)
        self.enable_motors_function(False)
        self.enable_motors_checkable_button.toggled.connect(self.enable_motors_function)
        self.enable_motors_checkable_label=QtWidgets.QLabel("Enable or disable motors")

        self.go_x_textbox=QtWidgets.QLineEdit()
        self.go_x_textbox.setPlaceholderText('x')
        self.go_y_textbox=QtWidgets.QLineEdit()
        self.go_y_textbox.setPlaceholderText('y')
        self.go_z_textbox=QtWidgets.QLineEdit()
        self.go_z_textbox.setPlaceholderText('z')

        self.go_button=QtWidgets.QPushButton("GO")
        self.go_button.clicked.connect(self.go)



    
        #main part of widget
        self.number_of_element_in_the_x_axis_name=QtWidgets.QLabel('number of elements on the x axis')
        self.number_of_element_in_the_x_axis_textbox=QtWidgets.QLineEdit(self)

        self.number_of_element_in_the_y_axis_name=QtWidgets.QLabel('number of elements on the y axis')
        self.number_of_element_in_the_y_axis_textbox=QtWidgets.QLineEdit(self)

        self.first_element_x_name=QtWidgets.QLabel('First element on x axis')
        self.first_element_x_textbox=QtWidgets.QLineEdit(self)
        #self.first_element_x_read_button=QtWidgets.QPushButton('Read', self)
        #self.first_element_x_read_button.clicked.connect(partial(self.read_position,"x",self.first_element_x_textbox))

        self.first_element_y_name=QtWidgets.QLabel('First element on y axis')
        self.first_element_y_textbox=QtWidgets.QLineEdit(self)
        #self.first_element_y_read_button=QtWidgets.QPushButton('Read', self)
        #self.first_element_y_read_button.clicked.connect(partial(self.read_position,"y",self.first_element_y_textbox))

        self.first_element_xy_read_button=QtWidgets.QPushButton('Read', self)
        self.first_element_xy_read_button.clicked.connect(partial(self.read_coordinates,"xy",self.first_element_x_textbox,self.first_element_y_textbox))
        

        #self.second_element_x_name=QtWidgets.QLabel('Second element on x axis')
        #self.second_element_x_textbox=QtWidgets.QLineEdit(self)
        #self.second_element_x_read_button=QtWidgets.QPushButton('Read', self)
        #self.second_element_x_read_button.clicked.connect(partial(self.read_position,"x",self.second_element_x_textbox))

        #self.second_element_y_name=QtWidgets.QLabel('Second element on y axis')
        #self.second_element_y_textbox=QtWidgets.QLineEdit(self)
        #self.second_element_y_read_button=QtWidgets.QPushButton('Read', self)
        #self.second_element_y_read_button.clicked.connect(partial(self.read_position,"y",self.second_element_y_textbox))

        #self.second_element_xy_read_button=QtWidgets.QPushButton('Read', self)
        #self.second_element_xy_read_button.clicked.connect(partial(self.read_coordinates,"xy",self.second_element_x_textbox,self.second_element_y_textbox))

        self.dx_calculation_name=QtWidgets.QLabel('Dx')
        self.dx_calculation_textbox=QtWidgets.QLineEdit(self)

        self.dy_calculation_name=QtWidgets.QLabel('Dy')
        self.dy_calculation_textbox=QtWidgets.QLineEdit(self)

        #self.dx_dy_calculation_calc_button=QtWidgets.QPushButton('Calculate', self)
        #self.dx_dy_calculation_calc_button.clicked.connect(partial(self.calculate_dx_dy,self.first_element_x_textbox.text(),self.first_element_y_textbox.text(),self.second_element_x_textbox.text(),self.second_element_y_textbox.text(),self.dx_calculation_textbox,self.dy_calculation_textbox))

        self.last_element_x_name=QtWidgets.QLabel('Last element on x axis')
        self.last_element_x_textbox=QtWidgets.QLineEdit(self)
        #self.last_element_x_read_button=QtWidgets.QPushButton('Read', self)

        self.last_element_y_name=QtWidgets.QLabel('Last element on y axis')
        self.last_element_y_textbox=QtWidgets.QLineEdit(self)
        #self.last_element_y_read_button=QtWidgets.QPushButton('Read', self)

        self.last_element_xy_read_button=QtWidgets.QPushButton('Read', self)
        self.last_element_xy_read_button.clicked.connect(partial(self.read_coordinates,"xy",self.last_element_x_textbox,self.last_element_y_textbox))

        self.theta_name=QtWidgets.QLabel('Calculated theta angle ??')
        #self.theta_textbox=QtWidgets.QLineEdit(self)
        #self.theta_read_button=QtWidgets.QPushButton('Calculate', self)

        self.name_patern_name=QtWidgets.QLabel('Name pattern')
        self.name_patern_textbox=QtWidgets.QLineEdit(self)
        self.name_patern_textbox.setToolTip("{col} - column marker (number) \n{col_char} - column marker (char) \n{row} - row marker (number) \n{row_char} - row marker (char)")

        self.generate_map_button=QtWidgets.QPushButton('Generate sequence', self)
        self.generate_map_button.clicked.connect(partial(self.generate_sequence,))



        #Devices connection
        self.make_connection_with_devices_button.clicked.connect(self.make_connection_with_devices)

    def make_connection_with_devices(self):
        if self.drive_motion_adresses_combo.currentText()!="None":
            self.MotionDriver=Esp300(self.drive_motion_adresses_combo.currentText())
            self.z_pos=self.MotionDriver.pos_1()
        else:
            self.MotionDriver=DummyMotionDriver(self.drive_motion_adresses_combo.currentText())
            print("DummyMotionDriver")



    def generate_sequence(self):
        number_of_element_in_the_x_axis=int(self.number_of_element_in_the_x_axis_textbox.text())
        number_of_element_in_the_y_axis=int(self.number_of_element_in_the_y_axis_textbox.text())
        first_element_x=float(self.first_element_x_textbox.text())
        first_element_y=float(self.first_element_y_textbox.text())
        dx_calculation=float(self.dx_calculation_textbox.text())
        dy_calculation=float(self.dy_calculation_textbox.text())
        last_element_x=float(self.last_element_x_textbox.text())
        last_element_y=float(self.last_element_y_textbox.text())
        name_pattern=self.name_patern_textbox.text()

        gc=generate_coord(first_element_x,first_element_y,number_of_element_in_the_x_axis,number_of_element_in_the_y_axis,dx_calculation,dy_calculation,last_element_x,last_element_y,name_pattern)

        self.theta_name.setText(str("Calculated theta angle {0} [rad]".format(gc['theta'])))

        #sequence generation
        seq_vector='- "Global "[x,y,name]"", "{0}"'.format(gc['move_vectors_prim'])

        with open('./example_sequence','w') as f:
            f.write(seq_vector)
        




    def read_position(self,axis,write_destination):
        #z=pos1
        #x=pos2
        #y=pos3
        match axis:
            case "x":
                position=self.MotionDriver.pos_2() 
            case "y":
                position=self.MotionDriver.pos_3()
            case "z":
                position=self.MotionDriver.pos_1()

        write_destination.setText(str(position))

    def read_coordinates(self,plane,write_axes1,write_axes2):
        #z=pos1
        #x=pos2
        #y=pos3
        match plane:
            case "xy":
                write_axes1.setText(str(self.MotionDriver.pos_2()))
                write_axes2.setText(str(self.MotionDriver.pos_3()))


    def calculate_dx_dy(self,f_x,f_y,s_x,s_y,dx_calculation_textbox,dy_calculation_textbox):
        #print("to dostałem:",self.first_element_x_textbox.text())

        dx=float(self.second_element_x_textbox.text())-float(self.first_element_x_textbox.text())
        dy=float(self.second_element_y_textbox.text())-float(self.first_element_y_textbox.text())
        dx_calculation_textbox.setText(str(dx))
        dy_calculation_textbox.setText(str(dy))



    
    
    def update_led_indicator(self, checked):
        if checked:
            self.led_indicator_label.setStyleSheet("background-color: green; border-radius: 10px;")
            self.connect_checkable_button.setText("Connect")
            self.MotionDriver.goTo_1(self.z_pos-float(self.make_connection_textbox.text()))

        else:
            self.led_indicator_label.setStyleSheet("background-color: red; border-radius: 10px;")
            self.connect_checkable_button.setText("Disconnect")
            self.MotionDriver.goTo_1(self.z_pos)
    
    def enable_motors_function(self, checked):
        if checked:
            self.MotionDriver.enable()
            self.enable_motors_checkable_button.setText("Disable")
            
        else:
            self.MotionDriver.disable() #to ma byc negacja tekstu wysietlanego na ekranie, wtedy jest dobrze.
            self.enable_motors_checkable_button.setText("Enable")
    

    def connect_disconnect(self,plane):
        match plane:
            case "xy":
                pass
        


    def _layout(self):
        layout = QtWidgets.QVBoxLayout()

        grid_layout=QtWidgets.QGridLayout()


        # Dodajemy przyciski do pierwszego wiersza (row 0)
        #for col in range(6):
        #    button = QtWidgets.QPushButton(f"Button {col + 1}")
        #    grid_layout.addWidget(button, 0, col)

        # Dodajemy pola tekstowe do drugiego wiersza (row 1)
        #for col in range(6):
        #    line_edit = QtWidgets.QLineEdit(f"Text {col + 1}")
        #    grid_layout.addWidget(line_edit, 1, col)
        
        grid_layout.addWidget(self.drive_motion_adresses_combo, 0, 0)
        grid_layout.addWidget(self.drive_motion_adresses_label, 1, 0)

        #grid_layout.addWidget(self.sourcemeter_adresses_combo, 0, 1)
        #grid_layout.addWidget(self.sourcemeter_adresses_combo_label, 1, 1)

        #grid_layout.addWidget(self.choice_sourcemeter_label_combo, 0, 2)
        #grid_layout.addWidget(self.choice_sourcemeter_label, 1, 2)

        grid_layout.addWidget(self.make_connection_with_devices_label, 0, 1)
        grid_layout.addWidget(self.make_connection_with_devices_button, 1, 1)

        #grid_layout.addWidget(self.resistance_label, 0, 4)
        #grid_layout.addWidget(self.resistance_read_button, 1, 4)

        grid_layout.addWidget(self.make_connection_textbox, 0, 2)
        grid_layout.addWidget(self.make_connection_label, 1, 2)

        grid_layout.addWidget(self.connect_checkable_button, 0, 3)
        grid_layout.addWidget(self.led_indicator_label, 1, 3)

        grid_layout.addWidget(self.enable_motors_checkable_button, 0, 4)
        grid_layout.addWidget(self.enable_motors_checkable_label, 1, 4)

        grid_layout.addWidget(self.go_x_textbox, 0, 5)
        grid_layout.addWidget(self.go_y_textbox, 1, 5)
        grid_layout.addWidget(self.go_z_textbox, 2, 5)

        grid_layout.addWidget(self.go_button, 1, 6)






        layout.addLayout(grid_layout)


        #main part of widget
        N=13
        row_n = [QtWidgets.QHBoxLayout() for i in range(N)]

        col_name =[QtWidgets.QVBoxLayout() for i in range(N)]
        col_field=[QtWidgets.QVBoxLayout() for i in range(N)]
        col_button=[QtWidgets.QVBoxLayout() for i in range(N)]
        
        # col_button=[None if i in {0,2,4,8} else QtWidgets.QVBoxLayout() for i in range(N)]

        
        col_name[0].addWidget(self.number_of_element_in_the_x_axis_name)
        col_field[0].addWidget(self.number_of_element_in_the_x_axis_textbox)

        col_name[1].addWidget(self.number_of_element_in_the_y_axis_name)
        col_field[1].addWidget(self.number_of_element_in_the_y_axis_textbox)

        col_name[2].addWidget(self.first_element_x_name)
        col_field[2].addWidget(self.first_element_x_textbox)
        #col_button[0].addWidget(self.first_element_x_read_button)
        col_name[3].addWidget(self.first_element_y_name)
        col_field[3].addWidget(self.first_element_y_textbox)
        col_button[3].addWidget(self.first_element_xy_read_button)
        #col_name[4].addWidget(self.second_element_x_name)
        #col_field[4].addWidget(self.second_element_x_textbox)
        #col_button[4].addWidget(self.second_element_x_read_button)
        #col_name[5].addWidget(self.second_element_y_name)
        #col_field[5].addWidget(self.second_element_y_textbox)
        #col_button[5].addWidget(self.second_element_xy_read_button)
        col_name[6].addWidget(self.dx_calculation_name)
        col_field[6].addWidget(self.dx_calculation_textbox)
        #col_button[4].addWidget(self.dx_calculation_read_button)
        col_name[7].addWidget(self.dy_calculation_name)
        col_field[7].addWidget(self.dy_calculation_textbox)
        #col_button[7].addWidget(self.dx_dy_calculation_calc_button)
        col_name[8].addWidget(self.last_element_x_name)
        col_field[8].addWidget(self.last_element_x_textbox)
        col_name[9].addWidget(self.last_element_y_name)
        col_field[9].addWidget(self.last_element_y_textbox)
        col_button[9].addWidget(self.last_element_xy_read_button)
        col_name[10].addWidget(self.theta_name)
        #col_field[7].addWidget(self.last_element_x_textbox)
        #col_button[8].addWidget(self.theta_read_button)
        col_name[11].addWidget(self.name_patern_name)
        col_field[11].addWidget(self.name_patern_textbox)
        col_field[12].addWidget(self.generate_map_button)

        for i in range(N):
            row_n[i].addLayout(col_name[i])
            row_n[i].addLayout(col_field[i])
            row_n[i].addLayout(col_button[i])
            layout.addLayout(row_n[i]) #tutaj juz ma odzwierciedlenie w wygladzie




        # Ustawienie głównego layoutu dla widgetu
        self.setLayout(layout)
        self.setWindowTitle('automatic station generator')
        #self.setGeometry(300, 300, 400, 200)
        
        
        #row_name_layout.addLayout(QtWidgets.QLabel('sth7'))



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = AutomaticStationGenerator()
    widget.open_widget()
    #widget.show()
    sys.exit(app.exec_())