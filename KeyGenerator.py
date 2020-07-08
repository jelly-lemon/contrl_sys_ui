from PySide2.QtCore import QSize, Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QDialog, QLabel, QLineEdit, QHBoxLayout, QPushButton, QVBoxLayout, QApplication, \
    QSizePolicy

import util


class GeneratorDialog(QDialog):
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
        self.cpu_input = QLineEdit()
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

        self.ok_btn = QPushButton(text="获取产品密钥")
        self.ok_btn.clicked.connect(self.activate)
        h_box3 = QHBoxLayout()
        h_box3.addStretch()
        h_box3.addWidget(self.ok_btn)

        layout = QVBoxLayout()
        layout.addLayout(h_box1)
        layout.addLayout(h_box2)
        layout.addWidget(self.info_label)
        layout.addLayout(h_box3)

        self.setLayout(layout)

    def print_info(self, info: str):
        """
        输出提示信息
        :param info:提示信息
        :return: 无
        """
        self.info_label.setText(info)

    def init_window(self):
        """
        初始化对话框窗口
        :return: 无
        """
        self.setWindowTitle("密钥生成器")
        app_icon = QIcon("./other/key.ico")
        self.setWindowIcon(app_icon)
        self.setFixedSize(600, 400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)  # 去掉默认对话框样式左上角出现的问号

    def activate(self):
        """
        激活按钮响应事件
        :return: 无
        """
        cpu = self.cpu_input.text()
        if cpu != "":
            key = util.des_encrypt(cpu)
            if key != "":
                self.key_input.setText(key)
                self.print_info("")
            else:
                self.print_info("输入的 CPU 序列号有误！序列号仅包含数字和英文字母！")
        else:
            self.print_info("请输入 CPU 序列号！")


if __name__ == '__main__':
    app = QApplication()

    generator = GeneratorDialog()
    generator.exec_()
