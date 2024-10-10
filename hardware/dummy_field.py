class DummyField:
    def __init__(self, adapter):
        self.field_step = 100
        self.field_constant = None
        self.polarity_control_enabled = False
        self.address_polarity_control = None

    def set_field(self, field):
        pass
    
    def set_voltage(self, voltage):
        pass

    def shutdown(self):
        pass
