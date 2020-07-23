from PySide2.QtCore import QObject, Signal, QThread

from Helper import Helper
from Model import Model


class WindowSignal(QObject):
    member = Signal(int)
    wind_speed = Signal(str)
    table = Signal(str)
    info = Signal(str, str)
    scanning_port = Signal(str)
    stop_polling = Signal()


message = []





