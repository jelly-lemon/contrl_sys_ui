from PySide2.QtGui import QStandardItemModel, QStandardItem

from DataCollectorModel import DataCollectorModel
import util


class Controller:
    def __init__(self, port: str = "COM4", collector_addr: str = "06"):
        self.dataCollectorModel = DataCollectorModel()

    def update_serial(self, port: str, collector_addr: str):
        if port != self.dataCollectorModel.get_port() or collector_addr != self.dataCollectorModel.get_collector_addr():
            self.dataCollectorModel.update_serial(port, collector_addr)

    def get_wind_speed(self, callback):
        wind_speed = self.dataCollectorModel.wind_speed()

        callback(wind_speed)



    def get_combobox_data(self, callback):
        port_name_list = util.get_port_list()

        # 回调主线程函数，更新界面
        callback(port_name_list)

    def get_table_data(self, callback):
        """
        {'1': ('故障代码', '控制代码', '锁状态', '实时角度'), ...}

        """

        data = self.dataCollectorModel.get_table_data()

        n_machine = len(data)  # 机器数量
        # 假数据
        if data == {} or data is None:

            for i in range(1, n_machine + 1):
                data['%d' % i] = ('故障代码' + str(i), '控制代码' + str(i),
                                  '锁状态' + str(i), '实时角度' + str(i))

        # 首先清理表格
        table_model = QStandardItemModel()
        table_model.clear()

        # 填充数据
        for machine_number in range(1, n_machine + 1):
            i, j = self.get_row_col(machine_number)

            item0 = QStandardItem(str(data[machine_number][0]))
            table_model.setItem(i, j, QStandardItem("%d号跟踪器故障代码" % (machine_number)))
            table_model.setItem(i, j + 1, item0)

            item1 = QStandardItem(str(data[machine_number][1]))
            table_model.setItem(i + 1, j, QStandardItem("%d号跟踪器控制代码" % (machine_number)))
            table_model.setItem(i + 1, j + 1, item1)

            item2 = QStandardItem(str(data[machine_number][2]))
            table_model.setItem(i + 2, j, QStandardItem("%d号跟踪器锁状态" % (machine_number)))
            table_model.setItem(i + 2, j + 1, item2)

            item3 = QStandardItem(str(data[machine_number][3]))
            table_model.setItem(i + 3, j, QStandardItem("%d号跟踪器实时角度" % (machine_number)))
            table_model.setItem(i + 3, j + 1, item3)

        callback(table_model)


    def get_row_col(self, machine_number):
        """
        给出机器编号，返回该机器参数的第一个参数的单元格位置
        :param machine_number:
        :return:
        """
        n_col = 5  # 规定一列显示 5 台机器

        i = ((machine_number - 1) % n_col) * 4
        j = int((machine_number - 1) / 5) * 2

        return i, j


