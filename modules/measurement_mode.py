from logic.vector import Vector
from app import SpinLabMeasurement
import logging
from abc import ABC, abstractmethod
from logic.hardware_creator import HardwareCreator

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class MeasurementMode(ABC):
    def __init__(self, procedure: SpinLabMeasurement):
        self.p: SpinLabMeasurement = procedure
        self.hardware_creator = HardwareCreator(procedure)

    def generate_points(self) -> list:
        if self.p.vector:
            vector_obj = Vector()
            self.point_list = vector_obj.generate_vector(self.p.vector)
        else:
            log.error("Vector is not defined")
            self.point_list = [1]
        return self.point_list

    @abstractmethod
    def initializing(self):
        pass

    @abstractmethod
    def operating(self, point) -> dict:
        pass

    @abstractmethod
    def end(self):
        pass
