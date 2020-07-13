import os

from PySide2.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor

from Model import Model
import util
import csv
from playsound import playsound


class Controller:
    """
    MainWindow 界面类的控制器
    """

    def one_key(self, cmd: str, append_info):
        """
        一键操作
        :param cmd:命令
        :param append_info:界面更新函数
        :return:无
        """
        code = "00 01"
        if cmd == "一键重启":
            code = "00 01"
        elif cmd == "一键上锁":
            code = "00 09"
        elif cmd == "一键解锁":
            code = "00 0A"
        elif cmd == "一键防风":
            code = "00 06"
        elif cmd == "一键除雪":
            code = "00 07"
        elif cmd == "一键清洗":
            code = "00 08"
        result = self.dataCollectorModel.one_key(code)
        if result:
            append_info("%s成功" % cmd, 'green')
        else:
            append_info("%s失败" % cmd, 'red')

    def __init__(self):
        """
        初始化控制器
        """
        self.last_port_list = None
        self.dataCollectorModel = Model()

    def get_member(self, update_member):
        """
        获取机器数量，并更新界面
        :param update_member:更新机器数量函数
        :return:无
        """
        member = self.dataCollectorModel.get_member()
        update_member(member)

    def send_control_code(self, machine_number, code, append_info):
        """
        发送控制代码
        :param machine_number:机器编号，十进制
        :param code: 控制代码，16 进制
        :param append_info: 回调函数
        :return:无
        """
        self.dataCollectorModel.send_control_code(machine_number, code)
        append_info("向 %d 号控制器发送控制代码 %s 成功" % (machine_number, code), 'green')

    def update_serial(self, port: str, baud_rate: str, collector_addr: str, ):
        """
        更新串口实例
        :param port:端口号
        :param collector_addr:数字采集器地址
        :return: 无
        """
        # 更新串口
        return self.dataCollectorModel.update_serial(port, baud_rate, collector_addr)

    def get_wind_speed(self, update_wind_speed):
        """
        获取风速
        :param update_wind_speed:回调函数，界面更新风速
        :return: 无
        """
        wind_speed = self.dataCollectorModel.wind_speed()
        self.write_wind_speed(wind_speed)
        update_wind_speed(wind_speed)

    def get_port_list(self, update_port):
        """
        获取下拉框数据
        :param callback:回调函数，界面更新下拉数据
        :return: 无
        """
        port_name_list = util.get_port_list()

        #
        # 和上次比没有变化，就不更新界面了
        #
        if self.last_port_list != port_name_list:
            self.last_port_list = port_name_list
            update_port(self.last_port_list)  # 回调主线程函数，更新界面

    def get_table_model(self, data: {}):
        n_machine = len(data)  # 机器数量
        error_number = ""  # 有问题机器编号
        table_model = QStandardItemModel()

        #
        # 填充 table_model
        #
        for machine_number in range(1, n_machine + 1):
            i, j = self.get_row_col(machine_number)

            if data[machine_number][0] != 0:
                error_number += str(machine_number) + " "

            error_code_item = QStandardItem(str(data[machine_number][0]))
            error_code_item.setEditable(False)
            break_code = data[machine_number][0]
            if 0 < break_code <= 10:
                error_code_item.setBackground(QBrush(QColor(255, 255, 0)))
            elif break_code == 255:
                error_code_item.setBackground(QBrush(QColor(255, 97, 0)))
            t0 = QStandardItem("%d号跟踪器故障代码" % (machine_number))
            t0.setEditable(False)

            table_model.setItem(i, j, t0)
            table_model.setItem(i, j + 1, error_code_item)

            t1 = QStandardItem("%d号跟踪器控制代码" % (machine_number))
            t1.setEditable(False)
            item1 = QStandardItem(str(data[machine_number][1]))

            table_model.setItem(i + 1, j, t1)
            table_model.setItem(i + 1, j + 1, item1)

            t2 = QStandardItem("%d号跟踪器锁状态" % (machine_number))
            t2.setEditable(False)
            item2 = QStandardItem(str(data[machine_number][2]))
            item2.setEditable(False)

            table_model.setItem(i + 2, j, t2)
            table_model.setItem(i + 2, j + 1, item2)

            t3 = QStandardItem("%d号跟踪器实时角度" % (machine_number))
            t3.setEditable(False)
            item3 = QStandardItem(str(data[machine_number][3]))
            item3.setEditable(False)

            table_model.setItem(i + 3, j, t3)
            table_model.setItem(i + 3, j + 1, item3)

        return table_model, error_number

    def get_table_data(self, update_table, update_member, append_info):
        """
        获取表格数据
        {'1': ('故障代码', '控制代码', '锁状态', '实时角度'), ...}
        :param update_table:回调函数，更新表格
        :return:无
        """
        data = self.dataCollectorModel.get_table_data()  # 获取表格原始数据

        #
        # 如果没获取到，就不更新
        #
        if data == {} or data is None:
            append_info("更新表格失败(串口返回数据有误)！")
            return

        #
        # 更新界面
        #
        table_model, error_number = self.get_table_model(data)
        update_table(table_model)  # 更新表格
        update_member(len(data))

        #
        # 如果存在机器有异常，就播放报警声，并写入日志
        #
        if error_number != "":
            playsound('./other/bee.mp3')  # 播放警报声
            self.write_error(error_number)  # 写在文件里
            append_info("有异常机器编号：" + error_number)  # 输出到窗口
        else:
            append_info("数据更新完成，无异常")

    def read_config(self):
        """
        读取配置文件
        :return:读取到的数据
        """
        try:
            file = open("./config.txt", mode="r", encoding="utf-8")
            s = file.readline()
            if s != "":
                return s.split()
        except IOError:
            pass

        return "", ""

    def write_config(self, baudrate, address) -> bool:
        """
        把配置写入文件，方便下次读取
        :param baudrate: 波特率
        :param address: 数采地址
        :return: 是否写入成功
        """
        file_path = "./config.txt"
        if file_path != "":
            file = open(file_path, mode="w+", encoding="utf-8")
            if file.write(baudrate + " " + address):
                file.close()
                return True

        return False

    def write_wind_speed(self, wind_speed: float):
        file_path = self.check_files("wind_speed")  # 检查文件是否存在
        self.write_csv(file_path, str(wind_speed))  # 写入到 csv 文件

    def write_csv(self, file_path: str, text: str):
        # 追加数据到末尾
        file = open(file_path, mode="a", encoding="utf-8")
        csv_write = csv.writer(file)
        data_row = [util.get_time(), str(text)]
        csv_write.writerow(data_row)
        file.close()

    def write_error(self, error_info: str):
        """
        保存出错日志到文件
        :param error_info:错误信息
        :return:无
        """
        file_path = self.check_files("error")  # 检查文件是否存在
        self.write_csv(file_path, error_info)

    def check_files(self, file_name: str) -> str:
        """
        检查文件是否存在，不存在就新建
        :return:文件所在路径
        """
        if file_name == "wind_speed":
            file_dir = "./wind_speed"
            file_path = file_dir + "/" + util.get_time()[0:10] + "-wind_speed.csv"
            csv_head = ["time", "wind_speed"]
        elif file_name == "error":
            file_dir = "./error_log"
            file_path = file_dir + "/" + util.get_time()[0:10] + "-error.csv"
            csv_head = ["time", "error"]
        else:
            return ""

        #
        # 不存在则新建
        #
        if os.path.exists(file_dir) is False:
            os.makedirs(file_dir)
        if os.path.exists(file_path) is False:
            file = open(file_path, mode="a", encoding="utf-8")
            csv_writer = csv.writer(file)
            csv_writer.writerow(csv_head)
            file.close()

        return file_path

    def get_row_col(self, machine_number):
        """
        给出机器编号，返回该机器参数的第一个参数的单元格位置
        :param machine_number:机器编号，10 进制
        :return:无
        """
        n_col = 5  # 规定一列显示 5 台机器
        i = ((machine_number - 1) % n_col) * 4
        j = int((machine_number - 1) / n_col) * 2

        return i, j

    def get_machine_number(self, i, j):
        """
        给出表格中的行、列，返回对应的机器编号
        :param i: 行
        :param j: 列
        :return: 机器编号
        """
        n_col = 5  # 规定一列显示 5 台机器
        machine_number = int(i / 4) + 1  # 一台机器有 4 行
        machine_number += int(j / 2) * n_col

        return machine_number
