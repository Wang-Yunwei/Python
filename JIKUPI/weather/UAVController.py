# -*- coding: utf-8 -*- 
# @Time : 2022/5/17 9:09 
# @Author : ZKL 
# @File : GPSCompute.py
'''
远程开关遥控器设置
'''

import binascii
import os
import threading
import time
import struct

from APPStartUtil.StartAppClient import StartAppClient
from AirCondition.AirConditionState import AirCondtionState
from BASEUtile.HangerState import HangerState
from BASEUtile.logger import Logger
from ConfigIni import ConfigIni
from SATA.SATACom import JKSATACOM
from StateFlag import StateFlag
from USBDevice.USBDeviceConfig import USBDeviceConfig
from WFCharge.WFState import WFState


class UAVController():
    '''
    远程开关遥控器设置
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
    def start_close_controller(self,flag_str):
        '''
        开启、关闭
        '''
        try:
            if self.configini.get_controller_ip()!="":
                if "open" in flag_str:#本身就是开机情况下，无需做开机操作
                    checkopen_times=2
                    checktime=0
                    while checktime<checkopen_times:
                        if self.pingComputer()=="success":
                            break
                        else:
                            checktime=checktime+1
                    if checktime<checkopen_times:
                        return "success"
                elif "close" in flag_str:#本身就是关机情况下，无需做关机操作
                    checkopen_times=2
                    checktime=0
                    while checktime<checkopen_times:
                        if self.pingComputer()=="success":
                            break
                        else:
                            checktime=checktime+1
                    if checktime==checkopen_times:
                        return "success"

            self.stateflag.set_weather_used()
            self.logger.get_log().info(f"---begin {flag_str} ----")
            statCom_wea = JKSATACOM(self.state, self.comconfig.get_device_info_weather(), 9600,
                                    self.comconfig.get_timeout_weather(),
                                    self.logger, None)

            # (1)触点闭合，按键按下
            #commond_down_close = "01 06 00 00 00 01 48 0A"
            commond_down_close = "0E 06 00 00 00 01 48 F5"
            statCom_wea.engine.Open_Engine()  # 打开串口
            statCom_wea.engine.Send_data(bytes.fromhex(commond_down_close))
            # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
            #commond_down_result = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
            statCom_wea.engine.Close_Engine()
            time.sleep(0.2)  # 等待0.5秒

            # (2)触点打开，按键抬起
            commond_up = "0E 06 00 00 00 00 89 35"  #
            statCom_wea.engine.Open_Engine()  # 打开串口
            statCom_wea.engine.Send_data(bytes.fromhex(commond_up))
            # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
            #result_up = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
            statCom_wea.engine.Close_Engine()
            time.sleep(0.2)  # 等待0.5秒
            #result_up = bytes.fromhex(self.hexShow(result_up))
            #self.logger.get_log().info(f"Lift up result is {result_up}")

            # (3)触点闭合，按键按下
            commond_down_close = "0E 06 00 00 00 01 48 F5"
            statCom_wea.engine.Open_Engine()  # 打开串口
            statCom_wea.engine.Send_data(bytes.fromhex(commond_down_close))
            # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
            # commond_down_result = statCom_wea.engine.Read_Size(9)  # 读取结果,读取个字节
            statCom_wea.engine.Close_Engine()
            time.sleep(2.0)  # 等待2秒

            # (4)触点打开，按键抬起
            commond_up = "0E 06 00 00 00 00 89 35"  #
            statCom_wea.engine.Open_Engine()  # 打开串口
            statCom_wea.engine.Send_data(bytes.fromhex(commond_up))
            # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
            # result_up = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
            statCom_wea.engine.Close_Engine()

            #2023-11-08避免抬起失败，重新做抬起操作
            #2023-12-18 避免抬起失败，重复做抬起操作5次
            for i in range(5):
                time.sleep(2)
                commond_up = "0E 06 00 00 00 00 89 35"  #
                statCom_wea.engine.Open_Engine()  # 打开串口
                statCom_wea.engine.Send_data(bytes.fromhex(commond_up))
                # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
                # result_up = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
                statCom_wea.engine.Close_Engine()
                self.stateflag.set_weather_free()
            # (5)读取机库当前状态
            # 通过ping 设置的相关IP值确定遥控器是否开机成功（必须设置）,同时更新机库的当前状态
            print(f"------------------------------开始检测是否开机成功----------------------------------")
            if self.configini.get_controller_ip()!="":
                wait_times=8 #检测30次，如果30次都没成功则认定开机失败，否则认定关机
                if "close" in flag_str:
                    time.sleep(5)
                    wait_times=1
                current_time=0
                while current_time<wait_times:
                    print(f"time is {current_time}")
                    if self.pingComputer()=="success":
                        break
                    else:
                        current_time=current_time+1
                        time.sleep(2)#等待2秒
                if current_time<wait_times:#能ping通
                    print(f"------------------open,set para is {flag_str}-------------")
                    self.state.set_uav_controller("open")
                    if "open" in flag_str:#要求开机
                        if self.configini.get_con_server_ip_port().strip()!="":
                            if "success" in self.checkAPPStarted():
                                return "success"
                            else:
                                self.state.set_uav_controller("close")
                                return "failed"
                        else:#不要求启动APP
                            return "success"
                    else:
                        return "failed"
                else:#ping不通
                    print(f"------------------close,set para is {flag_str}------------")
                    self.state.set_uav_controller("close")
                    if "close" in flag_str:
                        return "success"
                    else:
                        return "failed"
            else:#如果没有设置固定IP地址，则直接返回成功
                time.sleep(10)#10秒后返回成功
                return "success"
        except Exception as ex:
            # 2023-11-08避免抬起失败，重新做抬起操作
            time.sleep(2)
            self.logger.get_log().info(f"---异常后，做触点头抬起操作 ----")
            statCom_wea = JKSATACOM(self.state, self.comconfig.get_device_info_weather(), 9600,
                                    self.comconfig.get_timeout_weather(),
                                    self.logger, None)
            commond_up = "0E 06 00 00 00 00 89 35"  #
            statCom_wea.engine.Open_Engine()  # 打开串口
            statCom_wea.engine.Send_data(bytes.fromhex(commond_up))
            # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
            # result_up = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
            statCom_wea.engine.Close_Engine()
            self.stateflag.set_weather_free()
            self.logger.get_log().info(f"异常，{ex}")
            return "failed"


    def pingComputer(self):
        host=self.configini.get_controller_ip()
        #host = '172.16.22.150'
        if host=="":#如果IP为空
            return 'success'
        status1 = 'success'
        status2 = 'failed'

        nowTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        p = os.popen("ping " + host + " -c 2")
        line = p.read()
        print(line)
        if "无法访问目标主机" in line or "100% 包丢失" in line or "100% 丢失" in line:
            print(nowTime, host, status2)
            return status2
        else:
            print(nowTime, host, status1)
            return status1
    def checkAPPStarted(self):
        '''
        确定app是否开启成功
        '''
        appstartclient=StartAppClient(self.configini)
        return appstartclient.check_startup()


if __name__ == "__main__":
    logger = Logger(__name__)  # 日志记录
    wfcstate = WFState()
    airconstate = AirCondtionState()
    hangstate = HangerState(wfcstate,airconstate)
    configini=ConfigIni()
    stateflag = StateFlag(configini)
    ws = UAVController(hangstate,logger,configini,stateflag)
    ws.start_close_controller("open")
    #ws.lift_up()
    # #启用一个线程
    # ws.start_alarm()
    # ws.stop_alarm()
