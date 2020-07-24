import threading
import time
import serial
from serial import SerialException

import util
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

    def close_ser(self):
        """
        关闭串口
        :return:
        """
        if self.ser != None and self.ser.isOpen():
            self.ser.close()

    def get_member(self) -> int:
        """
        获取机器数量，必须在子线程中完成，因为有耗时操作
        :return:机器数量
        """
        n_machine = -1
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
        self.close_ser()

        #
        # 再新建
        #
        for i in range(3):
            try:
                self.ser = serial.Serial(port, int(baud_rate), timeout=5)  # 开启com3口，波特率，超时
                time.sleep(0.1)
                #
                # 保存串口信息到成员变量
                #
                if self.ser.isOpen():
                    self.port = port
                    self.collector_addr = collector_addr
                    self.baud_rate = baud_rate

                    return self.test_ser()  # 测试一下能否接收数据

            except SerialException:
                pass

        return False

    def test_ser(self):
        """
        测试串口是否正常
        :return:
        """
        data = self.write("03 0000 0001", 0.1)
        if data != "":
            return True

        return False

    def one_key(self, cmd: str) -> bool:
        """
        一键操作
        :param instruction:命令
        :return:
        """
        code = 1
        if cmd == "一键重启":
            code = 1
        elif cmd == "一键上锁":
            code = 9
        elif cmd == "一键解锁":
            code = 10
        elif cmd == "一键防风":
            code = 6
        elif cmd == "一键打平":
            code = 3
        elif cmd == "一键除雪":
            code = 7
        elif cmd == "一键清洗":
            code = 8
        elif cmd == "减少防风角度":
            code = 11
        elif cmd == "增加防风角度":
            code = 12
        else:
            code = int(cmd)

        instruction = "{:04x}".format(code).upper()

        if self.ser is None:
            return False
        data = self.write("06 01FF" + instruction, 0.1)
        if data != "":
            return True

        return False

    def send_control_code(self, machine_number: str, code: str) -> bool:
        """
        给控制器发送控制代码
        :param machine_number:机器编号，10 进制
        :param code:控制代码，16 进制
        :return:无
        """
        machine_number = "{:04X}".format((int(machine_number) - 1) * 4 + 3)
        code = "{:04X}".format(int(code, 16))  # 默认输入是 16 进制
        data = self.write("06" + machine_number + code, 0.1)
        if data != "":
            return True

        return False

    def get_table_data(self):
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
            #
            # 每次等待 0.2s，等待返回数据
            #
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
                return None

        if all_data is not None:
            return self.convert2dec(n_machine, all_data)

        return None

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
            t = data[start + 12:start + 16]
            angle = util.get_angle(t) / 100
            angle = "{:.2f}".format(angle)
            # print("十六进制：", t, "角度：", angle)

            machine_data.append(angle)

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
        self.ser.flushOutput()

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
