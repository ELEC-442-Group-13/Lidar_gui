import serial
import serial.tools.list_ports
import numpy as np
import threading
from collections import deque
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
from csv import writer
from datetime import datetime
import pytz

# Find available serial ports
ports = serial.tools.list_ports.comports(include_links=False)
baudrate = 115200  # Baudrate setting

ser_port = None
for port in ports:
    if port.vid == 1027:  # FTDI VID 1027
        ser_port = port.device
        print("Sensor found at:", ser_port)

if ser_port is None:
    raise Exception("No sensor found. Check connection!")

# Initialize serial connection
sensor = serial.Serial(ser_port, baudrate, timeout=1)

# Lock for thread synchronization
lock = threading.Lock()

# Buffer for storing received data
data_buffer = deque(maxlen=100)

# Create the figure for plotting
fig, ax = plt.subplots()

# Initialize the heatmap with zeros
cmap = 'Greens'  # Initial colormap
heatmap = ax.imshow(np.zeros((8, 8)), cmap=cmap, vmin=0, vmax=400)
plt.colorbar(heatmap)

# List to keep track of the text annotations
text_annotations = []


#time zone for logging
pacific_tz = pytz.timezone('America/Los_Angeles')

#ask for file name for data log file
file_name = input("file name for data logging: ")
header_list = ["time"]
for i in range(64):
    header_list.append('cell_{}'.format(i))

#create csv file
with open('{}.csv'.format(file_name), 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(header_list)

#log data variable
log_var = 0

def write_data(data):
    with open('{}.csv'.format(file_name), 'a', newline='') as csvfile:
        writer_obj = csv.writer(csvfile)
        writer_obj.writerow(data)

def start_log():
    global log_var
    log_var = 1

def end_log():
    global log_var
    log_var = 0

def read_serial():
    while True:
        raw_data = sensor.readline().decode().strip()
        data = raw_data.split(",")[:-1]
        try:
            arr_data = np.array(data, dtype=np.int32).reshape(8, 8)
            if(log_var == 1):
                curr_time = datetime.now(pacific_tz)
                np_mixed = np.array(data, dtype=object) 
                np_w_time = np.insert(np_mixed, 0, curr_time)
                write_data(np_w_time)
                
            with lock:
                data_buffer.append(arr_data)
        except ValueError:
            continue

def update(frame):
    with lock:
        if len(data_buffer) > 0:
            new_values = data_buffer[-1]  # Get latest sensor data
            heatmap.set_array(new_values)
        # Display values on each square of the heatmap
    for text in text_annotations:
        text.remove()
    
    # Create new text annotations for the updated data
    '''
    text_annotations.clear()
    for i in range(8):
        for j in range(8):
            text = ax.text(j, i, f'{new_values[i, j]}', ha='center', va='center', color='black', fontsize=8)
            text_annotations.append(text)
    '''
    return [heatmap]

# Function to change colormap
def change_cmap():
    global cmap, heatmap
    if cmap == 'Greens':
        cmap = 'hot'
    else:
        cmap = 'Greens'
    
    heatmap.set_cmap(cmap)
    fig.canvas.draw()

# Start serial reading thread
serial_thread = threading.Thread(target=read_serial, daemon=True)
serial_thread.start()

# Create the Tkinter root window
root = tk.Tk()
root.title("Sensor Heatmap Control")

# Create the Tkinter button to change colormap
button = tk.Button(root, text="Change Colormap", command=change_cmap)
button.pack()

#Add button to start datalog
button_log = tk.Button(root, text="startlog", command=start_log)
button_log.pack()

#Add button to end datalog
button_e = tk.Button(root, text="endlog", command=end_log)
button_e.pack()

# Embed the Matplotlib figure into Tkinter
canvas = FigureCanvasTkAgg(fig, master=root)  
canvas.get_tk_widget().pack()

# Create the animation
ani = animation.FuncAnimation(fig, update, interval=10, blit=False)

# Start Tkinter mainloop
root.mainloop()
