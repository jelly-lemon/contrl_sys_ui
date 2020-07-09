from PySide2.QtGui import Qt
from PySide2.QtWidgets import QDialog, QLabel, QVBoxLayout


class InfoDialog(QDialog):
    """
    常规提示对话框
    """

    def __init__(self, title: str, text: str):
        """
        设置标题、内容
        :param title: 标题
        :param text: 内容
        """
        super().__init__()
        self.setWindowTitle(title)

        #
        # 创建布局并添加控件，用来显示提示信息
        #
        label = QLabel(text)
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)  # 去掉默认对话框样式左上角出现的问号
