import time

import serial

if __name__ == '__main__':
    ser = serial.Serial("COM3", 9600, timeout=5)  # 开启com3口，波特率，超时
    ser.flushInput()  # 清空输入缓存（向控制器输入）

    # 向控制器发送数据
    ser.write(bytes.fromhex("010300000001840A"))

    time.sleep(1)  # 程序休眠 1 秒，等待控制器返回数据
    num = ser.inWaiting()  # 返回接收缓存字节数
    if num:
        data = ser.read(num)
        print(data.hex())

