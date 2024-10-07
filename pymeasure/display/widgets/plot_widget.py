#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import logging

import pyqtgraph as pg

from ..curves import ResultsCurve
from ..Qt import QtCore, QtWidgets
from .tab_widget import TabWidget
from .plot_frame import PlotFrame
from ...experiment import Procedure

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class PlotWidget(TabWidget, QtWidgets.QWidget):
    """ Extends :class:`PlotFrame<pymeasure.display.widgets.plot_frame.PlotFrame>`
    to allow different columns of the data to be dynamically chosen
    """
    
    sigCurveClicked = QtCore.Signal(object)

    def __init__(self, name, columns, x_axis=None, y_axis=None, refresh_time=0.2,
                 check_status=True, linewidth=1, parent=None):
        super().__init__(name, parent)
        self.columns = columns
        self.refresh_time = refresh_time
        self.check_status = check_status
        self.linewidth = linewidth
        self._setup_ui()
        self._layout()
        if x_axis is not None:
            self.columns_x.setCurrentIndex(self.columns_x.findText(x_axis))
            self.plot_frame.change_x_axis(x_axis)
        if y_axis is not None:
            self.columns_y.setCurrentIndex(self.columns_y.findText(y_axis))
            self.plot_frame.change_y_axis(y_axis)
            
        self.pointWidget = None
        self.isExpanded = False
        self.expandParam = None
        self.expandOffset = None

    def _setup_ui(self):
        self.columns_x_label = QtWidgets.QLabel(self)
        self.columns_x_label.setMaximumSize(QtCore.QSize(45, 16777215))
        self.columns_x_label.setText('X Axis:')
        self.columns_y_label = QtWidgets.QLabel(self)
        self.columns_y_label.setMaximumSize(QtCore.QSize(45, 16777215))
        self.columns_y_label.setText('Y Axis:')

        self.columns_x = QtWidgets.QComboBox(self)
        self.columns_y = QtWidgets.QComboBox(self)
        for column in self.columns:
            self.columns_x.addItem(column)
            self.columns_y.addItem(column)
        self.columns_x.activated.connect(self.update_x_column)
        self.columns_y.activated.connect(self.update_y_column)

        self.plot_frame = PlotFrame(
            self.columns[0],
            self.columns[1],
            self.refresh_time,
            self.check_status,
            parent=self,
        )
        self.updated = self.plot_frame.updated
        self.plot = self.plot_frame.plot
        self.plot.showGrid(x=True, y=True)
        self.columns_x.setCurrentIndex(0)
        self.columns_y.setCurrentIndex(1)

    def _layout(self):
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(0)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setSpacing(10)
        hbox.setContentsMargins(-1, 6, -1, 6)
        hbox.addWidget(self.columns_x_label)
        hbox.addWidget(self.columns_x)
        hbox.addWidget(self.columns_y_label)
        hbox.addWidget(self.columns_y)

        vbox.addLayout(hbox)
        vbox.addWidget(self.plot_frame)
        self.setLayout(vbox)

    def sizeHint(self):
        return QtCore.QSize(300, 600)

    def new_curve(self, results, color=pg.intColor(0), **kwargs):
        if 'pen' not in kwargs:
            kwargs['pen'] = pg.mkPen(color=color, width=self.linewidth)
        if 'antialias' not in kwargs:
            kwargs['antialias'] = False
        curve = ResultsCurve(results,
                             wdg=self,
                             x=self.plot_frame.x_axis,
                             y=self.plot_frame.y_axis,
                             symbol='o',
                             symbolPen=color,
                             symbolBrush=color,
                             symbolSize=5,
                             **kwargs,
                             )
        
        curve.sigClicked.connect(self.sigCurveClicked)
        curve.sigPointsClicked.connect(self.remove_points)
        curve.sigPointsHovered.connect(self.enlarge_point)
        
        return curve
    
    def enlarge_point(self, curve, spots):
        if curve.results.procedure.status == Procedure.RUNNING:
            return
        
        if not self.pointWidget.enabled:
            return

        for point in curve.scatter.points():
            point.setSymbol('o')
            point.setSize(5)
        
        for spot in spots:
            spot.setSymbol('x')
            spot.setSize(10)
    
    def remove_points(self, curve, spots):
        if curve.results.procedure.status == Procedure.RUNNING:
            return
        
        if not self.pointWidget.enabled:
            return

        for spot in spots:
            curve.remove_point(spot, self.pointWidget)

    def update_x_column(self, index):
        if self.pointWidget.enabled:
            self.pointWidget.undo_all()
            
        axis = self.columns_x.itemText(index)
        self.plot_frame.change_x_axis(axis)
        if self.isExpanded:
            self.expand(self.expandParam)

    def update_y_column(self, index):
        if self.pointWidget.enabled:
            self.pointWidget.undo_all()

        axis = self.columns_y.itemText(index)
        self.plot_frame.change_y_axis(axis)
        if self.isExpanded:
            self.expand(self.expandParam)
        
    def expand(self, param):
        curves = [item for item in self.plot.items if isinstance(item, ResultsCurve)]
        curves = [curve for curve in curves if curve.results.procedure.status != Procedure.RUNNING]
        self.expandParam = param
        max_amp = 0
        param_list = []
        for i, curve in enumerate(curves):
            amp = curve.get_amplitude()
            if amp > max_amp:
                max_amp = amp
            param_value = curve.get_param_value(param)
            param_list.append((param_value, i))
            
        self.expandOffset = max_amp * 1.1
            
        param_list.sort()
        offset_list = [0] * len(param_list)
    
        merged, i = 0, 0
        while i < len(param_list):
            while i < len(param_list) - 1 and param_list[i][0] == param_list[i+1][0]:
                offset_list[param_list[i][1]] =  i - merged
                merged += 1
                i += 1
            offset_list[param_list[i][1]] =  i - merged
            i += 1            

        for i, curve in enumerate(curves):
            curve.setOffset(offset_list[i] * self.expandOffset)
            
        self.isExpanded = True
                
    def collapse(self):
        self.plot_frame.collapse()
        self.isExpanded = False
        
    def on_finished(self):
        if self.isExpanded:
            self.expand(self.expandParam)

    def load(self, curve):
        curve.x = self.columns_x.currentText()
        curve.y = self.columns_y.currentText()
        curve.update_data()
        self.plot.addItem(curve)
        if self.isExpanded:
            self.expand(self.expandParam)

    def remove(self, curve):
        curve.isExpanded = False
        self.plot.removeItem(curve)
        if self.isExpanded:
            self.expand(self.expandParam)

    def set_color(self, curve, color):
        """ Change the color of the pen of the curve """
        curve.set_color(color)

    def preview_widget(self, parent=None):
        """ Return a widget suitable for preview during loading """
        return PlotWidget("Plot preview",
                          self.columns,
                          self.plot_frame.x_axis,
                          self.plot_frame.y_axis,
                          parent=parent,
                          )

    def clear_widget(self):
        self.plot.clear()
