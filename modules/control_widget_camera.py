import sys
import cv2
import numpy as np
from pymeasure.display.Qt import QtWidgets, QtCore, QtGui
from pyqtgraph.dockarea import DockArea, Dock

class CameraDock(Dock):
    signalDockClosed = QtCore.pyqtSignal(str, int)
    def __init__(self, name, id, available_channels, **kwargs):

        super(CameraDock, self).__init__(name, **kwargs)
        self.id = id
        self.camera_control = CameraWidget(available_channels)
        self.addWidget(self.camera_control)
        self.sigClosed.connect(self.on_close)

    def on_close(self):
        self.camera_control.on_close()
        self.signalDockClosed.emit(self.camera_control.channel, self.id)


class CameraWidget(QtWidgets.QWidget):
    def __init__(self, available_channels, parent=None):
        super(CameraWidget, self).__init__(parent)
        self.available_channels = available_channels
        self.prev_channel = "None"
        self.channel = "None"
        self.capture = None
        self.capture_width = 640
        self.capture_height = 480
        self.button_width = 100


        self._setup_ui()
        self._layout()
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30ms

    def _setup_ui(self):
        self.setWindowTitle("Camera Control")
        # self.setWindowIcon(QIcon(self.icon_path))

        self.image_label = QtWidgets.QLabel()
        self.image_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.setMinimumSize(640+100, 480)

        self.channel_cb = QtWidgets.QComboBox()
        for channel in self.available_channels:
            self.channel_cb.addItem(str(channel))
        self.channel_cb.currentTextChanged.connect(self.on_channel_change)
        self.channel_cb.setFixedWidth(self.button_width)
    
    def _layout(self):
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addWidget(self.channel_cb)
        self.main_layout.addWidget(self.image_label)
        self.setLayout(self.main_layout)
    
    def set_available_channels(self):
        self.channel_cb.blockSignals(True)
        self.channel_cb.clear()
        self.prev_channel = "None"
        self.channel = "None"
        for channel in self.available_channels:
            self.channel_cb.addItem(str(channel))
        self.channel_cb.blockSignals(False)

    def channel_occupied(self, channel):
        self.channel_cb.blockSignals(True)
        self.channel_cb.removeItem(self.channel_cb.findText(channel))
        self.channel_cb.blockSignals(False)

    def channel_released(self, channel):
        self.channel_cb.blockSignals(True)
        self.channel_cb.addItem(channel)
        self.channel_cb.blockSignals(False)


    def on_channel_change(self, text):
        if self.capture:
            self.capture.release()
            self.capture = None

        self.prev_channel = self.channel
        self.channel = text

        if self.channel != "None":
            self.capture = cv2.VideoCapture(int(self.channel), cv2.CAP_DSHOW)
            if not self.capture.isOpened():
                print(f"Failed to open channel {self.channel}")
                self.capture = None


    def update_frame(self):
        if self.channel is None or not self.capture:
            self.image_label.setText("No channel selected")
            return

        ret, frame = self.capture.read()
        if ret:
            frame = cv2.resize(frame, (self.capture_width, self.capture_height))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            converted_Qt_image = QtGui.QImage(frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
            self.image_label.setPixmap(QtGui.QPixmap.fromImage(converted_Qt_image))
        else:
            self.image_label.setText("Failed to capture frame")

    def resizeEvent(self, event):
        QtWidgets.QWidget.resizeEvent(self, event)
        self.change_size(event.size().width())


    def change_size(self, value):
        self.capture_width = value - (self.button_width + 50)
        self.capture_height = int(self.capture_width * 9 / 16) 

    def on_close(self):
        if self.capture:
            self.capture.release()
        self.close()


class CameraControl(QtWidgets.QWidget):
    object_name = "camera_control"

    def __init__(self,parent=None):
        super(CameraControl, self).__init__(parent)
        self.name = "Camera Control"
        self.icon_path = "modules\icons\Camera.ico"

        self.working_channels = ["None"]
        self.available_channels = []
        self.docks = []
        self.widget_count = 0

        self.get_working_channels()
        self._setup_ui()
        self._layout()
        
    def open_widget(self):
        self.show()

    def refresh_channels(self):
        self.get_working_channels()
        for dock in self.docks:
            dock.camera_control.available_channels = self.available_channels
            dock.camera_control.set_available_channels()

    def get_working_channels(self):
        dev_port = 0
        non_working_channels = ["None"]
        self.working_channels = ["None"]

        while len(non_working_channels) < 2:
            camera = cv2.VideoCapture(dev_port, cv2.CAP_DSHOW)
            if not camera.isOpened():
                non_working_channels.append(dev_port)
            else:
                is_reading, img = camera.read()
                if is_reading:
                    self.working_channels.append(str(dev_port))
                camera.release()
            dev_port += 1
 
        self.available_channels = self.working_channels.copy()

    def _setup_ui(self):
        self.setWindowTitle(self.name)
        # self.setWindowIcon(QIcon(self.icon_path))

        self.add_dock_btn=QtWidgets.QPushButton('Add Camera')
        self.add_dock_btn.clicked.connect(self.add_dock)

        self.refresh_btn = QtWidgets.QPushButton('Refresh')
        self.refresh_btn.clicked.connect(self.refresh_channels)

        self.dock_area=DockArea()
        self.add_dock()

    def _layout(self):
        self.main_layout = QtWidgets.QVBoxLayout()

        self.btn_layout = QtWidgets.QHBoxLayout()
        self.btn_layout.addWidget(self.add_dock_btn)
        self.btn_layout.addWidget(self.refresh_btn)

        self.main_layout.addLayout(self.btn_layout)
        self.main_layout.addWidget(self.dock_area)
        self.setLayout(self.main_layout)
        
    def add_dock(self):
        dock = CameraDock('Dock', self.widget_count, self.available_channels, closable=True, autoOrientation=False)
        dock.signalDockClosed.connect(self.on_dock_close)
        self.widget_count += 1
        self.docks.append(dock)
        dock.camera_control.channel_cb.currentTextChanged.connect(lambda channel: self.on_channel_change(channel, dock.id))
        self.dock_area.addDock(dock, 'right')

    def on_channel_change(self, channel, id):
        self.occupy_channel(channel, id)
        self.release_channel(self.docks[id].camera_control.prev_channel, id)
            
    def occupy_channel(self, channel, id):
        if channel == "None":
            return
        
        self.available_channels.remove(channel)
        for i in range(len(self.docks)):
            if i == id:
                continue
            self.docks[i].camera_control.channel_occupied(channel)

    def release_channel(self, channel, id):
        if channel == "None":
            return
        
        self.available_channels.append(channel)
        for i in range(len(self.docks)):
            if i == id:
                continue
            self.docks[i].camera_control.channel_released(channel)

    def on_dock_close(self, channel, id):
        self.release_channel(channel, id)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    camera_control = CameraControl()
    camera_control.show()
    sys.exit(app.exec_())
