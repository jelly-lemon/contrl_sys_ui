import threading
import time
import serial
from serial import SerialException

from util import *
import math


class Model():
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
        n_machine = 0
        data = self.write("03 0000 0001", 0.1)
        if data != "":
            n_machine = int(data[6:10], 16)

        return n_machine

    def update_serial(self, port: str, baud_rate: str, collector_addr: str):
        """
        更新串口实例
        :param port:端口号
        :param collector_addr:数字采集器地址
        :return: 无
        """
        #
        # 先关闭之前的
        #
        if self.ser != None:
            self.ser.close()

        #
        # 再新建
        #
        try:
            self.ser = serial.Serial(port, int(baud_rate), timeout=5)  # 开启com3口，波特率，超时
            time.sleep(0.1)
            #
            # 保存串口信息到成员变量
            #
            self.port = port
            self.collector_addr = collector_addr
            self.baud_rate = baud_rate
        except SerialException:
            return False  # 创建失败

        return self.test_ser()  # 测试一下能否接收数据

    def test_ser(self):
        """
        测试串口是否正常
        :return:
        """
        data = self.write("03 0000 0001", 0.1)
        if data != "":
            return True

        return False

    def one_key(self, instruction: str) -> bool:
        """
        一键操作
        :param instruction:命令
        :return:
        """
        if self.ser is None:
            return False
        data = self.write("06 01FF" + instruction, 0.1)
        if data != "":
            return True

        return False

    def send_control_code(self, machine_number: int, code: str) -> bool:
        """
        给控制器发送控制代码
        :param machine_number:机器编号，10 进制
        :param code:控制代码，16 进制
        :return:无
        """
        machine_number = "{:04X}".format((machine_number-1)*4 + 3)
        code = "{:04X}".format(int(code, 16))  # 默认输入是 16 进制
        data = self.write("06" + machine_number + code, 0.1)
        if data != "":
            return True

        return False

    def get_table_data(self) -> dict:
        """
        获取表格数据
        :return:表格数据
        """
        all_data = ""
        n_machine = self.machine_num()  # 先查询机器数量
        query_times = math.ceil(n_machine / 8)  # 一次最多查 8 台
        start_n = 2  # 开始字节位置
        rest_machine = n_machine
        for i in range(query_times):
            if n_machine - 8 > 0:
                #
                # 说明后面还需要查询
                #
                rest_machine -= 8
                number_hex = "{:#06X}".format(32)[2:]  # 32 个寄存器

            else:
                #
                # 这是最后一次查询了
                #
                number_hex = "{:#06X}".format(rest_machine * 4)[2:]

            #
            # 向控制器发送数据，允许有空格
            #
            start_addr = "{:#06X}".format(start_n)[2:]  # 查询起始地址
            start_n += 8
            data = self.write("03" + start_addr + number_hex, 0.2)
            if data != "":
                #
                # 不要前 6 位和后 4 位
                # 前 6 位（060340，表示寄存器地址06 + 功能码03 + 有效字节数40）
                # 后 4 位（CRC）
                #
                data = data[6:-4]
                all_data += data
            else:
                return {}

        # last_query_num = n_machine - (query_times - 1) * 8  # 最后一次查询机器数量
        # for i in range(1, query_times + 1):
        #     if i == query_times:
        #
        #         #
        #         # 最后一次查询
        #         #
        #         start_n += 32
        #         number_hex = "{:#06X}".format(last_query_num * 4)[2:]  # 寄存器数量
        #     else:
        #
        #         #
        #         # 不是最后一次查询
        #         #
        #         if start_n == 2:
        #             # 第一次查询
        #             start_n = 2
        #         else:
        #             start_n += 32
        #         number_hex = "{:#06X}".format(32)[2:]  # 32 个寄存器


        return self.convert2dec(n_machine, all_data)

    def convert2dec(self, n_machine, data) -> dict:
        """
        将原始十六进制字符串转成十进制整数，同时变成字典数据
        :param n_machine:
        :param data:
        :return:
        """
        new_data = {}
        for i in range(1, n_machine + 1):
            start = (i - 1) * 16
            machine_data = []
            machine_data.append(int(data[start:start + 4], 16))
            machine_data.append(int(data[start + 4:start + 8], 16))
            machine_data.append(int(data[start + 8:start + 12], 16))
            machine_data.append(int(data[start + 12:start + 16], 16))
            new_data[i] = machine_data

        return new_data

    def machine_num(self) -> int:
        """
        获取机器数量
        :return:机器数量
        """
        n_machine = -1
        data = self.write("03 0000 0001", 0.1)
        if data != "":
            n_machine = int(data[6:10], 16)

        return n_machine

    def wind_speed(self) -> float:
        """
        获取风速
        :return: 风速
        """
        wind_speed = -1
        data = self.write("03 0001 0001", 0.1)
        if data != "":
            wind_speed = int(data[6:10], 16) / 100

        return wind_speed

    def write(self, content: str, sleep: float) -> str:
        """
        #
        # 向控制器发送数据
        # 设备地址  功能码     寄存器起始地址     寄存器访问个数
        # 06        03        0000              0001
        :param content:指令内容
        :param sleep:等待时间
        :return:
        """
        self.ser.flushInput()  # 清空输入缓存（向串口发送）

        #
        # 向控制器发送数据
        #
        send_data = get_crc16(self.collector_addr + content)
        self.ser.write(bytes.fromhex(send_data))
        time.sleep(sleep)  # 程序休眠 x 秒，等待控制器返回数据

        #
        # 返回接收缓存字节数
        #
        num = self.ser.inWaiting()
        if num:
            data = self.ser.read(num)
            if is_crc16(data.hex()):
                return data.hex().upper()

        return ""

