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
from PyQt5.QtCore import Qt, QSettings
from logic.map_generator import generate_coord
#from modules.element_selection import ElementSelection
import json
from os import path
import ast
import logging
log = logging.getLogger(__name__) 
log.addHandler(logging.NullHandler()) 


class AutomaticStationGenerator(QtWidgets.QWidget):
    object_name = "automatic_station_generator"

    def __init__(self):
        super(AutomaticStationGenerator, self).__init__()
        self.state = False
        self.name = "Automatic Station"
        # self.icon_path = "modules\icons\AutomaticStationGenerator.ico"
        self.icon_path = path.join("modules", "icons", "AutomaticStationGenerator.ico")
        self.address_list = ["None"]
        self.address = "None"
        self.sequencer = None
        self.get_available_addresses()
        self._setup_ui()
        self._layout()

    def open_widget(self):
        self.get_available_addresses()
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

        if self.sample_in_plane_checkbox.isChecked():
            self.z_pos=self.MotionDriver.pos_3()
        else:
            self.z_pos=self.MotionDriver.pos_1()


    def read_for_go_button(self):
        if self.sample_in_plane_checkbox.isChecked():
            self.go_x_textbox.setText(format(self.MotionDriver.pos_2(),'f'))
            self.go_y_textbox.setText(format(self.MotionDriver.pos_1(),'f'))
            self.go_z_textbox.setText(format(self.MotionDriver.pos_3(),'f'))

        else:
            self.go_x_textbox.setText(format(self.MotionDriver.pos_2(),'f'))
            self.go_y_textbox.setText(format(self.MotionDriver.pos_3(),'f'))
            self.go_z_textbox.setText(format(self.MotionDriver.pos_1(),'f'))



    def _setup_ui(self):
        settings_file = 'automatic_station_generator_settings.ini'  # You can type full path there
        self.settings = QSettings(settings_file, QSettings.IniFormat)
        
        self.MotionDriver=DummyMotionDriver("")
        self.z_pos=self.MotionDriver.pos_1()
        
        self.setWindowTitle("Automatic station generator")
        self.setWindowIcon(QtGui.QIcon(self.icon_path))

        #first part of widget
        self.drive_motion_adresses_combo=QtWidgets.QComboBox()
        self.drive_motion_adresses_combo.addItems(self.address_list)
        self.drive_motion_adresses_label=QtWidgets.QLabel('Driver motion address')

        self.make_connection_with_devices_label=QtWidgets.QLabel('Make connection with devices')
        self.make_connection_with_devices_button=QtWidgets.QPushButton("connect")

        self.make_connection_label=QtWidgets.QLabel('Take off distance [mm]')
        self.make_connection_textbox=QtWidgets.QLineEdit(self)
        self.make_connection_textbox.setFixedSize(100,20)
        self.make_connection_textbox.setAlignment(Qt.AlignLeft)

        self.connect_checkable_button=QtWidgets.QPushButton("Take off")
        self.force_approach_button=QtWidgets.QPushButton("Force approach")
        self.force_approach_button.clicked.connect(self.force_approach_button_dialog)

        self.connect_checkable_button.setCheckable(True)
        self.led_indicator_label=QtWidgets.QLabel()
        self.led_indicator_label.setFixedSize(35,35)
        self.led_indicator_label.setAlignment(Qt.AlignCenter)
        
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

        self.sample_in_plane_checkbox=QtWidgets.QCheckBox("Perpendicular?",self)
        self.connect_with_sample(False)

        self.go_to_initialize_posotion_button=QtWidgets.QPushButton("Go to initialize position")
        self.go_to_initialize_posotion_button.clicked.connect(self.go_to_initialize_posotion)

        self.warning_using_dummy_textbox=QtWidgets.QLabel("")
        self.element_not_finded_textbox=QtWidgets.QLabel("")


        #main part of widget
        self.number_of_element_in_the_x_axis_name=QtWidgets.QLabel('number of elements on the x axis [int]')
        self.number_of_element_in_the_x_axis_textbox=QtWidgets.QLineEdit(self)

        self.number_of_element_in_the_y_axis_name=QtWidgets.QLabel('number of elements on the y axis [int]')
        self.number_of_element_in_the_y_axis_textbox=QtWidgets.QLineEdit(self)

        self.first_element_x_name=QtWidgets.QLabel('First element on x axis [mm]')
        self.first_element_x_textbox=QtWidgets.QLineEdit(self)

        self.first_element_y_name=QtWidgets.QLabel('First element on y axis [mm]')
        self.first_element_y_textbox=QtWidgets.QLineEdit(self)

        self.first_element_xy_read_button=QtWidgets.QPushButton('Read', self)
        self.first_element_xy_read_button.clicked.connect(partial(self.read_coordinates,self.first_element_x_textbox,self.first_element_y_textbox))

        self.dx_calculation_name=QtWidgets.QLabel('Dx [mm]')
        self.dx_calculation_textbox=QtWidgets.QLineEdit(self)

        self.dy_calculation_name=QtWidgets.QLabel('Dy [mm]')
        self.dy_calculation_textbox=QtWidgets.QLineEdit(self)

        self.last_element_x_name=QtWidgets.QLabel('Last element on x axis [mm]')
        self.last_element_x_textbox=QtWidgets.QLineEdit(self)

        self.last_element_y_name=QtWidgets.QLabel('Last element on y axis [mm]')
        self.last_element_y_textbox=QtWidgets.QLineEdit(self)

        self.last_element_xy_read_button=QtWidgets.QPushButton('Read', self)
        self.last_element_xy_read_button.clicked.connect(partial(self.read_coordinates,self.last_element_x_textbox,self.last_element_y_textbox))

        self.theta_name=QtWidgets.QLabel('Calculated theta angle [rad]')
        self.theta_value_name=QtWidgets.QLabel('??')

        self.name_patern_name=QtWidgets.QLabel('Name pattern [string]')
        self.name_patern_textbox=QtWidgets.QLineEdit(self)
        self.name_patern_textbox.setToolTip("{col} - column marker (number) \n{col_char} - column marker (char) \n{row} - row marker (number) \n{row_char} - row marker (char)")

        self.initial_row_name=QtWidgets.QLabel('First row [int/char]')
        self.initial_row_textbox=QtWidgets.QLineEdit(self)
        self.initial_row_textbox.setToolTip("Type column of element which you start")

        self.initial_column_name=QtWidgets.QLabel('First column [int/char]')
        self.initial_column_textbox=QtWidgets.QLineEdit(self)
        self.initial_column_textbox.setToolTip("Type column of element which you start")


        self.column_name_pattern_iterator_name=QtWidgets.QLabel('Column name iterator [int]')
        self.column_name_pattern_iterator_textbox=QtWidgets.QLineEdit(self)
        self.column_name_pattern_iterator_textbox.setToolTip("Type value of which program will increment name")


        self.row_name_pattern_iterator_name=QtWidgets.QLabel('row name iterator [int]')
        self.row_name_pattern_iterator_textbox=QtWidgets.QLineEdit(self)
        self.row_name_pattern_iterator_textbox.setToolTip("Type value of which program will increment name")

        self.generate_map_button=QtWidgets.QPushButton('Generate sequence', self)
        self.generate_map_button.clicked.connect(self.generate_sequence)

        self.element_selection_button=QtWidgets.QPushButton('Element selection', self)
        self.element_selection_button.clicked.connect(self.element_selection)

        self.go_to_element_textbox=QtWidgets.QLineEdit(self)
        self.go_to_element_button=QtWidgets.QPushButton('Go to element', self)
        self.go_to_element_button.clicked.connect(self.go_to_element)

        #Devices connection
        self.make_connection_with_devices_button.clicked.connect(self.make_connection_with_devices)

        self.load_settings()
        
    def save_settings(self):
        #saving parameters
        self.settings.setValue('drive_motion_adresses_combo', self.drive_motion_adresses_combo.currentIndex())
        self.settings.setValue('make_connection_textbox', self.make_connection_textbox.text())
        self.settings.setValue('sample_in_plane_checkbox', self.sample_in_plane_checkbox.isChecked())
        self.settings.setValue('go_to_element_textbox', self.go_to_element_textbox.text())
       

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
        self.settings.setValue('column_name_pattern_iterator_textbox', self.column_name_pattern_iterator_textbox.text())
        self.settings.setValue('row_name_pattern_iterator_textbox', self.row_name_pattern_iterator_textbox.text())

      

    def load_settings(self):
        self.drive_motion_adresses_combo.setCurrentIndex(int(self.settings.value('drive_motion_adresses_combo', 0)))
        self.make_connection_textbox.setText(self.settings.value('make_connection_textbox', ''))
        self.sample_in_plane_checkbox.setChecked(self.settings.value('sample_in_plane_checkbox', '').lower()=="true")
        self.go_to_element_textbox.setText(self.settings.value('go_to_element_textbox', ''))

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
        self.column_name_pattern_iterator_textbox.setText(self.settings.value('column_name_pattern_iterator_textbox', ''))
        self.row_name_pattern_iterator_textbox.setText(self.settings.value('row_name_pattern_iterator_textbox', ''))




    def closeEvent(self, event):
        self.save_settings()
        event.accept() 
    

    def force_approach_button_dialog(self):
        reply = QtWidgets.QMessageBox.question(self, 'Confirmation', 
                                     "Do to really want to force approach? - It can damage sample or connectors", 
                                     QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            self.force_approach()


    def force_approach(self):
        if self.get_motor_status():
            if self.sample_in_plane_checkbox.isChecked():
                self.MotionDriver.goTo_3(self.z_pos-float(self.make_connection_textbox.text()))
            else:
                self.MotionDriver.goTo_1(self.z_pos-float(self.make_connection_textbox.text()))
        else:
            if self.sample_in_plane_checkbox.isChecked():
                self.MotionDriver.goTo_3(self.z_pos)
            else:
                self.MotionDriver.goTo_1(self.z_pos)


    def go_to_element(self):

        if  path.isfile("./sequence"):
             with open("./sequence", "r") as f:
                sequence=ast.literal_eval(f.read().split('"')[5])
        else:
            print("Sequence doesn't exist - please generate it")
            return -2
        
        is_finded=False
        for sublist in sequence:
            if sublist[2]==self.go_to_element_textbox.text():
                finded=sublist
                is_finded=True
                if self.sample_in_plane_checkbox.isChecked():
                    self.z_pos=self.MotionDriver.pos_3()

                    self.MotionDriver.goTo_3(self.z_pos-float(self.make_connection_textbox.text())) #Take off
                    
                    self.MotionDriver.goTo_2(float(finded[0]))
                    self.MotionDriver.goTo_1(float(finded[1]))

                    self.MotionDriver.goTo_3(self.z_pos) #Approach

                    self.MotionDriver.pos_1() #Non sense reading position to stop program
                else:
                    self.z_pos=self.MotionDriver.pos_1()

                    self.MotionDriver.goTo_1(self.z_pos-float(self.make_connection_textbox.text())) #Take off
                    
                    self.MotionDriver.goTo_2(float(finded[0]))
                    self.MotionDriver.goTo_3(float(finded[1]))

                    self.MotionDriver.goTo_1(self.z_pos) #Approach

                    self.MotionDriver.pos_1() #Non sense reading position to stop program
                break
            else:
                pass
        
        if is_finded==False:
            self.element_not_finded_textbox.setText("Element not finded")
        else:
            self.element_not_finded_textbox.setText("")

        return 0



       


    def go_to_initialize_posotion(self):
        self.MotionDriver.goTo_1(0)
        self.MotionDriver.goTo_2(0)
        self.MotionDriver.goTo_3(0)


    def get_motor_status(self):
        return int(self.MotionDriver.is_motor_1_active())*int(self.MotionDriver.is_motor_2_active())*int(self.MotionDriver.is_motor_3_active())

    def make_connection_with_devices(self):
        if self.drive_motion_adresses_combo.currentText()!="None":
            self.MotionDriver=Esp300(self.drive_motion_adresses_combo.currentText())
            
            self.warning_using_dummy_textbox.setText("")
        else:
            self.MotionDriver=DummyMotionDriver(self.drive_motion_adresses_combo.currentText())
            self.warning_using_dummy_textbox.setText("Warning using dummy - device not connected")
            log.warning('Used dummy MotionDriver.')

        self.read_for_go_button()

        if self.sample_in_plane_checkbox.isChecked():
            self.z_pos=self.MotionDriver.pos_3()
        else:
            self.z_pos=self.MotionDriver.pos_1()

        motor_status=self.get_motor_status()
        if motor_status:
            self.enable_motors_checkable_button.setText("Disable")
        else:
            self.enable_motors_checkable_button.setText("Enable")


    def element_selection(self):
        out=self.generate_sequence()
        out.append(self.settings)
        out.append(self.save_settings)
        self.element_selection_widget=ElementSelection(*out)
        self.element_selection_widget.show()


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
        column_iterator=int(self.column_name_pattern_iterator_textbox.text())
        row_iterator=int(self.row_name_pattern_iterator_textbox.text())
        sample_in_plane=self.sample_in_plane_checkbox.isChecked()

        gc=generate_coord(first_element_x,first_element_y,number_of_element_in_the_x_axis,number_of_element_in_the_y_axis,dx_calculation,dy_calculation,last_element_x,last_element_y,name_pattern,initial_column,initial_row,column_iterator,row_iterator,sample_in_plane)

        self.theta_value_name.setText(str("{0} [rad]".format(gc['theta'])))

        #sequence generation
        seq_vector='- "Global "[x,y,name]"", "{0}"'.format(gc['move_vectors_prim'])

        with open('./sequence','w') as f:
            f.write(seq_vector)
            
        if self.sequencer is not None:
            self.sequencer.load_sequence(filename='./sequence')

        return [number_of_element_in_the_x_axis,number_of_element_in_the_y_axis,gc['move_vectors_prim'],self.sequencer]
    
    def read_coordinates(self,write_axes1,write_axes2):
        #z=pos1
        #x=pos2
        #y=pos3
        if self.sample_in_plane_checkbox.isChecked():
            write_axes1.setText(str(self.MotionDriver.pos_2()))
            write_axes2.setText(str(self.MotionDriver.pos_1()))
        else:
            write_axes1.setText(str(self.MotionDriver.pos_2()))
            write_axes2.setText(str(self.MotionDriver.pos_3())) 



    
    
    def connect_with_sample(self, checked):
        if checked and self.get_motor_status():
            if self.sample_in_plane_checkbox.isChecked():
                self.MotionDriver.goTo_3(self.z_pos-float(self.make_connection_textbox.text()))
            else:
                self.MotionDriver.goTo_1(self.z_pos-float(self.make_connection_textbox.text()))
            self.led_indicator_label.setStyleSheet("background-color: green; border-radius: 10px;")
            self.connect_checkable_button.setText("Approach")
        else:
            if self.sample_in_plane_checkbox.isChecked():
                self.MotionDriver.goTo_3(self.z_pos)
            else:
                self.MotionDriver.goTo_1(self.z_pos)
            self.led_indicator_label.setStyleSheet("background-color: red; border-radius: 10px;")
            self.connect_checkable_button.setText("Take off")
    
    def enable_motors_function(self):
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

        grid_layout.addWidget(self.make_connection_with_devices_button, 0, 1)
        grid_layout.addWidget(self.make_connection_with_devices_label, 1, 1)
        grid_layout.addWidget(self.warning_using_dummy_textbox, 2, 1)

        grid_layout.addWidget(self.make_connection_textbox, 0, 2)
        grid_layout.addWidget(self.make_connection_label, 1, 2)


        grid_layout.addWidget(self.force_approach_button, 0, 3)
        grid_layout.addWidget(self.connect_checkable_button, 1, 3)
        grid_layout.addWidget(self.led_indicator_label, 2, 3)

        grid_layout.addWidget(self.enable_motors_checkable_button, 0, 4)
        grid_layout.addWidget(self.enable_motors_checkable_label, 1, 4)

        grid_layout.addWidget(self.go_x_name, 0, 5)
        grid_layout.addWidget(self.go_y_name, 1, 5)
        grid_layout.addWidget(self.go_z_name, 2, 5)

        grid_layout.addWidget(self.go_x_textbox, 0, 6)
        grid_layout.addWidget(self.go_y_textbox, 1, 6)
        grid_layout.addWidget(self.go_z_textbox, 2, 6)

        grid_layout.addWidget(self.read_for_go_button_button,1,7)
        grid_layout.addWidget(self.go_button, 2, 7)

        grid_layout.addWidget(self.go_to_initialize_posotion_button, 0, 8)
        grid_layout.addWidget(self.sample_in_plane_checkbox,1,8)

        grid_layout.addWidget(self.go_to_element_textbox, 0, 9)
        grid_layout.addWidget(self.go_to_element_button,1,9)
        grid_layout.addWidget(self.element_not_finded_textbox,2,9)

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

        grid_layout2.addWidget(self.initial_column_name,10,0)
        grid_layout2.addWidget(self.initial_column_textbox,10,1)

        grid_layout2.addWidget(self.initial_row_name,11,0)
        grid_layout2.addWidget(self.initial_row_textbox,11,1)

        grid_layout2.addWidget(self.column_name_pattern_iterator_name,12,0)
        grid_layout2.addWidget(self.column_name_pattern_iterator_textbox,12,1)

        grid_layout2.addWidget(self.row_name_pattern_iterator_name,13,0)
        grid_layout2.addWidget(self.row_name_pattern_iterator_textbox,13,1)

        grid_layout2.addWidget(self.generate_map_button,14,1)
        grid_layout2.addWidget(self.element_selection_button,14,2)

        layout.addLayout(grid_layout2)

        self.setLayout(layout)
        self.setWindowTitle('automatic station generator')



class ElementSelection(QtWidgets.QWidget):
    def __init__(self,number_of_element_in_the_x_axis,number_of_element_in_the_y_axis,moves_vectors_prim,sequencer,settings,save_settings):
        super().__init__()
        self.number_of_element_in_the_x_axis=number_of_element_in_the_x_axis
        self.number_of_element_in_the_y_axis=number_of_element_in_the_y_axis
        self.moves_vectors_prim=moves_vectors_prim
        self.sequencer=sequencer
        self.settings=settings
        self.save_settings=save_settings
        #settings_file = 'automatic_station_generator_settings.ini'  # You can type full path there
        #self.settings = QSettings(settings_file, QSettings.IniFormat)
        self.initUI()
        self.load_previous_state()



    def extract_checked(self):
        new_sequence=[]
        for i in range(len(self.checkboxes)):
            if self.checkboxes[i].isChecked():
                new_sequence.append(self.moves_vectors_prim[i])

        #sequence generation
        seq_vector='- "Global "[x,y,name]"", "{0}"'.format(new_sequence)

        with open('./sequence','w') as f:
            f.write(seq_vector)
            
        if self.sequencer is not None:
            self.sequencer.load_sequence(filename='./sequence')

    def closeEvent(self, event):
        for i in range(0,len(self.checkboxes),1):
            self.settings.setValue('element_checked_{0}'.format(i), self.checkboxes[i].isChecked())
        event.accept() 

    def mark_unmark_all(self,checked):
        for i in range(len(self.checkboxes)):
            self.checkboxes[i].setChecked(checked)



    def load_previous_state(self):
        for i in range(0,len(self.checkboxes),1):
            self.checkboxes[i].setChecked(str(self.settings.value('element_checked_{0}'.format(i), '')).lower()=="true")

    def clean(self):
        for i in range(0,len(self.checkboxes),1):
            self.checkboxes[i].setChecked(0)

    def initUI(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.grid = QtWidgets.QGridLayout()
        self.checkboxes=[]


        self.clean_button=QtWidgets.QPushButton('Clean')
        self.clean_button.clicked.connect(self.clean)
        self.new_sequence_button = QtWidgets.QPushButton('Generate new sequence')
        self.mark_unmark_all_checkable_button = QtWidgets.QPushButton('Mark/unmark all')
        self.mark_unmark_all_checkable_button.setCheckable(True)
        self.mark_unmark_all(False)
        
        self.mark_unmark_all_checkable_button.toggled.connect(self.mark_unmark_all)
        self.new_sequence_button.clicked.connect(self.extract_checked)

        for row in range(self.number_of_element_in_the_y_axis):
            for col in range(self.number_of_element_in_the_x_axis):
                hbox = QtWidgets.QHBoxLayout()

                checkbox = QtWidgets.QCheckBox()
                self.checkboxes.append(checkbox)

                index=(row*self.number_of_element_in_the_x_axis+col)
                label = QtWidgets.QLabel(self.moves_vectors_prim[index][2])
                
                hbox.addWidget(checkbox)
                hbox.addWidget(label)

                self.grid.addLayout(hbox, self.number_of_element_in_the_x_axis-row, col)

        self.main_layout.addWidget(self.clean_button)
        self.main_layout.addWidget(self.mark_unmark_all_checkable_button)
        self.main_layout.addLayout(self.grid)
        self.main_layout.addWidget(self.new_sequence_button)
        

        self.setLayout(self.main_layout)

        self.setWindowTitle('Element selection')
        self.setGeometry(300, 300, 400, 300)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = AutomaticStationGenerator()
    widget.open_widget()
    sys.exit(app.exec_())