import time
import serial
from util import *
import math


class DataCollector():
    def __init__(self, port: str, collector_addr: str):
        self.ser = serial.Serial(port, 9600, timeout=5)  # 开启com3口，波特率，超时
        self.ser.flushInput()  # 清空输入缓存（向串口输入）

        self.port = port
        self.collector_addr = collector_addr

    def get_port(self):
        return self.port

    def close(self):
        self.ser.close()

    def query_data(self) -> dict:
        # 设备地址  功能码     寄存器起始地址     寄存器访问个数
        # 06        03        0001              0001
        all_data = ""

        n_machine = self.machine_num()

        query_times = math.ceil((n_machine * 4) / 32)
        last_query_num = n_machine % 32

        start_n = int()
        for i in range(query_times):
            if i == 0:
                start_n = 2
                number_hex = "{:#06X}".format(32)[2:]
            elif i == query_times - 1:
                start_n += 32
                number_hex = "{:#06X}".format(last_query_num)[2:]
            else:
                start_n += 32
                number_hex = "{:#06X}".format(32)[2:]

            start_addr = "{:#06X}".format(start_n)[2:]

            # 向控制器发送数据，允许有空格
            send_code = get_crc16(self.collector_addr + "03" + start_addr + number_hex)
            self.ser.write(bytes.fromhex(send_code))

            time.sleep(0.5)  # 如果太快读取数据可能还没全部发送过来
            num = self.ser.inWaiting()  # 返回接收缓存字节数
            if num:
                data = self.ser.read(num)
                print(data.hex()[6:-4])
                all_data += data.hex()[6:-4]

        return_data = {}
        for i in range(1, n_machine + 1):
            start = (i - 1) * 16

            machine_data = []
            machine_data.append(int(all_data[start:start + 4], 16))
            machine_data.append(int(all_data[start + 4:start + 8], 16))
            machine_data.append(int(all_data[start + 8:start + 12], 16))
            machine_data.append(int(all_data[start + 12:start + 16], 16))

            return_data[i] = machine_data

        return return_data

    def send_instruction(self):
        return

    def machine_num(self) -> int:
        """
        获取机器数量
        :return:机器数量
        """
        n_machine = -1

        self.ser.flushInput()  # 清空输入缓存（向串口发送）

        # 向控制器发送数据
        # 设备地址  功能码     寄存器起始地址     寄存器访问个数
        # 06        03        0000              0001
        self.ser.write(bytes.fromhex(get_crc16(self.collector_addr + " 03 0000 0001")))

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
        send_data = get_crc16(self.collector_addr + "03 0001 0001")
        self.ser.write(bytes.fromhex(send_data))

        time.sleep(0.1)  # 程序休眠 0.1 秒，等待控制器返回数据

        num = self.ser.inWaiting()  # 返回接收缓存字节数
        if num:
            data = self.ser.read(num)
            if is_crc16(data.hex()):
                wind_speed = int(data.hex()[6:10], 16)

        return wind_speed
