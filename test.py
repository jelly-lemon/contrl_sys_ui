from pyDes import des, CBC, PAD_PKCS5
import binascii

# 秘钥
KEY = 'abcJRIDO'

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
    de = str(de, 'utf-8').upper()
    return de