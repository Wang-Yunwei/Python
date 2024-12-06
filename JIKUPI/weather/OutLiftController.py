# -*- coding: utf-8 -*- 
# @Time : 2022/5/17 9:09 
# @Author : ZKL 
# @File : GPSCompute.py
'''
外置机库升降台控制
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


class OutLiftController():
    '''
    控制升降台升和降
    通过RS485协议获取
    '''
    # def __init__(self,state,log):
    #     self.state=state
    #     self.logger=log
    #     self.wait_time=30#等待30秒获取一次GPS数据

    def __init__(self,state,log,configini,stateflag):
        self.state = state
        self.logger = log
        self.configini=configini
        self.stateflag=stateflag
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
    def lift_up(self):
        '''
        升降台抬升
        '''
        try:
            self.stateflag.set_weather_used()
            self.logger.get_log().info(f"---begin lift up----")
            statCom_wea = JKSATACOM(self.state, self.comconfig.get_device_info_weather(), self.comconfig.get_bps_weather(),
                                    self.comconfig.get_timeout_weather(),
                                    self.logger, None)

            # 下降触点关闭
            commond_down_close = "0B 06 00 01 00 00 D8 A0"
            statCom_wea.engine.Open_Engine()  # 打开串口
            statCom_wea.engine.Send_data(bytes.fromhex(commond_down_close))
            # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
            commond_down_result = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
            statCom_wea.engine.Close_Engine()
            self.logger.get_log().info(f"---begin lift up commond_down_result is {commond_down_result}----")
            time.sleep(3)
            # 升降台上升命令
            commond_up = "0B 06 00 00 00 01 48 A0 "  #
            statCom_wea.engine.Open_Engine()  # 打开串口
            statCom_wea.engine.Send_data(bytes.fromhex(commond_up))
            # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
            result_up = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
            statCom_wea.engine.Close_Engine()
            result_up = bytes.fromhex(self.hexShow(result_up))
            self.logger.get_log().info(f"Lift up result is {result_up}")
            self.state.set_out_lift('up')
            self.stateflag.set_weather_free()
        except Exception as ex:
            self.stateflag.set_weather_free()
    def lift_down(self):
        '''
        升降台降低
        '''
        try:
            self.stateflag.set_weather_used()
            self.logger.get_log().info(f"---begin lift down----")
            statCom_wea = JKSATACOM(self.state, self.comconfig.get_device_info_weather(), self.comconfig.get_bps_weather(),
                                    self.comconfig.get_timeout_weather(),
                                    self.logger, None)
            #上升触点关闭
            commond_up_close="0B 06 00 00 00 00 89 60"
            statCom_wea.engine.Open_Engine()  # 打开串口
            statCom_wea.engine.Send_data(bytes.fromhex(commond_up_close))
            # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
            commond_up_result = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
            statCom_wea.engine.Close_Engine()
            self.logger.get_log().info(f"---begin lift down commond_up_result is {commond_up_result}----")
            time.sleep(3)
            # 升降台降低指令
            commond_down_open = "0B 06 00 01 00 01 19 60"  #
            statCom_wea.engine.Open_Engine()  # 打开串口
            statCom_wea.engine.Send_data(bytes.fromhex(commond_down_open))
            # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
            commond_down = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
            statCom_wea.engine.Close_Engine()
            commond_down = bytes.fromhex(self.hexShow(commond_down))
            self.logger.get_log().info(f"Lift down result is {commond_down}")
            self.state.set_out_lift('down')
            self.stateflag.set_weather_free()
        except Exception as ex:
            self.stateflag.set_weather_free()


if __name__ == "__main__":
    logger = Logger(__name__)  # 日志记录
    wfcstate = WFState()
    airconstate = AirCondtionState()
    hangstate = HangerState(wfcstate,airconstate)
    configini=ConfigIni()
    ws = OutLiftController(hangstate,logger,configini)
    #ws.lift_up()
    # #启用一个线程
    # ws.start_alarm()
    # ws.stop_alarm()
