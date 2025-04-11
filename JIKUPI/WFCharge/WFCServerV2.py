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


class WFCServerV2:  # 定义无线充电服务端
    def __init__(self, logger):
        # self.wf_state = wf_state  # 无线充电当前状态信息
        self.logger = logger
        # self.comconfig = USBDeviceConfig()
        # self.engine = Communication(device_info, bps, timeout,self.logger)  # 串口初始化:
        self.engine = SerialHelper(Port=USBDeviceConfig.get_serial_usb_charge(),
                                   BaudRate=USBDeviceConfig.get_serial_bps_charge(),
                                   ByteSize=USBDeviceConfig.get_serial_bytesize_charge(),
                                   Parity=USBDeviceConfig.get_serial_parity_charge(),
                                   Stopbits=USBDeviceConfig.get_serial_stopbits_charge(), thresholdValue=2)

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
                if ("ChargeStart" in result or "BatteryStart" in result) and "BatteryFull" not in result and (
                        "ConnectError" not in result and "PositionError" not in result and "ConnectBreak" not in result and "VrecError" not in result and "InputCurrentError" not in result and "ChargeFail" not in result):
                    result = "success"
                    WFState.set_battery_state("charging")
                else:
                    result = "chargeerror"

            elif commond == "Standby":
                result = self.standby()
                self.logger.get_log().info(f"Standby result: {result}")
                if result == "" or "ConnectError" in result or "PositionError" in result or "ConnectBreak" in result or "VrecError" in result or "InputCurrentError" in result:
                    result = "SERIOUS ERROR"
                elif result == "error":
                    result = "chargeerror"
                elif "Standby Order Received" in result:
                    WFState.set_battery_state("standby")
                    result = "success"
                else:
                    result = "chargeerror"
            elif commond == "TakeOff":
                result = self.takeoff()
                self.logger.get_log().info(f"TakeOff result: {result}")
                if result != "" and ("TakeOffSuccess" in result) and (
                        "ConnectError" not in result and "PositionError" not in result and "ConnectBreak" not in result and "VrecError" not in result and "InputCurrentError" not in result and "TakeOffFail" not in result):
                    WFState.set_battery_state("takeoff")  # 开机成功
                    result = "success"
                else:
                    result = 'chargeerror'
            elif commond == "DroneOff":
                result = self.droneoff()
                self.logger.get_log().info(f"DroneOff result: {result}")
                if result != "" and ("OffSuccess" in result) and (
                        "ConnectError" not in result and "PositionError" not in result and "ConnectBreak" not in result and "VrecError" not in result and "InputCurrentError" not in result and "OffFail" not in result):
                    WFState.set_battery_state("close")  # 关机状态
                    result = "success"
                else:
                    result = "chargeerror"
            elif commond == "Check":
                result = self.check()
                if "ConnectError" in result or "PositionError" in result or "ConnectBreak" in result or "VrecError" in result or "InputCurrentError" in result:
                    result = "chargeerror"
                else:
                    result = "success"
                return result
            else:
                self.logger.get_log().info(f"输入命令不正确,输入命令为{commond}")
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
            result = ""
            # 发送命令
            self.logger.get_log().info(f"发送充电命令--Charge")
            self.engine.start()
            self.engine.write("Charge".encode('ascii'), isHex=False)
            value1 = ""
            thread_read = threading.Thread(target=self.engine.read)
            thread_read.setDaemon(True)
            thread_read.start()
            time.sleep(57)  # 等待57秒
            self.engine.stop()
            result = self.engine.value
            # print(f"Charge--充电指令，返回结果：{result}")

            if "ConnectError" in result or "PositionError" in result or "ConnectBreak" in result or "VrecError" in result or "InputCurrentError" in result:
                print(f"非常严重的错误，可能机身位置不正确导致，必须重启发射端才能解决")
                result = "error"
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
            result = ""
            # times = 3
            # 发送命令
            self.logger.get_log().info(f"发送待机命令--Standby")
            self.engine.start()
            self.engine.write("Standby".encode('ascii'), isHex=False)
            thread_read = threading.Thread(target=self.engine.read)
            thread_read.setDaemon(True)
            thread_read.start()
            time.sleep(30)  # 等待30秒
            self.engine.stop()
            result = self.engine.value
            # print(f"Standby--，返回结果：{result}")
            if "ConnectError" in result or "PositionError" in result or "ConnectBreak" in result or "VrecError" in result or "InputCurrentError" in result:
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
            result = ""

            # 发送命令
            self.logger.get_log().info(f"发送开机命令--TakeOff")
            self.engine.start()
            self.engine.write("TakeOff".encode('ascii'), isHex=False)
            thread_read = threading.Thread(target=self.engine.read)
            thread_read.setDaemon(True)
            thread_read.start()
            time.sleep(35)  # 等待30秒
            self.engine.stop()
            result = self.engine.value
            print(f"TakeOff--开机指令，返回结果：{result}")
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
            result = ""
            # 发送命令
            self.logger.get_log().info(f"发送关机命令--DroneOff")
            self.engine.start()
            self.engine.write("DroneOff".encode('ascii'), isHex=False)
            thread_read = threading.Thread(target=self.engine.read)
            thread_read.setDaemon(True)
            thread_read.start()
            time.sleep(35)  # 等待30秒
            self.engine.stop()
            result = self.engine.value
            print(f"DroneOff--关机指令，返回结果：{result}")
            return result
        except Exception as e:
            self.logger.get_log().info(f"DroneOff--关机指令异常，{e}")
            return 'error'

    def check(self):  # 状态读取,需要创建线程读取状态，每60秒检测一次，主要为检测无人机是否关机
        try:
            result = ""
            if WFState.get_battery_state() == "charging":  # 只检测正在充电时候的状态
                # 发送命令
                self.logger.get_log().info(f"状态信息获取--check")
                self.engine.start()
                self.engine.write("Check".encode('ascii'), isHex=False)
                thread_read = threading.Thread(target=self.engine.read)
                thread_read.setDaemon(True)
                thread_read.start()
                time.sleep(10)  # 等待30秒
                self.engine.stop()
                result = self.engine.value
                self.logger.get_log().info(f"check指令，返回结果：{result}")
                if "DroneOff" in result:  # 无人机关机
                    WFState.set_battery_state("close")
                elif "DroneCharge" in result:
                    WFState.set_battery_state("charging")
            return result
        except Exception as e:
            self.logger.get_log().info(f"check--指令异常，{e}")
            return 'error'

    def check_thread(self):  # check线程启动
        while True:
            self.check()
            time.sleep(90)  # 等待90秒


if __name__ == "__main__":
    state = WFState()  # 创建对象
    logger = Logger(__name__)  # 日志记录
    WFC = WFCServerV2(state, logger)
    WFC.operator_charge("DroneOff")

    # Standby 错误指令：Connect Error
    # Charge---，返回结果：Vrec Range Error!
    # Charge Order Received
    # Vrec Range Error!
