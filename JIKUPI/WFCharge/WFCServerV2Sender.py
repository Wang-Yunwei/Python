# -*- coding: utf-8 -*- 
# @Time : 2022/1/5 22:41 
# @Author : ZKL 
# @File : WFCServer.py
# 机库无线充电服务端
import threading
import time

from SATA.SATACom import Communication
from SATA.SerialUtils import SerialUtils
import WFCharge.WFState as WFState
from BASEUtile.logger import Logger
import USBDevice.USBDeviceConfig as USBDeviceConfig


class WFCServerV2Sender:  # 定义无线充电服务端
    def __init__(self, logger):
        # self.state = wf_state  # 无线充电当前状态信息
        self.logger = logger
        # self.comconfig = comconfig
        self.engine = SerialUtils(thresholdValue=2)

    def operator_charge(self, commond):
        """
        充电操作
        :param commond:
        :return:
        """
        try:
            result = "error"
            if commond == "Standby":
                result = self.standby()
            elif commond == "Charge":
                result = self.charge()
            elif commond == "TakeOff":
                result = self.takeoff()
            elif commond == "DroneOff":
                result = self.droneoff()
            elif commond == "Check":
                result = self.check()
            else:
                print("输入命令不正确")
                return 'commond-error'
        except Exception as e:
            self.logger.get_log().info(f"充电操作异常，{e}")
            return "exception-error"
        return result

    def charge(self):
        """
        无线充电充电操作
        :return:
        """
        try:
            result = "chargeerror"
            waittime = 57
            times = 0
            # 发送命令
            self.logger.get_log().info(f"发送充电命令--Charge")
            self.engine.start()
            self.engine.write("Charge".encode('ascii'), isHex=False)
            self.engine.stop()
            while times < waittime:
                time.sleep(1)  # 等待25秒
                times += 1
                if WFState.get_battery_state() == "charging":
                    return "success"
            return result
        except Exception as e:
            self.logger.get_log().info(f"充电命令异常，{e}")
            return 'error'

    def standby(self):
        '''
        无线充电standby 操作
        :return:
        '''
        try:
            waittime = 25  # 等待时间
            times = 0
            result = "chargeerror"
            # 发送命令
            self.logger.get_log().info(f"发送待机命令--Standby")
            self.engine.start()
            self.engine.write("Standby".encode('ascii'), isHex=False)
            self.engine.stop()
            while times < waittime:
                time.sleep(1)  # 等待25秒
                times += 1
                if WFState.get_battery_state() == "standby":
                    return "success"
            return result
        except Exception as e:
            self.logger.get_log().info(f"待机命令异常，{e}")
            return 'error'

    def takeoff(self):
        """
        无人机启动操作
        :return:
        """
        try:
            result = "chargeerror"
            times = 0
            waittime = 30
            # 发送命令
            self.logger.get_log().info(f"发送开机命令--TakeOff")
            self.engine.start()
            self.engine.write("TakeOff".encode('ascii'), isHex=False)
            self.engine.stop()
            while times < waittime:
                time.sleep(1)  # 等待25秒
                times += 1
                if WFState.get_battery_state() == "takeoff":
                    return "success"
            return result
        except Exception as e:
            self.logger.get_log().info(f"TakeOff--开机命令异常，{e}")
            return 'error'

    def droneoff(self):
        """
        关闭无人机
        :return:
        """
        try:
            result = "chargeerror"
            times = 0
            waittime = 30
            # 发送命令
            self.logger.get_log().info(f"发送关机命令--DroneOff")
            self.engine.start()
            self.engine.write("DroneOff".encode('ascii'), isHex=False)
            self.engine.stop()
            while times < waittime:
                time.sleep(1)  # 等待25秒
                times += 1
                if WFState.get_battery_state() == "close":
                    return "success"
            return result
        except Exception as e:
            self.logger.get_log().info(f"DroneOff--关机指令异常，{e}")
            return 'error'

    def check(self):  # 状态读取,需要创建线程读取状态，每60秒检测一次，主要为检测无人机是否关机
        try:
            result = "success"
            waittime = 1
            # 发送命令
            self.logger.get_log().info(f"发送待机命令--Check")
            self.engine.start()
            self.engine.write("Check".encode('ascii'), isHex=False)
            time.sleep(waittime)  # 等待0.2秒
            self.engine.stop()
            return result
        except Exception as e:
            self.logger.get_log().info(f"待机命令异常，{e}")
            return 'error'

    def check_thread(self):  # check线程启动
        while True:
            self.check()
            time.sleep(90)  # 等待90秒


if __name__ == "__main__":
    state = WFState()  # 创建对象
    logger = Logger(__name__)  # 日志记录
    # WFC=WFCServerV2(state,logger)
    # WFC.operator_charge("DroneOff")

    # Standby 错误指令：Connect Error
    # Charge---，返回结果：Vrec Range Error!
    # Charge Order Received
    # Vrec Range Error!
