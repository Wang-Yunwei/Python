# import sys
# import threading
# import time
import serial
import binascii


class SerialHelper(object):
    def __init__(self, Port="/dev/ttyUSBCharge", BaudRate="115200", ByteSize="8", Parity="N", Stopbits="1"):
        self.l_serial = None
        self.alive = False
        self.port = Port
        self.baudrate = BaudRate
        self.bytesize = ByteSize
        self.parity = Parity
        self.stopbits = Stopbits
        self.thresholdValue = 70
        self.receive_data = ""
        self.value=""

    def start(self):
        self.l_serial = serial.Serial()
        self.l_serial.port = self.port
        self.l_serial.baudrate = self.baudrate
        self.l_serial.bytesize = int(self.bytesize)
        #self.l_serial.parity = self.parity
        #self.l_serial.stopbits = int(self.stopbits)
        self.l_serial.parity = serial.PARITY_ODD
        self.l_serial.timeout = 10

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
        while self.alive:
            try:
                number = self.l_serial.inWaiting()
                if number:
                    self.receive_data += self.l_serial.read(number).decode("ascii")
                    if self.thresholdValue <= len(self.receive_data):
                        #self.value+=self.receive_data
                        print(self.receive_data)
                        self.receive_data = ""
            except Exception as ex:
                print(ex)
                pass

    def write(self, data, isHex=False):
        if self.alive:
            if self.l_serial.isOpen():
                if isHex:
                    data = data.replace(" ", "").replace("\n", "")
                    data = binascii.unhexlify(data)
                self.l_serial.write(data)


if __name__ == '__main__':
    import math
    #d=math.sqrt(35.9*35.9+24*24)
    print(f"{2*math.atan(6.29/9)*(180/math.pi)}")
    print(f"{math.tan((82.9/2)*0.0174533)*9}")