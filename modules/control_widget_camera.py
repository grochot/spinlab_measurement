import os
os.environ["OPENCV_LOG_LEVEL"]="SILENT"
import sys
import cv2
import numpy as np
from pymeasure.display.Qt import QtWidgets, QtGui, QtCore
from pyqtgraph.dockarea import DockArea, Dock


class VideoThread(QtCore.QThread):
    frame_captured = QtCore.pyqtSignal(np.ndarray)
    error = QtCore.pyqtSignal(str)

    def __init__(self, source, parent=None):
        super(VideoThread, self).__init__(parent)
        self.source = source
        self.capture = None
        self.running = False

    def run(self):
        self.running = True
        if "rtsp://" in self.source:
            self.capture = cv2.VideoCapture(self.source)
        else:
            self.capture = cv2.VideoCapture(int(self.source), cv2.CAP_DSHOW)
        
        if not self.capture.isOpened():
            self.error.emit("Failed to open video stream")
            return

        while self.running:
            ret, frame = self.capture.read()
            if ret:
                self.frame_captured.emit(frame)
                self.msleep(2)
            else:
                self.error.emit("Failed to capture frame")
                break

    def stop(self):
        self.running = False
        self.quit()
        self.wait()
        if self.capture:
            self.capture.release()


class IpDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(IpDialog, self).__init__(parent)
        self.setWindowTitle("IP Camera")

        self.ip_edit = None

        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.ip_edit = QtWidgets.QLineEdit("rtsp://")
        ip_regex = QtCore.QRegExp(r"^rtsp://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        ip_validator = QtGui.QRegExpValidator(ip_regex, self.ip_edit)
        self.ip_edit.setValidator(ip_validator)

        self.buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def _layout(self):
        self.main_layout = QtWidgets.QFormLayout()

        self.main_layout.addRow("IP Address", self.ip_edit)
        self.main_layout.addWidget(self.buttons)

        self.setLayout(self.main_layout)
        

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
        self.capture_thread = None
        self.data_stripe = True
        self.sharpen_on = False
        self.capture_width = 640
        self.capture_height = 480
        self.button_width = 100
        self.brightness = 50
        self.frame_to_save = None

        # Variables for zooming
        self.zoom_factor = 1.0
        self.zoom_center = None

        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.image_label = QtWidgets.QLabel()
        self.image_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid black; font-size: 20px;")

        self.setMinimumSize(640+self.button_width, 480)

        self.channel_cb = QtWidgets.QComboBox()
        for channel in self.available_channels:
            self.channel_cb.addItem(str(channel))
        self.channel_cb.currentTextChanged.connect(self.on_channel_change)
        self.channel_cb.setFixedWidth(self.button_width)

        self.save_img_btn = QtWidgets.QPushButton("Save Image")
        self.save_img_btn.clicked.connect(self.save_image)
        self.save_img_btn.setFixedWidth(self.button_width)  

        self.brightness_sld = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.brightness_sld.setRange(0, 100)
        self.brightness_sld.setValue(50)
        self.brightness_sld.setFixedWidth(self.button_width)
        self.brightness_sld.valueChanged.connect(self.update_brightness)

        self.data_stripe_checkbox = QtWidgets.QCheckBox("Show data")
        self.data_stripe_checkbox.setChecked(True)
        self.data_stripe_checkbox.stateChanged.connect(self.toggle_data_stripe)

        self.sharpen_checkbox = QtWidgets.QCheckBox("Sharpen video")
        self.sharpen_checkbox.setChecked(False)
        self.sharpen_checkbox.stateChanged.connect(self.toggle_sharpen)

        self.brightness_text = QtWidgets.QLabel("Brightness")
        self.brightness_text.setFixedWidth(self.button_width)
        self.brightness_text.setFixedHeight(20)

        self.channel_text = QtWidgets.QLabel("Channel:")
        self.channel_text.setFixedWidth(self.button_width)
        self.channel_text.setFixedHeight(20)

    def _layout(self):
        self.main_layout = QtWidgets.QHBoxLayout()

        self.button_layout = QtWidgets.QVBoxLayout()
        self.button_layout.addWidget(self.channel_text)
        self.button_layout.addWidget(self.channel_cb)
        self.button_layout.addWidget(self.save_img_btn)
        self.button_layout.addWidget(self.brightness_text)
        self.button_layout.addWidget(self.brightness_sld)
        self.button_layout.addWidget(self.sharpen_checkbox)
        self.button_layout.addWidget(self.data_stripe_checkbox)
        self.button_layout.addStretch()

        self.main_layout.addLayout(self.button_layout)
        self.main_layout.addWidget(self.image_label)
        self.setLayout(self.main_layout)

    def update_brightness(self, value):
        self.brightness = value

    def save_image(self):
        if self.channel is None or not self.capture_thread:
            return

        path_to_save = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Image', 'image.jpg', 'Image Files (*.png *.jpg *.bmp)')[0]
        if path_to_save != "":
            cv2.imwrite(str(path_to_save), self.frame_to_save)
        else:
            print("Failed to capture frame")
    
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
        if self.capture_thread:
            self.capture_thread.frame_captured.disconnect(self.process_frame)
            self.capture_thread.stop()
            self.capture_thread = None

        self.prev_channel = self.channel
        self.channel = text

        if self.channel != "None":
            self.image_label.setText("Loading...")
            
            self.capture_thread = VideoThread(self.channel)
            self.capture_thread.frame_captured.connect(self.process_frame)
            self.capture_thread.error.connect(self.frame_capture_failed)
            self.capture_thread.start()
            return
        
        self.image_label.setText("No channel selected")
            
    def frame_capture_failed(self, error):
        self.capture_thread.frame_captured.disconnect(self.process_frame)
        self.capture_thread.stop()
        self.capture_thread = None
        self.image_label.setText(error)

    def toggle_data_stripe(self, state):
        self.data_stripe = state
    
    def toggle_sharpen(self, state):
        self.sharpen_on = state

    def process_frame(self, frame):
        brightness = self.brightness - 50
        frame = cv2.convertScaleAbs(frame, beta=brightness)

        if self.data_stripe:
            timestamp = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
            cv2.putText(frame, timestamp, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

        if self.sharpen_on:
            frame = self.sharpen_frame(frame)

        if self.zoom_center is not None and self.zoom_factor != 1.0:
            frame = self.apply_zoom(frame)

        frame_1080p = cv2.resize(frame, (1920, 1080))
        self.frame_to_save = frame_1080p

        if self.zoom_factor == 1.0:
            self.change_size(self.image_label.width(), self.image_label.height())
            frame = cv2.resize(frame, (self.capture_width, self.capture_height))

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        converted_Qt_image = QtGui.QImage(frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        self.image_label.setPixmap(QtGui.QPixmap.fromImage(converted_Qt_image))

    def apply_zoom(self, frame):
        # h, w, _ = frame.shape
        h = self.image_label.height()
        w = self.image_label.width()
        center_x, center_y = self.zoom_center
        zoom_w, zoom_h = int(w / self.zoom_factor), int(h / self.zoom_factor)

        start_x = max(0, center_x - zoom_w // 2)
        end_x = min(w, center_x + zoom_w // 2)
        start_y = max(0, center_y - zoom_h // 2)
        end_y = min(h, center_y + zoom_h // 2)

        frame = frame[start_y:end_y, start_x:end_x]
        return cv2.resize(frame, (w, h))

    def sharpen_frame(self, frame):
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
        sharpened = cv2.filter2D(frame, -1, kernel)
        return sharpened

    def resizeEvent(self, event):
        QtWidgets.QWidget.resizeEvent(self, event)
        self.change_size(self.image_label.width(), self.image_label.height())

    def change_size(self, width, height):
        new_width = width
        new_height = int(new_width * 9 / 16)
        if new_height > height:
            new_height = height
            new_width = int(new_height * 16 / 9)
        self.capture_width = new_width
        self.capture_height = new_height

    def on_close(self):
        if self.capture_thread:
            self.capture_thread.stop()
        self.close()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_factor = min(4.0, self.zoom_factor * 1.1)
        else:
            self.zoom_factor = max(1.0, self.zoom_factor / 1.1)
        print(self.zoom_factor)

        cursor_pos = self.image_label.mapFromGlobal(QtGui.QCursor.pos())
        print(cursor_pos.x(), cursor_pos.y())

        if cursor_pos.x() > 0 and cursor_pos.y() > 0 and self.zoom_factor > 1.0:
            self.zoom_center = (cursor_pos.x(), cursor_pos.y())
        
        # self.update_frame()



class CameraControl(QtWidgets.QWidget):
    object_name = "camera_control"

    def __init__(self,parent=None):
        super(CameraControl, self).__init__(parent)
        self.name = "Camera Control"
        self.icon_path = "modules\icons\Camera.ico"

        self.working_channels = ["None"]
        self.available_channels = []
        self.added_ip_channels = []

        self.docks = []
        self.widget_count = 0

        self.get_working_channels()
        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        self.setWindowTitle(self.name)
        self.setWindowIcon(QtGui.QIcon(self.icon_path))

        self.add_dock_btn=QtWidgets.QPushButton('Add Camera')
        self.add_dock_btn.clicked.connect(self.add_dock)

        self.refresh_btn = QtWidgets.QPushButton('Refresh')
        self.refresh_btn.clicked.connect(self.refresh_channels)

        self.add_ip_cam_btn = QtWidgets.QPushButton('Add IP Camera')
        self.add_ip_cam_btn.clicked.connect(self.open_ip_dialog)

        self.dock_area=DockArea()
        self.add_dock()

    def _layout(self):
        self.main_layout = QtWidgets.QVBoxLayout()

        self.btn_layout = QtWidgets.QHBoxLayout()
        self.btn_layout.addWidget(self.add_dock_btn)
        self.btn_layout.addWidget(self.refresh_btn)
        self.btn_layout.addWidget(self.add_ip_cam_btn)

        self.main_layout.addLayout(self.btn_layout)
        self.main_layout.addWidget(self.dock_area)
        self.setLayout(self.main_layout)
    
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


        while len(non_working_channels) < 5:
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
        self.available_channels.extend(self.added_ip_channels)

    def open_ip_dialog(self):
        ip_dialog = IpDialog()
        if ip_dialog.exec_():
            ip = ip_dialog.ip_edit.text()
            self.added_ip_channels.append(ip)
            self.release_channel(ip, -1)

        
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

    # cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_SILENT)
    app = QtWidgets.QApplication(sys.argv)
    camera_control = CameraControl()
    camera_control.show()
    sys.exit(app.exec_())
