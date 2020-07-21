import datetime
import time

from PySide2.QtCore import QThread, QObject, Signal, Slot
from PySide2.QtWidgets import QApplication, QInputDialog, QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel



class MyInputDialog(QDialog):
    def __init__(self):
        super().__init__()

        #
        # 输入框
        #
        self.input = QLineEdit()


        #
        # label 标签
        #
        self.label_1 = QLabel()

        #
        # label_2
        #
        self.label_2 = QLabel()

        #
        # 发送按钮
        #
        self.ok_btn = QPushButton(text="发送")
        self.ok_btn.clicked.connect(self.submit)

        layout = QVBoxLayout()
        layout.addWidget(self.input)
        layout.addWidget(self.label_1)
        layout.addWidget(self.label_2)
        layout.addWidget(self.ok_btn)
        self.setLayout(layout)

    @Slot(str, str)
    def update_label1(self, result, other):
        self.label_1.setText("更新标签成功：" + result + other)

    @Slot(str)
    def update_label2(self, result):
        self.label_2.setText("更新标签成功：" + result)

    def submit(self):
        msg = self.input.text()
        message.append(msg)




class Worker(QThread):
    def __init__(self, parent):
        super().__init__()
        self.signals = Communicate()
        self.signals.label_singal.connect(parent.update_label1)
        self.signals.table_singal.connect(parent.update_label2)

    def run(self):
        while True:
            print("执行子线程")
            if len(message) != 0:
                msg = message.pop(0)
                if msg == "label_1":
                    self.get_label1()
                elif msg == "label_2":
                    self.get_label2()
            else:
                time.sleep(0.1)

    def get_label1(self):
        #
        # 模拟耗时操作，去获取数据
        #
        self.signals.label_singal.emit(get_time(), "第二个参数")

    def get_label2(self):
        self.signals.table_singal.emit(get_time())



class Communicate(QObject):
    label_singal = Signal(str, str)
    table_singal = Signal(str)

def get_time() -> str:
    """
    获取当前时间，返回时间字符串，如：2020-06-12 11:13:22
    :return:时间字符串
    """
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return now_time

#
# 消息队列，全局变量
#
message = []


if __name__ == '__main__':
    app = QApplication()


    #
    # 显示输入框
    #
    dial = MyInputDialog()
    dial.show()

    worker = Worker(dial)
    worker.start()

    app.exec_()




