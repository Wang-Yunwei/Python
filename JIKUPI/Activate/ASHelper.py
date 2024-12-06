"""
AES加密解密工具类
数据块128位
key 为16位
字符集utf-8
输出为base64
AES加密模式 为cbc
填充 pkcs7padding
"""

import base64
import os

from Crypto.Cipher import AES


class AESHelper(object):
    def __init__(self, password, iv):
        self.password=password.encode('utf-8')
        self.iv= iv.encode('utf-8')

    def pkcs7padding(self, text):
        """
        明文使用PKCS7填充
        最终调用AES加密方法时，传入的是一个byte数组，要求是16的整数倍，因此需要对明文进行处理
        :param text: 待加密内容(明文)
        :return:
        """
        bs = AES.block_size  # 16
        length = len(text)
        bytes_length = len(bytes(text, encoding='utf-8'))
        # tips：utf-8编码时，英文占1个byte，而中文占3个byte
        padding_size = length if(bytes_length == length) else bytes_length
        padding = bs - padding_size % bs
        # tips：chr(padding)看与其它语言的约定，有的会使用''
        padding_text = chr(padding) * padding
        return text + padding_text

    def pkcs7unpadding(self, text):
        """
        处理使用PKCS7填充过的数据
        :param text: 解密后的字符串
        :return:
        """
        length = len(text)
        unpadding = ord(text[length-1])
        return text[0:length-unpadding]

    def encrypt(self, content):
        """
        AES加密
        模式cbc
        填充pkcs7
        :param key: 密钥
        :param content: 加密内容
        :return:
        """
        cipher = AES.new(self.password, AES.MODE_CBC, self.iv)
        content_padding = self.pkcs7padding(content)
        encrypt_bytes = cipher.encrypt(bytes(content_padding, encoding='utf-8'))
        result = str(base64.b64encode(encrypt_bytes), encoding='utf-8')
        return result

    def decrypt(self, content):
        """
        AES解密
        模式cbc
        去填充pkcs7
        :param key:
        :param content:
        :return:
        """
        cipher = AES.new(self.password, AES.MODE_CBC, self.iv)
        encrypt_bytes = base64.b64decode(content)
        decrypt_bytes = cipher.decrypt(encrypt_bytes)
        result = str(decrypt_bytes, encoding='utf-8')
        result = self.pkcs7unpadding(result)
        return result

def get_aes():
    # AES_SECRET和AES_IV分别为密钥和偏移量
    AES_SECRET='zyhk_wkzn1234567'#秘钥必须为16的倍数
    AES_IV='sari_zyhk1234567'#偏移量，一个16 byte长度的字节
    aes_helper = AESHelper(AES_SECRET, AES_IV)
    return aes_helper