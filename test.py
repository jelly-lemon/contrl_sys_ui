import time

import serial
from serial.tools import list_ports

from util import *

if __name__ == '__main__':
    ser = serial.Serial("COM4", 9600, timeout=5)  # 开启com3口，波特率，超时
    ser.flushInput()  # 清空输入缓存（向串口输入）

    # 向控制器发送数据，允许有空格
    # '060300020027A5A7'
    send_code = get_crc16("06 03" + "00 02" + "00 27")
    ser.write(bytes.fromhex(send_code))

    time.sleep(1)  # 程序休眠 1 秒，等待控制器返回数据
    num = ser.inWaiting()  # 返回接收缓存字节数
    if num:
        data = ser.read(num)
        print(data.hex())