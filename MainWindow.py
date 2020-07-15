import threading
from functools import partial
from threading import Timer

from PySide2.QtCore import QModelIndex
from PySide2.QtWidgets import QSplitter, QHeaderView, QApplication, QAction
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import Qt, QColor, QTextCursor, QIcon
import util
from Controller import Controller
from InfoDialog import InfoDialog
from LoginDialog import LoginDialog
from ModifyDialog import ModifyDialog


class MainWindow():
    """
    控制系统的主窗口
    """

    def __init__(self):
        """
        初始化界面
        """
        #
        # 成员变量
        #
        self.isPolling = False  # 是否在轮询中
        self.controller = Controller()  # 控制器
        self.polling_timer = None  # 轮询定时器，设成成员变量是为了能够取消定时器
        self.scanning_timer = None  # 扫描定时器，设成成员变量是为了能够取消定时器
        self.first_scanning = True  # 第一次扫描

        #
        # 初始化界面
        #
        self.ui = QUiLoader().load('./QtDesigner/main_window.ui')  # 加载 UI 文件，self.ui 就是应用中 MainWindow 这个对象
        self.init_window()  # 初始化主窗口
        self.init_interval_combobox()  # 初始化轮询时间下拉框
        self.init_splitter()  # 初始化分离器
        self.init_table()  # 初始化表格
        self.init_output_edit()  # 初始化输出信息的窗口
        self.init_menu_bar()  # 初始化菜单
        self.init_port()  # 初始化端口列表

        self.ui.btn_submit.clicked.connect(self.start_polling)  # 绑定点击事件

    def init_port(self):
        """
        初始化端口
        :return:无
        """
        self.start_scanning()  # 开始扫描端口

    def init_window(self):
        """
        初始化主窗口
        :return: 无
        """
        self.ui.setWindowTitle("光伏集群现场监控")  # 窗口标题

        #
        # 左上角图标，任务栏图标
        #
        app_icon = QIcon("./other/logo.ico")
        self.ui.setWindowIcon(app_icon)

        #
        # 读取配置文件
        #
        baudrate, address = self.controller.read_config()
        if baudrate != "" and address != "":
            self.ui.edit_baudrate.setText(baudrate)
            self.ui.edit_addr.setText(address)

    def init_menu_bar(self):
        """
        初始化菜单栏
        :return: 无
        """
        self.ui.restart.triggered.connect(partial(self.one_key_timer, self.ui.restart.text()))
        self.ui.lock.triggered.connect(partial(self.one_key_timer, self.ui.lock.text()))
        self.ui.unlock1.triggered.connect(partial(self.one_key_timer, self.ui.unlock1.text()))
        self.ui.wind_bread.triggered.connect(partial(self.one_key_timer, self.ui.wind_bread.text()))
        self.ui.snow_removal.triggered.connect(partial(self.one_key_timer, self.ui.snow_removal.text()))
        self.ui.clean_board.triggered.connect(partial(self.one_key_timer, self.ui.clean_board.text()))
        self.ui.sub_angle.triggered.connect(partial(self.one_key_timer, self.ui.sub_angle.text()))
        self.ui.add_angle.triggered.connect(partial(self.one_key_timer, self.ui.add_angle.text()))
        self.ui.about.triggered.connect(self.show_about)


    def init_interval_combobox(self):
        """
        初始化轮询时间下拉列表框
        :return: 无
        """
        interval_list = ['5 s', '10 s', '15 s', '30 s', '60 s']
        self.ui.combobox_interval.addItems(interval_list)

    def init_splitter(self):
        """
        初始化分离器控件
        :return: 无
        """
        self.main_splitter = QSplitter(Qt.Vertical)  # 新建一个分离器，垂直分离

        #
        # 分离器添加控件
        #
        self.main_splitter.addWidget(self.ui.tableView)
        self.main_splitter.addWidget(self.ui.output_edit)

        #
        # 设置窗口比例
        #
        self.main_splitter.setStretchFactor(0, 8)
        self.main_splitter.setStretchFactor(1, 2)

        self.ui.data_layout.addWidget(self.main_splitter)  # 把这个 splitter 放在一个布局里才能显示出来

    def init_output_edit(self):
        """
        初始化输出框
        :return: 无
        """
        self.ui.output_edit.setReadOnly(True)  # 禁止编辑

        #
        # 添加右键菜单
        #
        self.ui.output_edit.setContextMenuPolicy(Qt.ActionsContextMenu) # 允许右键菜单
        send_option = QAction(self.ui.output_edit)         # 具体菜单项
        send_option.setText("清除内容")
        send_option.triggered.connect(self.ui.output_edit.clear)  # 点击菜单中的具体选项执行的函数
        self.ui.output_edit.addAction(send_option)



    def init_table(self):
        """
        初始化表格样式
        :return:无
        """
        self.ui.tableView.verticalHeader().setVisible(False)  # 隐藏垂直表头
        #self.ui.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)  # 设置每列宽度：根据表头调整表格宽度
        self.ui.tableView.resizeColumnsToContents() # 根据内容调整列宽
        self.ui.tableView.clicked.connect(self.handle_table_click)  # 鼠标左键点击事件

    def start_scanning(self):
        """
        开始扫描端口
        :return:无
        """
        self.scanning_timer = Timer(0, self.scanning_port)
        self.scanning_timer.setName("scanning_start_timer")
        self.scanning_timer.setDaemon(True)  # 设置为守护线程，主线程退出时子线程强制退出
        self.scanning_timer.start()

    def scanning_port(self):
        """
        扫描端口
        :return:无
        """
        self.controller.get_port_list(self.update_port)  # 执行本次扫描任务
        self.next_scanning()  # 准备下一次扫描线程

    def next_scanning(self):
        """
        准备下一次扫描端口
        :return: 无
        """
        self.scanning_timer = Timer(0.5, self.scanning_port)
        self.scanning_timer.setName("scanning_timer")
        self.scanning_timer.setDaemon(True)
        self.scanning_timer.start()

    def show_about(self):
        """
        显示关于信息
        :return: 无
        """
        dial = InfoDialog("关于", "四川近日点新能源科技有限公司\n联系电话：028-xxxxxxx")
        dial.exec_()  # 进入事件循环，不关闭不会退出循环

    def one_key_timer(self, cmd):
        """
        用 Timer 开启一个子线程来完成任务
        :param cmd:命令
        :return:无
        """
        t = Timer(0, self.one_key, [cmd])
        t.setDaemon(True)
        t.start()

    def one_key(self, cmd):
        """
        一键命令
        :param cmd:命令
        :return:无
        """
        self.update_serial()  # 更新串口对象
        self.controller.one_key(cmd, self.append_info)  # 发送命令

    def update_member(self, member):
        """
        更新成员数
        :param member:成员数
        :return:无
        """
        self.ui.label_member.setText(str(member))

    def update_port(self, port_name_list: list):
        """
        初始化下拉列表框
        :return:无
        """
        # 扫描端口
        self.ui.box_com_port.clear()
        self.ui.box_com_port.addItems(port_name_list)
        if len(port_name_list) > 0:
            self.append_info("共扫描到 %d 个串口设备：%s" % (len(port_name_list), port_name_list))
            self.ui.btn_submit.setEnabled(True)  # 可以轮询
        else:
            self.append_info("未检测到任何串口设备，请检查连接是否正常", 'red')
            self.ui.btn_submit.setEnabled(False)  # 禁止轮询

    def append_info(self, info: str, color: str = 'black'):
        """
        输出框追加信息信息
        :param info:需要显示的信息
        :return:
        """
        black = QColor(0, 0, 0)
        if color == 'red':
            c = QColor(255, 0, 0)
        elif color == 'green':
            c = QColor(0, 128, 0)
        else:
            c = black

        #
        # 使用指定颜色追加文本，然后恢复为黑色
        #
        self.ui.output_edit.setTextColor(c)
        self.ui.output_edit.append(util.get_time() + " " + info)  # 显示文本
        self.ui.output_edit.setTextColor(black)
        self.ui.output_edit.moveCursor(QTextCursor.End)  # 输出信息后滚动到最后

    def handle_table_click(self, item: QModelIndex):
        """
        处理表格左键点击事件
        :param item:点击的单元格
        :return:无
        """
        #
        # 首先获取点击的行、列号
        # 判断点击的单元格是否可点击，如果可以，
        # 就弹出编辑对话框
        #
        i = item.row()
        j = item.column()
        if self.is_editable(i, j):
            #
            # 如果在轮询的话，立即停止，并标记需要恢复
            #
            if self.isPolling:
                self.stop_polling()

            #
            # 根据行号、列号计算出机器编号，然后显示修改窗口
            #
            machine_number = self.controller.get_machine_number(i, j)
            self.show_modify_dialog(machine_number)

    def is_editable(self, i, j) -> bool:
        """
        判断该单元格是否可编辑
        :param i:行，从 0 开始
        :param j:列，从 0 开始
        :return:是否可编辑
        """
        #
        # i % 4 == 1 表示 i 在控制代码行
        # j % 2 == 1 表示 j 在控制代码列
        #
        if i % 4 == 1 and j % 2 == 1:
            return True
        return False

    def set_enable(self, enable: bool):
        """
        是否允许编辑串口参数相关
        :param enable: 是否允许
        :return: 无
        """
        self.ui.box_com_port.setEnabled(enable)  # 端口下拉框
        self.ui.edit_baudrate.setEnabled(enable)  # 波特率
        self.ui.edit_addr.setEnabled(enable)  # 地址
        self.ui.combobox_interval.setEnabled(enable)  # 轮询时间

    def start_polling(self):
        """
        开始轮询按钮响应函数
        提交轮询 or 停止轮询
        :return:无
        """
        if not self.isPolling:
            self.isPolling = True
            self.ui.btn_submit.setText("停止轮询")
            self.set_enable(False)  # 禁止编辑

            #
            # 开始轮询
            #
            self.polling_timer = Timer(0, self.poling)
            self.polling_timer.setName("polling_start_timer")
            self.polling_timer.setDaemon(True)
            self.append_info("开始轮询")
            self.polling_timer.start()


        else:
            self.stop_polling()

    def poling(self):
        """
        轮询查询
        :return:无
        """

        if self.update_serial():
            #
            # 更新界面
            #
            self.controller.get_table_data(self.update_table, self.update_member, self.append_info)  # 更新表格
            # self.append_info("表格更新完成")
            self.controller.get_wind_speed(self.update_wind_speed)  # 更新风速
            # self.append_info("风速更新完成")
            # self.append_info("开始下一次轮询")
            self.next_polling()  # 准备下一次轮询




    def stop_polling(self):
        """
        立即停止轮询
        :return:无
        """
        #
        # 如果正在轮询，就停止轮询
        # 点击“停止轮询”，则按钮立即显示“开始轮询”
        #
        if self.isPolling:
            self.ui.btn_submit.setText("开始轮询")
            self.set_enable(True)  # 恢复允许编辑
            self.isPolling = False
            self.append_info("结束轮询")  # 信息台输出结束信息

            #
            # 强制停止子线程
            #
            if self.polling_timer is not None and self.polling_timer.is_alive():
                util.stop_thread(self.polling_timer)
                self.controller.close_ser()

    def next_polling(self):
        """
        设置一个定时器，到了一定时间后就启动轮询
        :return:无
        """
        interval = int(self.ui.combobox_interval.currentText()[:-2])  # 获取间隔时间下拉框的值
        self.polling_timer = Timer(interval, self.poling)
        self.polling_timer.setName("polling_timer")
        self.polling_timer.setDaemon(True)
        self.polling_timer.start()

    def update_serial(self) -> bool:
        """
        更新串口对象
        :return: 无
        """
        com_port = self.ui.box_com_port.currentText()  # 端口号
        collector_addr = self.ui.edit_addr.text()  # 数采地址
        baudrate = self.ui.edit_baudrate.text()  # 波特率

        if self.controller.update_serial(com_port, baudrate, collector_addr) is False:
            self.append_info("端口不存在 或 串口波特率有误 或 数采地址有误 或 串口没有回复，请检查", 'red')
            self.stop_polling()
            return False

        self.controller.write_config(baudrate, collector_addr)

        return True

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

    def show_modify_dialog(self, machine_number: int):
        """
        显示发送控制代码的对话框
        :return: 无
        """
        input_dial = ModifyDialog("发送控制代码", "%d 号控制器：" % machine_number)
        if input_dial.exec_():
            code = int(input_dial.textValue())
            if 1 <= code <= 99:
                #
                # 发送控制代码
                #
                if self.update_serial():
                    self.send_code(machine_number, code)  # 启动子线程，发送控制代码

            else:
                #
                # 提示输入有误
                #
                info = "输入的控制代码有误！控制代码只能是：1~99"
                dial = InfoDialog("提示", info)
                dial.exec_()  # 进入事件循环

    def send_code(self, machine_number: int, code: int) -> None:
        """
        发送控制代码
        :param machine_number:机器编号
        :param code:控制代码
        :return:无
        """
        code = '{:04X}'.format(code)    # 十进制控制代码转十六进制

        #
        # 让子线程来完成发送控制代码任务
        #
        t = threading.Thread(target=self.controller.send_control_code,
                             args=(machine_number, code, self.append_info, self.start_polling))
        t.setDaemon(True)   # 设置为守护线程，主线程退出时子线程强制退出
        t.start()           # 子线程执行



if __name__ == '__main__':
    app = QApplication([])  # 初始化应用

    #
    # 检查是否需要验证产品密钥
    #
    login_dial = LoginDialog()
    if login_dial.check() or login_dial.exec_():
        #
        # 显示界面
        #
        main_window = MainWindow()  # 创建主窗口
        # main_window.ui.show()  # 按实际大小显示窗口
        main_window.ui.showMaximized()  # 全屏显示窗口，必须要用，不然不显示界面

        app.exec_()  # 进入事件循环
