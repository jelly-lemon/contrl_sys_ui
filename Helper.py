import os

from PySide2.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor

from Model import Model
import util
import csv


class Helper:
    """
    MainWindow 界面类的控制器
    """

    def __init__(self):
        """
        初始化控制器
        """
        self.last_port_list = None
        self.dataCollectorModel = Model()

    def get_table_model(self, table_data: str):

        data = eval(table_data)

        n_machine = len(data)  # 机器数量
        error_number = ""  # 有问题机器编号
        table_model = QStandardItemModel()


        yellow = QColor(255, 255, 0)
        orange = QColor(255, 97, 0)
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
                error_code_item.setBackground(QBrush(yellow))
            elif break_code == 255:
                error_code_item.setBackground(QBrush(orange))
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

    def read_config(self):
        """
        读取配置文件
        :return:读取到的数据
        """
        try:
            file = open("./other/config.txt", mode="r", encoding="utf-8")
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
        file_dir = "./other"
        file_name = "config.txt"
        file_path = file_dir + "/" + file_name

        if os.path.exists(file_dir) is False:
            os.makedirs(file_dir)

        file = open(file_path, mode="w+", encoding="utf-8")
        if file.write(baudrate + " " + address):
            file.close()
            return True

        return False

    def write_wind_speed(self, wind_speed: float, collector_addr):
        """
        写入风速到 CSV 文件
        :param wind_speed:
        :return:
        """
        file_dir = "./wind_speed"
        file_name = util.get_time()[0:10] + "-" + collector_addr + "-wind_speed.csv"
        file_path = file_dir + "/" + file_name

        if os.path.exists(file_dir) is False:
            os.makedirs(file_dir)

        file = open(file_path, "a+", newline="")
        csv_write = csv.writer(file)
        data_row = [util.get_time(), str(wind_speed)]
        csv_write.writerow(data_row)
        file.close()

    # def write_csv(self, file_path: str, text: str):
    #     # 追加数据到末尾
    #     file = open(file_path, mode="a", encoding="utf-8", newline="")
    #     csv_write = csv.writer(file)
    #     data_row = [util.get_time(), str(text)]
    #     csv_write.writerow(data_row)
    #     file.close()

    def write_error(self, error_info: str, collector_addr: str):
        """
        保存出错日志到文件
        日期-数采地址
        :param error_info:错误信息
        :return:无
        """
        file_dir = "./error_log"
        file_name = util.get_time()[0:10] + "-" + collector_addr + ".csv"
        file_path = file_dir + "/" + file_name

        if os.path.exists(file_dir) is False:
            os.makedirs(file_dir)

        file = open(file_path, "a+", newline="")
        csv_write = csv.writer(file)
        data_row = [util.get_time(), error_info]
        csv_write.writerow(data_row)
        file.close()

    # def check_files(self, file_name: str) -> str:
    #     """
    #     检查文件是否存在，不存在就新建
    #     :return:文件所在路径
    #     """
    #     if file_name == "wind_speed":
    #         file_dir = "./wind_speed"
    #         file_path = file_dir + "/" + util.get_time()[0:10] + "-wind_speed.csv"
    #         csv_head = ["time", "wind_speed"]
    #     elif file_name == "error":
    #         file_dir = "./error_log"
    #         file_path = file_dir + "/" + util.get_time()[0:10] + "-error.csv"
    #         csv_head = ["time", "error"]
    #     else:
    #         return ""
    #
    #     #
    #     # 不存在则新建
    #     #
    #     if os.path.exists(file_dir) is False:
    #         os.makedirs(file_dir)
    #     if os.path.exists(file_path) is False:
    #         file = open(file_path, mode="a", encoding="utf-8")
    #         csv_writer = csv.writer(file)
    #         csv_writer.writerow(csv_head)
    #         file.close()
    #
    #     return file_path

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
