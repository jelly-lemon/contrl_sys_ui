import time

from PySide2.QtWidgets import QApplication, QMessageBox, QHeaderView, QTableWidgetItem, QSplitter, QMainWindow
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import Qt

import serial

import math
import util
from DataCollector import DataCollector


class MainWindow():
    def __init__(self):
        # super().__init__()

        # 一些其它对象
        self.data_collector = DataCollector()

        # 加载 UI 文件，self.ui 就是应用中 MainWindow 这个对象
        self.ui = QUiLoader().load('./QtDesigner/main_window.ui')

        # 初始化窗口
        self.ui.setWindowTitle("监控界面")

        # 初始化组件顺序，不可打乱
        #self.ui.input_layout.setSpacing(0)



        self.init_splitter()
        self.init_ouput_edit()
        self.init_table(self.data_collector.machine_num())
        self.init_combobox()

    def init_combobox(self):
        # 扫描端口
        port_list = util.get_port_list()
        self.ui.box_com_port.addItems(port_list)
        if len(port_list) > 0:
            self.append_info("共扫描到 %d 个串口设备：%s" % (len(port_list), port_list))
        else:
            self.append_info("未检测到任何串口设备")

    def init_splitter(self):

        # 新建一个分离器，垂直分离
        self.main_splitter = QSplitter(Qt.Vertical)

        # 分离器添加控件
        self.main_splitter.addWidget(self.ui.table_1)
        self.main_splitter.addWidget(self.ui.output_edit)


        # 设置窗口比例
        self.main_splitter.setStretchFactor(0, 8)
        self.main_splitter.setStretchFactor(1, 2)

        # self.main_splitter.show()   # 这样会单独跑出来一个窗口

        # 把这个 splitter 放在一个布局里才能显示出来
        self.ui.data_layout.addWidget(self.main_splitter)

    def init_ouput_edit(self):
        """
        初始化输出框
        :return: 无
        """
        self.ui.output_edit.setReadOnly(True)  # 禁止编辑
        self.ui.output_edit.setPlainText(util.get_time() + " 界面初始化完成！")  # 显示文本

    def append_info(self, info: str):
        self.ui.output_edit.append(util.get_time() + " " + info)  # 显示文本

    def init_table(self, n: int):
        """
        初始化表格
        :param n:机器数量
        :return:无
        """
        # 隐藏默认垂直表头
        self.ui.table_1.verticalHeader().setVisible(False)  # 隐藏垂直表头

        # 设置每列宽度：根据内容调整表格宽度
        self.ui.table_1.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # 设置表格行、列
        self.n_machine_each_col = 5  # 设置一列显示的机器数量
        n_row = self.n_machine_each_col * 4  # 一台机器需要4行来显示
        n_col = math.ceil(n / self.n_machine_each_col) * 2  # 向上取整，算出要多少列
        self.ui.table_1.setRowCount(n_row)
        self.ui.table_1.setColumnCount(n_col)

        # 设置水平表头
        col_name = ['名称', '值']
        for i in range(2, n_col):
            # 重复出现表头：['名称', '值']
            col_name.append(col_name[0] if i % 2 == 0 else col_name[1])
        self.ui.table_1.setHorizontalHeaderLabels(col_name)

        # 每 2 列的标题
        item_tuple = ("跟踪器故障代码", "跟踪器控制代码", "跟踪器锁状态", "跟踪器实时角度")

        # 填充表格所有标题
        for count in range(n):
            for i in range(4):
                item_name = ("%d号" % (count + 1)) + item_tuple[i]

                item_row = i + (count * 4) % n_row  # 根据机器编号找到表格行号
                item_col = int(count / self.n_machine_each_col) * 2  # 根据机器编号和每列可显示机器数量找到表格列号

                item = QTableWidgetItem(item_name)
                self.ui.table_1.setItem(item_row, item_col, item)

        # 立即刷新表格，显示更新后的内容
        # 不是这么回事，先留着
        # self.ui.table_1.repaint()



        self.show_data()

        # 对表格单元格进行监听，单元格编辑完成后进入该事件
        # 该怎么做呢
        self.ui.table_1.itemChanged.connect(self.submit_control_code)

    def submit_control_code(self, item):
        i = item.row()
        j = item.column()
        self.append_info("发送" + self.ui.table_1.item(i, j-1).text() + "：" + item.text())

        #print("(%d,%d):%s" % (i, j, item.text()))


    def show_data(self):
        """
        {'1': ('故障代码', '控制代码', '锁状态', '实时角度'), ...}
        :param data:
        :return:
        """
        data = self.data_collector.query_data()
        if data == {}:
            # 假数据
            for i in range(self.data_collector.machine_num()):
                data['%d' % (i + 1)] = ('故障代码' + str(i+1), '控制代码' + str(i+1),
                                        '锁状态' + str(i+1), '实时角度' + str(i+1))

        for machine_number in range(self.data_collector.machine_num()):
            i, j = self.get_row_col_at(machine_number + 1)
            item0 = QTableWidgetItem(data['%d' % (machine_number + 1)][0])
            item1 = QTableWidgetItem(data['%d' % (machine_number + 1)][1])
            item2 = QTableWidgetItem(data['%d' % (machine_number + 1)][2])
            item3 = QTableWidgetItem(data['%d' % (machine_number + 1)][3])

            self.ui.table_1.setItem(i, j, item0)
            self.ui.table_1.item(i, j - 1).setFlags(self.ui.table_1.item(i, j - 1).flags()
                                                    & ~Qt.ItemIsEnabled)
            self.ui.table_1.item(i, j).setFlags(self.ui.table_1.item(i, j).flags()
                                                    & ~Qt.ItemIsEnabled)

            self.ui.table_1.setItem(i + 1, j, item1)
            self.ui.table_1.item(i + 1, j - 1).setFlags(self.ui.table_1.item(i + 1, j - 1).flags()
                                                        & ~Qt.ItemIsEnabled)

            self.ui.table_1.setItem(i + 2, j, item2)
            self.ui.table_1.item(i + 2, j- 1).setFlags(self.ui.table_1.item(i + 2, j- 1).flags()
                                                                & ~Qt.ItemIsEnabled)
            self.ui.table_1.item(i + 2, j).setFlags(self.ui.table_1.item(i + 2, j).flags()
                                                                & ~Qt.ItemIsEnabled)

            self.ui.table_1.setItem(i + 3, j, item3)
            self.ui.table_1.item(i + 3, j - 1).setFlags(self.ui.table_1.item(i + 3, j - 1).flags()
                                                                & ~Qt.ItemIsEnabled)
            self.ui.table_1.item(i + 3, j).setFlags(self.ui.table_1.item(i + 3, j).flags()
                                                                & ~Qt.ItemIsEnabled)




        self.append_info("数据读取完成！")

        # n_row = self.ui.table_1.rowCount()
        #
        # # 表格的行号从 0 开始
        # for count in range(self.data_collector.get_machine_num()):
        #     for i in range(4):
        #         item_row = i + (count * 4) % n_row  # 根据机器编号找到表格行号
        #         item_col = int(count / self.n_machine_each_col) * 2 + 1  # 根据机器编号和每列可显示机器数量找到表格列号
        #
        #         item = QTableWidgetItem("获取错误")
        #         self.ui.table_1.setItem(item_row, item_col, item)


    def get_row_col_at(self, machine_number):
        """
        给出机器编号，返回该机器参数的第一个参数的单元格位置
        :param machine_number:
        :return:
        """
        machine_number -= 1
        n_row = self.ui.table_1.rowCount()
        i = (machine_number * 4) % n_row
        j = int(machine_number / self.n_machine_each_col) * 2 + 1
        return i, j


if __name__ == '__main__':
    app = QApplication([])  # 初始化应用
    main_window = MainWindow()  # 创建主窗口

    # main_window.ui.show()  # 按实际大小显示窗口
    main_window.ui.showMaximized()  # 全屏显示窗口，必须要用，不然不显示界面

    app.exec_()  # 进入事件循环
