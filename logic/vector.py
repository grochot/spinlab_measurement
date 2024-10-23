import numpy as np


class Vector:
    def __init__(self):
        pass

    def generate_vector(self, vec: str) -> list:
        ranges = vec.split(",")
        numbers = []
        if len(ranges) == 3:
            start = float(ranges[0])
            no_point = int(ranges[1])
            stop = float(ranges[2])
            numbers = list(np.linspace(start, stop, no_point))
        w = 1
        if len(ranges) > 3:
            start = float(ranges[0])
            no_point = int(ranges[1])
            stop = float(ranges[2])
            numbers = list(np.linspace(start, stop, no_point))
            for i in range(2, len(ranges) - 2, 2):
                start = float(ranges[i])
                no_point = int(ranges[i + 1])
                stop = float(ranges[i + 2])

                if w < len(range(2, len(ranges) - 2, 2)):
                    numbers = numbers + list(np.linspace(start, stop, no_point + 1))[1:]
                else:
                    numbers = numbers + list(np.linspace(start, stop, no_point + 1))[1:]
                w = w + 1
        return numbers
    
    def generate_ranges(self, vec: str) -> list:
        ranges = vec.split(",")
        numbers = []

        start_tab=[]
        no_point_tab=[]
        stop_tab=[]

        if len(ranges) == 3:
            start = float(ranges[0])
            no_point = int(ranges[1])
            stop = float(ranges[2])
            
            start_tab.append(start)
            no_point_tab.append(no_point_tab)
            stop_tab.append(stop_tab)

            #numbers = list(np.linspace(start, stop, no_point))
        w = 1
        if len(ranges) > 3:
            start = float(ranges[0])
            no_point = int(ranges[1])
            stop = float(ranges[2])
            numbers = list(np.linspace(start, stop, no_point))
            for i in range(2, len(ranges) - 2, 2):
                start = float(ranges[i])
                no_point = int(ranges[i + 1])
                stop = float(ranges[i + 2])

                if w < len(range(2, len(ranges) - 2, 2)):
                    numbers = numbers + list(np.linspace(start, stop, no_point + 1))[1:]
                else:
                    numbers = numbers + list(np.linspace(start, stop, no_point + 1))[1:]
                w = w + 1

                start_tab.append(start)
                no_point_tab.append(no_point_tab)
                stop_tab.append(stop_tab)
        return [start_tab,no_point,stop_tab]


# v = Vector()

# print(v.generate_vector("1,10,10,5,20,10,30"))
