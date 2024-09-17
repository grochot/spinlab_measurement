from pymeasure.display.windows.managed_dock_window import ManagedDockWindow
from pymeasure.experiment.procedure import Procedure
from pymeasure.experiment.parameters import FloatParameter, BooleanParameter

from PyQt5 import QtWidgets
import sys


class FitProcedure(Procedure):
    SETTINGS, PARAMETERS, NOT_VISIBLE = 0, 1, 2

    layout_type = BooleanParameter("Layout type", default=PARAMETERS, vis_cond=(NOT_VISIBLE))
    h_res = FloatParameter("Resonance field", default=0.0, units="Oe", vis_cond=PARAMETERS)
    freq = FloatParameter("Frequency", default=0.0, units="Hz", vis_cond=PARAMETERS)

    DATA_COLUMNS = ["h_res", "freq"]


class AnalysisWindow(ManagedDockWindow):
    def __init__(self):
        super().__init__(
            procedure_class=FitProcedure, inputs=["layout_type", "h_res", "freq"], x_axis="h_res", y_axis="freq", inputs_in_scrollarea=True
        )
        self.setWindowTitle("Analysis")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AnalysisWindow()
    window.show()
    sys.exit(app.exec_())
