# -*- coding: utf-8 -*- 
# @Time : 2023/2/14 18:56 
# @Author : ZKL 
# @File : ChargeAtTime.py
'''
定时启动充电流程，每天晚上12点定时启动充电
作为一个线程执行，每隔半小时检测一次是否启动自动充电，如果恰好在0点到1点之间就启动充电（前提配置夜间12点定时充电流程）
'''
import datetime
import time

from WFCharge.JCCServerM300 import JCCServerM300
from WFCharge.JCCServerM300Sender import JCCServerM300Sender
# from WFCharge.JCCServerV2 import M300JCCServerV2
from WFCharge.JCCServerV2M300Single import JCCServerV2M300Single
from WFCharge.JCCServerV3M300 import JCCServerV3M300
from WFCharge.WFCServer import WFCServer
from WFCharge.WFCServerV2 import WFCServerV2
from WFCharge.WFCServerV2Sender import WFCServerV2Sender
import SerialUsedStateFlag as SerialUsedStateFlag
import WFCharge.WFState as WFState
import BASEUtile.Config as Config


class ChargeAtTime():
    def __init__(self, logger):
        self.waittime = 1800  # 等待1800秒检测一次
        self.comstate_flag = SerialUsedStateFlag
        # self.wf_state=wf_state
        self.logger = logger
        # self.hangerstate=hangerstate
        # self.comconfig = comconfig
        pass

    def start_task_thread(self):
        '''
        启动充电检测线程
        '''
        while True:
            # 如果有夜间充电配置
            # if 配置了夜间充电:
            # if 时间在凌晨0点和1点之间
            # 启动充电
            now_time = time.strftime("%H:%M:%S", time.localtime())
            current_battery_value = WFState.get_battery_value()
            state = WFState.get_battery_state()
            if Config.get_is_night_charge():  # 配置了夜间充电动作
                if "00:00:00" < now_time < "01:00:00":
                    if current_battery_value != "100":  # 2023-11-14如果电量不为100，则启动夜间充电
                        self.logger.get_log().info(f"当前时间为{datetime.datetime.now()},启动夜间充电")
                        self.exe_charge_command("Charge")
                    else:
                        self.logger.get_log().info(f"当前时间为{datetime.datetime.now()},电量为100，不启动夜间充电")
            time.sleep(self.waittime)

    def exe_charge_command(self, commond):
        '''
        执行充电相关命令
        :param commond:
        :return:
        '''
        global WFC
        try:
            result = ""
            if self.comstate_flag.get_is_used_serial_charge() == False:
                self.comstate_flag.set_used_serial_charge()
                try:
                    if Config.get_charge_version() == "wfc":  # 无线充电
                        if Config.get_wfc_version() == 'V1.0':  # V1.0版本
                            WFC = WFCServer(self.logger)
                            result = WFC.operator_charge(commond)
                        elif Config.get_wfc_version() == 'V2.0':  # V2.0版本
                            if Config.get_is_wfc_double_connect() == False:
                                WFC = WFCServerV2(self.logger)
                            else:
                                WFC = WFCServerV2Sender(self.logger)
                            result = WFC.operator_charge(commond)
                    else:  # 触点充电
                        if Config.get_wlc_version() == "V1.0":
                            if Config.get_is_wfc_double_connect() == True:  # 全双工通信
                                WFC = JCCServerM300Sender(self.logger)
                            else:
                                WFC = JCCServerM300(self.logger)
                        elif Config.get_wlc_version() == "V2.0":  # V2.0
                            WFC = JCCServerV2M300Single(self.logger)
                        elif Config.get_wlc_version() == "V3.0":  # V3.0
                            WFC = JCCServerV3M300(self.logger)
                        result = WFC.operator_charge(commond)
                    self.comstate_flag.set_used_serial_free_charge()
                except Exception as charex:
                    self.comstate_flag.set_used_serial_free_charge()
            else:
                self.logger.get_log().info(f"websocket 充电指令{commond}无法执行，因为充电串口被占用")
                result = "chargeerror"
            return result
        except Exception as ex:
            self.logger.get_log().info(f"websocket 充电指令{commond}执行异常")
            return "chargeerror"
