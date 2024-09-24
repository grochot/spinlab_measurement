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
import json
from os import path
#from generator_widget_automatic_station import AutomaticStationGenerator

class ElementSelection(QtWidgets.QWidget):
    def __init__(self,): #pododawaj tutaj zmienne ktore cie interesuja z poprzedniego idegtu
        super().__init__()

        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        pass


    def _layout(self):
        pass



#if __name__ == "__main__":
#    app = QtWidgets.QApplication(sys.argv)
#    widget = AutomaticStationGenerator()
#    widget.open_widget()
#    sys.exit(app.exec_())