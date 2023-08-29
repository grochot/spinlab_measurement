import numpy as np
class Vector():
	def __init__(self):
		pass

	def generate_vector(self, vec):
		ranges = vec.split(',')
		numbers = []
		if len(ranges) == 3:
			start = float(ranges[0])
			step = float(ranges[1])
			stop = float(ranges[2])
			numbers = list(np.arange(start, stop+step, step))
		w = 1
		if len(ranges) > 3:
			start = float(ranges[0])
			step = float(ranges[1])
			stop = float(ranges[2])
			numbers = list(np.arange(start, stop, step))
			for i in range(2, len(ranges)-2,2):
				start = float(ranges[i])
				step = float(ranges[i + 1])
				stop = float(ranges[i + 2])

				if w < len(range(2, len(ranges)-2,2)) :
					numbers= numbers + list(np.arange(start, stop, step))
				else:
					numbers= numbers + list(np.arange(start, stop+step, step))
				w = w + 1
		return numbers


