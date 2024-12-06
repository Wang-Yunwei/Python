# -*- coding: utf-8 -*- 
# @Time : 2022/3/10 22:43 
# @Author : ZKL 
# @File : SerialHelp.py

import serial
import binascii


class SerialHelper(object):
    def __init__(self, Port="/dev/ttyUSBCharge", BaudRate="115200", ByteSize="8", Parity="N", Stopbits="1",thresholdValue=64):
        self.l_serial = None
        self.alive = False
        self.port = Port
        self.baudrate = BaudRate
        self.bytesize = ByteSize
        self.parity = Parity
        self.stopbits = Stopbits
        self.thresholdValue = thresholdValue #接收至少多少个字符才算接收到信息
        self.receive_data = ""
        self.value=""

    def start(self):
        self.l_serial = serial.Serial()
        self.l_serial.port = self.port
        self.l_serial.baudrate = self.baudrate
        self.l_serial.bytesize = int(self.bytesize)
        self.l_serial.parity = self.parity
        self.l_serial.stopbits = int(self.stopbits)
        self.l_serial.timeout = 1

        try:
            self.l_serial.open()
            if self.l_serial.isOpen():
                self.alive = True
        except:
            self.alive = False

    def stop(self):
        self.alive = False
        if self.l_serial.isOpen():
            self.l_serial.close()

    def read(self):
        self.value="" #必须赋值为空，否则不消除对象实例的情况下，数据会累积
        while self.alive:
            #print("alive")
            try:
                number = self.l_serial.inWaiting()
                if number:
                    self.receive_data += self.l_serial.read(number).decode("ascii")
                    if self.thresholdValue <= len(self.receive_data):
                        self.value+=self.receive_data
                        #print(self.receive_data)
                        self.receive_data = ""
            except Exception as ex:
                pass

    def write(self, data, isHex=False):
        if self.alive:
            if self.l_serial.isOpen():
                if isHex:
                    data = data.replace(" ", "").replace("\n", "")
                    data = binascii.unhexlify(data)
                self.l_serial.write(data)


if __name__ == '__main__':
    import threading

    ser = SerialHelper()
    ser.start()
    ser.write("DroneOff".encode('ascii'), isHex=False)
    value1=""
    thread_read = threading.Thread(target=ser.read)
    thread_read.setDaemon(False)
    thread_read.start()
    import time
    time.sleep(30)
    ser.stop()
    print("********************************")
    print(ser.value)