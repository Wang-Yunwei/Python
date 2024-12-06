# -*- coding: utf-8 -*- 
# @Time : 2023/10/26 14:10 
# @Author : ZKL 
# @File : ModbusUtils.py
'''
Modbus CRC校验工具
'''
# CRC-16-MODBUS
def calculate_crc16(data: bytes) -> int:
    # 初始化crc为0xFFFF
    crc = 0xFFFF

    # 循环处理每个数据字节
    for byte in data:
        # 将每个数据字节与crc进行异或操作
        crc ^= byte

        # 对crc的每一位进行处理
        for _ in range(8):
            # 如果最低位为1，则右移一位并执行异或0xA001操作(即0x8005按位颠倒后的结果)
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            # 如果最低位为0，则仅将crc右移一位
            else:
                crc = crc >> 1

    # 返回最终的crc值
    new_crc=f"{crc:04X}"
    new_crc=new_crc[2:]+" "+new_crc[:2]
    return new_crc


# from binascii import *
# import crcmod
#
#
# # 生成CRC16-MODBUS校验码
# def crc16Add(read):
#     crc16 = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)
#     data = read.replace(" ", "")  # 消除空格
#     readcrcout = hex(crc16(unhexlify(data))).upper()
#     str_list = list(readcrcout)
#     # print(str_list)
#     if len(str_list) == 5:
#         str_list.insert(2, '0')  # 位数不足补0，因为一般最少是5个
#     crc_data = "".join(str_list)  # 用""把数组的每一位结合起来  组成新的字符串
#     # print(crc_data)
#     read = read.strip() + ' ' + crc_data[4:] + ' ' + crc_data[2:4]  # 把源代码和crc校验码连接起来
#     # print('CRC16校验:', crc_data[4:] + ' ' + crc_data[2:4])
#     print(read)
#     return read


# if __name__ == '__main__':
#     crc16Add("01 06 00 66 00 C8 00 00")

if __name__ == '__main__':

    # 测试数据
    test_data = bytes.fromhex("0D 06 00 00 01 04")
    # test_data = bytes("Hello, world!", encoding='utf-8')

    # 计算CRC-16校验码
    crc16 = calculate_crc16(test_data)

    # 输出校验码值
    print(f'CRC-16校验码值为: 0x{crc16}')
