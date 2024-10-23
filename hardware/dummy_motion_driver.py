import random as rd

class DummyMotionDriver:
    def __init__(self, resourceName):
        pass

    def pos_1(self):
        return 0.387

    def pos_2(self):
        return round(rd.random(),5)

    def pos_3(self):
        return round(rd.random(),5)
    
    def enable(self):
        print("Enabled")
    
    def disable(self):
        print("Disabled")

    def goTo_1(self,position):
        print("go_to1",position)

    def goTo_2(self,position):
        print("go_to2",position)

    def goTo_3(self,position):
        print("go_to3",position)

    def is_motor_1_active(self):
        return 1
    
    def is_motor_2_active(self):
        return 1
    
    def is_motor_3_active(self):
        return 1
    

    def define_home_1(self):
        pass

    def define_home_2(self):
        pass

    def define_home_3(self):
        pass

    def high_level_motion_driver(self,global_xyname,sample_in_plane,disconnect_length):
        pass


    def disconnect(self,sample_in_plane,disconnect_length):
        pass

    def init_position(self,sample_in_plane):
        pass


    def get_motor_status(self):
        return int(self.is_motor_1_active())*int(self.is_motor_2_active())*int(self.is_motor_3_active())
    
    def define_home_all_axes(self):
        self.define_home_1()
        self.define_home_2()
        self.define_home_3()
