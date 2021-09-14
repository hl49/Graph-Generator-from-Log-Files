# Compare data REAL vs SIM

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as md
import datetime
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
from tools import LogFileData

rl_file_path = ''
sl_file_path = ''

def write_txt(txt, path):
	txt.configure(state = 'normal')
	txt.delete(0.0)
	txt.insert(0.0, path)
	txt.configure(state = 'disabled')


def get_rl_path(txt_real):
	global rl_file_path
	rl_file_path = tk.filedialog.askopenfilename(filetypes = [("log", ".log")])
	write_txt(txt_real, rl_file_path)

def get_sl_path(txt_sim):
	global sl_file_path
	sl_file_path = tk.filedialog.askopenfilename(filetypes = [("txt", ".txt")])
	write_txt(txt_sim, sl_file_path)


def compare_logs(window):
	global rl_file_path
	global sl_file_path
	rl_file_path = 'D:/EPN/PIGR-1901/Logs 2020/V16_11DIC2020/00000179.log'
	sl_file_path = 'D:/EPN/PIGR-1901/uas/Xplane/validacion/comparison/sim_logs/179/Data_00000147.txt'

	try :
		fh = open(sl_file_path, 'r')
	except:
		tk.messagebox.showerror("ERROR","Error while opening sim data")
		return

	try :
		real_data = LogFileData(rl_file_path)
	except:
		tk.messagebox.showerror("ERROR","Error while opening real data")
		return

	# Hide window
	window.withdraw()

	########################### Process Real Data

	# Select data
	t = np.array(real_data.data['BAT']['TimeUS'])
	idx_i, idx_f = real_data.select_auto_data(t)

	# Calculate values in time
	t = t[idx_i:idx_f]
	t = (t-t[0])
	dt_real = [datetime.datetime(2000,1,1) + 
		datetime.timedelta(microseconds=int(i)) for i in t]

	# Get voltage and current, then calculate power
	volt_real = np.array(real_data.data['BAT']['Volt'][idx_i:idx_f])
	curr_real = np.array(real_data.data['BAT']['Curr'][idx_i:idx_f])
	power_real = volt_real * curr_real


	########################### Process Sim Data

	# Denife label what contain data of interest
	data_label = {'lat,deg':0,'lon,deg':0,'alt,ftmsl':0,
		'power,1,hp':0, 'batt1,volt':0}

	# Dictionary used to store the whole info
	sim_data = {key:[] for key in data_label}

	# Read header file and find position of the values
	line = fh.readline().strip().replace(' ','').replace('_','')[:-1].split('|')
	n_col = 0	# Variable to store number of columns in file
	for param in line:
		if param in data_label: data_label[param] = n_col
		n_col += 1


	# Read data and store in dictionary
	for line in fh:
		if not line: continue
		line = line.strip().replace(' ','')[:-1].split('|')
		if len(line) == n_col:
			for key in sim_data:
				sim_data[key].append(float(line[data_label[key]]))

	volt_sim = np.array(sim_data['batt1,volt'])
	power_sim = np.array(sim_data['power,1,hp']) * 745.7


	######### Scale values
	len_real = len(volt_real)
	len_sim = len(volt_sim)

	volt_sim_sample = np.resize(volt_sim, (len_real, round(volt_sim.shape[0]/len_real)))
	volt_sim_sample = np.mean(volt_sim_sample, axis=1)
	volt_sim_sample = np.abs(volt_sim_sample)

	power_sim_sample = np.resize(power_sim, (len_real, round(power_sim.shape[0]/len_real)))
	power_sim_sample = np.mean(power_sim_sample, axis=1)
	power_sim_sample = np.abs(power_sim_sample)
	
	current_sim = power_sim_sample/volt_sim_sample
	print(volt_real.shape)
	print(volt_sim_sample.shape)

	print(len_real)
	print(len_sim)


	########################### Plot values
	fig, ax= plt.subplots(3, 1, sharex = True)
	ax[0].plot(dt_real, volt_real, label = 'real', linewidth = 0.8, color = 'C0')
	ax[1].plot(dt_real, curr_real, label = 'real', linewidth = 0.8, color = 'C1')
	ax[2].plot(dt_real, power_real, label = 'real', linewidth = 0.8, color = 'C2')
	ax[0].plot(dt_real, volt_sim_sample, label = 'sim', linewidth = 0.8, color = 'C3')
	ax[1].plot(dt_real, current_sim, label = 'sim', linewidth = 0.8, color = 'C3')
	ax[2].plot(dt_real, power_sim_sample, label = 'sim', linewidth = 0.8, color = 'C3')
	[[ax[i].grid(), ax[i].legend(fontsize = 16)]  for i in range(3)]

	# Configure labels
	ylabels = ['Voltage (V)', 'Current (A)', 'Power (W)']
	[ax[i].set_ylabel(ylabels[i], fontsize = 16) for i in range(3)]
	fig.suptitle('REAL VS SIM', fontsize = 24)

	# Set X axis to time format
	plt.gcf().autofmt_xdate()
	xfmt = md.DateFormatter('%H:%M:%S')
	plt.gca().xaxis.set_major_formatter(xfmt)
	plt.get_current_fig_manager().window.showMaximized()
	fig.subplots_adjust(top=0.925, bottom=0.140, left=0.085, right=0.98,)
	# if title: plt.suptitle(title, fontsize=26)
	plt.show()

	window.deiconify()

def main ():
	# Create window
	window = tk.Tk()
	window.title("REAL VS SIM DATA")
	window.geometry("400x130")
	window.resizable(0, 0)
	frame_1 = tk.Frame(master = window, borderwidth = 1)
	frame_1.pack()
	frame_2 = tk.Frame(master = window, borderwidth = 1)
	frame_2.pack()
	frame_3 = tk.Frame(master = window, borderwidth = 1)
	frame_3.pack()

	# Button to read logs from real data
	btn_real = tk.Button(master = frame_1, text = 'Real Log', width = 10, 
		command = lambda: get_rl_path(txt_real))
	btn_real.grid(row = 0, column = 0)

	txt_real = tk.Text(master = frame_1, height = 1, 
		width = 36,	state = 'disabled')
	txt_real.grid(row = 0, column = 1, padx = 8, pady = 12)

	# Button to read logs from real data
	btn_sim = tk.Button(master = frame_2, text = 'Sim Log', width = 10, 
		command = lambda: get_sl_path(txt_sim))
	btn_sim.grid(row = 0, column = 0)

	txt_sim = tk.Text(master = frame_2, height = 1, 
		width = 36, state = 'disabled')
	txt_sim.grid(row = 0, column = 1, padx = 8, pady = 12)

	# Button to proceed in the comparison
	btn_compare = tk.Button(master = frame_3, text = 'COMPARE', width = 10,
		command = lambda:compare_logs(window))
	btn_compare.grid(row = 0, column = 0)

	window.mainloop()



if __name__ == '__main__':
	main()