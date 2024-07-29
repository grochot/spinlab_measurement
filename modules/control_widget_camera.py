import os
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from pyqtgraph.dockarea import DockArea, Dock
import logging
import numpy as np

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

        # self.thread_pool: QtCore.QThreadPool = QtCore.QThreadPool()
        self.thread_pool = QtCore.QThreadPool.globalInstance()

        self.camera_docks: list[CameraDock] = []
        self.max_docks: int = 4
        self.dock_count: int = 0

        self.working_channels: list[str] = ["None"] + [
            str(channel) for channel in get_camera_indexes()
        ]
        self.free_channels: list[str] = self.working_channels.copy()

        self._setup_ui()
        self._layout()

    def _setup_ui(self) -> None:
        self.setWindowTitle("Camera Control")
        self.setMinimumSize(1024, 576)

        self.add_dock_button = QtWidgets.QPushButton("Add Camera")
        self.add_dock_button.clicked.connect(self.add_dock)

        self.dock_area = DockArea(self)
        self.add_dock()

    def _layout(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.add_dock_button)
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
            self.free_channels.remove(channel)
        except ValueError:
            return
        for dock in self.camera_docks:
            if dock.id == id:
                continue
            dock.channel_occupied(channel)

    def release_channel(self, channel: str, id: int) -> None:
        if channel == "None":
            return
        self.free_channels.append(channel)
        for dock in self.camera_docks:
            if dock.id == id:
                continue
            dock.channel_released(channel)

    def on_dock_close(self, dock) -> None:
        self.camera_docks.remove(dock)
        self.release_channel(dock.channel, -1)
        self.add_dock_button.setEnabled(True)

    def closeEvent(self, event):
        for dock in self.camera_docks:
            dock.stop_video()
        event.accept()

    def showEvent(self, event):
        for dock in self.camera_docks:
            if dock.channel != "None":
                dock.start_video(dock.channel)
        event.accept()

    def shutdown(self):
        for dock in self.camera_docks:
            dock.stop_video()
        self.thread_pool.waitForDone()
        self.close()


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

        self.channel_combobox = QtWidgets.QComboBox()
        self.channel_combobox.currentTextChanged.connect(self.on_channel_change)
        for channel in self.channels:
            self.channel_combobox.addItem(channel)

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

        utils_layout.addWidget(self.channel_combobox)
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
        save_task = SaveImageTask(self.video_task)
        self.thread_pool.start(save_task)

    def start_video(self, channel: str):
        self.image_label.setText("Opening camera...")
        self.video_task = VideoTask(
            Signals(),
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

    def channel_occupied(self, channel: str):
        self.channel_combobox.blockSignals(True)
        self.channel_combobox.removeItem(self.channel_combobox.findText(channel))
        self.channel_combobox.blockSignals(False)

    def channel_released(self, channel: str):
        self.channel_combobox.blockSignals(True)
        self.channel_combobox.addItem(channel)
        self.channel_combobox.blockSignals(False)

    def resizeEvent(self, ev: QtGui.QResizeEvent) -> None:
        if self.video_task:
            self.video_task.label_size = self.image_label.size()
        super().resizeEvent(ev)


class Signals(QtCore.QObject):
    sigPixmapReady = QtCore.pyqtSignal(QtGui.QPixmap)
    sigError = QtCore.pyqtSignal(str)


class VideoTask(QtCore.QRunnable):
    def __init__(
        self,
        signal: Signals,
        channel: str,
        label_size: QtCore.QSize,
        show_timestamp: bool = False,
        sharpen: bool = False,
        brightness: int = 50,
    ):
        super(VideoTask, self).__init__()
        self.signal = signal
        self.channel: str = channel
        self.capture = None
        self.running: bool = False
        self.label_size = label_size
        self.show_timestamp: bool = show_timestamp
        self.sharpen: bool = sharpen
        self.brightness: int = brightness
        self.current_frame = None

        self.mutex = QtCore.QMutex()

    def run(self):
        self.running = True

        self.capture = cv2.VideoCapture(int(self.channel), cv2.CAP_DSHOW)
        if not self.capture.isOpened():
            self.signal.sigError.emit("Failed to open camera")
            return

        while self.running:
            is_read, frame = self.capture.read()
            if is_read:
                frame = cv2.convertScaleAbs(frame, alpha=self.brightness / 50)

                if self.sharpen:
                    frame = self.sharpen_image(frame)

                if self.show_timestamp:
                    frame = self.add_timestamp(frame)

                self.mutex.lock()
                self.current_frame = frame
                self.mutex.unlock()

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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    camera_control = CameraControl(nested=False)
    camera_control.show()
    sys.exit(app.exec_())
