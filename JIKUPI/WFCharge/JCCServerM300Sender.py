# -*- coding: utf-8 -*- 
# @Time : 2022/6/5 22:41
# @Author : ZKL 
# @File : JCCServerM300Sender.py
# 机库接触充电服务端
import threading
import time

# from ConfigIni import ConfigIni
from JKController.BarRepeat.JKBarRepeatCharge import JKBarRepeatCharge
from SATA.SerialUtils import SerialUtils
from BASEUtile.logger import Logger
import WFCharge.WFState as WFState
import BASEUtile.Config as Config
# import USBDevice.USBDeviceConfig as USBDeviceConfig


class JCCServerM300Sender:  # 定义接触充电服务端
    """
    Standby：          Standby Order Received
    Charge            Charge Order Received
                      【等relay响】
                      ChargeStart
                      【等充满】
                      BatteryFull
    TakeOff           TakeOff Order Received
                      【等无人机启动完成】
                      TakeOffOk
    DroneOff          Off Order Received
                      【等关机】
                      OffOk
    Check:            Station:OFF;Drone:OFF                                #充电箱没开，无人机没工作
                      Station:ON;Drone:Charge.BAT1:B_CHARGE;BAT2:B_COOL    #充电箱工作，1号电池充电，2号没有
                      Station:ON;Drone:Charge.BAT1:B_CHARGE;BAT2:B_CHARGE  #充电箱工作，1号电池充电，2号电池充电
                      Station:OFF;Drone:ON                                 #充电箱没开，无人机工作
    Connect:         对频操作；Connect Order Received；Connect Finished

    """

    def __init__(self, logger):
        # self.hangstate=hangstate
        # self.state = state  # 充电箱当前状态信息
        self.logger = logger
        # self.comconfig = USBDeviceConfig()
        self.engine = SerialUtils(thresholdValue=2)
        # self.iniconfig = Config

    def operator_charge(self, commond):
        """
        无线充电操作
        :param commond:
        :return:
        """
        try:
            result = "error"
            if commond == "Standby":
                result = self.standby()
            elif commond == "Charge":
                result = self.charge()
                if Config.get_is_repeat_bar() is True:
                    if result == "chargeerror":  # 充电失败情况下，要重新做一下推杆的打开和失败操作
                        jkbarRepeat = JKBarRepeatCharge(self.logger)
                        if jkbarRepeat.repeat_bar() == False:
                            self.logger.get_log().info(f"充电失败，推杆复位再夹紧失败，充电返回失败")
                            result = "chargeerror"
                        else:  # 夹紧了，可以进行充电操作了
                            result = self.charge()
            elif commond == "TakeOff":
                result = self.takeoff()
            elif commond == "DroneOff":
                result = self.droneoff()
            elif commond == "Check":
                result = self.Check()
            elif commond == "DisplayOn":
                result = self.DisplayOn()
            elif commond == "DisplayOff":
                result = self.DisplayOff()
            elif commond == "Connect":
                result = self.Connect()
            else:
                print("输入命令不正确")
                return 'commond-error'
        except Exception as e:
            self.logger.get_log().info(f"充电操作异常，{e}")
            return "exception-error"
        return result

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
            self.logger.get_log().info(f"发送命令--Standby")
            self.engine.start()
            self.engine.write("Standby".encode('ascii'), isHex=False)
            self.engine.stop()
            while times < waittime:
                time.sleep(1)  # 等待25秒
                times += 1
                if WFState.get_battery_state() == "standby":
                    time.sleep(7)  # 强制等待9秒，待standbyOK收到
                    return "success"
            return result
        except Exception as e:
            self.logger.get_log().info(f"待机命令异常，{e}")
            return 'error'

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
                    time.sleep(8)  # 强制等待8秒，等待是否有降温操作
                    if WFState.get_battery_state() == "cool":  # 2023-06-02修复
                        return "chargeerror"
                    return "success"
            return result
        except Exception as e:
            self.logger.get_log().info(f"充电命令异常，{e}")
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
                    time.sleep(3)  # 强制等待3秒，待standbyOK收到
                    WFState.set_battery_state("takeoff")
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
                    time.sleep(9)  # 强制等待9秒，待standbyOK收到
                    WFState.set_battery_state("close")
                    return "success"
            return result
        except Exception as e:
            self.logger.get_log().info(f"DroneOff--关机指令异常，{e}")
            return 'error'

    def Connect(self):
        """
        关闭无人机
        :return:
        """
        try:
            result = "chargeerror"
            times = 0
            waittime = 40
            # 发送命令
            self.logger.get_log().info(f"发送关机命令--Connect")
            self.engine.start()
            self.engine.write("Connect".encode('ascii'), isHex=False)
            self.engine.stop()
            while times < waittime:
                time.sleep(1)  # 等待25秒
                times += 1
                if WFState.get_battery_state() == "connect":
                    time.sleep(3)  # 强制等待9秒，待standbyOK收到
                    WFState.set_battery_state("connect")
                    return "success"
            return result
        except Exception as e:
            self.logger.get_log().info(f"connect--对频指令异常，{e}")
            return 'error'

    def Check(self):
        """
        状态检查
        :return:
        """
        try:
            result = "success"
            waittime = 0.2
            # 发送命令
            self.logger.get_log().info(f"发送命令--Check")
            self.engine.start()
            self.engine.write("Check".encode('ascii'), isHex=False)
            time.sleep(waittime)  # 等待0.2秒
            self.engine.stop()
            return result
        except Exception as e:
            self.logger.get_log().info(f"check命令异常，{e}")
            return 'error'

    def DisplayOn(self):
        """
        状态检查
        :return:
        """
        try:
            result = "success"
            waittime = 0.2
            # 发送命令
            self.logger.get_log().info(f"发送命令--DisplayOn")
            self.engine.start()
            self.engine.write("DisplayOn".encode('ascii'), isHex=False)
            time.sleep(waittime)  # 等待0.2秒
            self.engine.stop()
            return result
        except Exception as e:
            self.logger.get_log().info(f"DisplayOn命令异常，{e}")
            return 'error'

    def DisplayOff(self):
        """
        状态检查
        :return:
        """
        try:
            result = "success"
            waittime = 0.2
            # 发送命令
            self.logger.get_log().info(f"发送命令--DisplayOff")
            self.engine.start()
            self.engine.write("DisplayOff".encode('ascii'), isHex=False)
            time.sleep(waittime)  # 等待0.2秒
            self.engine.stop()
            return result
        except Exception as e:
            self.logger.get_log().info(f"DisplayOff命令异常，{e}")
            return 'error'


if __name__ == "__main__":
    # Sstate = StationState()#创建对象
    # Dstate = DroneState()  # 创建对象
    # logger = Logger(__name__)#日志记录
    # M300JCC = M300JCCServer(Sstate, Dstate, logger)
    # M300JCC.operator_charge("Check")
    pass

    # Standby 错误指令：Connect Error
    # Charge---，返回结果：Vrec Range Error!
    # Charge Order Received
    # Vrec Range Error!
