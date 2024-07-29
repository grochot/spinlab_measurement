import os
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from pyqtgraph.dockarea import DockArea, Dock
import logging
import numpy as np
import json

os.environ["OPENCV_LOG_LEVEL"] = "SILENT"
import cv2

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_camera_indexes(limit: int = 5) -> list[int]:
    port = 0
    non_working_ports = []
    working_ports = []
    while len(non_working_ports) < limit:
        cap = cv2.VideoCapture(port, cv2.CAP_DSHOW)
        if not cap.isOpened():
            non_working_ports.append(port)
        else:
            is_read, _ = cap.read()
            if is_read:
                working_ports.append(port)
        cap.release()
        port += 1
    return working_ports


class CameraControl(QtWidgets.QWidget):
    object_name = "camera_control"

    def __init__(self, parent=None):
        super(CameraControl, self).__init__(parent)
        self.name = "Camera Control"
        # self.icon_path = "modules\icons\Camera.ico"
        self.icon_path = os.path.join("modules", "icons", "Camera.ico")

        app = QtWidgets.QApplication.instance()
        app.aboutToQuit.connect(self.shutdown)

        self.ip_camera_widget = IpCameraWidget()
        self.ip_camera_widget.sigAddIpCamera.connect(self.add_ip_camera)
        self.ip_camera_widget.sigRemoveIpCamera.connect(self.remove_ip_camera)

        # self.thread_pool: QtCore.QThreadPool = QtCore.QThreadPool()
        self.thread_pool = QtCore.QThreadPool.globalInstance()

        self.camera_docks: list[CameraDock] = []
        self.max_docks: int = 4
        self.dock_count: int = 0

        self.free_channels: list[str] = ["None"] + self.ip_camera_widget.ip_cameras
        self.get_camera_indexes()

        self.free_channels_mutex = QtCore.QMutex()

        self._setup_ui()
        self._layout()

    def get_camera_indexes(self) -> None:
        try:
            self.add_ip_camera_button.setEnabled(False)
        except AttributeError:
            pass

        for dock in self.camera_docks:
            dock.channel_combobox.setEnabled(False)

        task = GetCameraIndexesTask()
        task.signals.sigCameraIndexesReady.connect(self.on_camera_indexes_ready)
        self.thread_pool.start(task)

    def on_camera_indexes_ready(self, indexes: list[int]) -> None:
        with QtCore.QMutexLocker(self.free_channels_mutex):
            self.free_channels = (
                ["None"]
                + [str(index) for index in indexes]
                + self.ip_camera_widget.ip_cameras
            )
        self.add_ip_camera_button.setEnabled(True)
        for dock in self.camera_docks:
            dock.channels = self.free_channels
            dock.reset_channels()
            dock.channel_combobox.setEnabled(True)

    def _setup_ui(self) -> None:
        self.setWindowTitle("Camera Control")
        self.setMinimumSize(1024, 576)

        self.add_dock_button = QtWidgets.QPushButton("Add dock")
        self.add_dock_button.clicked.connect(self.add_dock)

        self.refresh_button = QtWidgets.QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_channels)

        self.add_ip_camera_button = QtWidgets.QPushButton("IP cameras")
        self.add_ip_camera_button.clicked.connect(self.open_camera_widget)
        self.add_ip_camera_button.setEnabled(False)

        self.dock_area = DockArea(self)
        self.add_dock()

    def _layout(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.add_dock_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.add_ip_camera_button)

        layout.addLayout(button_layout)
        layout.addWidget(self.dock_area)
        self.setLayout(layout)

    def add_dock(self) -> None:
        if len(self.camera_docks) == self.max_docks - 1:
            self.add_dock_button.setEnabled(False)

        dock: CameraDock = CameraDock(
            self.dock_count, self.free_channels, self.thread_pool
        )
        self.dock_count += 1
        dock.sigDockClose.connect(self.on_dock_close)
        dock.sigChannelChange.connect(self.on_channel_change)

        self.camera_docks.append(dock)
        self.dock_area.addDock(dock, "right")

    def on_channel_change(
        self, prev_channel: str, new_channel: str, dock_id: int
    ) -> None:
        self.occupy_channel(new_channel, dock_id)
        self.release_channel(prev_channel, dock_id)

    def occupy_channel(self, channel: str, id: int) -> None:
        if channel == "None":
            return
        try:
            with QtCore.QMutexLocker(self.free_channels_mutex):
                self.free_channels.remove(channel)
        except ValueError:
            return
        for dock in self.camera_docks:
            if dock.id == id:
                continue
            dock.remove_channel(channel)

    def release_channel(self, channel: str, id: int) -> None:
        if channel == "None":
            return
        with QtCore.QMutexLocker(self.free_channels_mutex):
            self.free_channels.append(channel)
        for dock in self.camera_docks:
            if dock.id == id:
                continue
            dock.add_channel(channel)

    def on_dock_close(self, dock) -> None:
        self.camera_docks.remove(dock)
        self.release_channel(dock.channel, -1)
        self.add_dock_button.setEnabled(True)

    def open_camera_widget(self):
        self.ip_camera_widget.show()

    def stop_all_videos(self) -> None:
        for dock in self.camera_docks:
            dock.stop_video()

    def refresh_channels(self) -> None:
        self.stop_all_videos()

        with QtCore.QMutexLocker(self.free_channels_mutex):
            self.free_channels = ["None"] + self.ip_camera_widget.ip_cameras
        self.get_camera_indexes()

    def add_ip_camera(self, ip: str) -> None:
        with QtCore.QMutexLocker(self.free_channels_mutex):
            self.free_channels.append(ip)
        for dock in self.camera_docks:
            dock.add_channel(ip)

    def remove_ip_camera(self, ip: str) -> None:
        with QtCore.QMutexLocker(self.free_channels_mutex):
            try:
                self.free_channels.remove(ip)
            except ValueError:
                pass

        for dock in self.camera_docks:
            dock.remove_channel(ip)

    def closeEvent(self, event):
        self.stop_all_videos()
        self.ip_camera_widget.close()
        event.accept()

    def showEvent(self, event):
        for dock in self.camera_docks:
            if dock.channel != "None":
                dock.start_video(dock.channel)
        event.accept()

    def shutdown(self):
        self.stop_all_videos()
        self.thread_pool.waitForDone()


class IpCameraWidget(QtWidgets.QWidget):
    sigAddIpCamera = QtCore.pyqtSignal(str)
    sigRemoveIpCamera = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(IpCameraWidget, self).__init__(parent)
        self.setWindowTitle("IP Cameras")

        self.ip_cameras: list[str] = []

        self._setup_ui()
        self._layout()
        self.load_ip_cameras()

    def _setup_ui(self):
        self.setMinimumWidth(400)

        self.ip_edit = QtWidgets.QLineEdit("rtsp://")
        ip_regex = QtCore.QRegExp(r"^rtsp://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        ip_validator = QtGui.QRegExpValidator(ip_regex)
        self.ip_edit.setValidator(ip_validator)

        self.add_button = QtWidgets.QPushButton("Add")
        self.add_button.clicked.connect(self.add_ip_camera)

        self.camera_table = QtWidgets.QTableWidget()
        self.camera_table.setColumnCount(2)
        self.camera_table.setHorizontalHeaderLabels(["IP", ""])
        self.camera_table.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch
        )
        self.camera_table.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeToContents
        )

    def _layout(self):
        layout = QtWidgets.QVBoxLayout()

        add_layout = QtWidgets.QHBoxLayout()
        add_layout.addWidget(self.ip_edit)
        add_layout.addWidget(self.add_button)

        layout.addLayout(add_layout)
        layout.addWidget(self.camera_table)

        self.setLayout(layout)

    def add_ip_camera(self):
        ip = self.ip_edit.text()
        if ip not in self.ip_cameras:
            self.sigAddIpCamera.emit(ip)
            self.ip_cameras.append(ip)
            self.add_camera_to_table(ip)
            self.save_ip_cameras()

    def add_camera_to_table(self, ip: str):
        row_position = self.camera_table.rowCount()
        self.camera_table.insertRow(row_position)
        self.camera_table.setItem(row_position, 0, QtWidgets.QTableWidgetItem(ip))

        remove_button = QtWidgets.QPushButton("Remove")
        remove_button.clicked.connect(lambda: self.remove_ip_camera(ip))
        self.camera_table.setCellWidget(row_position, 1, remove_button)

    def remove_ip_camera(self, ip: str):
        self.sigRemoveIpCamera.emit(ip)
        row = self.ip_cameras.index(ip)
        self.ip_cameras.remove(ip)
        self.camera_table.removeRow(row)
        self.save_ip_cameras()

    def save_ip_cameras(self):
        with open("ip_cameras.json", "w") as file:
            json.dump(self.ip_cameras, file)

    def load_ip_cameras(self):
        try:
            if os.path.exists("ip_cameras.json"):
                with open("ip_cameras.json", "r") as file:
                    self.ip_cameras = json.load(file)
                    for ip in self.ip_cameras:
                        self.add_camera_to_table(ip)
        except json.JSONDecodeError:
            pass


class CameraDock(Dock):
    sigDockClose = QtCore.pyqtSignal(object)
    sigChannelChange = QtCore.pyqtSignal(str, str, int)

    def __init__(
        self, id, channels: list[str], thread_pool: QtCore.QThreadPool, parent=None
    ):
        super(CameraDock, self).__init__("Camera", closable=True, autoOrientation=False)
        self.parent = parent

        self.id: int = id
        self.channels = channels
        self.channel: str = "None"
        self.thread_pool: QtCore.QThreadPool = thread_pool
        self.video_task: VideoTask = None
        self.is_dragging: bool = False
        self.last_mouse_pos: QtCore.QPoint = None

        self.sigClosed.connect(self.dock_close_event)

        self._setup_ui()
        self._layout()

    def _setup_ui(self) -> None:
        self.central_widget = QtWidgets.QWidget()

        self.image_label = QtWidgets.QLabel()
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.image_label.setMinimumSize(320, 180)
        self.image_label.setStyleSheet("border: 1px solid black;")
        self.image_label.setText("No camera selected")

        self.channel_label = QtWidgets.QLabel("Source:")
        self.channel_combobox = QtWidgets.QComboBox()
        if len(self.channels) == 1:
            self.channel_combobox.setEnabled(False)
        self.channel_combobox.currentTextChanged.connect(self.on_channel_change)
        self.channel_combobox.addItems(self.channels)

        self.timestamp_checkbox = QtWidgets.QCheckBox("Timestamp")
        self.timestamp_checkbox.setChecked(False)
        self.timestamp_checkbox.stateChanged.connect(self.on_timestamp_change)

        self.sharpen_checkbox = QtWidgets.QCheckBox("Sharpen")
        self.sharpen_checkbox.setChecked(False)
        self.sharpen_checkbox.stateChanged.connect(self.on_sharpen_change)

        self.brightness_label = QtWidgets.QLabel("Brightness")

        self.brightness_slider = ResetableSlider(QtCore.Qt.Horizontal)
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setValue(50)
        self.brightness_slider.setTickInterval(10)
        self.brightness_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.brightness_slider.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        )
        self.brightness_slider.valueChanged.connect(self.on_brightness_change)

        self.save_button = QtWidgets.QPushButton("Save Image")
        self.save_button.clicked.connect(self.save_image)

    def _layout(self) -> None:
        main_layout = QtWidgets.QHBoxLayout()
        utils_layout = QtWidgets.QVBoxLayout()

        utils_layout.addWidget(self.channel_label)
        utils_layout.addWidget(self.channel_combobox)

        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        utils_layout.addWidget(line)

        utils_layout.addWidget(self.timestamp_checkbox)
        utils_layout.addWidget(self.sharpen_checkbox)

        utils_layout.addWidget(self.brightness_label)
        utils_layout.addWidget(self.brightness_slider)

        utils_layout.addWidget(self.save_button)

        utils_layout.addStretch()
        main_layout.addLayout(utils_layout)
        main_layout.addWidget(self.image_label)
        self.central_widget.setLayout(main_layout)
        self.addWidget(self.central_widget)

    def on_channel_change(self, channel: str) -> None:
        self.sigChannelChange.emit(self.channel, channel, self.id)
        self.channel = channel

        self.stop_video()

        if channel == "None":
            self.image_label.setText("No camera selected")
            return

        self.start_video(channel)

    def on_timestamp_change(self, state: int) -> None:
        if not self.video_task:
            return
        self.video_task.show_timestamp = state == QtCore.Qt.Checked

    def on_sharpen_change(self, state: int) -> None:
        if not self.video_task:
            return
        self.video_task.sharpen = state == QtCore.Qt.Checked

    def on_brightness_change(self, value: int) -> None:
        if not self.video_task:
            return
        self.video_task.brightness = value

    def save_image(self):
        if not self.video_task:
            return
        save_task = SaveImageTask(self.video_task)
        self.thread_pool.start(save_task)

    def start_video(self, channel: str):
        self.image_label.setText("Opening camera...")
        self.video_task = VideoTask(
            channel,
            self.image_label.size(),
            self.timestamp_checkbox.isChecked(),
            self.sharpen_checkbox.isChecked(),
            self.brightness_slider.value(),
        )
        self.video_task.signal.sigPixmapReady.connect(self.update_image)
        self.video_task.signal.sigError.connect(self.image_label.setText)
        self.thread_pool.start(self.video_task)

    def stop_video(self):
        if self.video_task:
            self.video_task.stop()
            self.video_task = None

    def update_image(self, pixmap: QtGui.QPixmap) -> None:
        self.image_label.setPixmap(pixmap)

    def dock_close_event(self):
        self.sigDockClose.emit(self)
        self.stop_video()

    def remove_channel(self, channel: str):
        self.channel_combobox.blockSignals(True)
        if channel == self.channel:
            self.stop_video()
            self.image_label.setText("No camera selected")
            self.channel = "None"
            self.channel_combobox.setCurrentText("None")
        self.channel_combobox.removeItem(self.channel_combobox.findText(channel))
        self.channel_combobox.blockSignals(False)

    def add_channel(self, channel: str):
        self.channel_combobox.blockSignals(True)
        self.channel_combobox.addItem(channel)
        self.channel_combobox.blockSignals(False)

    def reset_channels(self):
        self.channel = "None"
        self.image_label.setText("No camera selected")
        self.channel_combobox.blockSignals(True)
        self.channel_combobox.clear()
        self.channel_combobox.addItems(self.channels)
        self.channel_combobox.blockSignals(False)

    def resizeEvent(self, ev: QtGui.QResizeEvent) -> None:
        if self.video_task:
            self.video_task.label_size = self.image_label.size()
        super().resizeEvent(ev)

    def wheelEvent(self, ev: QtGui.QWheelEvent) -> None:
        if not self.video_task:
            return

        if self.image_label.geometry().contains(ev.pos()):
            if ev.angleDelta().y() > 0:
                self.video_task.zoom = min(6, self.video_task.zoom + 1)
            else:
                self.video_task.zoom = max(0, self.video_task.zoom - 1)
        super().wheelEvent(ev)

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        if not self.video_task:
            return

        if self.image_label.geometry().contains(ev.pos()):
            if ev.button() == QtCore.Qt.RightButton:
                self.video_task.zoom = 0

            if (
                ev.button() == QtCore.Qt.LeftButton
                and not self.is_dragging
                and self.video_task.zoom > 0
            ):
                self.is_dragging = True
                self.last_mouse_pos = ev.pos()

        super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
        if self.video_task:
            if self.image_label.geometry().contains(ev.pos()):
                if self.is_dragging:
                    delta = self.last_mouse_pos - ev.pos()
                    self.video_task.pan(delta)
                    self.last_mouse_pos = ev.pos()

        super().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
        if ev.button() == QtCore.Qt.LeftButton:
            self.is_dragging = False

        super().mouseReleaseEvent(ev)


class VideoTaskSignals(QtCore.QObject):
    sigPixmapReady = QtCore.pyqtSignal(QtGui.QPixmap)
    sigError = QtCore.pyqtSignal(str)


class VideoTask(QtCore.QRunnable):
    def __init__(
        self,
        channel: str,
        label_size: QtCore.QSize,
        show_timestamp: bool = False,
        sharpen: bool = False,
        brightness: int = 50,
    ):
        super(VideoTask, self).__init__()
        self.signal: VideoTaskSignals = VideoTaskSignals()
        self.channel: str = channel
        self.capture = None
        self.running: bool = False
        self.label_size = label_size
        self.show_timestamp: bool = show_timestamp
        self.sharpen: bool = sharpen
        self.brightness: int = brightness
        self.current_frame = None

        self.zoom: int = 0
        self.pan_offset: QtCore.QPoint = QtCore.QPoint(0, 0)

        self.current_frame_mutex = QtCore.QMutex()

    def run(self):
        self.running = True
        if "rtsp://" in self.channel:
            self.capture = cv2.VideoCapture(self.channel, cv2.CAP_FFMPEG)
        else:
            self.capture = cv2.VideoCapture(int(self.channel), cv2.CAP_DSHOW)

        if not self.capture.isOpened():
            self.signal.sigError.emit("Failed to open camera")
            return

        while self.running:
            is_read, frame = self.capture.read()
            if is_read:

                frame = self.apply_zoom(frame)

                frame = self.adjust_brightness(frame)

                if self.sharpen:
                    frame = self.sharpen_image(frame)

                if self.show_timestamp:
                    frame = self.add_timestamp(frame)

                with QtCore.QMutexLocker(self.current_frame_mutex):
                    self.current_frame = frame

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = QtGui.QImage(
                    frame.data,
                    frame.shape[1],
                    frame.shape[0],
                    QtGui.QImage.Format_RGB888,
                )
                pixmap = QtGui.QPixmap.fromImage(image)
                scaled_pixmap = pixmap.scaled(
                    self.label_size,
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation,
                )
                self.signal.sigPixmapReady.emit(scaled_pixmap)
                QtCore.QThread.msleep(2)
            else:
                self.signal.sigError.emit("Failed to capture frame")
                break

    def adjust_brightness(self, frame):
        return cv2.convertScaleAbs(frame, alpha=self.brightness / 50)

    def add_timestamp(self, frame):
        font = cv2.FONT_HERSHEY_SIMPLEX
        timestamp = str(
            QtCore.QDateTime.currentDateTime().toString("hh:mm:ss dd.MM.yyyy")
        )

        frame_height = frame.shape[0]
        font_scale = frame_height / 500
        thickness = 2

        text_size = cv2.getTextSize(timestamp, font, font_scale, thickness)[0]
        origin = (frame.shape[1] - text_size[0] - 10, frame.shape[0] - 10)

        cv2.putText(
            frame,
            timestamp,
            origin,
            font,
            font_scale,
            (0, 0, 0),
            thickness * 2,
            cv2.LINE_AA,
        )
        cv2.putText(
            frame,
            timestamp,
            origin,
            font,
            font_scale,
            (255, 255, 255),
            thickness,
            cv2.LINE_AA,
        )
        return frame

    def sharpen_image(self, frame):
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(frame, -1, kernel)
        return sharpened

    def apply_zoom(self, frame):
        if self.zoom == 0:
            return frame
        center_x, center_y = frame.shape[1] // 2, frame.shape[0] // 2

        radius_x, radius_y = int(center_x / (self.zoom + 1)), int(
            center_y / (self.zoom + 1)
        )

        min_x, max_x = (
            center_x - radius_x + self.pan_offset.x(),
            center_x + radius_x + self.pan_offset.x(),
        )
        min_y, max_y = (
            center_y - radius_y + self.pan_offset.y(),
            center_y + radius_y + self.pan_offset.y(),
        )

        min_x = max(0, min_x)
        min_y = max(0, min_y)
        max_x = min(frame.shape[1], max_x)
        max_y = min(frame.shape[0], max_y)

        cropped = frame[min_y:max_y, min_x:max_x]

        frame = cv2.resize(cropped, frame.shape[1::-1], interpolation=cv2.INTER_LINEAR)
        return frame

    def pan(self, delta: QtCore.QPoint):
        self.pan_offset += delta
        self.pan_offset.setX(
            min(
                max(self.pan_offset.x(), -self.label_size.width() // 2),
                self.label_size.width() // 2,
            )
        )
        self.pan_offset.setY(
            min(
                max(self.pan_offset.y(), -self.label_size.height() // 2),
                self.label_size.height() // 2,
            )
        )

    def stop(self):
        self.running = False
        self.signal.sigPixmapReady.disconnect()
        self.signal.sigError.disconnect()
        if self.capture:
            self.capture.release()

    def get_current_frame(self):
        self.mutex.lock()
        frame = self.current_frame
        self.mutex.unlock()
        return frame
        self.mutex.lock()
        self.zoom = value
        self.mutex.unlock()


class ResetableSlider(QtWidgets.QSlider):
    def __init__(self, *args, **kwargs):
        super(ResetableSlider, self).__init__(*args, **kwargs)

    def mousePressEvent(self, ev: QtGui.QMouseEvent | None) -> None:
        if ev.button() == QtCore.Qt.RightButton:
            self.setValue(50)
        return super().mousePressEvent(ev)


class SaveImageTask(QtCore.QRunnable):
    def __init__(self, video_task: VideoTask):
        super(SaveImageTask, self).__init__()
        self.video_task = video_task

    def run(self):
        frame = self.video_task.get_current_frame()
        if frame is not None:
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                None,
                "Save Image",
                "",
                "Images (*.png *.jpg *.jpeg);;All Files (*)",
            )
            if file_path:
                cv2.imwrite(file_path, frame)


class GetCameraIndexesTaskSignals(QtCore.QObject):
    sigCameraIndexesReady = QtCore.pyqtSignal(list)


class GetCameraIndexesTask(QtCore.QRunnable):
    def __init__(self, limit: int = 5):
        super(GetCameraIndexesTask, self).__init__()
        self.limit = limit
        self.signals: GetCameraIndexesTaskSignals = GetCameraIndexesTaskSignals()

    def run(self):
        indexes = get_camera_indexes(self.limit)
        self.signals.sigCameraIndexesReady.emit(indexes)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    camera_control = CameraControl()
    camera_control.show()
    sys.exit(app.exec_())
