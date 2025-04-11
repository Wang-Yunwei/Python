# -*- coding: utf-8 -*- 
# @Time : 2022/6/5 22:41
# @Author : ZKL 
# @File : JCCServerM300.py
# 机库接触充电服务端
import threading
import time

from SATA.SATACom import Communication
from SATA.SerialHelp import SerialHelper
import USBDevice.USBDeviceConfig as USBDeviceConfig
import WFCharge.WFState as WFState
from BASEUtile.logger import Logger


class JCCServerM300:  # 定义接触充电服务端
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
    """

    def __init__(self, logger):
        # WFState = state  # 充电箱当前状态信息
        self.logger = logger
        # self.comconfig=USBDeviceConfig()
        # self.engine = Communication(device_info, bps, timeout,self.logger)  # 串口初始化:
        self.engine = SerialHelper(Port=USBDeviceConfig.get_serial_usb_charge(), BaudRate=USBDeviceConfig.get_serial_bps_charge(),
                                   ByteSize=USBDeviceConfig.get_serial_bytesize_charge(), Parity=USBDeviceConfig.get_serial_parity_charge(),
                                   Stopbits=USBDeviceConfig.get_serial_stopbits_charge(),
                                   thresholdValue=2)

    def operator_charge(self, commond):
        """
        无线充电操作
        :param commond:
        :return:
        """
        try:
            result = "error"
            if commond == "Standby" or commond=="standby":
                result = self.standby()
                self.logger.get_log().info(f"Standby result: {result}")
                if "Standby Order Received" in result:
                    WFState.set_battery_state("standby")
                    # WFState.set_state("OFF")
                    result = "success"
                elif result == "" or "ConnectError" in result or "ButtonError" in result or "BatteryError!" in result or "Error" in result:
                    result = "SERIOUS ERROR"
                else:
                    result = "chargeerror"

            elif commond == "Charge":
                result = self.charge()
                self.logger.get_log().info(f"Charge result: {result}")
                if "Charge Order Received" in result and "Connected" in result and "ChargeStart" in result:
                    WFState.set_battery_state("charging")
                    # WFState.set_state("charging")
                    if "BatteryFull" in result:
                        WFState.set_battery_state("close")
                        WFState.set_battery_value("100")
                    if "B_COOL" in result or "BatteryCool" in result:#2023-6-2 新增充电时候，电池高温，直接返回充电失败
                        WFState.set_battery_state("cool")
                        return "chargeerror"
                    result = "success"
                elif result == "" or "ConnectError" in result or "ButtonError" in result or "BatteryError!" in result or "Error" in result:
                    result = "SERIOUS ERROR"
                else:
                    result = "chargeerror"


            elif commond == "TakeOff":
                result = self.takeoff()
                self.logger.get_log().info(f"TakeOff result: {result}")
                if "TakeOff Order Received" in result and "TakeOffOk" in result:
                    WFState.set_battery_state("takeoff")
                    # self.D_state.set_state("ON")
                    result = "success"
                elif result == "" or "ConnectError" in result or "ButtonError" in result or "BatteryError" in result or "Error" in result:
                    result = "SERIOUS ERROR"
                else:
                    result = "chargeerror"


            elif commond == "DroneOff":
                result = self.droneoff()
                self.logger.get_log().info(f"DroneOff result: {result}")
                if "Off Order Received" in result and "OffOk" in result:
                    WFState.set_battery_state("close")
                    # self.D_state.set_state("OFF")
                    result = "success"
                elif result == "" or "ConnectError" in result or "ButtonError" in result or "BatteryError!" in result or "Error" in result:
                    result = "SERIOUS ERROR"
                else:
                    result = "chargeerror"
            elif commond == "Check":
                result = self.Check()
                self.logger.get_log().info(f"Check result: {result}")
                if "Station:OFF" in result:  # 充电箱关
                    WFState.set_station_state("OFF")
                    # 判断是否为充满电关闭
                    if WFState.get_battery_state() == "charging" and WFState.get_battery_value() == "4":  # 上一个时刻还是充电，这个时刻已经是关机状态，则判定为充满关机
                        WFState.set_battery_value("100")
                    if "Drone:OFF" in result:
                        WFState.set_battery_state("close")
                        result = "success"
                    elif "Drone:ON" in result:
                        WFState.set_battery_state("takeoff")
                        result = "success"
                    else:
                        WFState.set_battery_state("outage")  # 追加的新状态 充电箱断电
                        result = "chargeerror"
                elif "Station:ON" in result:  # 充电箱开
                    WFState.set_station_state("ON")
                    if "Drone:OFF" in result:
                        # 判断是否为充满电关闭
                        if WFState.get_battery_state() == "charging" and WFState.get_battery_value() == "4":  # 上一个时刻还是充电，这个时刻已经是关机状态，则判定为充满关机
                            WFState.set_battery_value("100")
                        WFState.set_battery_state("close")
                        result = "success"
                    elif "Drone:ON" in result:
                        # 判断是否为充满电关闭
                        if WFState.get_battery_state() == "charging" and WFState.get_battery_value() == "4":  # 上一个时刻还是充电，这个时刻已经是关机状态，则判定为充满关机
                            WFState.set_battery_value("100")
                        WFState.set_battery_state("takeoff")
                        result = "success"
                    elif "Drone:Charge" in result:  # 充电中状态
                        WFState.set_battery_state("charging")
                        if "Cap:0~25%" in result:
                            WFState.set_battery_value("1")
                        elif "Cap:25~50%" in result:
                            WFState.set_battery_value("2")
                        elif "Cap:50~75%" in result:
                            WFState.set_battery_value("3")
                        elif "Cap:75~100%" in result:
                            WFState.set_battery_value("4")
                        if "BatteryFull" in result:
                            WFState.set_battery_value("100")
                        result = "success"
                    else:
                        WFState.set_battery_state("outage")  # 追加的新状态 充电箱断电
                        result = "chargeerror"

                elif result == "" or "ConnectError" in result or "ButtonError" in result or "BatteryError!" in result or "Error" in result:
                    WFState.set_battery_state("outage")  # 追加的新状态 充电箱断电
                    result = "SERIOUS ERROR"
                elif "BatteryFull" in result:
                    WFState.set_battery_value("100")
                    result = "success"
                else:
                    WFState.set_battery_state("outage")  # 追加的新状态 充电箱断电
                    result = "chargeerror"
            else:
                self.logger.get_log().info(f"输入命令不正确{commond}")
                return 'commond-error'
        except Exception as e:
            self.logger.get_log().info(f"无线充电操作异常，{e}")
            WFState.set_battery_state("outage")  # 追加的新状态 充电箱断电
            return "exception-error"
        return result

    def standby(self):
        '''
        无线充电standby 操作
        :return:
        '''
        try:
            result = ""

            # 发送命令
            self.logger.get_log().info(f"发送待机命令--Standby")
            self.engine.start()
            self.engine.write("Standby".encode('ascii'), isHex=False)
            value1 = ""
            thread_read = threading.Thread(target=self.engine.read)
            thread_read.setDaemon(True)
            thread_read.start()
            time.sleep(25)  # 等待20秒
            self.engine.stop()
            result = self.engine.value

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
            result = ""

            # 发送命令
            self.logger.get_log().info(f"发送充电命令--Charge")
            self.engine.start()
            self.engine.write("Charge".encode('ascii'), isHex=False)
            value1 = ""
            thread_read = threading.Thread(target=self.engine.read)
            thread_read.setDaemon(True)
            thread_read.start()
            time.sleep(57)  # 等待50秒
            self.engine.stop()
            result = self.engine.value
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
            result = ""
            # 发送命令
            self.logger.get_log().info(f"发送开机命令--TakeOff")
            self.engine.start()
            self.engine.write("TakeOff".encode('ascii'), isHex=False)
            value1 = ""
            thread_read = threading.Thread(target=self.engine.read)
            thread_read.setDaemon(True)
            thread_read.start()
            time.sleep(30)  # 等待80秒
            self.engine.stop()
            result = self.engine.value
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
            value1 = ""
            thread_read = threading.Thread(target=self.engine.read)
            thread_read.setDaemon(True)
            thread_read.start()
            time.sleep(30)  # 等待30秒
            self.engine.stop()
            result = self.engine.value
            # print(f"DroneOff--关机指令，返回结果：{result}")
            return result
        except Exception as e:
            self.logger.get_log().info(f"DroneOff--关机指令异常，{e}")
            return 'error'

    def Check(self):
        """
        状态检查
        :return:
        """
        try:
            result = "false"

            # 发送命令
            self.logger.get_log().info(f"发送待机命令--Check")
            self.engine.start()
            self.engine.write("Check".encode('ascii'), isHex=False)
            value1 = ""
            thread_read = threading.Thread(target=self.engine.read)
            thread_read.setDaemon(True)
            thread_read.start()
            time.sleep(0.2)  # 等待5秒
            self.engine.stop()
            # print(self.engine.receive_data)
            # print(self.engine.value)
            result = self.engine.value
            # print(f"check--，返回结果：{result}")

            return result
        except Exception as e:
            self.logger.get_log().info(f"待机命令异常，{e}")
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
