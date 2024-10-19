# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 13:31:36 2024

@author: IE
"""

import numpy as np
import json

list= [[3.38514, -1.95961, 'A5'], [2.7851399999999997, -1.95961, 'B5'], [2.1851399999999996, -1.95961, 'C5'], [1.58514, -1.95961, 'D5'], [0.9851399999999999, -1.95961, 'E5'], [0.3851399999999998, -1.95961, 'F5'], [-0.21485999999999983, -1.95961, 'G5'], [-0.8148600000000004, -1.95961, 'H5'], [-1.41486, -1.95961, 'I5'], [-2.0148599999999997, -1.95961, 'J5'], [-2.61486, -1.95961, 'K5'], [-3.21486, -1.95961, 'L5']]
sublist=[3.38514, -1.95961, 'A5']

#%%
with open('../example_sequence','r') as f:
	seq=f.read()

#split=json.loads(str(seq.split('"')[5]))
tmp=(seq.split('"')[5]
print(type(tmp))

#%%find

element_id="B5"
for sublist in list:
	if sublist[2]==element_id:
		finded=sublist
		break
