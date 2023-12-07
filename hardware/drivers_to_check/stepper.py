from hardware.instrument import Instrument
import time
import visa

class Stepper(Instrument):

    def CallibrationAzim(self, stepazimcal):
        self.write("CAL 0;{}".format(stepazimcal))

    def GoToZeroAzim(self):
        self.write("POS 0; -560")

    def GoToZeroPol(self):
        self.write("POS 1; 970")

    def CalibrationPolar(self, steppolarcal):
        self.write("CAL 1;{}".format(steppolarcal))

    def MoveAzim(self, stepazim):
        self.write("MOVE 0; {}".format(stepazim))

    def MovePolar(self, steppolar):
        self.write("MOVE 1; {}".format(steppolar))

    def PositionAzim(self, positionazim):
        self.write("POS 0; {}".format((positionazim*4.722222)-560))

    def PositionPolar(self, positionpolar):
        self.write("POS 1; {}".format((positionpolar*4.577777)+960))

    def AskPosition(self, eng):
        self.position=self.write("POS? {}".format(eng))
        return self.position

    def AskMove(self, engine):
        time.sleep(1)
        self.done = self.ask("MOVE {};0".format(engine))
        self.done = self.ask("MOVE {};0".format(engine))
        self.done = self.ask("MOVE {};0".format(engine))
        self.done = self.ask("MOVE {};0".format(engine))
        while self.done[0] == "B":
            self.done = self.AskMove(0)
        return self.done


    def __init__(self, adapter, **kwargs):
        super(Stepper, self).__init__(
            adapter, "Stepper", **kwargs
        )


# test = Stepper("ASRL3")
# # test.CallibrationAzim(5000)
# # test.AskMove(0)
# test.PositionAzim(0)
# test.AskMove(0)
# # print("done")
# # test.CalibrationPolar(-5000)
# # test.AskMove(1)
# # test.PositionPolar(0)
#
#
#
#
#
# #
# # rm = visa.ResourceManager()
# # scope = rm.get_instrument('ASRL3')
# # scope.timeout = 5000
# # scope.baud_rate = 115200
# # print(scope.query("POS? 0"))






