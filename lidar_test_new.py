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
import time


LIDAR_PORT = "/dev/ttyUSB1"
BAUD_RATE = 115200


# LidarSensor class definition
class LidarSensor:

    def __init__(self):
        self.ser = None
        self.port = LIDAR_PORT
        self.baudrate = BAUD_RATE
        
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"Connected to Lidar sensor on {self.port}")
        except:
            print("Lidar sensor not found, exiting...")
            exit()
        
    def get_reading(self):

        self.ser.reset_input_buffer() # flush the input buffer

        # make sure we get a full sample off of the serial port (EXTREMELY SKETCH)
        data = []
        while not len(data) == 64:
            raw_data = self.ser.readline().decode().strip()
            data = raw_data.split(",")[:-1]

        return data


if __name__ == "__main__":

    lidar = LidarSensor()
    
    while (1):
        data = lidar.get_reading()
        print(data)
        time.sleep(0.5)