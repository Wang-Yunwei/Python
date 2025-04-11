# -*- coding: utf-8 -*- 
# @Time : 2022/5/17 9:09 
# @Author : ZKL 
# @File : GPSCompute.py
'''
机库GPS检测，并将检测到的GPS信息进行推送
经度，纬度
'''

import binascii
import threading
import time
import struct

import USBDevice
import BASEUtile.HangarState as HangarState
from BASEUtile.logger import Logger
from SATA.SATACom import JKSATACOM
import USBDevice.USBDeviceConfig as USBDeviceConfig


# from WFCharge.WFState import WFState


class GPSInfo():
    '''
    获取气象信息
    '''

    # def __init__(self,state,log):
    #     self.state=state
    #     self.logger=log
    #     self.wait_time=30#等待30秒获取一次GPS数据

    def __init__(self, log):
        # self.state = state
        self.logger = log
        self.wait_time = 5  # 等待30秒获取一次GPS数据
        # self.comconfig = comconfig

    def hex_to_float(self, h):
        '''
        将十六进制转换为单精度浮点数
        :param h:
        :return:
        '''
        i = int(h, 16)
        return struct.unpack('<f', struct.pack('<I', i))[0]

    def start_get_gps(self):
        # 启动获取GPS信息的线程
        statCom_gps = JKSATACOM(USBDeviceConfig.get_serial_usb_gps(), USBDeviceConfig.get_serial_bps_gps(),
                                USBDeviceConfig.get_serial_timeout_gps(),
                                self.logger, None)
        gps_longitude = 0.0  # 推送的经度
        gps_latitude = 0.0  # 推送的纬度
        while True:
            try:
                if statCom_gps is None:
                    statCom_gps = JKSATACOM(USBDeviceConfig.get_serial_usb_gps(), USBDeviceConfig.get_serial_bps_gps(),
                                            USBDeviceConfig.get_serial_timeout_gps(),
                                            self.logger, None)
                # 发送天气操作命令
                commond_long = "07 03 00 02 00 02 65 AD"  # 经度
                commond_latitude = "07 03 00 05 00 02 D4 6C"  # 纬度
                statCom_gps.engine.Open_Engine()  # 打开串口
                statCom_gps.engine.Send_data(bytes.fromhex(commond_long))
                # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
                time.sleep(1)
                result_long = statCom_gps.engine.read_all_data()  # 读取结果,读取9个字节
                statCom_gps.engine.Close_Engine()
                time.sleep(5)
                statCom_gps.engine.Open_Engine()  # 打开串口
                statCom_gps.engine.Send_data(bytes.fromhex(commond_latitude))
                # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
                time.sleep(1)
                result_latitude = statCom_gps.engine.read_all_data()  # 读取结果,读取9个字节
                statCom_gps.engine.Close_Engine()

                if result_long == b'' or result_latitude == b'':
                    # time.sleep(30)
                    statCom_gps = None
                    print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}gps串口获取值为空")
                    continue
                # if len(result_long) == 0:
                #    self.state.set_GPS(f"{gps_longitude},{gps_latitude}")
                # else:
                if len(result_long) > 0:
                    data_long = binascii.b2a_hex(result_long[3:7]).decode('ascii')
                    data_latitude = binascii.b2a_hex(result_latitude[3:7]).decode('ascii')
                    gps_longitude = self.hex_to_float(data_long)
                    gps_latitude = self.hex_to_float(data_latitude)
                    self.logger.get_log().info(f"gps---经纬度返回值为：{gps_longitude},{gps_latitude}")
                    if gps_longitude < 10 or gps_latitude < 1:
                        continue
                    # print(f"gps---经纬度返回值为：{self.hex_to_float(data_long)},{self.hex_to_float(data_latitude)}")
                    HangarState.set_gps_value(f"{gps_longitude},{gps_latitude}")
                    # print(self.state.getHangerState())
                    # pass
                    # print(int(windspeed,16)/10,winddir,int(rainnum,16))
                time.sleep(self.wait_time)  # 有此操作，信号获取数据稳定
            except Exception as e:
                print(f"gps异常{e}")
                time.sleep(self.wait_time)
                statCom_gps = None
                continue

    def start_get_gps_RTK(self):
        # 启动获取GPS信息的线程
        statCom_gps = JKSATACOM(USBDeviceConfig.get_serial_usb_gps(), USBDeviceConfig.get_serial_bps_gps(),
                                USBDeviceConfig.get_serial_timeout_gps(),
                                self.logger, None)
        gps_longitude = 0.0  # 推送的经度
        gps_latitude = 0.0  # 推送的纬度
        while True:
            try:
                if statCom_gps is None:
                    statCom_gps = JKSATACOM(USBDeviceConfig.get_serial_usb_gps(),
                                            USBDeviceConfig.get_serial_bps_gps(), USBDeviceConfig.get_serial_timeout_gps(),
                                            self.logger, None)
                statCom_gps.engine.Open_Engine()  # 打开串口
                time.sleep(1)
                data_result = statCom_gps.engine.read_lines()  # 确认读取一行数据还是100行数据
                # data_result = statCom_gps.engine.read_all_data()  # 读取结果,读取9个字节
                self.logger.get_log().info(f"获取到的结果GPS数据结果为{data_result}")
                statCom_gps.engine.Close_Engine()
                if len(data_result) > 0:
                    # gps_longitude = (float)(data_result[0].split(b',')[4]) / 100  # 东经
                    # gps_latitude = (float)(data_result[0].split(b',')[2]) / 100  # 北纬
                    gps_longitude = self.decimal_degrees(*self.dm(float(data_result[0].split(b',')[4])))  # 东经
                    gps_latitude = self.decimal_degrees(*self.dm(float(data_result[0].split(b',')[2])))  # 北纬
                    self.logger.get_log().info(f"gps---经纬度返回值为：{gps_longitude},{gps_latitude}")
                    if gps_longitude < 10 or gps_latitude < 1:
                        continue
                    # print(f"gps---经纬度返回值为：{self.hex_to_float(data_long)},{self.hex_to_float(data_latitude)}")
                    HangarState.set_gps_value(f"{gps_longitude - 0.00001},{gps_latitude + 0.00001}")
                    # print(self.state.getHangerState())
                    # pass
                    # print(int(windspeed,16)/10,winddir,int(rainnum,16))
                time.sleep(self.wait_time)  # 有此操作，信号获取数据稳定
            except Exception as e:
                print(f"gps异常---{e}")
                time.sleep(self.wait_time)
                statCom_gps = None
                continue

    def dm(self, x):
        degrees = int(x) // 100
        minutes = x - 100 * degrees

        return degrees, minutes

    def decimal_degrees(self, degrees, minutes):
        return degrees + minutes / 60

        # print(decimal_degrees(*dm(3648.5518)))


if __name__ == "__main__":
    pass
    # logger = Logger(__name__)  # 日志记录
    # # wfcstate = WFState()
    # # hangstate = HangarState(wfcstate, None)
    # conini = ConfigIni()
    # comconfig = USBDeviceConfig(conini)
    # ws = GPSInfo(logger, comconfig)
    # # #启用一个线程
    # th = threading.Thread(target=ws.start_get_gps_RTK(), args=())
    # th.start()
    # th.join()  # 等待子进程结束
