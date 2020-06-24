import time
from threading import Timer

from PySide2.QtWidgets import QApplication, QMessageBox, QHeaderView, QTableWidgetItem, QSplitter, QMainWindow
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import Qt
from PySide2.QtCore import Slot, Signal, SignalInstance, QObject, SIGNAL, QThread

import serial

import math

import util
from DataCollector import DataCollector


class MainWindow():

    def __init__(self):
        # super().__init__()
        self.data_collector = None

        self.timer = None




        # 加载 UI 文件，self.ui 就是应用中 MainWindow 这个对象
        self.ui = QUiLoader().load('./QtDesigner/main_window.ui')

        # 初始化窗口
        self.ui.setWindowTitle("监控界面")

        # 初始化组件顺序，不可打乱
        # self.ui.input_layout.setSpacing(0)

        self.isPolling = False

        self.init_splitter()
        self.init_ouput_edit()

        self.init_combobox()

        # button 点击事件
        self.ui.btn_submit.clicked.connect(self.submit_poling)

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
        # self.ui.output_edit.setPlainText(util.get_time() + " 界面初始化完成！")  # 显示文本

    def append_info(self, info: str):
        self.ui.output_edit.append(util.get_time() + " " + info)  # 显示文本

    def init_table(self):
        """
        初始化表格
        :param n:机器数量
        :return:无
        """

        n = self.data_collector.machine_num()

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

        # self.update_table()

    def submit_poling(self):
        """
        提交轮询
        :return:无
        """
        # 获取控件的值
        com_port = self.ui.box_com_port.currentText()
        collector_addr = self.ui.edit_addr.text()

        if self.data_collector != None:
            self.data_collector.close()

        self.data_collector = DataCollector(com_port, collector_addr)

        # 初始化表格
        self.ui.table_1.clear() # 清除表格中所有内容
        self.init_table()   # 初始化表格

        # 更新表格
        #self.update_table()

        if not self.isPolling:
            # 点击“开始轮询”，则按钮立即显示“停止轮询”
            self.ui.btn_submit.setText("停止轮询")
            # 下拉框、输入框都不可修改
            self.ui.box_com_port.setEditable(False)
            self.ui.edit_addr.setReadOnly(True)
            # 开始轮询
            self.timer = Timer(0, self.poling)
            self.timer.start()

            self.isPolling = True

        else:
            # 点击“停止轮询”，则按钮立即显示“开始轮询”
            self.ui.btn_submit.setText("开始轮询")
            # 下拉框、输入框恢复
            self.ui.box_com_port.setEditable(True)
            self.ui.edit_addr.setReadOnly(True)
            # 停止轮询
            self.timer.cancel()

            self.isPolling = False


    def poling(self):
        """
        轮询查询
        :return:无
        """
        self.timer = Timer(30, self.poling)
        self.timer.start()

        #self.update_table()


        data = self.data_collector.query_data() # 请求数据，放在子线程中完成

        self.update_table(data)





    def submit_control_code(self, item):
        i = item.row()
        j = item.column()
        self.append_info("发送" + self.ui.table_1.item(i, j - 1).text() + "：" + item.text())


    # 谁来调用？
    @Slot(str)
    def update_table(self, data: dict):
        """
        {'1': ('故障代码', '控制代码', '锁状态', '实时角度'), ...}
        只允许更新表格，其余的耗时操作不要放在这
        :param data:
        :return:
        """


        if data == {} or data is None:
            # 假数据
            for i in range(self.data_collector.machine_num()):
                data['%d' % (i + 1)] = ('故障代码' + str(i + 1), '控制代码' + str(i + 1),
                                        '锁状态' + str(i + 1), '实时角度' + str(i + 1))

        for machine_number in range(1, self.data_collector.machine_num() + 1):
            i, j = self.get_row_col_at(machine_number)

            item0 = QTableWidgetItem(str(data[machine_number][0]))
            item1 = QTableWidgetItem(str(data[machine_number][1]))
            item2 = QTableWidgetItem(str(data[machine_number][2]))
            item3 = QTableWidgetItem(str(data[machine_number][3]))

            self.ui.table_1.setItem(i, j, item0)
            # self.ui.table_1.item(i, j - 1).setFlags(self.ui.table_1.item(i, j - 1).flags()
            #                                         & ~Qt.ItemIsEnabled)
            # self.ui.table_1.item(i, j).setFlags(self.ui.table_1.item(i, j).flags()
            #                                     & ~Qt.ItemIsEnabled)

            self.ui.table_1.setItem(i + 1, j, item1)
            self.ui.table_1.item(i + 1, j - 1).setFlags(self.ui.table_1.item(i + 1, j - 1).flags()
                                                        & ~Qt.ItemIsEnabled)

            self.ui.table_1.setItem(i + 2, j, item2)
            # self.ui.table_1.item(i + 2, j - 1).setFlags(self.ui.table_1.item(i + 2, j - 1).flags()
            #                                             & ~Qt.ItemIsEnabled)
            # self.ui.table_1.item(i + 2, j).setFlags(self.ui.table_1.item(i + 2, j).flags()
            #                                         & ~Qt.ItemIsEnabled)

            self.ui.table_1.setItem(i + 3, j, item3)
            # self.ui.table_1.item(i + 3, j - 1).setFlags(self.ui.table_1.item(i + 3, j - 1).flags()
            #                                             & ~Qt.ItemIsEnabled)
            # self.ui.table_1.item(i + 3, j).setFlags(self.ui.table_1.item(i + 3, j).flags()
            #                                         & ~Qt.ItemIsEnabled)

        # 对表格单元格进行监听，单元格编辑完成后进入该事件
        # 该怎么做呢
        #self.ui.table_1.itemChanged.connect(self.submit_control_code)

        self.append_info("表格数据更新完成！")

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
