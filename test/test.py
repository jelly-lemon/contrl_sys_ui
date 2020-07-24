import os
import sys

import PySide2.QtCore

if __name__ == '__main__':
    path = os.getcwd() + r"\log\wind_speed"
    if os.path.exists(path):
        os.system("explorer.exe %s" % path)
    else:
        print(path, "不存在")



