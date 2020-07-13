#!/usr/bin/env python
# encoding: utf-8
'''
#-------------------------------------------------------------------#
#                   CONFIDENTIAL --- CUSTOM STUDIOS                 #     
#-------------------------------------------------------------------#
#                                                                   #
#                   @Project Name : contrl_sys_ui                 #
#                                                                   #
#                   @File Name    : send_test.py                      #
#                                                                   #
#                   @Programmer   : Adam                            #
#                                                                   #  
#                   @Start Date   : 2020/7/13 19:13                 #
#                                                                   #
#                   @Last Update  : 2020/7/13 19:13                 #
#                                                                   #
#-------------------------------------------------------------------#
# Classes:                                                          #
#                                                                   #
#-------------------------------------------------------------------#
'''
import time

import serial

from util import get_crc16, is_crc16

if __name__ == '__main__':
    ser = serial.Serial('COM4', 9600, timeout=5)  # 开启com3口，波特率，超时
    ser.flushInput()  # 清空输入缓存（向串口发送）

    #
    # 向控制器发送数据
    #
    collector_addr = '01'
    option = '03'
    start = '0000'
    number = '0001'
    send_data = get_crc16(collector_addr + option + start + number)
    ser.write(bytes.fromhex(send_data))
    time.sleep(0.1)  # 程序休眠 x 秒，等待控制器返回数据

    #
    # 返回接收缓存字节数
    #
    num = ser.inWaiting()
    if num:
        data = ser.read(num)
        if is_crc16(data.hex()):
            print(data.hex().upper())
