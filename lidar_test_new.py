"""
Object for getting samples from our lidar module. Samples are read from the module using an STM32, which in turn communicates
with this script to get data.
"""

import serial
import time


LIDAR_PORT = "/dev/ttyUSB1"
BAUD_RATE = 115200


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