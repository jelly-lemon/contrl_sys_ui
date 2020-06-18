import datetime

def get_time() -> str:
    """
    获取当前时间，返回时间字符串，如：2020-6-12 11:13:22
    :return:时间字符串
    """
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return now_time