# Functions creted to handle logs data.
import numpy as np
import datetime
import sys, os
import matplotlib.pyplot as plt
import matplotlib.dates as md
from mpl_toolkits import mplot3d


def convert_deg(lng = 0):
	d = int(lng)
	m = int(60 * abs(lng - d))
	s = 3600 * abs(lng - d) - 60 *m
	return d,m,s

def convert_type(var, frmt):
	if frmt in 'abBhHiIqQ':
		var = int(var)
	elif frmt in 'fdLcCeE':
		var = float(var)
	return var

def save_fig(folder_name, file_name, fig):
	if not os.path.exists(folder_name): os.makedirs(folder_name)
	f_path = os.path.dirname(__file__)
	f_path = os.path.join(f_path, folder_name)
	fig.savefig(os.path.join(f_path, file_name), dpi=300)	


def plot_3d_points(variables, description, names):

	gps, var = variables
	lat, lng, alt = gps
	title, label =  description
	folder_name, file_name = names

	# Create figure to plot data
	fig = plt.figure()
	ax = plt.axes(projection='3d')
	ax.xaxis.pane.fill = False
	ax.xaxis.pane.set_edgecolor('white')
	ax.yaxis.pane.fill = False
	ax.yaxis.pane.set_edgecolor('white')
	ax.zaxis.pane.fill = False
	ax.zaxis.pane.set_edgecolor('white')
	ax.grid(False)

	# Plot GPS points and assign a color depending 
	# on the value of the error
	cs = ax.scatter(lat, lng, alt , s = 10, c = var, cmap = 'jet')
	cbar = plt.colorbar(cs)
	fig.suptitle(title, fontsize = 28)
	if label: cbar.ax.set_title(label, fontsize = 18)

	plt.get_current_fig_manager().window.showMaximized()
	fig.subplots_adjust(top=0.925, bottom=0.140, left=0.085, right=0.98,)
	plt.get_current_fig_manager().window.showMaximized()
	plt.show()

	# Save image if sub field and folder name were defined
	if folder_name :
		save_fig(folder_name, file_name, fig)



class LogFileData:

	def __init__(self, fname):
		self.data = self.open_log(fname)
	
	# Read al the data from a log and store it in a dictionary
	def open_log(self, file_name):
		params = dict()
		try:
			fh = open(file_name, 'r')
		except:
			print("Error while opening file")
			quit()

		# Create dictionary structure
		for line in fh:
			if not line.startswith('FMT,'): continue
			fmt = line.strip().replace(' ','').split(',')
			if fmt[3] in params: continue
			params[fmt[3]] = {sub:[] for sub in fmt[4:]}
		fh.seek(0)
		for line in fh:
			if line.startswith('FMT') or line.startswith('PARM') : continue
			pkg = line.strip().replace(" ","").split(',')
			if pkg[0] in params.keys():
				header = list(params[pkg[0]].keys())
				type_val = header[0]
				for i in range(1, len(header)):
					params[pkg[0]][header[i]].append(convert_type(pkg[i], type_val[i-1]))
		fh.close()
		return params

	# Select time rage only in the AUTOMODE profile
	def select_auto_data(self, t_data):
		# In case empty data is passed
		if len(t_data) == 0:
			print('No time data available')
			quit()

		# Get data and modes from log
		time = self.data['MODE']['TimeUS']
		modes = self.data['MODE']['ModeNum']

		# Get the largest range of data in Automode
		max_time = 0
		ti = None
		tf = None
		for i in range(len(modes)):
			if modes[i] == 10:
				if (i+1)<len(modes):
					dt = time[i+1] - time[i]
					if dt > max_time:
						max_time = dt
						ti, tf = time[i], time[i+1]
				else:
					ti, tf = time[i], None
		if ti == None and tf == None:
			print('No Auto Mode available')
			quit()

		# Calculate de indexes of the interval
		idxs =[0,0]
		for i in range(len(t_data)):	
			if t_data[i] > ti:
				idxs[0] = i
				break
		if tf == None: idxs[1] = len(t_data)
		else:
			for i in reversed(range(len(t_data))):
				if t_data[i] < tf:
					idxs[1] = i
					break

		return idxs[0], idxs[1]

	# Plot any variable in the log vs time
	def plot_data(self, log_field, sub_fields=[], ylabel='', title='', folder_name=''):
		# If there's no sub field it returns None value and does
		# not execute the remaining lines.
		if sub_fields == []: return

		# Determine range on time within the UAV executes 
		# auto mode
		t = np.array(self.data[log_field]['TimeUS'])
		idx_i, idx_f = self.select_auto_data(t)

		# Select data in the range that auto-mode was run
		# t = (t-t[0])[idx_i:idx_f]
		t = t[idx_i:idx_f]
		t = (t-t[0])

		# Convert time array to datetime format in order to
		# plot the values in the x axis.
		# In case hour and minutes will be required use the next line:
		# dt = [time_on + datetime.timedelta(microseconds=int(i)) for i in t]
		dt = [datetime.datetime(2000,1,1) + datetime.timedelta(microseconds=int(i)) for i in t]
		fig = plt.figure()
		ax = plt.axes()
		for var in sub_fields:
			y = np.array(self.data[log_field][var])[idx_i:idx_f]
			ax.plot(dt,y, label=var, linewidth=0.8)
		ax.set_xlabel('Time (h:m:s)', fontsize=26)
		if ylabel: ax.set_ylabel(ylabel, fontsize=26)
		if title: ax.set_title(title, fontsize=34)
		plt.xticks(fontsize=20)
		plt.yticks(fontsize=20)

		# Set X axis to time format
		plt.gcf().autofmt_xdate()
		xfmt = md.DateFormatter('%H:%M:%S')
		plt.gca().xaxis.set_major_formatter(xfmt)
		plt.legend(fontsize=18)
		plt.grid()
		plt.get_current_fig_manager().window.showMaximized()
		fig.subplots_adjust(top=0.925, bottom=0.150, left=0.085, right=0.98,)
		plt.show()	

		# Save image if sub field and folder name were defined
		if folder_name :
			file_name = log_field + str([key for key in sub_fields]) + '.png'
			save_fig(folder_name, file_name, fig)


	# Show two subplots, the first one plots the calculated and real variables
	# the second one plots the error between the variables.
	def plot_error(self, log_field = '', var_calc = '', var_real = '',
			ylabel='', folder_name=''):
		# If there's no sub field it returns None value and does
		# not execute the remaining lines.
		if not (log_field and var_calc and var_real): return

		# Determine range on time within the UAV executes 
		# auto mode
		t = np.array(self.data[log_field]['TimeUS'])
		idx_i, idx_f = self.select_auto_data(t)

		# Select data in the range that auto-mode was run
		# t = (t-t[0])[idx_i:idx_f]
		t = t[idx_i:idx_f]
		t = (t-t[0])

		# Convert time array to datetime format in order to
		# plot the values in the x axis.
		# In case hour and minutes will be required use the next line:
		# dt = [time_on + datetime.timedelta(microseconds=int(i)) for i in t]
		dt = [datetime.datetime(2000,1,1) + datetime.timedelta(microseconds=int(i)) for i in t]

		#Create a figure object
		fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
		# fig = plt.figure()
		# ax = plt.axes()

		# Get variables data and calculate the error variables
		# to be shown.
		y1 = np.array(self.data[log_field][var_calc])[idx_i:idx_f]
		y2 = np.array(self.data[log_field][var_real])[idx_i:idx_f]
		error = y1 - y2

		# Plot variables
		ax1.plot(dt, y1, label = var_calc, linewidth = 0.8 )
		ax1.plot(dt, y2, label = var_real, linewidth = 0.8 )
		if ylabel: ax1.set_ylabel(ylabel, fontsize=24)
		ax1.set_title(var_calc + ' & ' + var_real, fontsize=28)
		ax1.legend(fontsize=18)
		ax1.tick_params(labelsize = 20)
		ax1.grid()

		# Plot error
		ax2.plot(dt, error, label = 'Error', linewidth = 0.8 )
		if ylabel: ax2.set_ylabel(ylabel, fontsize=24)
		ax2.set_title('Error', fontsize=24)
		ax2.set_xlabel('Time (m:s)', fontsize=26)
		ax2.legend(fontsize=18)
		ax2.tick_params(labelsize = 20)
		ax2.tick_params(axis="x", labelsize = 22)
		ax2.grid()


		# Set X axis to time format
		fig.autofmt_xdate()
		xfmt = md.DateFormatter('%M:%S')
		# plt.gca().xaxis.set_major_formatter(xfmt)
		ax2.xaxis.set_major_formatter(xfmt)
		plt.get_current_fig_manager().window.showMaximized()
		fig.subplots_adjust(top=0.925, bottom=0.140, left=0.085, right=0.98,)
		# if title: plt.suptitle(title, fontsize=26)
		plt.show()	

		# Save image if sub field and folder name were defined
		if folder_name :
			file_name = log_field + '[\''+ var_calc +'\',\'' + var_real + '\']_error.png'
			save_fig(folder_name, file_name, fig)


	# Get data from GPS to calculate the date & time
	def date_calc(self, gps_weeks = 0, gps_ms = 0, gps_lng = 0):
		gps_week = self.data['GPS']['GWk'][0]
		gps_ms = self.data['GPS']['GMS'][0]
		gps_lng = self.data['GPS']['Lng'][0]
		i = datetime.datetime(1980,1,6)
		w = datetime.timedelta(weeks=gps_weeks)
		d, m, s = convert_deg(gps_lng)
		h = datetime.timedelta(hours=d/15)
		m = datetime.timedelta(minutes=m)
		s = datetime.timedelta(seconds=s)
		ms = datetime.timedelta(milliseconds = gps_ms)
		time_on = i+w+h+m+s+ms
		return time_on

	# Get waypoints from the log and save the data in 
	# a mission file.
	def save_waypoints(self, fname = ''):
		if not fname :
			print('No file name specified')
			return
			
		fname = fname +'_wp.txt'
		header = 'QGC WPL 110\n'
		ctot = self.data['CMD']['CTot'][0]
		cnum = self.data['CMD']['CNum']
		cid = self.data['CMD']['CId']
		prm1 = self.data['CMD']['Prm1']
		prm2 = self.data['CMD']['Prm2']
		prm3 = self.data['CMD']['Prm3']
		prm4 = self.data['CMD']['Prm4']
		lat = self.data['CMD']['Lat']
		lng = self.data['CMD']['Lng']
		alt = self.data['CMD']['Alt']
		fh = open(fname, 'w')
		fh.write(header)
		for i in range(ctot):
			fh.write(str(cnum[i])+'\t0\t3\t'+str(cid[i])+'\t'+
					str(int(prm1[i]))+'\t'+str(int(prm2[i]))+'\t'+
					str(int(prm3[i]))+'\t'+str(int(prm4[i]))+'\t'+
					str(lat[i])+'\t'+str(lng[i])+'\t'+
					str(int(alt[i]))+'\t1\n')
		fh.close()

	# Return GPS data
	def get_gps_data(self):
		t = np.array(self.data['GPS']['TimeUS'])
		idx_i, idx_f = self.select_auto_data(t)
		lat = self.data['GPS']['Lat'][idx_i:idx_f]
		lng = self.data['GPS']['Lng'][idx_i:idx_f]
		alt = self.data['GPS']['Alt'][idx_i:idx_f]
		gps = (lat, lng, alt)
		return gps

	# Plot gps data from AutoMode
	def process_gps_data(self):
		# Get gps data from function
		lat, lng, alt = self.get_gps_data()

		# Plot the trajectory
		fig = plt.figure()
		ax = plt.axes(projection='3d')
		ax.xaxis.pane.fill = False
		ax.xaxis.pane.set_edgecolor('white')
		ax.yaxis.pane.fill = False
		ax.yaxis.pane.set_edgecolor('white')
		ax.zaxis.pane.fill = False
		ax.zaxis.pane.set_edgecolor('white')
		ax.grid(False)
		ax.plot(lat, lng, alt, marker='>', markevery=30)
		plt.get_current_fig_manager().window.showMaximized()
		plt.show()


	# Plot the magnitude of an error in the 3D graph
	def plot_error_in_3d(self, log_field = '', var_calc = '', var_real = '', 
						label = '', folder_name = ''):

		# If there's no sub field it returns None value and does
		# not execute the remaining lines.
		if not log_field: return

		# Get gps data from function
		gps = self.get_gps_data()
		# Determine range on time within the UAV executes 
		# auto mode
		t = np.array(self.data[log_field]['TimeUS'])
		idx_i, idx_f = self.select_auto_data(t)

		if (var_calc and var_real):
			# Get variables data and calculate the error variables
			# to be shown.
			y1 = np.array(self.data[log_field][var_calc])[idx_i:idx_f]
			y2 = np.array(self.data[log_field][var_real])[idx_i:idx_f]
			error = y1 - y2
			# Assign error to var variable in order to send it to plot function
			var = error

			# Generate title and file name
			title = var_calc + ' & '+ var_real + ' Error'
			file_name = log_field + '[\''+ var_calc +'\',\'' + var_real + '\']_error_in_map.png'

		elif log_field in ['PIDA', 'PIDP', 'PIDR', 'PIDS', 'PIDY']:
			# Get pid variables
			p = np.array(self.data[log_field]['P'][idx_i:idx_f])
			i = np.array(self.data[log_field]['I'][idx_i:idx_f])
			d = np.array(self.data[log_field]['D'][idx_i:idx_f])

			# Calculate resulting PID
			pid = p + i + d
			# Assign pid to var variable in order to send it to plot function
			var = pid

			# Generate title, label and file name
			title = log_field + ' Effort'
			label = log_field
			file_name = log_field + '_effort_.png'

		# Return None in case there's no field available
		else:
			return

		# Resize error to match the length of the GPS position data
		length = len(gps[0])
		resized_var = np.resize(var, (length, round(var.shape[0]/length)))
		resized_var = np.mean(resized_var, axis=1)
		resized_var = np.abs(resized_var)

		# Pack all variables to call plot_3d_points fuction in order to 
		# plot with this data
		variables = (gps, resized_var)
		description = (title, label)
		names = (folder_name, file_name)
		plot_3d_points(variables, description, names)


	def plot_waypoints(self, log_num = '', lines = False, folder_name = '', 
						real_gps = False):

		# If log_num emty, fuction return a None value
		if not log_num: return

		# Read Waypoints of interest
		ctot = self.data['CMD']['CTot'][0]
		cid = np.array(self.data['CMD']['CId'])[0:ctot]
		idx = np.where((cid == 16) | (cid == 21) | (cid == 31) )
		alt_h = self.data['CMD']['Alt'][0]

		# Ignore starting point
		lat = np.array(self.data['CMD']['Lat'])[idx][1:]
		lng = np.array(self.data['CMD']['Lng'])[idx][1:]
		alt = np.array(self.data['CMD']['Alt'])[idx][1:] + alt_h

		# Create figure to plot data
		fig = plt.figure()
		ax = plt.axes(projection='3d')
		ax.xaxis.pane.fill = False
		ax.xaxis.pane.set_edgecolor('white')
		ax.yaxis.pane.fill = False
		ax.yaxis.pane.set_edgecolor('white')
		ax.zaxis.pane.fill = False
		ax.zaxis.pane.set_edgecolor('white')
		ax.grid(False)

		cs = ax.scatter(lat, lng, alt, s = 30, c = 'red',
						edgecolor = 'k')
		ax.plot(lat, lng, alt, linewidth = 0.75)

		# Get gps data and plot if real_gps = True
		if real_gps:
			lat, lng, alt = self.get_gps_data()
			ax.plot(lat, lng, alt, marker='>', markevery=30)

		ax.view_init(24, 15)
		fig.suptitle('Waypoints: ' + log_num + '.log' , fontsize = 28)
		file_name = 'waypoints_'+ log_num + '.png'
		plt.get_current_fig_manager().window.showMaximized()
		fig.subplots_adjust(top=0.925, bottom=0.140, left=0.085, right=0.98,)
		plt.get_current_fig_manager().window.showMaximized()
		plt.show()

		# Save image if sub field and folder name were defined
		if folder_name :
			save_fig(folder_name, file_name, fig)



def main():
	pass

if __name__ == '__main__':
	main()