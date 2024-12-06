# -*- coding: utf-8 -*- 
# @Time : 2022/5/17 9:09 
# @Author : ZKL 
# @File : GPSCompute.py
'''
机库警报控制
'''

import binascii
import threading
import time
import struct

from AirCondition.AirConditionState import AirCondtionState
from BASEUtile.HangerState import HangerState
from BASEUtile.logger import Logger
from ConfigIni import ConfigIni
from SATA.SATACom import JKSATACOM
from USBDevice.USBDeviceConfig import USBDeviceConfig
from WFCharge.WFState import WFState


class AlarmController():
    '''
    获取天气(凤向，风速，温度，湿度，降雨，雨量，烟感)信息
    通过RS485协议获取
    '''
    # def __init__(self,state,log):
    #     self.state=state
    #     self.logger=log
    #     self.wait_time=30#等待30秒获取一次GPS数据

    def __init__(self,state,log,configini):
        self.state = state
        self.logger = log
        self.wait_time = 10  # 等待3秒获取一次气象信息，并推送给到web平台
        self.configini=configini
        self.comconfig=USBDeviceConfig(self.configini)

    def hex_to_float(self,h):
        '''
        将十六进制转换为单精度浮点数
        :param h:
        :return:
        '''
        i = int(h, 16)
        return struct.unpack('<f', struct.pack('<I', i))[0]

    def get_num_f_h(self,h_value):
        '''
        十六进制补码取反，入参为十六进制数
        :return:结果为十进制数
        '''
        num = int(h_value, 16)
        if (num & 0x8000 == 0x8000):
            num = -((num - 1) ^ 0xFFFF)
        return num

    def hexShow(self,argv):
        '''
        十六进制去除特殊字符
        '''
        hLen = len(argv)
        out_s=''
        for i in range(hLen):
            out_s = out_s + '{:02X}'.format(argv[i]) + ' '
        return out_s
    def start_alarm(self):
        '''
        打开警报
        '''
        statCom_wea = JKSATACOM(self.state, self.comconfig.get_device_info_weather(), self.comconfig.get_bps_weather(),
                                self.comconfig.get_timeout_weather(),
                                self.logger, None)
        # 打开警报命令
        commond_start_alarm = "0C 06 00 0D 00 00 19 14"  #
        time.sleep(2)
        statCom_wea.engine.Open_Engine()  # 打开串口
        statCom_wea.engine.Send_data(bytes.fromhex(commond_start_alarm))
        # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
        result_start_alarm = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
        statCom_wea.engine.Close_Engine()
        result_start_alarm = bytes.fromhex(self.hexShow(result_start_alarm))
        self.logger.get_log().info(f"Alarm start result is {result_start_alarm}")
        self.state.set_alarm("open")


    def stop_alarm(self):
        '''
        关闭警报
        '''
        '''
        打开警报
        '''
        statCom_wea = JKSATACOM(self.state, self.comconfig.get_device_info_weather(), self.comconfig.get_bps_weather(),
                                self.comconfig.get_timeout_weather(),
                                self.logger, None)
        # 关闭警报命令
        commond_start_alarm = "0C 06 00 16 00 01 A8 D3"  #
        time.sleep(2)
        statCom_wea.engine.Open_Engine()  # 打开串口
        statCom_wea.engine.Send_data(bytes.fromhex(commond_start_alarm))
        # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
        result_stop_alarm = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
        statCom_wea.engine.Close_Engine()
        result_stop_alarm = bytes.fromhex(self.hexShow(result_stop_alarm))
        print(f"stop result is {result_stop_alarm}")
        self.state.set_alarm("close")
    def start_green_light(self):
        '''
        开启绿灯常亮
        '''
        statCom_wea = JKSATACOM(self.state, self.comconfig.get_device_info_weather(), self.comconfig.get_bps_weather(),
                                self.comconfig.get_timeout_weather(),
                                self.logger, None)
        # 关闭警报命令
        commond_start_alarm = "0C 06 00 C2 00 13 68 E6"  #
        time.sleep(2)
        statCom_wea.engine.Open_Engine()  # 打开串口
        statCom_wea.engine.Send_data(bytes.fromhex(commond_start_alarm))
        # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
        #result_stop_alarm = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
        statCom_wea.engine.Close_Engine()
    def start_green_light_slow(self):
        '''
        开启绿灯慢闪
        '''
        statCom_wea = JKSATACOM(self.state, self.comconfig.get_device_info_weather(), self.comconfig.get_bps_weather(),
                                self.comconfig.get_timeout_weather(),
                                self.logger, None)
        # 关闭警报命令
        commond_start_alarm = "0C 06 00 C2 00 23 68 F2"  #
        time.sleep(2)
        statCom_wea.engine.Open_Engine()  # 打开串口
        statCom_wea.engine.Send_data(bytes.fromhex(commond_start_alarm))
        # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
        # result_stop_alarm = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
        statCom_wea.engine.Close_Engine()
    def start_green_light_fast(self):
        '''
        开启绿灯爆闪
        '''
        statCom_wea = JKSATACOM(self.state, self.comconfig.get_device_info_weather(), self.comconfig.get_bps_weather(),
                                self.comconfig.get_timeout_weather(),
                                self.logger, None)
        # 关闭警报命令
        commond_start_alarm = "0C 06 00 C2 00 33 69 3E"  #
        time.sleep(2)
        statCom_wea.engine.Open_Engine()  # 打开串口
        statCom_wea.engine.Send_data(bytes.fromhex(commond_start_alarm))
        # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
        # result_stop_alarm = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
        statCom_wea.engine.Close_Engine()

    def start_red_light(self):
        '''
        开启红灯常亮
        '''
        statCom_wea = JKSATACOM(self.state, self.comconfig.get_device_info_weather(), self.comconfig.get_bps_weather(),
                                self.comconfig.get_timeout_weather(),
                                self.logger, None)
        # 关闭警报命令
        commond_start_alarm = "0C 06 00 C2 00 11 E9 27"  #
        time.sleep(2)
        statCom_wea.engine.Open_Engine()  # 打开串口
        statCom_wea.engine.Send_data(bytes.fromhex(commond_start_alarm))
        # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
        # result_stop_alarm = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
        statCom_wea.engine.Close_Engine()

    def start_red_light_slow(self):
        '''
        开启红灯慢闪
        '''

        statCom_wea = JKSATACOM(self.state, self.comconfig.get_device_info_weather(), self.comconfig.get_bps_weather(),
                                self.comconfig.get_timeout_weather(),
                                self.logger, None)
        # 关闭警报命令
        commond_start_alarm = "0C 06 00 C2 00 21 E9 33"  #
        time.sleep(2)
        statCom_wea.engine.Open_Engine()  # 打开串口
        statCom_wea.engine.Send_data(bytes.fromhex(commond_start_alarm))
        # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
        # result_stop_alarm = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
        statCom_wea.engine.Close_Engine()
    def start_red_light_fast(self):
        '''
        开启红灯爆闪
        '''
        statCom_wea = JKSATACOM(self.state, self.comconfig.get_device_info_weather(), self.comconfig.get_bps_weather(),
                                self.comconfig.get_timeout_weather(),
                                self.logger, None)
        # 关闭警报命令
        commond_start_alarm = "0C 06 00 C2 00 31 E8 FF"  #
        time.sleep(2)
        statCom_wea.engine.Open_Engine()  # 打开串口
        statCom_wea.engine.Send_data(bytes.fromhex(commond_start_alarm))
        # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
        # result_stop_alarm = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
        statCom_wea.engine.Close_Engine()

    def start_yellow_light(self):
        '''
        开启黄灯常亮
        '''
        statCom_wea = JKSATACOM(self.state, self.comconfig.get_device_info_weather(), self.comconfig.get_bps_weather(),
                                self.comconfig.get_timeout_weather(),
                                self.logger, None)
        # 关闭警报命令
        commond_start_alarm = "0C 06 00 C2 00 12 A9 26"  #
        time.sleep(2)
        statCom_wea.engine.Open_Engine()  # 打开串口
        statCom_wea.engine.Send_data(bytes.fromhex(commond_start_alarm))
        # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
        # result_stop_alarm = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
        statCom_wea.engine.Close_Engine()

    def start_yellow_light_slow(self):
        '''
        开启黄灯慢闪
        '''
        statCom_wea = JKSATACOM(self.state, self.comconfig.get_device_info_weather(), self.comconfig.get_bps_weather(),
                                self.comconfig.get_timeout_weather(),
                                self.logger, None)
        # 关闭警报命令
        commond_start_alarm = "0C 06 00 C2 00 22 A9 32"  #
        time.sleep(2)
        statCom_wea.engine.Open_Engine()  # 打开串口
        statCom_wea.engine.Send_data(bytes.fromhex(commond_start_alarm))
        # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
        # result_stop_alarm = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
        statCom_wea.engine.Close_Engine()

    def start_yellow_light_fast(self):
        '''
        开启黄灯爆闪
        '''
        statCom_wea = JKSATACOM(self.state, self.comconfig.get_device_info_weather(), self.comconfig.get_bps_weather(),
                                self.comconfig.get_timeout_weather(),
                                self.logger, None)
        # 关闭警报命令
        commond_start_alarm = "0C 06 00 C2 00 32 A8 FE"  #
        time.sleep(2)
        statCom_wea.engine.Open_Engine()  # 打开串口
        statCom_wea.engine.Send_data(bytes.fromhex(commond_start_alarm))
        # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
        # result_stop_alarm = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
        statCom_wea.engine.Close_Engine()

if __name__ == "__main__":
    logger = Logger(__name__)  # 日志记录
    wfcstate = WFState()
    airconstate = AirCondtionState()
    hangstate = HangerState(wfcstate,airconstate)
    configini=ConfigIni()
    ws = AlarmController(hangstate,logger,configini)
    # #启用一个线程
    # ws.start_alarm()
    # ws.stop_alarm()
