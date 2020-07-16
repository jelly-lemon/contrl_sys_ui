#!/usr/bin/env python
# encoding: utf-8
'''
#-------------------------------------------------------------------#
#                   CONFIDENTIAL --- CUSTOM STUDIOS                 #     
#-------------------------------------------------------------------#
#                                                                   #
#                   @Project Name : contrl_sys_ui                 #
#                                                                   #
#                   @File Name    : queue_test.py                      #
#                                                                   #
#                   @Programmer   : Adam                            #
#                                                                   #  
#                   @Start Date   : 2020/7/16 9:53                 #
#                                                                   #
#                   @Last Update  : 2020/7/16 9:53                 #
#                                                                   #
#-------------------------------------------------------------------#
# Classes:                                                          #
#                                                                   #
#-------------------------------------------------------------------#
'''
import queue
import threading

from PySide2.QtCore import QObject, QThread, Signal


class MainWindow(QObject):
    def append_info(self, data):
        print("append_info:", data)

    def update_table(self, data):
        print("update_table:", data)

    def update_member(self, data):
        print("update_member:", data)


class WorkerThread(QThread):
    def __init__(self, parent=None):
        super().__init__()
        self.signal = Communicate()
        self.signal.update_table.connect(parent.update_table)
        self.signal.update_member.connect(parent.update_member)

    def run(self):
        self.signal.update_table.emit("[角度，1]")
        # while True:
        #     if q.empty() is False:
        #         cmd = q.get_nowait()
        #         print(cmd)
        #         if cmd.find("get_table") != -1:
        #             self.get_table()
        #         elif cmd.find("get_member") != -1:
        #             self.get_member()


    def get_table(self):
        print("子线程 get_table")
        self.signal.update_table.emit("[角度，1]")

    def get_member(self):
        print("子线程 get_member")
        self.signal.update_member.emit("19")




class Communicate(QObject):
    update_table = Signal(str)
    update_member = Signal(str)

#
# 全局变量
#
q = queue.Queue()

if __name__ == '__main__':

    window = MainWindow()

    workder = WorkerThread(window)
    workder.start()

    while True:
        cmd = input("Input cmd:")
        q.put(cmd)



