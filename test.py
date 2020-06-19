import time
from util import *
import serial
from DataCollector import *




if __name__ == '__main__':
    data_collector = DataCollector()
    print("风速：", data_collector.wind_speed())







