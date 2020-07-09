from PySide2.QtGui import Qt
from PySide2.QtWidgets import QInputDialog


class ModifyDialog(QInputDialog):
    """
    发送控制代码的对话框
    """

    def __init__(self, title: str, text: str):
        """
        设置对话框标题、显示内容
        :param title: 标题
        :param text: 内容
        """
        super().__init__()
        self.setWindowTitle(title)
        self.setLabelText(text)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)  # 去掉问号
