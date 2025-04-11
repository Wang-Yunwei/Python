# -*- coding: utf-8 -*- 
# @Time : 2022/1/5 22:41 
# @Author : ZKL 
# @File : WFCServer.py
# 机库无线充电服务端
import threading
import time

from SATA.SATACom import Communication
from SATA.SerialHelp import SerialHelper
import USBDevice.USBDeviceConfig as USBDeviceConfig
import WFCharge.WFState as WFState
from BASEUtile.logger import Logger
import BASEUtile.Config as Config


class WFCServer:  # 定义无线充电服务端
    def __init__(self, logger):
        # self.wf_state = wf_state  # 无线充电当前状态信息
        self.logger = logger
        self.config = Config
        # self.comconfig = USBDeviceConfig()
        # self.engine = Communication(device_info, bps, timeout,self.logger)  # 串口初始化:
        self.engine = SerialHelper(Port=USBDeviceConfig.get_serial_usb_charge(),
                                   BaudRate=USBDeviceConfig.get_serial_bps_charge(),
                                   ByteSize=USBDeviceConfig.get_serial_bytesize_charge(),
                                   Parity=USBDeviceConfig.get_serial_parity_charge(),
                                   Stopbits=USBDeviceConfig.get_serial_stopbits_charge())

    def operator_charge(self, commond):
        """
        无线充电操作
        :param commond:
        :return:
        """
        try:
            result = "error"
            if commond == "Charge":
                result = self.charge()
                self.logger.get_log().info(f"Charge result: {result}")
                if result == "" or "Connect Error" in result or "Vrec Range Error" in result or "Position Error!" in result or "Error" in result or "DroneStartFail" in result or "BatteryFull!" in result:
                    result = "SERIOUS ERROR"
                elif result == "error":
                    result = "chargeerror"
                else:
                    WFState.set_battery_state("charging")
                    result = "success"
            elif commond == "Standby":
                result = self.standby()
                self.logger.get_log().info(f"Standby result: {result}")
                if result == "" or "Connect Error" in result or "Vrec Range Error" in result or "Position Error!" in result or "Error" in result:
                    result = "SERIOUS ERROR"
                elif result == "error":
                    result = "chargeerror"
                else:
                    WFState.set_battery_state("standby")
                    result = "success"
            elif commond == "TakeOff":
                result = self.takeoff()
                self.logger.get_log().info(f"TakeOff result: {result}")
                if result != "" and (
                        "Take Off Success" in result or "Rx_CHARGE_CC" in result or "Success" in result or (
                        "Rx_TAKE_OFF_CHECK" in result and "Take Off Fail" not in result and "BatteryVoltageLow" not in result and "Connect Error" not in result)):
                    WFState.set_battery_state("takeoff")  # 开机成功
                    result = "success"
                else:
                    result = 'chargeerror'
            elif commond == "DroneOff":
                result = self.droneoff()
                self.logger.get_log().info(f"DroneOff result: {result}")
                if result != "" and ("Off Success" in result or "Success" in result or (
                        "Rx_OFF_CHECK" in result and "Off Fail" not in result and "Connect Error" not in result)):
                    WFState.set_battery_state("close")  # 关机状态
                    result = "success"
                else:
                    result = "chargeerror"
            else:
                print("输入命令不正确")
                return 'commond-error'
        except Exception as e:
            self.logger.get_log().info(f"无线充电操作异常，{e}")
            return "exception-error"
        return result

    def charge(self):
        """
        无线充电充电操作
        :return:
        """
        try:
            result = "false"
            times = 3
            while result == "false" and times > 0:
                # 发送命令
                self.logger.get_log().info(f"发送充电命令--Charge")
                self.engine.start()
                self.engine.write("Charge".encode('ascii'), isHex=False)
                value1 = ""
                thread_read = threading.Thread(target=self.engine.read)
                thread_read.setDaemon(True)
                thread_read.start()
                time.sleep(35)  # 等待30秒
                self.engine.stop()
                result = self.engine.value
                print(f"Charge--充电指令，返回结果：{result}")
                if "false" in result:
                    self.engine.value = ""
                    result = "false"
                    times = times - 1
                    continue
                else:
                    break
            if "Connect Error" in result or "Vrec Range Error" in result:
                print(f"非常严重的错误，可能机身位置不正确导致，必须重启发射端才能解决")
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
            result = "false"
            times = 3
            while result == "false" and times > 0:
                # 发送命令
                self.logger.get_log().info(f"发送待机命令--Standby")
                self.engine.start()
                self.engine.write("Standby".encode('ascii'), isHex=False)
                value1 = ""
                thread_read = threading.Thread(target=self.engine.read)
                thread_read.setDaemon(True)
                thread_read.start()
                time.sleep(25)  # 等待30秒
                self.engine.stop()
                result = self.engine.value
                print(f"Standby--，返回结果：{result}")
                if "false" in result:
                    self.engine.value = ""
                    result = "false"
                    times = times - 1
                    continue
                else:
                    break
            if "Connect Error" in result or "Vrec Range Error" in result:
                print(f"非常严重的错误，可能机身位置不正确导致，必须重启发射端才能解决")
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
            result = "false"
            times = 3
            while result == "false" and times > 0:
                # 发送命令
                self.logger.get_log().info(f"发送开机命令--TakeOff")
                self.engine.start()
                self.engine.write("TakeOff".encode('ascii'), isHex=False)
                value1 = ""
                thread_read = threading.Thread(target=self.engine.read)
                thread_read.setDaemon(True)
                thread_read.start()
                time.sleep(40)  # 等待30秒
                self.engine.stop()
                result = self.engine.value
                print(f"TakeOff--开机指令，返回结果：{result}")
                if "false" in result:
                    self.engine.value = ""
                    result = "false"
                    times = times - 1
                    continue
                else:
                    break
            if "Take Off Success".lower() in result.lower():
                print("--------------开机成功----------------")
            else:
                print("--------------success is not in result----------------")
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
            result = "false"
            times = 3
            while result == "false" and times > 0:
                # 发送命令
                self.logger.get_log().info(f"发送关机命令--DroneOff")
                self.engine.start()
                self.engine.write("DroneOff".encode('ascii'), isHex=False)
                value1 = ""
                thread_read = threading.Thread(target=self.engine.read)
                thread_read.setDaemon(True)
                thread_read.start()
                time.sleep(45)  # 等待30秒
                self.engine.stop()
                result = self.engine.value
                print(f"DroneOff--关机指令，返回结果：{result}")
                if "false" in result:
                    self.engine.value = ""
                    result = "false"
                    times = times - 1
                    continue
                else:
                    break
            if "Off Success".lower() in result.lower():
                print("--------------关闭成功----------------")
            else:
                print("--------------success is not in result----------------")
            return result
        except Exception as e:
            self.logger.get_log().info(f"DroneOff--关机指令异常，{e}")
            return 'error'


if __name__ == "__main__":
    state = WFState()  # 创建对象
    logger = Logger(__name__)  # 日志记录
    WFC = WFCServer(state, logger)
    WFC.operator_charge("DroneOff")

    # Standby 错误指令：Connect Error
    # Charge---，返回结果：Vrec Range Error!
    # Charge Order Received
    # Vrec Range Error!
