import datetime

from serial.tools import list_ports


def get_time() -> str:
    """
    获取当前时间，返回时间字符串，如：2020-6-12 11:13:22
    :return:时间字符串
    """
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return now_time

def get_port_list() -> list:

    port_name_list = list()
    # 获取端口列表，列表中为 ListPortInfo 对象
    port_list = list(list_ports.comports())

    num = len(port_list)

    if num > 0:
        for i in range(num):
            # 将 ListPortInfo 对象转化为 list
            port_name = list(port_list[i])
            port_name_list.append(port_name[0])

    return port_name_list



def get_crc16(str: str) -> str:
    """
    输入需要计算 CRC 校验码的十六进制字符串，如“ABCD”，然后返回带了 CRC 校验码的字符串“ABCDBF15”
    :param str:十六进制字符串
    :return:带了 CRC 校验码的字符串
    """
    str = str.replace(" ","").upper()   # 去除所有空格，转为大写
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
    str = str.replace(" ","").upper()
    print("接收数据：" + str)
    print("校验数据：" + get_crc16(str[:-4]))

    if str == get_crc16(str[:-4]):
        return True
    return False
