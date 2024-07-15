from ..Qt import QtWidgets, QtCore, QtGui
from .tab_widget import TabWidget

class FlowLayout(QtWidgets.QLayout):
    def __init__(self, parent=None):
        super().__init__(parent)

        if parent is not None:
            self.setContentsMargins(QtCore.QMargins(0, 0, 0, 0))

        self._item_list = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self._item_list.append(item)

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list[index]

        return None

    def takeAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)

        return None

    def expandingDirections(self):
        return QtCore.Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._do_layout(QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()

        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())

        size += QtCore.QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()

        for item in self._item_list:
            style = item.widget().style()
            layout_spacing_x = style.layoutSpacing(
                QtWidgets.QSizePolicy.PushButton, QtWidgets.QSizePolicy.PushButton, QtCore.Qt.Horizontal
            )
            layout_spacing_y = style.layoutSpacing(
                QtWidgets.QSizePolicy.PushButton, QtWidgets.QSizePolicy.PushButton, QtCore.Qt.Vertical
            )
            space_x = spacing + layout_spacing_x
            space_y = spacing + layout_spacing_y
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y()

class DeviceWidget(QtWidgets.QWidget):
    def __init__(self, device, parent=None):
        super().__init__(parent)
        self.device = device

        self._setup_ui()
        self._layout()


    def _setup_ui(self):
        self.button = QtWidgets.QPushButton()
        self.button.setIcon(QtGui.QIcon(self.device.icon_path))
        self.button.setIconSize(QtCore.QSize(75, 75))
        self.button.setFixedSize(90, 90)
        self.button.clicked.connect(self.device.open_widget)

        self.label = QtWidgets.QLabel(self.device.name)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

    def _layout(self):
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.button, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(self.label, alignment=QtCore.Qt.AlignCenter)
        self.setLayout(layout)
class DevicesWidget(TabWidget, QtWidgets.QWidget):
    def __init__(self, name, devices, parent=None):
        super().__init__(name, parent)
        self.devices = devices
        self.devices_widgets = []

        for device in self.devices:
            setattr(self, device.object_name, device())

        self._setup_ui()
        self._layout()

    def _setup_ui(self):
        for device in self.devices:
            widget = DeviceWidget(getattr(self, device.object_name))
            self.devices_widgets.append(widget)

        self.scroll_area = QtWidgets.QScrollArea()

    def _layout(self):
        container = QtWidgets.QWidget()
        layout = FlowLayout(container)
        for widget in self.devices_widgets:
            layout.addWidget(widget)
        container.setLayout(layout)
        
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(container)
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.scroll_area)
        self.setLayout(main_layout)
        
