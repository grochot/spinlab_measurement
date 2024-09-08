#%%Load variables
import numpy as np



#variables_from_widget
number_of_element_in_the_x_axis=5
number_of_element_in_the_y_axis=3
first_element_x=0.37
first_element_y=0.37
second_element_x=1.37
second_element_y=0.37
dx_calculation=1
dy_calculation=1
last_element_x=10.37
last_element_y=0.5
#end


#%%function
def generate_coord(first_element_x,first_element_y,number_of_element_in_the_x_axis,number_of_element_in_the_y_axis,dx_calculation,dy_calculation,last_element_x,last_element_y,name_pattern,initial_column,initial_row):
	try:
		initial_column_int=int(initial_column)
	except ValueError:
		initial_column_int=ord(initial_column.upper())-65
	
	try:
		initial_row_int=int(initial_row)
	except ValueError:
		initial_row_int=ord(initial_row.upper())-65
	
	
	move_vectors_prim=np.zeros((number_of_element_in_the_x_axis*number_of_element_in_the_y_axis,2))
	
	x_moves=0*first_element_x+np.arange(0,number_of_element_in_the_x_axis,1)*dx_calculation #tutaj jest terz przejscie do ukladu wlasnego
	y_moves=0*first_element_y+np.arange(0,number_of_element_in_the_y_axis,1)*(-1*dy_calculation)
	
	theta=np.arcsin((last_element_y-first_element_y)/(last_element_x-first_element_x))
	   
	
	x_moves_prim=np.zeros(x_moves.shape)
	y_moves_prim=np.zeros(y_moves.shape)
	
	
	cos_theta=np.cos(theta)
	sin_theta=np.sin(theta)
	
	move_vectors_prim=[]
	#names=[]
	i=0
	for y_idx in range(y_moves.shape[0]):
		for x_idx in range(x_moves.shape[0]):
			x_moves_prim=x_moves[x_idx]*cos_theta-y_moves[y_idx]*sin_theta+first_element_x
			y_moves_prim=x_moves[x_idx]*sin_theta+y_moves[y_idx]*cos_theta+first_element_y
	

			name=name_pattern.replace("{col}",str(initial_column_int+x_idx)).replace("{row}",str(initial_row_int+y_idx)).replace("{col_char}",chr(65+x_idx+initial_column_int)).replace("{row_char}",chr(65+y_idx+initial_row_int))
			move_vectors_prim.append([x_moves_prim,y_moves_prim,name])
			
			i+=1
	return {'move_vectors_prim':move_vectors_prim,'theta':theta}




if __name__=='__main__':
	coord=generate_coord(first_element_x,first_element_y,number_of_element_in_the_x_axis,number_of_element_in_the_y_axis,dx_calculation,dy_calculation,last_element_x,last_element_y)