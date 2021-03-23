import numpy as np
import sys
import os
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
# Path of the this file
f_path = os.path.dirname(os.path.realpath(__file__))
f_path = f_path[0:f_path.rfind('\\')] + '\\comparison\\' 

# Directories to be used in order to read and save
# modified missions
wps_path = os.path.join(f_path, 'wps\\')
sim_path = os.path.join(f_path, 'wps_simulations\\')

def modify_waypoints():
	global window
	path_file = filedialog.askopenfilename(filetypes = [("txt", ".txt")])
	file_name = path_file.split('/')[-1]

	try:
		fh = open(path_file)
	except:
		print('Error, file cannot be opened')

	# Read each way point from the mission file
	wps = []
	for line in fh:
		wps.append(line.split('\t'))
	lat = np.array([float(wps[i][8]) for i in range(1,len(wps))])
	lng = np.array([float(wps[i][9]) for i in range(1,len(wps))])
	
	# New latitude and longitude for simulation
	lat_o, lng_o = -0.1058602, -78.3551253

	# Move mission to simulation position
	lat_d = lat_o - lat[0]
	lng_d = lng_o - lng[0]
	for i in range(lat.shape[0]):
		if lat[i] == 0.0: continue
		lat[i] = lat[i] + lat_d
	for i in range(lng.shape[0]):
		if lng[i] == 0.0: continue
		lng[i] = lng[i] + lng_d

	fh = open(sim_path + file_name, 'w')
	fh.write(str(wps[0][0]))
	for i in range(1, len(wps)):
		[fh.write(j + '\t') for j in wps[i][:8]]
		fh.write(str(np.around(lat[i-1],7))+'\t')
		fh.write(str(np.around(lng[i-1],7))+'\t')
		fh.write(str(wps[i][-2])+'\t')
		fh.write(str(wps[i][-1]))
	fh.close()
	messagebox.showinfo("Conversion", "Done!")


def main():
	global window
	window = Tk()
	window.title('Select File')
	btn = Button(window, text = 'Open Mission', width = 25, command = modify_waypoints)
	btn.grid(column = 0, row = 0, padx = 0, pady = 5)
	window.mainloop()

if __name__ == '__main__':
	main()


# print(	file_name.split('.')[0])

# print(list(params['NTUN'].keys())[1:])

# for key in list(params['NTUN'].keys())[1:]:
# 	print(type(key), key)
# 	print(params['NTUN'][key])

# data = dict()
# try:
# 	fh = open(path_file + file_name, 'r')
# except:
# 	print("Error while opening file")
# 	quit()
# for line in fh:
# 	if not line.startswith('FMT'): continue
# 	l = line.strip().replace(" ","").split(',')
# 	data[l[3]] = {item : [] for item in l[4:]}

# fh.close()
# data = { k:v for k, v in sorted(data.items())}
# # [print(key, data[key]) for key in data.keys()]
# s = str(data)
# s = s.replace("}, ","},\n")
# fh = open('log_structure.py', 'w')
# fh.write(s)
# fh.close

# data = {key : { sub :[] for sub in params[key]} for key in params.keys()}