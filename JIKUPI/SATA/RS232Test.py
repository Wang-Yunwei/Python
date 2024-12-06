# -*- coding: utf-8 -*- 
# @Time : 2023/3/27 11:41 
# @Author : ZKL 
# @File : RS232Test.py
import logging

import serial
import time
from threading import RLock
from BASEUtile.logger import Logger

lock = RLock()

class RS232_Device():
    connected = False
    connection = None
    busy = False

    def __init__(self, device_name=None, com=None, port=19200,
                 request=False, hello=None, answer=None, termin=None,
                 timesleep=0.2):
        '''
        返回一个com连接对象
        :param device_name: 设置设备名称
        :param com: 设置com口
        :param request: 设置是否握手:若 Ture,connected 握手后会改变为True
        :param hello: 设置握手发送数据
        :param answer: 设置握手返回数据
        :param termin: 命令 自动加入结束符
        '''
        self.com = com
        self.device_name = device_name
        self.port = port
        self.request = request
        self.hello = hello
        self.answer = answer
        self.termin = termin
        self.timesleep = timesleep

    def __repr__(self):
        return '<%s(%s)><connected? -%s>' % (self.device_name, self.com, self.connected)

    def connect(self):

        if not self.busy:
            try:
                self.connection = serial.Serial(self.com, self.port, bytesize=8, parity='N', stopbits=1, timeout=1)
                if self.request == False:
                    self.connected = True
                print('%s 打开成功,开启端口为%s,波特率为%s' % (self.device_name, self.com, self.port))
            except serial.serialutil.SerialException as e:
                self.busy = False
                print('%s 打开失败,端口%s已被开启或无此端口,%s' % (self.device_name, self.com, str(e)))

        if all((self.request, self.connection)):
            if self.answer in self.query(self.hello).encode('utf-8'):
                self.connected = True
                print('%s 握手成功' % self.device_name)
            else:
                self.connected = False
                print('%s 通讯失败,请确认端口连接及设备状态！' % self.device_name)

        return self.connected

    def open(self):
        if self.connection:
            try:
                self.connection.open()
                print('%s 打开成功,开启端口为%s,波特率为%s' % (self.device_name, self.com, self.port))
            except serial.serialutil.SerialException as e:
                self.busy = False
                print('%s 打开失败,端口%s已被开启或无此端口,%s' % (self.device_name, self.com, str(e)))

    def close(self):
        if self.busy:
            self.connection.close()
            print('%s 通讯成功关闭!' % self.device_name)
            self.busy = False
            self.connected = False

    def get_in_waiting(self):
        time.sleep(self.timesleep)
        return self.connection.read(self.connection.in_waiting)

    def _query(self, value):
        with lock:
            self.get_in_waiting()
            if self.termin:
                value += self.termin
            self.connection.write(value.encode())
            time.sleep(0.05)
            data = self.get_in_waiting().decode('utf-8', 'ignore')
            self.busy = False
            return data

    def query(self, value):
        if self.busy:
            time.sleep(0.05)
            return self.query(value)
        return self._query(value)

    def _write(self, value):
        with lock:
            self.busy = True
            self.get_in_waiting()
            if self.termin:
                value += self.termin
            self.connection.write(value.encode())
            time.sleep(0.05)
            self.busy = False

    def write(self, value):
        if self.busy:
            time.sleep(0.05)
            return self.write(value)
        return self._write(value)
if __name__=="__main__":
    rs232=RS232_Device(device_name='测试',com='',port=9600)
    rs232.connect()
    rs232.write('')
    rs232.query(None)

