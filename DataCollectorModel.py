import threading
import time
import serial
from serial import SerialException

from util import *
import math


class DataCollectorModel():
    """
    MainWindow 数据模型
    """
    def __init__(self):
        self.ser = None
        self.port = None
        self.collector_addr = None
        self.baud_rate = None

    def get_member(self) -> int:
        """
        获取机器数量，必须在子线程中完成，因为有耗时操作
        :return:机器数量
        """
        n_machine = -1


        self.ser.flushInput()  # 清空输入缓存（向串口发送）
        # 向控制器发送数据
        # 设备地址  功能码     寄存器起始地址     寄存器访问个数
        # 06        03        0000              0001
        self.ser.write(bytes.fromhex(get_crc16(self.collector_addr + "03 0000 0001")))


        time.sleep(0.1)  # 程序休眠 0.1 秒，等待控制器返回数据

        num = self.ser.inWaiting()  # 返回接收缓存字节数
        if num:
            data = self.ser.read(num)
            if is_crc16(data.hex()):
                n_machine = int(data.hex()[6:10], 16)

        return n_machine

    def update_serial(self, port: str, baud_rate: str, collector_addr: str):
        """
        更新串口实例
        :param port:端口号
        :param collector_addr:数字采集器地址
        :return: 无
        """
        # 先关闭之前的
        if self.ser != None:
            self.ser.close()

        # 再新建
        try:
            self.ser = serial.Serial(port, int(baud_rate), timeout=5)  # 开启com3口，波特率，超时
            self.ser.flushInput()  # 清空输入缓存（向串口输入）

            self.port = port
            self.collector_addr = collector_addr
            self.baud_rate = baud_rate
        except SerialException:
            # 创建失败
            return False

        return self.test_ser()

    def test_ser(self):
        """
        测试串口是否正常
        :return:
        """
        # 查询机器数量
        self.ser.flushInput()  # 清空输入缓存（向串口发送）

        # 向控制器发送数据
        # 设备地址  功能码     寄存器起始地址     寄存器访问个数
        # 06        03        0000              0001
        self.ser.write(bytes.fromhex(get_crc16(self.collector_addr + "03 0000 0001")))

        time.sleep(0.1)  # 程序休眠 0.1 秒，等待控制器返回数据

        num = self.ser.inWaiting()  # 返回接收缓存字节数
        if num:
            return True
        return False



    def get_port(self):
        """
        返回当前串口号
        :return: 当前串口号
        """
        return self.port

    def get_collector_addr(self):
        """
        返回当前数采地址
        :return: 当前数采地址
        """
        return self.collector_addr

    def one_key(self, instruction: str) -> bool:
        """
        一键操作
        :param instruction:
        :return:
        """
        if self.ser == None:
            return False
        self.ser.flushInput()  # 清空输入缓存（向串口发送）
        self.ser.write(bytes.fromhex(get_crc16(self.collector_addr + "06 01FF" + instruction)))
        time.sleep(0.1)  # 程序休眠 0.1 秒，等待控制器返回数据
        num = self.ser.inWaiting()  # 返回接收缓存字节数
        if num:
            data = self.ser.read(num)
            if is_crc16(data.hex()):
                return True

        return False

    def send_control_code(self, machine_number: int, code: str):
        """
        给控制器发送控制代码
        :param machine_number:机器编号，10 进制
        :param code:控制代码，16 进制
        :return:无
        """
        self.ser.flushInput()  # 清空输入缓存（向串口发送）

        # 向控制器发送数据
        # 设备地址  功能码     寄存器起始地址     寄存器访问个数
        # 06        03        0000              0001

        machine_number += 1
        machine_number = "{:#06X}".format(machine_number)[2:]

        # 默认输入是 16 进制
        code = "{:#06X}".format(int(code, 16))[2:]

        instruction_code = bytes.fromhex(get_crc16(self.collector_addr + "06" +
                                                   machine_number + code))
        self.ser.write(instruction_code)

        time.sleep(0.3)  # 如果太快读取数据可能还没全部发送过来
        num = self.ser.inWaiting()  # 返回接收缓存字节数
        if num:
            data = self.ser.read(num)
            print(data.hex().upper())

    def get_table_data(self) -> dict:
        """
        获取表格数据，必须在子线程中完成，因为有耗时操作
        :return:无
        """
        # 设备地址  功能码     寄存器起始地址     寄存器访问个数
        # 06        03        0001              0001
        all_data = ""

        n_machine = self.machine_num()  # 先查询机器数量

        query_times = math.ceil(n_machine / 8)  # 一次最多查 8 台
        last_query_num = n_machine - (query_times - 1) * 8  # 最后一次查询机器数量

        start_n = 2  # 开始字节位置
        for i in range(1, query_times + 1):
            # print(i)
            if i == query_times:
                # 最后一次
                start_n += 32
                # 寄存器数量
                number_hex = "{:#06X}".format(last_query_num * 4)[2:]

            else:
                # 不是最后一次查询
                if start_n == 2:
                    # 第一次查询
                    start_n = 2
                else:
                    start_n += 32

                # 32 个寄存器
                number_hex = "{:#06X}".format(32)[2:]

            # 查询起始地址
            start_addr = "{:#06X}".format(start_n)[2:]

            # 向控制器发送数据，允许有空格
            send_code = get_crc16(self.collector_addr + "03" + start_addr + number_hex)
            self.ser.write(bytes.fromhex(send_code))

            time.sleep(0.2)  # 如果太快读取数据可能还没全部发送过来
            num = self.ser.inWaiting()  # 返回接收缓存字节数
            if num:
                data = self.ser.read(num)
                if is_crc16(data.hex()):
                    print(data.hex()[6:-4])
                    all_data += data.hex()[6:-4]
                else:
                    return {}

        return_data = {}
        for i in range(1, n_machine + 1):
            start = (i - 1) * 16

            machine_data = []
            # print(i, all_data[start:])
            # print(i, all_data[start:start + 4])
            machine_data.append(int(all_data[start:start + 4], 16))
            machine_data.append(int(all_data[start + 4:start + 8], 16))
            machine_data.append(int(all_data[start + 8:start + 12], 16))
            machine_data.append(int(all_data[start + 12:start + 16], 16))

            return_data[i] = machine_data

        return return_data

    def machine_num(self) -> int:
        """
        获取机器数量，必须在子线程中完成，因为有耗时操作
        :return:机器数量
        """
        n_machine = -1

        self.ser.flushInput()  # 清空输入缓存（向串口发送）

        # 向控制器发送数据
        # 设备地址  功能码     寄存器起始地址     寄存器访问个数
        # 06        03        0000              0001
        self.ser.write(bytes.fromhex(get_crc16(self.collector_addr + "03 0000 0001")))

        time.sleep(0.1)  # 程序休眠 0.1 秒，等待控制器返回数据

        num = self.ser.inWaiting()  # 返回接收缓存字节数
        if num:
            data = self.ser.read(num)
            if is_crc16(data.hex()):
                n_machine = int(data.hex()[6:10], 16)

        return n_machine

    def wind_speed(self) -> float:
        """
        必须在子线程中完成，因为有耗时操作
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
                wind_speed = int(data.hex()[6:10], 16) / 100

        return wind_speed
