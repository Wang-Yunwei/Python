# -*- coding: utf-8 -*- 
# @Time : 2023/3/27 11:34 
# @Author : ZKL 
# @File : COMTESTUtils.py
import time

import serial


def hexShow(self, argv):
    '''
    十六进制去除特殊字符
    '''
    hLen = len(argv)
    out_s = ''
    for i in range(hLen):
        out_s = out_s + '{:02X}'.format(argv[i]) + ' '
    return out_s

commond=''

comstate = serial.Serial(
    timeout=1,
    port='',
    baudrate=9600,
    parity=serial.PARITY_EVEN,  # 可以不写
    stopbits=serial.STOPBITS_ONE,  # 可以不写
    bytesize=serial.EIGHTBITS)  # 可以不写

comstate.write(bytes.fromhex(commond))
time.sleep(0.1)
count = comstate.inWaiting()
# 数据的接收
# 可以根据实际情况做修改，比如：当没有响应传回时，等待+判断
result = b''
if count == 0:
    print('没有响应传回1')
if count > 0:
    result = comstate.read(count)
    result = bytes.fromhex(hexShow(result))
comstate.flushInput()  # 清除缓存区数据。当代码在循环中执行时，不加这句代码会造成count累加
comstate.close()