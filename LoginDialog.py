import os

from PySide2.QtCore import QSize
from PySide2.QtGui import QIcon, Qt
from PySide2.QtWidgets import QDialog, QLabel, QLineEdit, QHBoxLayout, QPushButton, QVBoxLayout, QSizePolicy

import util


class LoginDialog(QDialog):
    """
    登录窗口
    """

    def __init__(self):
        """
        初始化产品验证登录界面
        """
        super().__init__()

        self.init_window()

        #
        # 创建布局并添加控件，用来显示提示信息
        #
        cpu_label = QLabel("CPU 序列号：")
        self.cpu_input = QLineEdit(util.get_cpu())
        self.cpu_input.setReadOnly(True)
        h_box1 = QHBoxLayout()
        h_box1.addWidget(cpu_label)
        h_box1.addWidget(self.cpu_input)

        key_label = QLabel("  产品密钥：")
        self.key_input = QLineEdit()
        h_box2 = QHBoxLayout()
        h_box2.addWidget(key_label)
        h_box2.addWidget(self.key_input)

        policy = QSizePolicy()
        policy.setVerticalPolicy(QSizePolicy.Fixed)
        self.info_label = QLabel("")
        self.info_label.setSizePolicy(policy)

        self.ok_btn = QPushButton(text="立即激活")
        self.ok_btn.clicked.connect(self.activate)
        phone_label = QLabel("请拨打电话 15108303256 获取产品密钥")
        h_box3 = QHBoxLayout()
        h_box3.addStretch()
        h_box3.addWidget(phone_label)
        h_box3.addWidget(self.ok_btn)

        layout = QVBoxLayout()
        layout.addLayout(h_box1)
        layout.addLayout(h_box2)
        layout.addWidget(self.info_label)
        layout.addLayout(h_box3)

        self.setLayout(layout)

    def init_window(self):
        """
        初始化对话框窗口
        :return: 无
        """
        self.setWindowTitle("请输入产品密钥")
        app_icon = QIcon("./other/logo.png")
        self.setWindowIcon(app_icon)
        self.resize(QSize(600, 400))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)  # 去掉默认对话框样式左上角出现的问号

    def check(self) -> bool:
        """
        检查密钥是否合法，合法就直接进入主程序
        :return: 无
        """
        key = self.read_key()
        if key != "":
            if util.get_cpu() == util.des_descrypt(key):
                return True

        return False

    def activate(self):
        """
        激活按钮响应事件
        :return: 无
        """
        cpu = self.cpu_input.text()
        key = self.key_input.text()
        if key == "":
            self.info_label.setText("请输入产品密钥！")

        if key != "":
            if util.des_descrypt(key) == cpu:
                self.write_key(key)
                self.accept()
            else:
                self.info_label.setText("密钥有误，激活失败！")


    def write_key(self, key):
        """
        写入产品密钥到文件
        :param key:产品密钥
        :return:无
        """
        key_file_path = "./other/key.txt"
        key_file = open(key_file_path, "w+")  # 没有文件会自动创建
        key_in_file = key_file.readline()  # 先读取

        #
        # 和传进来的 key 进行比较
        # 如果一样，则不写入
        # 不一样则覆盖写入
        #
        if key_in_file != key:
            key_file.write(key)

    def read_key(self) -> str:
        """
        读取产品密钥
        :return:产品密钥字符串
        """
        key_file_path = "./other/key.txt"  # 先判断有没有文件
        if os.path.exists(key_file_path):
            key_file = open(key_file_path, "r")
            return key_file.readline()  # 先读取

        return ""