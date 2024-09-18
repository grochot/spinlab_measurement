from logic.vector import Vector
from app import SpinLabMeasurement
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class MeasurementMode:
    def __init__(self, procedure):
        self.p: SpinLabMeasurement = procedure
        pass
    
    def generate_points(self):
        if self.p.vector != "":
            self.vector_obj = Vector()
            self.point_list = self.vector_obj.generate_vector(self.p.vector)
        else:
            log.error("Vector is not defined")
            self.point_list = [1]
        return self.point_list

    def initializing(self):
        raise NotImplementedError

    def operating(self, point):
        raise NotImplementedError

    def end(self):
        raise NotImplementedError
