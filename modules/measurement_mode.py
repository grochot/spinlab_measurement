class MeasurementMode:
    def __init__(self, procedure):
        pass
    
    def generate_points(self):
        raise NotImplementedError

    def initializing(self):
        raise NotImplementedError

    def operating(self, point):
        raise NotImplementedError

    def end(self):
        raise NotImplementedError
