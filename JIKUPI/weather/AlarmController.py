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

# from AirCondition.AirConditionState import AirCondtionState
import BASEUtile.HangarState as HangarState
from BASEUtile.logger import Logger
import BASEUtile.Config as Config
from SATA.SATACom import JKSATACOM
import USBDevice.USBDeviceConfig as USBDeviceConfig


# from WFCharge.WFState import WFState


class AlarmController():
    '''
    获取天气(凤向，风速，温度，湿度，降雨，雨量，烟感)信息
    通过RS485协议获取
    '''

    # def __init__(self,state,log):
    #     self.state=state
    #     self.logger=log
    #     self.wait_time=30#等待30秒获取一次GPS数据

    def __init__(self, log):
        # self.state = state
        self.logger = log
        self.wait_time = 10  # 等待3秒获取一次气象信息，并推送给到web平台
        # USBDeviceConfig=USBDeviceConfig()

    def hexShow(self, argv):
        '''
        十六进制去除特殊字符
        '''
        hLen = len(argv)
        out_s = ''
        for i in range(hLen):
            out_s = out_s + '{:02X}'.format(argv[i]) + ' '
        return out_s

    def start_alarm(self):
        '''
        打开警报、声音
        '''
        self.logger.get_log().info(f"[AlarmController.start_alarm]打开警报声音-开始")
        statCom_wea = JKSATACOM(USBDeviceConfig.get_serial_usb_weather(), USBDeviceConfig.get_serial_bps_weather(),
                                USBDeviceConfig.get_serial_timeout_weather(),
                                self.logger, None)
        # 打开警报命令
        # commond_start_alarm = "0C 06 00 0D 00 00 19 14"  # 响一次
        commond_start_alarm = "0C 06 00 08 00 01 C8 D5"  # 循环响
        time.sleep(2)
        statCom_wea.engine.Open_Engine()  # 打开串口
        statCom_wea.engine.Send_data(bytes.fromhex(commond_start_alarm))
        # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
        result_start_alarm = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
        statCom_wea.engine.Close_Engine()
        result_start_alarm = bytes.fromhex(self.hexShow(result_start_alarm))
        self.logger.get_log().info(f"[AlarmController.start_alarm]打开警报结果为:{result_start_alarm}")
        HangarState.set_alarm_state("open")

    def stop_alarm(self):
        '''
        关闭警报、声音
        '''
        self.logger.get_log().info(f"[AlarmController.stop_alarm]关闭警报声音-开始")
        statCom_wea = JKSATACOM(USBDeviceConfig.get_serial_usb_weather(), USBDeviceConfig.get_serial_bps_weather(),
                                USBDeviceConfig.get_serial_timeout_weather(),
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
        self.logger.get_log().info(f"[AlarmController.stop_alarm]关闭警报-结束,返回结果为:{result_stop_alarm}")
        HangarState.set_alarm_state("close")

    def start_green_light(self):
        '''
        开启绿灯常亮
        '''
        self.logger.get_log().info(f"[AlarmController.start_green_light]开启绿灯常亮-开始")
        statCom_wea = JKSATACOM(USBDeviceConfig.get_serial_usb_weather(), USBDeviceConfig.get_serial_bps_weather(),
                                USBDeviceConfig.get_serial_timeout_weather(),
                                self.logger, None)
        # 关闭警报命令
        commond_start_alarm = "0C 06 00 C2 00 13 68 E6"  #
        time.sleep(2)
        statCom_wea.engine.Open_Engine()  # 打开串口
        result = statCom_wea.engine.Send_data(bytes.fromhex(commond_start_alarm))
        # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
        # result_stop_alarm = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
        statCom_wea.engine.Close_Engine()
        self.logger.get_log().info(f"[AlarmController.start_green_light]开启绿灯常亮-结束,返回结果为:{result}")

    def start_green_light_slow(self):
        '''
        开启绿灯慢闪
        '''
        self.logger.get_log().info(f"[AlarmController.start_green_light_slow]开启绿灯慢闪-开始")
        statCom_wea = JKSATACOM(USBDeviceConfig.get_serial_usb_weather(), USBDeviceConfig.get_serial_bps_weather(),
                                USBDeviceConfig.get_serial_timeout_weather(),
                                self.logger, None)
        # 关闭警报命令
        commond_start_alarm = "0C 06 00 C2 00 23 68 F2"  #
        time.sleep(2)
        statCom_wea.engine.Open_Engine()  # 打开串口
        result = statCom_wea.engine.Send_data(bytes.fromhex(commond_start_alarm))
        # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
        # result_stop_alarm = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
        statCom_wea.engine.Close_Engine()
        self.logger.get_log().info(f"[AlarmController.start_green_light_slow]开启绿灯慢闪-结束,返回结果为:{result}")

    def start_green_light_fast(self):
        '''
        开启绿灯爆闪
        '''
        self.logger.get_log().info(f"[AlarmController.start_green_light_fast]开启绿灯爆闪-开始")
        statCom_wea = JKSATACOM(USBDeviceConfig.get_serial_usb_weather(), USBDeviceConfig.get_serial_bps_weather(),
                                USBDeviceConfig.get_serial_timeout_weather(),
                                self.logger, None)
        # 关闭警报命令
        commond_start_alarm = "0C 06 00 C2 00 33 69 3E"  #
        time.sleep(2)
        statCom_wea.engine.Open_Engine()  # 打开串口
        result = statCom_wea.engine.Send_data(bytes.fromhex(commond_start_alarm))
        # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
        # result_stop_alarm = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
        statCom_wea.engine.Close_Engine()
        self.logger.get_log().info(f"[AlarmController.start_green_light_fast]开启绿灯爆闪-结束,返回结果为:{result}")

    def start_red_light(self):
        '''
        开启红灯常亮
        '''
        self.logger.get_log().info(f"[AlarmController.start_red_light]开启红灯常亮-开始")
        statCom_wea = JKSATACOM(USBDeviceConfig.get_serial_usb_weather(), USBDeviceConfig.get_serial_bps_weather(),
                                USBDeviceConfig.get_serial_timeout_weather(),
                                self.logger, None)
        # 关闭警报命令
        commond_start_alarm = "0C 06 00 C2 00 11 E9 27"  #
        time.sleep(2)
        statCom_wea.engine.Open_Engine()  # 打开串口
        result = statCom_wea.engine.Send_data(bytes.fromhex(commond_start_alarm))
        # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
        # result_stop_alarm = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
        statCom_wea.engine.Close_Engine()
        self.logger.get_log().info(f"[AlarmController.start_red_light]开启红灯常亮-结束,返回结果为:{result}")

    def start_red_light_slow(self):
        '''
        开启红灯慢闪
        '''
        self.logger.get_log().info(f"[AlarmController.start_red_light_slow]开启红灯慢闪-开始")
        statCom_wea = JKSATACOM(USBDeviceConfig.get_serial_usb_weather(), USBDeviceConfig.get_serial_bps_weather(),
                                USBDeviceConfig.get_serial_timeout_weather(),
                                self.logger, None)
        # 关闭警报命令
        commond_start_alarm = "0C 06 00 C2 00 21 E9 33"  #
        time.sleep(2)
        statCom_wea.engine.Open_Engine()  # 打开串口
        result = statCom_wea.engine.Send_data(bytes.fromhex(commond_start_alarm))
        # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
        # result_stop_alarm = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
        statCom_wea.engine.Close_Engine()
        self.logger.get_log().info(f"[AlarmController.start_red_light_slow]开启红灯慢闪-结束,返回结果为:{result}")

    def start_red_light_fast(self):
        '''
        开启红灯爆闪
        '''
        self.logger.get_log().info(f"[AlarmController.start_red_light_fast]开启红灯爆闪-开始")
        statCom_wea = JKSATACOM(USBDeviceConfig.get_serial_usb_weather(), USBDeviceConfig.get_serial_bps_weather(),
                                USBDeviceConfig.get_serial_timeout_weather(),
                                self.logger, None)
        # 关闭警报命令
        commond_start_alarm = "0C 06 00 C2 00 31 E8 FF"  #
        time.sleep(2)
        statCom_wea.engine.Open_Engine()  # 打开串口
        result = statCom_wea.engine.Send_data(bytes.fromhex(commond_start_alarm))
        # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
        # result_stop_alarm = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
        statCom_wea.engine.Close_Engine()
        self.logger.get_log().info(f"[AlarmController.start_red_light_fast]开启红灯爆闪-结束,返回结果为:{result}")

    def start_yellow_light(self):
        '''
        开启黄灯常亮
        '''
        self.logger.get_log().info(f"[AlarmController.start_yellow_light]开启黄灯常亮-开始")
        statCom_wea = JKSATACOM(USBDeviceConfig.get_serial_usb_weather(), USBDeviceConfig.get_serial_bps_weather(),
                                USBDeviceConfig.get_serial_timeout_weather(),
                                self.logger, None)
        # 关闭警报命令
        commond_start_alarm = "0C 06 00 C2 00 12 A9 26"  #
        time.sleep(2)
        statCom_wea.engine.Open_Engine()  # 打开串口
        result = statCom_wea.engine.Send_data(bytes.fromhex(commond_start_alarm))
        # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
        # result_stop_alarm = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
        statCom_wea.engine.Close_Engine()
        self.logger.get_log().info(f"[AlarmController.start_yellow_light]开启黄灯常亮-结束,返回结果为:{result}")

    def start_yellow_light_slow(self):
        '''
        开启黄灯慢闪
        '''
        self.logger.get_log().info(f"[AlarmController.start_yellow_light_slow]开启黄灯慢闪-开始")
        statCom_wea = JKSATACOM(USBDeviceConfig.get_serial_usb_weather(), USBDeviceConfig.get_serial_bps_weather(),
                                USBDeviceConfig.get_serial_timeout_weather(),
                                self.logger, None)
        # 关闭警报命令
        commond_start_alarm = "0C 06 00 C2 00 22 A9 32"  #
        time.sleep(2)
        statCom_wea.engine.Open_Engine()  # 打开串口
        result = statCom_wea.engine.Send_data(bytes.fromhex(commond_start_alarm))
        # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
        # result_stop_alarm = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
        statCom_wea.engine.Close_Engine()
        self.logger.get_log().info(f"[AlarmController.start_yellow_light_slow]开启黄灯慢闪-结束,返回结果为:{result}")

    def start_yellow_light_fast(self):
        '''
        开启黄灯爆闪
        '''
        self.logger.get_log().info(f"[AlarmController.start_yellow_light_fast]开启黄灯爆闪-开始")
        statCom_wea = JKSATACOM(USBDeviceConfig.get_serial_usb_weather(), USBDeviceConfig.get_serial_bps_weather(),
                                USBDeviceConfig.get_serial_timeout_weather(),
                                self.logger, None)
        # 关闭警报命令
        commond_start_alarm = "0C 06 00 C2 00 32 A8 FE"  #
        time.sleep(2)
        statCom_wea.engine.Open_Engine()  # 打开串口
        result = statCom_wea.engine.Send_data(bytes.fromhex(commond_start_alarm))
        # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
        # result_stop_alarm = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
        statCom_wea.engine.Close_Engine()
        self.logger.get_log().info(f"[AlarmController.start_yellow_light_fast]开启黄灯爆闪-结束,返回结果为:{result}")


if __name__ == "__main__":
    # logger = Logger(__name__)  # 日志记录
    pass
    # wfcstate = WFState()
    # airconstate = AirCondtionState()
    # hangstate = HangarState(wfcstate, airconstate)
    # configini=ConfigIni()
    # ws = AlarmController(hangstate,logger,configini)
    # #启用一个线程
    # ws.start_alarm()
    # ws.stop_alarm()
