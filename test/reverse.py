import numpy as np

vector = np.linspace(-100, 100, 9) 

vector_rev = vector[::-1]
vec_final = np.append(vector[0:-1], vector_rev)
print(vec_final)