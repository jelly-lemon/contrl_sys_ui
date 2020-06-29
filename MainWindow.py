import threading

from threading import Timer

from PySide2.QtWidgets import QApplication, QHeaderView, QSplitter, QMainWindow, \
    QAction, QInputDialog, QLineEdit
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import Qt

import util
from Controller import Controller


class MainWindow(QMainWindow):
    """
    主窗口类
    """

    def __init__(self):
        super().__init__()

        # 成员变量
        self.isPolling = False  # 是否在轮询中
        self.controller = Controller()  # 控制器
        self.timer = None   # 定时器，设成成员变量是为了能够取消定时器

        # 加载 UI 文件，self.ui 就是应用中 MainWindow 这个对象
        self.ui = QUiLoader().load('./QtDesigner/main_window.ui')

        # 窗口标题
        self.ui.setWindowTitle("监控界面")
        # 初始化下拉列表框
        self.controller.get_combobox_data(self.init_combobox)
        # 初始化分离器
        self.init_splitter()
        # 初始化表格
        self.init_table()
        # 输出信息的窗口
        self.init_output_edit()
        # 轮询按钮点击事件
        self.ui.btn_submit.clicked.connect(self.submit_poling)

        # 初始化右键菜单
        self.init_context_menu()

    def update_member(self, member):
        """
        更新成员数
        :param member:成员数
        :return:无
        """
        self.ui.label_member.setText(str(member))



    def init_combobox(self, port_name_list: list):
        """
        初始化下拉列表框
        :return:无
        """
        # 扫描端口
        self.ui.box_com_port.addItems(port_name_list)
        if len(port_name_list) > 0:
            self.append_info("共扫描到 %d 个串口设备：%s" % (len(port_name_list), port_name_list))
        else:
            self.append_info("未检测到任何串口设备")

    def init_splitter(self):
        """
        初始化分离器控件
        :return: 无
        """
        # 新建一个分离器，垂直分离
        self.main_splitter = QSplitter(Qt.Vertical)

        # 分离器添加控件
        self.main_splitter.addWidget(self.ui.tableView)
        self.main_splitter.addWidget(self.ui.output_edit)

        # 设置窗口比例
        self.main_splitter.setStretchFactor(0, 8)
        self.main_splitter.setStretchFactor(1, 2)

        # self.main_splitter.show()   # 这样会单独跑出来一个窗口

        # 把这个 splitter 放在一个布局里才能显示出来
        self.ui.data_layout.addWidget(self.main_splitter)

    def init_output_edit(self):
        """
        初始化输出框
        :return: 无
        """
        self.ui.output_edit.setReadOnly(True)  # 禁止编辑

    def append_info(self, info: str):
        """
        输出框追加信息信息
        :param info:需要显示的信息
        :return:
        """
        self.ui.output_edit.append(util.get_time() + " " + info)  # 显示文本

    def init_table(self):
        """
        初始化表格样式
        :return:无
        """
        # 隐藏默认垂直表头
        self.ui.tableView.verticalHeader().setVisible(False)  # 隐藏垂直表头
        # 设置每列宽度：根据内容调整表格宽度
        self.ui.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def submit_poling(self):
        """
        提交轮询
        :return:无
        """
        # 获取控件的值
        com_port = self.ui.box_com_port.currentText()  # 端口号
        collector_addr = self.ui.edit_addr.text()  # 数采地址
        baudrate = self.ui.edit_baudrate.text() # 波特率

        self.controller.update_serial(com_port, baudrate, collector_addr)

        if not self.isPolling:
            # 点击“开始轮询”，则按钮立即显示“停止轮询”
            self.ui.btn_submit.setText("停止轮询")

            # 下拉框、输入框都不可修改
            self.ui.box_com_port.setEnabled(False)
            self.ui.edit_baudrate.setEnabled(False)
            self.ui.edit_addr.setEnabled(False)
            self.ui.edit_interval.setEnabled(False)


            # 开始轮询
            self.timer = Timer(0, self.poling)
            self.timer.start()
            self.isPolling = True
            self.append_info("开始轮询")



        else:
            # 点击“停止轮询”，则按钮立即显示“开始轮询”
            self.ui.btn_submit.setText("开始轮询")
            # 下拉框、输入框恢复

            self.ui.box_com_port.setEnabled(True)
            self.ui.edit_baudrate.setEnabled(True)
            self.ui.edit_addr.setEnabled(True)
            self.ui.edit_interval.setEnabled(True)

            # 停止轮询
            self.timer.cancel()
            self.isPolling = False
            self.append_info("结束轮询")

    def poling(self):
        """
        轮询查询
        :return:无
        """

        interval = int(self.ui.edit_interval.text())
        self.timer = Timer(interval, self.poling)
        self.timer.start()

        self.controller.get_table_data(self.update_table, self.update_member, self.append_info)
        self.controller.get_wind_speed(self.update_wind_speed)


    def update_wind_speed(self, wind_speed):
        """
        更新风速
        :param wind_speed:风速值
        :return: 无
        """
        self.ui.label_wind_speed.setText(str(wind_speed) + " m/s")

    def update_table(self, table_model):
        """
        更新表格数据
        :param table_model:表格数据模型
        :return:无
        """
        self.ui.tableView.setModel(table_model)

        # 对表格单元格进行监听，单元格编辑完成后进入该事件
        # 该怎么做呢
        # self.table_model.itemChanged.connect(self.submit_control_code)

        self.append_info("数据更新完成！")

    def init_context_menu(self):
        """
        初始化右键菜单
        :return:
        """
        # tableView 允许右键菜单
        self.ui.tableView.setContextMenuPolicy(Qt.ActionsContextMenu)

        # 具体菜单项
        send_option = QAction(self.ui.tableView)
        send_option.setText("发送控制代码")
        send_option.triggered.connect(self.show_modify_dialog)

        # tableView 添加具体的右键菜单
        self.ui.tableView.addAction(send_option)

    def show_modify_dialog(self):
        """
        显示发送控制代码的对话框
        :return: 无
        """

        i = self.ui.tableView.currentIndex().row()
        j = self.ui.tableView.currentIndex().column()
        if i % 4 == 1 and j % 2 == 1:
            machine_number = self.controller.get_machine_number(i, j)
            text, okPressed = QInputDialog.getText(self, "发送控制代码", "%d 号控制器：" % machine_number, QLineEdit.Normal, "")
            if okPressed and text != '':
                t1 = threading.Thread(target=self.controller.send_control_code,
                                      args=(machine_number, text, self.append_info))
                t1.start()  # 子线程执行


if __name__ == '__main__':
    app = QApplication([])  # 初始化应用
    main_window = MainWindow()  # 创建主窗口

    # main_window.ui.show()  # 按实际大小显示窗口
    main_window.ui.showMaximized()  # 全屏显示窗口，必须要用，不然不显示界面

    app.exec_()  # 进入事件循环
