import time

from PySide2.QtCore import QThread

import util
from WindowSignal import WindowSignal


class CheckWorker(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.signal = WindowSignal()
        self.signal.scanning_port.connect(parent.update_port)
        self.last_port_list = None

    def run(self):
        while True:
            port_list = util.get_port_list()
            if self.last_port_list != port_list:
                self.signal.scanning_port.emit(str(port_list))
                self.last_port_list = port_list
            time.sleep(0.2)