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
        self.write("RDGMODE 1,{},1,1,1".format(resolution))
   
    def measure(self):
        self.field = self.ask("RDGFIELD?")
        return float(self.field)
    
# gg = Lakeshore("GPIB0::12::INSTR")
# print(float(gg.measure()))