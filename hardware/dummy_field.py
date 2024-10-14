class DummyField:
    def __init__(self, adapter):
        self.field_step = 100
        self.field_constant = None
        self.polarity_control_enabled = False
        self.address_polarity_control = None

    def set_field(self, field: float) -> float:
        return 0

    def set_voltage(self, voltage: float) -> float:
        return 0

    def shutdown(self):
        pass
