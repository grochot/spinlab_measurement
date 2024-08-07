from pymeasure.instruments import Instrument

class Lakeshore(Instrument):
    def __init__(self, resourceName, **kwargs):
        kwargs.setdefault('read_termination', '\n')
        super().__init__(
            resourceName,
            "LakeShore 475",
            includeSCPI=True,
            **kwargs
        )
    def range(self, range):
        self.write("RANGE {}".format(range))
    
    def resolution(self, resolution):
        resolution_dict = {"3 digits": 0,"4 digits": 1,"5 digits": 2}
        self.write("RDGMODE 1,{},1,1,1".format(resolution_dict[resolution]))
   
    def measure(self):
        self.field = self.ask("RDGFIELD?")
        return float(self.field)
    
# gg = Lakeshore("GPIB1::12::INSTR")
# gg.resolution("3 digits")