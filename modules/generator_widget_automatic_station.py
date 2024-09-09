import pyvisa as visa
from pymeasure.display.Qt import QtCore, QtWidgets, QtGui
import sys
sys.path.append("/home/mariusz/moje_pliki/programowanie/python/spinlab_measurement/")
sys.path.append("C:\\Users\\IE\\git\\spinlab_measurement")
from logic.find_instrument import FindInstrument
from hardware.dummy_motion_driver import DummyMotionDriver
from hardware.esp300_simple import Esp300
from hardware.keithley2400 import Keithley2400
from functools import partial
from PyQt5.QtCore import Qt, QSettings
from logic.map_generator import generate_coord
import json

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

        if self.sample_in_plane_checkbox.isChecked():
            self.MotionDriver.goTo_2(self.go_x_textbox.text())
            self.MotionDriver.goTo_1(self.go_y_textbox.text())
            self.MotionDriver.goTo_3(self.go_z_textbox.text())
        else:
            self.MotionDriver.goTo_2(self.go_x_textbox.text())
            self.MotionDriver.goTo_3(self.go_y_textbox.text())
            self.MotionDriver.goTo_1(self.go_z_textbox.text())


    def read_for_go_button(self):
        self.go_x_textbox.setText(str(self.MotionDriver.pos_2()))
        self.go_y_textbox.setText(str(self.MotionDriver.pos_3()))
        self.go_z_textbox.setText(str(self.MotionDriver.pos_1()))


    def _setup_ui(self):
        settings_file = 'automatic_station_generator_settings.ini'  # Możesz tutaj podać pełną ścieżkę np. '/path/to/my_custom_settings.ini'
        self.settings = QSettings(settings_file, QSettings.IniFormat)
        

        self.MotionDriver=DummyMotionDriver("trash")
        self.z_pos=self.MotionDriver.pos_1()
        print(self.z_pos)
        

        self.setWindowTitle("Automatic station generator")
        self.setWindowIcon(QtGui.QIcon(self.icon_path))

        #first part of widget
        self.drive_motion_adresses_combo=QtWidgets.QComboBox()
        self.drive_motion_adresses_combo.addItems(self.address_list) #dodaj prawdziwe
        self.drive_motion_adresses_label=QtWidgets.QLabel('Driver motion address')

        self.make_connection_with_devices_label=QtWidgets.QLabel('Make connection with devices')
        self.make_connection_with_devices_button=QtWidgets.QPushButton("connect")

        self.make_connection_label=QtWidgets.QLabel('connect distance [mm]')
        self.make_connection_textbox=QtWidgets.QLineEdit(self)
        self.make_connection_textbox.setFixedSize(100,20)
        self.make_connection_textbox.setAlignment(Qt.AlignLeft)

        self.connect_checkable_button=self.checkable_button = QtWidgets.QPushButton("disconnect")
        self.connect_checkable_button.setCheckable(True)
        self.led_indicator_label=QtWidgets.QLabel()
        self.led_indicator_label.setFixedSize(35,35)
        self.led_indicator_label.setAlignment(Qt.AlignCenter)
        self.connect_with_sample(False)
        self.connect_checkable_button.toggled.connect(self.connect_with_sample)

        self.enable_motors_checkable_button= QtWidgets.QPushButton("NO INFO")
        self.enable_motors_checkable_button.clicked.connect(self.enable_motors_function)
        self.enable_motors_checkable_label=QtWidgets.QLabel("Enable or disable motors")

        self.go_x_textbox=QtWidgets.QLineEdit()
        self.go_y_textbox=QtWidgets.QLineEdit()
        self.go_z_textbox=QtWidgets.QLineEdit()

        self.go_x_name=QtWidgets.QLabel('x [mm]')
        self.go_y_name=QtWidgets.QLabel('y [mm]')
        self.go_z_name=QtWidgets.QLabel('z [mm]')

        self.go_button=QtWidgets.QPushButton("GO")
        self.go_button.clicked.connect(self.go)

        self.read_for_go_button_button=QtWidgets.QPushButton("Read")
        self.read_for_go_button_button.clicked.connect(self.read_for_go_button)

        self.sample_in_plane_checkbox=QtWidgets.QCheckBox("Sample in plane")
    
        #main part of widget
        self.number_of_element_in_the_x_axis_name=QtWidgets.QLabel('number of elements on the x axis')
        self.number_of_element_in_the_x_axis_textbox=QtWidgets.QLineEdit(self)

        self.number_of_element_in_the_y_axis_name=QtWidgets.QLabel('number of elements on the y axis')
        self.number_of_element_in_the_y_axis_textbox=QtWidgets.QLineEdit(self)

        self.first_element_x_name=QtWidgets.QLabel('First element on x axis')
        self.first_element_x_textbox=QtWidgets.QLineEdit(self)

        self.first_element_y_name=QtWidgets.QLabel('First element on y axis')
        self.first_element_y_textbox=QtWidgets.QLineEdit(self)

        self.first_element_xy_read_button=QtWidgets.QPushButton('Read', self)
        self.first_element_xy_read_button.clicked.connect(partial(self.read_coordinates,"xy",self.first_element_x_textbox,self.first_element_y_textbox))

        self.dx_calculation_name=QtWidgets.QLabel('Dx')
        self.dx_calculation_textbox=QtWidgets.QLineEdit(self)

        self.dy_calculation_name=QtWidgets.QLabel('Dy')
        self.dy_calculation_textbox=QtWidgets.QLineEdit(self)

        self.last_element_x_name=QtWidgets.QLabel('Last element on x axis')
        self.last_element_x_textbox=QtWidgets.QLineEdit(self)

        self.last_element_y_name=QtWidgets.QLabel('Last element on y axis')
        self.last_element_y_textbox=QtWidgets.QLineEdit(self)

        self.last_element_xy_read_button=QtWidgets.QPushButton('Read', self)
        self.last_element_xy_read_button.clicked.connect(partial(self.read_coordinates,"xy",self.last_element_x_textbox,self.last_element_y_textbox))

        self.theta_name=QtWidgets.QLabel('Calculated theta angle')
        self.theta_value_name=QtWidgets.QLabel('??')

        self.name_patern_name=QtWidgets.QLabel('Name pattern')
        self.name_patern_textbox=QtWidgets.QLineEdit(self)
        self.name_patern_textbox.setToolTip("{col} - column marker (number) \n{col_char} - column marker (char) \n{row} - row marker (number) \n{row_char} - row marker (char)")

        self.initial_row_name=QtWidgets.QLabel('First row')
        self.initial_row_textbox=QtWidgets.QLineEdit(self)
        self.initial_row_textbox.setToolTip("Type column of element which you start")

        self.initial_column_name=QtWidgets.QLabel('First column')
        self.initial_column_textbox=QtWidgets.QLineEdit(self)
        self.initial_column_textbox.setToolTip("Type column of element which you start")

        self.generate_map_button=QtWidgets.QPushButton('Generate sequence', self)
        self.generate_map_button.clicked.connect(self.generate_sequence)

        #Devices connection
        self.make_connection_with_devices_button.clicked.connect(self.make_connection_with_devices)

        self.load_settings()
        
    def save_settings(self):
        # Zapisanie wartości do QSettings
        self.settings.setValue('drive_motion_adresses_combo', self.drive_motion_adresses_combo.currentIndex())
        self.settings.setValue('make_connection_textbox', self.make_connection_textbox.text())
        self.settings.setValue('sample_in_plane_checkbox', self.sample_in_plane_checkbox.isChecked())
       

        self.settings.setValue('first_element_x_textbox', self.first_element_x_textbox.text())
        self.settings.setValue('first_element_y_textbox', self.first_element_y_textbox.text())
        self.settings.setValue('number_of_element_in_the_x_axis_textbox', self.number_of_element_in_the_x_axis_textbox.text())
        self.settings.setValue('number_of_element_in_the_y_axis_textbox', self.number_of_element_in_the_y_axis_textbox.text())
        self.settings.setValue('dx_calculation_textbox', self.dx_calculation_textbox.text())
        self.settings.setValue('dy_calculation_textbox', self.dy_calculation_textbox.text())
        self.settings.setValue('last_element_x_textbox', self.last_element_x_textbox.text())
        self.settings.setValue('last_element_y_textbox', self.last_element_y_textbox.text())
        self.settings.setValue('name_patern_textbox', self.name_patern_textbox.text())
        self.settings.setValue('initial_row_textbox', self.initial_row_textbox.text())
        self.settings.setValue('initial_column_textbox', self.initial_column_textbox.text())
      

    def load_settings(self):
        self.drive_motion_adresses_combo.setCurrentIndex(int(self.settings.value('drive_motion_adresses_combo', 0)))
        self.make_connection_textbox.setText(self.settings.value('make_connection_textbox', ''))
        self.sample_in_plane_checkbox.setChecked(self.settings.value('sample_in_plane_checkbox', '').lower()=="true")

        self.first_element_x_textbox.setText(self.settings.value('first_element_x_textbox', ''))
        self.first_element_y_textbox.setText(self.settings.value('first_element_y_textbox', ''))
        self.number_of_element_in_the_x_axis_textbox.setText(self.settings.value('number_of_element_in_the_x_axis_textbox', ''))
        self.number_of_element_in_the_y_axis_textbox.setText(self.settings.value('number_of_element_in_the_y_axis_textbox', ''))
        self.dx_calculation_textbox.setText(self.settings.value('dx_calculation_textbox', ''))
        self.dy_calculation_textbox.setText(self.settings.value('dy_calculation_textbox', ''))
        self.last_element_x_textbox.setText(self.settings.value('last_element_x_textbox', ''))
        self.last_element_y_textbox.setText(self.settings.value('last_element_y_textbox', ''))
        self.name_patern_textbox.setText(self.settings.value('name_patern_textbox', ''))
        self.initial_row_textbox.setText(self.settings.value('initial_row_textbox', ''))
        self.initial_column_textbox.setText(self.settings.value('initial_column_textbox', ''))



    def closeEvent(self, event):
        self.save_settings()  # Zapisanie ustawień
        event.accept() 




    def get_motor_status(self):
        return self.MotionDriver.is_motor_1_active()*self.MotionDriver.is_motor_2_active()*self.MotionDriver.is_motor_3_active()

    def make_connection_with_devices(self):
        if self.drive_motion_adresses_combo.currentText()!="None":
            self.MotionDriver=Esp300(self.drive_motion_adresses_combo.currentText())
        else:
            self.MotionDriver=DummyMotionDriver(self.drive_motion_adresses_combo.currentText())
            print("DummyMotionDriver")

        self.read_for_go_button()
        self.z_pos=self.MotionDriver.pos_1()
        motor_status=self.get_motor_status()
        if motor_status:
            self.enable_motors_checkable_button.setText("Disable")
        else:
            self.enable_motors_checkable_button.setText("Enable")



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
        initial_column=self.initial_column_textbox.text()
        initial_row=self.initial_row_textbox.text()

        gc=generate_coord(first_element_x,first_element_y,number_of_element_in_the_x_axis,number_of_element_in_the_y_axis,dx_calculation,dy_calculation,last_element_x,last_element_y,name_pattern,initial_column,initial_row)

        self.theta_value_name.setText(str("{0} [rad]".format(gc['theta'])))

        #sequence generation
        seq_vector='- "Global "[x,y,name]"", "{0}"'.format(gc['move_vectors_prim'])

        with open('./example_sequence','w') as f:
            f.write(seq_vector)

        #data migration
        with open('./logic/parameters.json', 'r+') as file:
            data = json.load(file)
            data['disconnect_length']=float(self.make_connection_textbox.text())
            data['sample_in_plane']=float(self.sample_in_plane_checkbox.isChecked())
            file.seek(0)
            json.dump(data,file,indent=4)
            file.truncate()

            




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



    
    
    def connect_with_sample(self, checked):
        if checked and self.get_motor_status():
            self.led_indicator_label.setStyleSheet("background-color: green; border-radius: 10px;")
            self.connect_checkable_button.setText("Connect")
            self.MotionDriver.goTo_1(self.z_pos-float(self.make_connection_textbox.text()))

        else:
            self.led_indicator_label.setStyleSheet("background-color: red; border-radius: 10px;")
            self.connect_checkable_button.setText("Disconnect")
            self.MotionDriver.goTo_1(self.z_pos)
    
    def enable_motors_function(self, checked):
        
        motor_status=self.get_motor_status()

        if motor_status:
            self.MotionDriver.disable()
            
        else:
            self.MotionDriver.enable() #to ma byc negacja tekstu wysietlanego na ekranie, wtedy jest dobrze.

        motor_status=self.get_motor_status()

        if motor_status:
            self.enable_motors_checkable_button.setText("Disable")
        else:
            self.enable_motors_checkable_button.setText("Enable")


    def _layout(self):
        layout = QtWidgets.QVBoxLayout()

        grid_layout=QtWidgets.QGridLayout()

        grid_layout.addWidget(self.drive_motion_adresses_combo, 0, 0)
        grid_layout.addWidget(self.drive_motion_adresses_label, 1, 0)

        grid_layout.addWidget(self.make_connection_with_devices_label, 0, 1)
        grid_layout.addWidget(self.make_connection_with_devices_button, 1, 1)

        grid_layout.addWidget(self.make_connection_textbox, 0, 2)
        grid_layout.addWidget(self.make_connection_label, 1, 2)

        grid_layout.addWidget(self.connect_checkable_button, 0, 3)
        grid_layout.addWidget(self.led_indicator_label, 1, 3)

        grid_layout.addWidget(self.enable_motors_checkable_button, 0, 4)
        grid_layout.addWidget(self.enable_motors_checkable_label, 1, 4)

        grid_layout.addWidget(self.go_x_name, 0, 5)
        grid_layout.addWidget(self.go_y_name, 1, 5)
        grid_layout.addWidget(self.go_z_name, 2, 5)

        grid_layout.addWidget(self.go_x_textbox, 0, 6)
        grid_layout.addWidget(self.go_y_textbox, 1, 6)
        grid_layout.addWidget(self.go_z_textbox, 2, 6)

        grid_layout.addWidget(self.go_button, 2, 7)
        grid_layout.addWidget(self.read_for_go_button_button,1,7)

        grid_layout.addWidget(self.sample_in_plane_checkbox,1,8)
        layout.addLayout(grid_layout)

        line=QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(line)
        
        #main part of widget
        grid_layout2=QtWidgets.QGridLayout()

        grid_layout2.addWidget(self.number_of_element_in_the_x_axis_name, 0, 0)
        grid_layout2.addWidget(self.number_of_element_in_the_x_axis_textbox,0,1)

        grid_layout2.addWidget(self.number_of_element_in_the_y_axis_name,1,0)
        grid_layout2.addWidget(self.number_of_element_in_the_y_axis_textbox,1,1)

        grid_layout2.addWidget(self.first_element_x_name,2,0)
        grid_layout2.addWidget(self.first_element_x_textbox,2,1)

        grid_layout2.addWidget(self.first_element_y_name,3,0)
        grid_layout2.addWidget(self.first_element_y_textbox,3,1)
        grid_layout2.addWidget(self.first_element_xy_read_button,3,2)

        grid_layout2.addWidget(self.dx_calculation_name,4,0)
        grid_layout2.addWidget(self.dx_calculation_textbox,4,1)

        grid_layout2.addWidget(self.dy_calculation_name,5,0)
        grid_layout2.addWidget(self.dy_calculation_textbox,5,1)

        grid_layout2.addWidget(self.last_element_x_name,6,0)
        grid_layout2.addWidget(self.last_element_x_textbox,6,1)

        grid_layout2.addWidget(self.last_element_y_name,7,0)
        grid_layout2.addWidget(self.last_element_y_textbox,7,1)
        grid_layout2.addWidget(self.last_element_xy_read_button,7,2)

        grid_layout2.addWidget(self.theta_name,8,0)
        grid_layout2.addWidget(self.theta_value_name,8,1)
        
        grid_layout2.addWidget(self.name_patern_name,9,0)
        grid_layout2.addWidget(self.name_patern_textbox,9,1)

        grid_layout2.addWidget(self.initial_row_name,10,0)
        grid_layout2.addWidget(self.initial_row_textbox,10,1)

        grid_layout2.addWidget(self.initial_column_name,11,0)
        grid_layout2.addWidget(self.initial_column_textbox,11,1)

        grid_layout2.addWidget(self.generate_map_button,12,1)

        layout.addLayout(grid_layout2)


        # Ustawienie głównego layoutu dla widgetu
        self.setLayout(layout)
        self.setWindowTitle('automatic station generator')


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = AutomaticStationGenerator()
    widget.open_widget()
    sys.exit(app.exec_())