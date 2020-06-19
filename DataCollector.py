import time
import serial
from util import *


class DataCollector():
    def __init__(self):
        n = 0
        self.ser = serial.Serial("COM4", 9600, timeout=5)  # 开启com3口，波特率，超时
        self.ser.flushInput()  # 清空输入缓存（向串口输入）

    def query_data(self) -> dict:
        # 向控制器发送数据
        self.ser.write(bytes.fromhex("010300000001840A"))

        time.sleep(1)  # 程序休眠 1 秒，等待控制器返回数据
        num = self.ser.inWaiting()  # 返回接收缓存字节数
        if num:
            data = self.ser.read(num)
            print(data.hex())

        return {}

    def send_instruction(self):
        return

    def machine_num(self) -> int:
        """
        获取机器数量
        :return:机器数量
        """
        n_machine = 0

        self.ser.flushInput()  # 清空输入缓存（向串口发送）

        # 向控制器发送数据
        send_data = get_crc16("0603 0001 0001")
        self.ser.write(bytes.fromhex(send_data))

        time.sleep(0.1)  # 程序休眠 0.1 秒，等待控制器返回数据

        num = self.ser.inWaiting()  # 返回接收缓存字节数
        if num:
            data = self.ser.read(num)
            if is_crc16(data.hex()):
                n_machine = int(data.hex()[6:10], 16)



        return n_machine

    def wind_speed(self) -> int:
        """
        获取风速
        :return: 风速
        """
        wind_speed = -1
        self.ser.flushInput()  # 清空输入缓存（向串口发送）

        # 向控制器发送数据
        send_data = get_crc16("0603 0001 0001")
        self.ser.write(bytes.fromhex(send_data))

        time.sleep(0.1)  # 程序休眠 0.1 秒，等待控制器返回数据

        num = self.ser.inWaiting()  # 返回接收缓存字节数
        if num:
            data = self.ser.read(num)
            if is_crc16(data.hex()):

                wind_speed = int(data.hex()[6:10], 16)

        return wind_speed




