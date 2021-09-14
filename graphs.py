# Call tools file to create an LogeFileData object and
# create graphs 
import numpy as np
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import filedialog
from tools import LogFileData
path_file = ''

# Fuction that is called when user selects a log file
def process_log():
	global path_file
	global log_num
	global data_log
	global window

	# Create var to get and store de file's path
	path_file = filedialog.askopenfilename(filetypes=[("log",".log")])

	# Get log number to create a folder with that name
	log_num = path_file.split('/')[-1].split('.')[0]
	data_log = LogFileData(path_file)
	window.withdraw()
	# data_log.plot_power_in_3d(log_num = log_num, folder_name = log_num)
	data_log.plot_waypoints(log_num = log_num, folder_name = log_num)
	# plot_pids_in_3d()
	# plot_3d_errors()
	# plot_errors()
	# plot_subfields()
	# data_log.process_gps_data()
	del data_log
	window.deiconify()



# Plot PID data
def plot_pids_in_3d():
	global data_log
	global log_num

	data_log.plot_error_in_3d(log_field = 'PIDR', folder_name = log_num)

	data_log.plot_error_in_3d(log_field = 'PIDP', folder_name = log_num)

	data_log.plot_error_in_3d(log_field = 'PIDY', folder_name = log_num)

	data_log.plot_error_in_3d(log_field = 'PIDS', folder_name = log_num)


# Plot errors in the 3D Trajectory
def plot_3d_errors():
	global data_log
	global log_num

	data_log.plot_error_in_3d(log_field = 'CTUN', var_calc = 'NavPitch',
		var_real = 'Pitch', label = 'Degrees (°)', folder_name = log_num)

	data_log.plot_error_in_3d(log_field = 'CTUN', var_calc = 'NavRoll', 
		var_real = 'Roll', label= 'Degrees (°)', folder_name = log_num)
	
	data_log.plot_error_in_3d(log_field = 'CTUN', var_calc = 'ThrDem', 
		var_real = 'ThrOut', label= 'Percentage (%)', folder_name = log_num)
	
	data_log.plot_error_in_3d(log_field = 'NTUN', var_calc = 'NavBrg', 
		var_real = 'TargBrg', label= 'Degrees (°)', folder_name = log_num)

# Plot errors from the defined subfileds
def plot_errors():
	global data_log
	global log_num

	data_log.plot_error(log_field = 'CTUN', var_calc = 'NavPitch', 
		var_real = 'Pitch', ylabel= 'Degrees (°)', folder_name = log_num)

	data_log.plot_error(log_field = 'CTUN', var_calc = 'NavRoll', 
		var_real = 'Roll', ylabel= 'Degrees (°)', folder_name = log_num)
	
	data_log.plot_error(log_field = 'CTUN', var_calc = 'ThrDem', 
		var_real = 'ThrOut', ylabel= 'Percentage (%)', folder_name = log_num)
	
	data_log.plot_error(log_field = 'NTUN', var_calc = 'NavBrg', 
		var_real = 'TargBrg', ylabel= 'Degrees (°)', folder_name = log_num)


# Plot subfields data vs time.
def plot_subfields(file_name = 'default'):
	global data_log
	global log_num

	data_log.plot_data(log_field = 'CTUN', sub_fields=['RdrOut'], 
						ylabel = 'Centi-degrees (°)', title = 'Rudder Out',
						folder_name = log_num)

	data_log.plot_data(log_field = 'NTUN', sub_fields = ['WpDist'], 
						ylabel = 'Distance (m)', title = 'Waypoint Distance',
						folder_name = log_num)

	data_log.plot_data(log_field = 'NTUN', sub_fields = ['AltErr'], 
						ylabel = 'Height (m)', title = 'Height Error',
						folder_name = log_num)

	data_log.plot_data(log_field = 'NTUN', sub_fields = ['XT'], 
						ylabel = 'Distance (m)', title = 'Distance from Travel Segment',
						folder_name = log_num)

	data_log.plot_data(log_field = 'NTUN', sub_fields = ['ArspdErr'], 
						ylabel = 'Speed (m/s)', title = 'Air Speed Error',
						folder_name = log_num)

def main():
	global window
	window = Tk()
	window.title('Select File')
	window.resizable(0, 0)
	# window.geometry('350x200')
	btn = Button(window, text = 'Read Log', width = 25, command = process_log)
	btn.grid(column = 0, row = 0, padx = 0, pady = 5)
	window.mainloop()

if __name__ == '__main__':
	main()