import time

from PySide2.QtCore import QThread
from serial import SerialException

from Model import Model
from WindowSignal import WindowSignal, message


class SerialWorker(QThread):
    def __init__(self, parent):
        super().__init__()
        self.signal = WindowSignal()
        self.model = Model()
        self.work = False  # 默认不工作

        #
        # 绑定槽函数
        #
        self.signal.member.connect(parent.update_member)
        self.signal.wind_speed.connect(parent.update_wind_speed)
        self.signal.table.connect(parent.update_table)
        self.signal.info.connect(parent.append_info)
        self.signal.stop_polling.connect(parent.stop_polling)

    def run(self):
        while True:
            if len(message) != 0:
                msg = message.pop(0)
                cmd = msg['cmd']
                if self.work:
                    try:
                        if cmd == "member":
                            self.get_member()
                        elif cmd == "wind_speed":
                            self.get_wind_speed()
                        elif cmd == "table":
                            self.get_table()
                        elif cmd == "one_key":
                            self.one_key(msg["option"])
                        elif cmd == "send_control_code":
                            self.send_control_code(msg['machine_number'], msg['code'])
                    except SerialException:
                        self.emit_info("端口被拔出！", "red")
                        self.work = False
                        self.signal.stop_polling.emit()

                if cmd == "update_serial":
                    self.update_serial(msg['com_port'], msg['baud_rate'], msg['collector_addr'])
                elif cmd == 'close_serial':
                    self.model.close_ser()


            else:
                time.sleep(0.1)

    def update_serial(self, com_port, baud_rate, collector_addr):
        if self.model.update_serial(com_port, baud_rate, collector_addr) is False:
            self.emit_info("无法与串口建立连接，请检查端口号、波特率、数采地址是否正确，数采是否接电", "red")
            self.signal.stop_polling.emit()
            self.work = False

        else:
            self.emit_info("与串口 %s 建立通信" % com_port, 'green')
            self.work = True

    # def update_serial_again(self, com_port, baud_rate, collector_addr):
    #     """
    #     再次尝试更新串口，不能用递归，不然可能会无限递归下去
    #     :param com_port:
    #     :param baud_rate:
    #     :param collector_addr:
    #     :return:
    #     """
    #     message.append({'cmd': 'update_serial', 'com_port': com_port, 'collector_addr': collector_addr,
    #                     'baud_rate': baud_rate})

    #
    # 以下函数有读 or 写操作
    #
    def send_control_code(self, machine_number, code):
        if self.model.send_control_code(machine_number, code):
            self.emit_info("向 %s 号机器发送控制代码成功：%s" % (machine_number, code), 'green')
        else:
            self.emit_info("向 %s 号机器发送控制代码失败" % machine_number, 'red')

    def one_key(self, cmd):
        if self.model.one_key(cmd):
            self.emit_info("%s成功" % cmd, 'green')
        else:
            self.emit_info("%s失败，无法向串口读取或写入数据" % cmd, 'red')

    def get_member(self):
        n = self.model.get_member()
        if n == -1:
            self.emit_info("获取成员数失败！", "red")
        else:
            self.signal.member.emit(n)

    def get_wind_speed(self):
        wind_speed = self.model.wind_speed()
        if wind_speed == -1:
            self.emit_info("获取风速失败！", "red")
        else:
            self.signal.wind_speed.emit(str(wind_speed))

    def get_table(self):
        table_data = self.model.get_table_data()
        if table_data is not None:
            self.signal.table.emit(str(table_data))
            self.emit_info("表格数据更新成功")
        else:
            self.emit_info("表格数据获取失败！", 'red')

    def emit_info(self, text: str, color: str = 'black'):
        """
        输出信息框追加消息
        :param text: 文字
        :param color: 颜色
        :return: 无
        """
        self.signal.info.emit(text, color)
