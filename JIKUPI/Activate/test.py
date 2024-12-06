#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 2023-02-20

from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

code = 'utf-8'
offset = b'python1234567890'  # 字节
mykey = 'my_python_key_20230220ABC_ComeOn'
key = mykey.encode(code)#秘钥编码
mode = AES.MODE_CBC


# 加16位
def addTo16(txt):
    if len(txt.encode(code)) % 16:
        add = 16 - (len(txt.encode(code)) % 16)
    else:
        add = 0
    txt = txt + ('\0' * add)
    return txt.encode(code)


# 解密数据函数
def decryptData(text):
    cryptor = AES.new(key, mode, offset)
    plain_text = cryptor.decrypt(a2b_hex(text))
    return bytes.decode(plain_text).rstrip('\0')


# 加密数据函数
def encryptData(text):
    # Incorrect AES key length (15 bytes)
    text = addTo16(text)
    cryptos = AES.new(key, mode, offset)

    cipher_text = cryptos.encrypt(text)
    return b2a_hex(cipher_text)


# 程序入口
if __name__ == '__main__':
    # 加密
    text = "My Name is Python"
    encryptStr = encryptData(text)
    # 解密
    decryptStr = decryptData(encryptStr)
    print("加密串数据:", encryptStr)
    print("解密串数据:", decryptStr)