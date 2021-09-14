## Code in order to read waypoints from log

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
	path = path_file[0:path_file.find(log_num)] 
	data_log = LogFileData(path_file)
	window.withdraw()
	data_log.save_waypoints(fname = path + log_num)
	print("File saved")
	del data_log
	window.deiconify()


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