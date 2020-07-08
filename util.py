import ctypes
import datetime
import inspect
import wmi
from pyDes import des, CBC, PAD_PKCS5
import binascii

from serial.tools import list_ports

def get_time() -> str:
    """
    获取当前时间，返回时间字符串，如：2020-06-12 11:13:22
    :return:时间字符串
    """
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return now_time

def get_port_list() -> list:
    """
    获取串口列表
    :return: 串口列表
    """
    port_name_list = []
    port_list = list(list_ports.comports())  # 获取端口列表，列表中为 ListPortInfo 对象
    num = len(port_list)
    if num > 0:
        for i in range(num):
            port_name = list(port_list[i])  # 将 ListPortInfo 对象转化为 list
            port_name_list.append(port_name[0])

    return port_name_list

def get_crc16(str: str) -> str:
    """
    输入需要计算 CRC 校验码的十六进制字符串，如“ABCD”，然后返回带了 CRC 校验码的字符串“ABCDBF15”
    :param str:十六进制字符串
    :return:带了 CRC 校验码的字符串
    """
    str = str.replace(" ", "").upper()  # 去除所有空格，转为大写
    data = bytearray.fromhex(str)
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for i in range(8):
            if ((crc & 1) != 0):
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    crc_code = hex(((crc & 0xff) << 8) + (crc >> 8))[2:]
    crc_code = "{:#06X}".format(int(crc_code, 16))[2:]
    result = str + crc_code

    return result.upper()

def is_crc16(str: str) -> bool:
    """
    用 CRC16 判断接收到的数据是否正确
    :param str: 接收到的数据，带 CRC16 校验码
    :return: 如果正确返回 True，否则返回 False
    """
    str = str.replace(" ", "").upper()
    if str == get_crc16(str[:-4]):
        return True

    return False


def stop_thread(thread):
    """
    立即停止该线程
    :param thread:需要停止的线程
    :return: 无
    """
    tid = thread.ident
    exctype = SystemExit

    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def get_cpu() -> str:
    """
    获取 CPU 的序列号
    :return: CPU 的序列号
    """
    c = wmi.WMI()
    return c.Win32_Processor()[0].ProcessorId



def des_encrypt(s: str) -> str:
    """
    DES 加密
    :param s: 原始字符串
    :return: 加密后字符串，16进制
    """
    secret_key = KEY
    iv = secret_key
    k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    en = k.encrypt(s, padmode=PAD_PKCS5)
    en = binascii.b2a_hex(en)
    en = str(en, "utf-8").upper()
    return en

# 秘钥
KEY = 'abcJRIDO'

def des_descrypt(s: str) -> str:
    """
    DES 解密
    :param s: 加密后的字符串，16进制
    :return:  解密后的字符串
    """
    secret_key = KEY
    iv = secret_key
    k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    de = k.decrypt(binascii.a2b_hex(s), padmode=PAD_PKCS5)
    try:
        de = str(de, 'utf-8').upper()
    except UnicodeDecodeError:
        return ""

    return de