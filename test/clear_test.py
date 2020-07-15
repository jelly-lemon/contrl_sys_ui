#!/usr/bin/env python
# encoding: utf-8
'''
#-------------------------------------------------------------------#
#                   CONFIDENTIAL --- CUSTOM STUDIOS                 #     
#-------------------------------------------------------------------#
#                                                                   #
#                   @Project Name : contrl_sys_ui                 #
#                                                                   #
#                   @File Name    : clear_test.py                      #
#                                                                   #
#                   @Programmer   : Adam                            #
#                                                                   #  
#                   @Start Date   : 2020/7/15 10:13                 #
#                                                                   #
#                   @Last Update  : 2020/7/15 10:13                 #
#                                                                   #
#-------------------------------------------------------------------#
# Classes:                                                          #
#                                                                   #
#-------------------------------------------------------------------#
'''
from PySide2.QtGui import Qt
from PySide2.QtWidgets import QApplication, QTextEdit, QAction

def my_func():
    print("hello")

if __name__ == '__main__':
    app = QApplication()

    edit = QTextEdit()
    edit.setContextMenuPolicy(Qt.ActionsContextMenu)


    # 具体菜单项
    send_option = QAction(edit)
    send_option.setText("清除内容")
    send_option.triggered.connect(edit.clear)  # 点击菜单中的“发送控制代码”执行的函数

    # tableView 添加具体的右键菜单
    edit.addAction(send_option)


    edit.show()


    app.exec_()