from PyQt5 import QtWidgets, QtCore, QtGui


class SplitterHandle(QtWidgets.QSplitterHandle):
    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QColor(100, 100, 100))

        handle_rect = self.rect()
        circle_radius = 2
        spacing = 6

        y = (handle_rect.height() - circle_radius * 2) // 2
        center_x = handle_rect.width() // 2
        
        painter.drawEllipse(center_x - spacing - circle_radius, y, circle_radius * 2, circle_radius * 2)
        painter.drawEllipse(center_x - circle_radius, y, circle_radius * 2, circle_radius * 2)
        painter.drawEllipse(center_x + spacing - circle_radius, y, circle_radius * 2, circle_radius * 2)
            


class Splitter(QtWidgets.QSplitter):
    def createHandle(self):
        return SplitterHandle(self.orientation(), self)
