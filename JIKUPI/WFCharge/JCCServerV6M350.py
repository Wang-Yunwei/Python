# -*- coding: utf-8 -*- 
# @Time : 2022/09/19 22:41
# @Author : ZKL 
# @File : JCCServerM300.py
# 黑砂触点充电
'''
处理充电过程中有压差、或者电池有高温等待的时候，要求两个电池能同时充电
'''
import binascii
import math
import threading
import time

# from BASEUtile.loggerColl import LoggerColl
import BASEUtile.Config as Config
from JKController.BarRepeat.JKBarRepeatCharge import JKBarRepeatCharge
from SATA.SATACom import Communication
from SATA.SerialHelp import SerialHelper
import USBDevice.USBDeviceConfig as USBDeviceConfig
from WFCharge.M300VolFit import M300VolFit
import WFCharge.WFState as WFState
import BASEUtile.HangarState as HangarState
from BASEUtile.logger import Logger
import USBDevice.ComSerial as ComSerial
import BASEUtile.BusinessConstant as BusinessConstant
import BASEUtile.BusinessUtil as BusinessUtil


class JCCServerV6M350:  # 定义接触充电服务端
    """
    M300、M350充电,可以获取电量
    """

    def __init__(self, logger):
        self._logger = logger
        self._check_command = "0A 04 00 00 00 0E 70 B5"  # 电池状态
        self._open_charge_command_a = "0A 06 00 03 00 02 F9 70"  # A电池充电
        self._open_power_command_a = "0A 06 00 03 00 01 B9 71"  # A电池开机
        self._close_power_command_a = "0A 06 00 03 00 00 78 B1"  # A电池关机或停止充电
        self._open_charge_command_b = "0A 06 00 04 00 02 48 B1"  # B电池充电
        self._open_power_command_b = "0A 06 00 04 00 01 08 B0"  # B电池开机
        self._close_power_command_b = "0A 06 00 04 00 00 C9 70"  # B电池关机或停止充电
        self._open_charge_command = "0A 10 00 03 00 02 04 00 02 00 02 B6 9F"  # A、B电池充电
        self._open_power_command = "0A 10 00 03 00 02 04 00 01 00 01 06 9E "  # A、B电池开机
        self._close_power_command = "0A 10 00 03 00 02 04 00 00 00 00 96 9E"  # A、B电池关机或停止充电
        self._com_serial = None
        self._init_serial()

    def _init_serial(self):
        try:
            self._com_serial = ComSerial.get_com_serial(BusinessConstant.USB_CHARGE)
        except Exception as ex:
            self._logger.get_log().info(
                f"[JCCServerV5._init_serial]初始化串口{BusinessConstant.USB_CHARGE}异常,异常信息为:{str(ex)}")

    def operator_charge(self, commond):
        """
        无线充电操作
        :param commond:
        :return:
        """
        try:
            result = "error"
            if commond == "Standby" or commond == "standby":
                result = self.standby()
            elif commond == "Charge":
                result = self.charge()
                if Config.get_is_repeat_bar():
                    if result == "chargeerror" or result == "error" or result == "chargeerror(null)":  # 充电失败情况下，要重新做一下推杆的打开和失败操作
                        jkbarRepeat = JKBarRepeatCharge(self._logger)
                        if jkbarRepeat.repeat_bar() == False:
                            self._logger.get_log().info(f"充电失败，推杆复位再夹紧失败，充电返回失败")
                            result = "chargeerror"
                        else:  # 夹紧了，可以进行充电操作了
                            result = self.charge()
            elif commond == "TakeOff":
                result = self.takeoff()
            elif commond == "DroneOff":
                result = self.droneoff()
            elif commond == "Check":
                result = self.Check()
            else:
                self._logger.get_log().info(f"[JCCServerV6M350.operator_charge]输入命令不正确:{commond}")
                return 'commond-error'
        except Exception as ex:
            self._logger.get_log().info(f"[JCCServerV6M350.operator_charge]充电操作异常，{ex}")
            WFState.set_battery_state("unknown")  # 未知状态
            return "exception-error(获取不到下位机充电信息；请确认为2.0版本充电，检查充电硬件设备)"
        # time.sleep(20)
        # result="success"
        return result

    def standby(self):
        """
        无线充电standby 操作
        关闭A电源，关闭B电源
        :return:
        """
        try:
            self._logger.get_log().info(f"[JCCServerV6M350.standby]执行待机命令-开始")
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            BusinessUtil.open_serial(self._com_serial, self._logger)
            result = BusinessConstant.ERROR
            for i in range(10):
                BusinessUtil.execute_command_hex(self._close_power_command, self._com_serial, self._logger)
                time.sleep(2)
                result_state = BusinessUtil.execute_command_hex(self._check_command, self._com_serial, self._logger,
                                                                is_hex=True, byte_size=0)
                # 电池状态 0：关机中 1：开机中 2：充电中
                result_a = BusinessUtil.hexString_to_int(result_state[22:26])
                result_b = BusinessUtil.hexString_to_int(result_state[26:30])
                online_a = BusinessUtil.hexString_to_int(result_state[6:10])
                online_b = BusinessUtil.hexString_to_int(result_state[10:14])
                self._logger.get_log().info(
                    f"[JCCServerV6M350.standby]执行待机命令-循环{i + 1},电池A是否在线:{online_a},电池B是否在线:{online_b},电池A状态:{result_a},电池B状态:{result_b}")
                if result_a == 0 and result_b == 0:
                    WFState.set_battery_state(BusinessConstant.CHARGE_STATE_STANDBY)
                    result = BusinessConstant.SUCCESS
                    break
            self._logger.get_log().info(f"[JCCServerV6M350.standby]执行待机命令-结束,返回结果为:{result}")
            return result
        except Exception as e:
            self._logger.get_log().info(f"[JCCServerV6M350.standby]执行待机命令-异常,异常信息为:{e}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def charge(self):
        """
        充电充电操作,关机充电,两块电池同时充电
        :return:
        """
        try:
            self._logger.get_log().info(f"[JCCServerV6M350.charge]执行充电命令-开始")
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            BusinessUtil.open_serial(self._com_serial, self._logger)
            # 首先关机操作
            BusinessUtil.execute_command_hex(self._close_power_command, self._com_serial, self._logger)
            time.sleep(10)
            result = BusinessConstant.ERROR
            for i in range(10):
                BusinessUtil.execute_command_hex(self._open_charge_command, self._com_serial, self._logger)
                time.sleep(2)
                result_state = BusinessUtil.execute_command_hex(self._check_command, self._com_serial, self._logger,
                                                                is_hex=True, byte_size=0)
                # 电池状态 0：关机中 1：开机中 2：充电中
                result_a = BusinessUtil.hexString_to_int(result_state[22:26])
                result_b = BusinessUtil.hexString_to_int(result_state[26:30])
                online_a = BusinessUtil.hexString_to_int(result_state[6:10])
                online_b = BusinessUtil.hexString_to_int(result_state[10:14])
                self._logger.get_log().info(
                    f"[JCCServerV6M350.charge]执行充电命令-循环{i + 1},电池A是否在线:{online_a},电池B是否在线:{online_b},电池A状态:{result_a},电池B状态:{result_b}")
                if result_a == 2 and result_b == 2:
                    WFState.set_battery_state(BusinessConstant.CHARGE_STATE_CHARGING)
                    result = BusinessConstant.SUCCESS
                    break
            # 如果不是同时充电,在进行关机操作
            if result != BusinessConstant.SUCCESS:
                time.sleep(1)
                BusinessUtil.execute_command_hex(self._close_power_command, self._com_serial, self._logger)
            self._logger.get_log().info(f"[JCCServerV6M350.charge]执行充电命令-结束,返回结果为:{result}")
            return result
        except Exception as e:
            self._logger.get_log().info(f"[JCCServerV6M350.charge]执行充电命令-异常,异常信息为:{e}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def takeoff(self):
        """
        无人机启动操作
        :return:
        """
        try:
            self._logger.get_log().info(f"[JCCServerV6M350.takeoff]执行开机命令-开始")
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            BusinessUtil.open_serial(self._com_serial, self._logger)
            # 首先开机操作
            BusinessUtil.execute_command_hex(self._open_power_command, self._com_serial, self._logger)
            time.sleep(10)
            result = BusinessConstant.ERROR
            for i in range(10):
                time.sleep(2)
                result_state = BusinessUtil.execute_command_hex(self._check_command, self._com_serial, self._logger,
                                                                is_hex=True, byte_size=0)
                # 电池状态 0：关机中 1：开机中 2：充电中
                result_a = BusinessUtil.hexString_to_int(result_state[22:26])
                result_b = BusinessUtil.hexString_to_int(result_state[26:30])
                online_a = BusinessUtil.hexString_to_int(result_state[6:10])
                online_b = BusinessUtil.hexString_to_int(result_state[10:14])
                self._logger.get_log().info(
                    f"[JCCServerV6M350.takeoff]执行开机命令-循环{i + 1},电池A是否在线:{online_a},电池B是否在线:{online_b},电池A状态:{result_a},电池B状态:{result_b}")
                if result_a == 1 and result_b == 1:
                    WFState.set_battery_state(BusinessConstant.CHARGE_STATE_TAKEOFF)
                    result = BusinessConstant.SUCCESS
                    break
            self._logger.get_log().info(f"[JCCServerV6M350.takeoff]执行开机命令-结束,返回结果为:{result}")
            return result
        except Exception as e:
            self._logger.get_log().info(f"[JCCServerV6M350.takeoff]执行开机命令-异常,异常信息为:{e}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def droneoff(self):
        """
        关闭无人机
        :return:
        """
        try:
            self._logger.get_log().info(f"[JCCServerV6M350.droneoff]执行关机命令-开始")
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            BusinessUtil.open_serial(self._com_serial, self._logger)
            # 首先关机操作
            BusinessUtil.execute_command_hex(self._close_power_command, self._com_serial, self._logger)
            time.sleep(10)
            result = BusinessConstant.ERROR
            for i in range(10):
                time.sleep(2)
                result_state = BusinessUtil.execute_command_hex(self._check_command, self._com_serial, self._logger,
                                                                is_hex=True, byte_size=0)
                # 电池状态 0：关机中 1：开机中 2：充电中
                result_a = BusinessUtil.hexString_to_int(result_state[22:26])
                result_b = BusinessUtil.hexString_to_int(result_state[26:30])
                online_a = BusinessUtil.hexString_to_int(result_state[6:10])
                online_b = BusinessUtil.hexString_to_int(result_state[10:14])
                self._logger.get_log().info(
                    f"[JCCServerV6M350.droneoff]执行关机命令-循环{i + 1},电池A是否在线:{online_a},电池B是否在线:{online_b},电池A状态:{result_a},电池B状态:{result_b}")
                if result_a == 0 and result_b == 0:
                    WFState.set_battery_state(BusinessConstant.CHARGE_STATE_TAKEOFF)
                    result = BusinessConstant.SUCCESS
                    break
            self._logger.get_log().info(f"[JCCServerV6M350.droneoff]执行关机命令-结束,返回结果为:{result}")
            return result
        except Exception as e:
            self._logger.get_log().info(f"[JCCServerV6M350.droneoff]执行关机命令-异常,异常信息为:{e}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def Check(self):
        """
        状态检查
        :return:
        """
        try:
            self._logger.get_log().info(f"[JCCServerV6M350.Check]执行状态检查命令-开始")
            BusinessUtil.open_serial(self._com_serial, self._logger)
            result = BusinessUtil.execute_command_hex(self._check_command, self._com_serial, self._logger, is_hex=True,
                                                      byte_size=0)
            if result == "" or result == BusinessConstant.ERROR:
                self._logger.get_log().info(
                    f"[JCCServerV6M350.Check]执行状态检查命令-未获取电池信息")
                result = BusinessConstant.ERROR
            else:
                # 电池状态 0：关机中 1：开机中 2：充电中
                result_a = BusinessUtil.hexString_to_int(result[22:26])
                result_b = BusinessUtil.hexString_to_int(result[26:30])
                # 电池在线状态 0：电池未在位 1：电池在位
                online_a = BusinessUtil.hexString_to_int(result[6:10])
                online_b = BusinessUtil.hexString_to_int(result[10:14])
                # 电压
                voltage_a = BusinessUtil.hexString_to_int(result[30:34]) / 1000
                voltage_b = BusinessUtil.hexString_to_int(result[34:38]) / 1000
                # 电流
                current_a = BusinessUtil.hexString_to_int(result[46:50]) / 1000
                current_b = BusinessUtil.hexString_to_int(result[50:54]) / 1000
                # 电量
                charge_value_a = BusinessUtil.hexString_to_int(result[54:58])
                charge_value_b = BusinessUtil.hexString_to_int(result[58:62])
                if charge_value_a > charge_value_b:
                    WFState.set_battery_value(charge_value_b)
                else:
                    WFState.set_battery_value(charge_value_a)
                # 如果满电,进行关机操作
                if charge_value_a >= BusinessConstant.CHARGE_FULL_VALUE and charge_value_b >= BusinessConstant.CHARGE_FULL_VALUE:
                    self.droneoff()
                self._logger.get_log().info(
                    f"[JCCServerV6M350.Check]执行状态检查命令-电池A是否在线:{online_a},电池B是否在线:{online_b},电池A状态:{result_a},电池B状态:{result_b},"
                    f"电池A电压：{voltage_a},电池B电压：{voltage_b},电池A电流：{current_a},电池B电流：{current_b},电池A电量：{charge_value_a},电池B电量：{charge_value_b}")
                result = BusinessConstant.SUCCESS
            self._logger.get_log().info(f"[JCCServerV6M350.Check]执行状态检查命令-结束,返回结果为:{result}")
            return result
        except Exception as e:
            self._logger.get_log().info(f"[JCCServerV6M350.Check]执行状态检查命令-异常,异常信息为:{e}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)


if __name__ == '__main__':
    logger = Logger(__name__)
    jcc = JCCServerV6M350(logger)
    for i in range(10):
        jcc.operator_charge("Check")
        time.sleep(20)
        jcc.operator_charge("TakeOff")
        time.sleep(20)
        jcc.operator_charge("DroneOff")
        time.sleep(20)
        jcc.operator_charge("Charge")
        time.sleep(20)
        jcc.operator_charge("Standby")
        time.sleep(20)
