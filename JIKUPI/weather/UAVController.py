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
import BASEUtile.HangarState as HangarState
from BASEUtile.logger import Logger
import USBDevice.USBDeviceConfig as USBDeviceConfig
import USBDevice.ComSerial as ComSerial
import BASEUtile.Config as Config
import BASEUtile.BusinessConstant as BusinessConstant
import BASEUtile.BusinessUtil as BusinessUtil


class UAVController:
    """
    远程开关遥控器设置
    通过RS485协议获取
    """

    def __init__(self, logger):
        self._logger = logger
        self._open_controller_command = "0E 06 00 00 00 01 48 F5"
        self._close_controller_command = "0E 06 00 00 00 00 89 35"
        self._state_controller_command = "0E 03 00 00 00 01 84 F5"
        self._open_return_command = "0E 06 00 01 00 01 19 35"
        self._close_return_command = "0E 06 00 01 00 00 D8 F5"
        self._state_return_command = "0E 03 00 01 00 01 D5 35"
        self._com_serial = ComSerial.get_com_serial(BusinessConstant.USB_WEATHER)

    def open_controller(self):
        """
        打开遥控器：遥控器开启需要一次短按,一次长按
        """
        try:
            self._logger.get_log().info(f"[UAVController.open_controller]手柄开启-开始")
            result = self._pingComputer(2)
            if result == BusinessConstant.SUCCESS:
                self._logger.get_log().info(f"[UAVController.open_controller]手柄开启,已经开启,无需再次开启")
                return BusinessConstant.SUCCESS
            BusinessUtil.open_serial(self._com_serial, self._logger)
            # 短按一次遥控器开机按钮-按下
            self._logger.get_log().info(f"[UAVController.open_controller]手柄开启-第一次按下")
            BusinessUtil.execute_command_hex(self._open_controller_command, self._com_serial, self._logger, is_hex=True)
            time.sleep(0.2)
            # 短按一次遥控器开机按钮-抬起
            self._logger.get_log().info(f"[UAVController.open_controller]手柄开启-第一次抬起")
            BusinessUtil.execute_command_hex(self._close_controller_command, self._com_serial, self._logger,
                                             is_hex=True)
            time.sleep(0.2)

            # 长按一次遥控器开机按钮-按下
            self._logger.get_log().info(f"[UAVController.open_controller]手柄开启-第二次按下")
            BusinessUtil.execute_command_hex(self._open_controller_command, self._com_serial, self._logger, is_hex=True)
            time.sleep(2)
            # 长按一次遥控器开机按钮-抬起
            self._logger.get_log().info(f"[UAVController.open_controller]手柄开启-第二次抬起")
            BusinessUtil.execute_command_hex(self._close_controller_command, self._com_serial, self._logger,
                                             is_hex=True)
            time.sleep(0.2)
            # 判断如果继电器是否已经关闭，如果未关闭，做5次关闭操作
            result = BusinessUtil.execute_command_hex(self._state_controller_command, self._com_serial, self._logger,
                                                      is_hex=True)
            result = BusinessUtil.get_int_data_from_serial(result)
            if result == 1:
                for i in range(5):
                    self._logger.get_log().info(f"[UAVController.open_controller]手柄开启-第二次抬起不成功，重复进行抬起操作，重复第{i+1}次")
                    BusinessUtil.execute_command_hex(self._close_controller_command, self._com_serial, self._logger,
                                                     is_hex=True)
            # 如果ping通遥控器ip说明已经开启
            time.sleep(10)
            if Config.get_controller_ip() != "":
                result = self._pingComputer(10)
                if result == BusinessConstant.SUCCESS:
                    if Config.get_con_server_ip_port().strip() != "":
                        result = self._checkAPPStarted()
                        self._logger.get_log().info(f"[UAVController.open_controller]手柄开启-APP是否开通,返回值为:{result}")
            else:
                result = BusinessConstant.SUCCESS
            self._logger.get_log().info(f"[UAVController.open_controller]手柄开启-结束,返回值为:{result}")
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[UAVController.open_controller]手柄开启-异常,异常信息为:{ex}")
            # 异常，做一次继电器关闭操作
            BusinessUtil.execute_command_hex(self._close_controller_command, self._com_serial, self._logger,
                                             is_hex=True)
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def close_controller(self):
        """
        关闭遥控器：遥控器关闭需要一次短按,一次长按
        """
        try:
            self._logger.get_log().info(f"[UAVController.close_controller]手柄关闭-开始")
            result = self._pingComputer(2)
            if result == BusinessConstant.ERROR:
                self._logger.get_log().info(f"[UAVController.close_controller]手柄关闭,已经关闭,无需再次关闭")
                return BusinessConstant.SUCCESS
            BusinessUtil.open_serial(self._com_serial, self._logger)
            # 短按一次遥控器开机按钮-按下
            self._logger.get_log().info(f"[UAVController.close_controller]手柄关闭-第一次按下")
            BusinessUtil.execute_command_hex(self._open_controller_command, self._com_serial, self._logger, is_hex=True)
            time.sleep(0.2)
            # 短按一次遥控器开机按钮-抬起
            self._logger.get_log().info(f"[UAVController.close_controller]手柄关闭-第一次抬起")
            BusinessUtil.execute_command_hex(self._close_controller_command, self._com_serial, self._logger,
                                             is_hex=True)
            time.sleep(0.2)
            # 长按一次遥控器开机按钮-按下
            self._logger.get_log().info(f"[UAVController.close_controller]手柄关闭-第二次按下")
            BusinessUtil.execute_command_hex(self._open_controller_command, self._com_serial, self._logger, is_hex=True)
            time.sleep(2)
            # 长按一次遥控器开机按钮-抬起
            self._logger.get_log().info(f"[UAVController.close_controller]手柄关闭-第二次抬起")
            BusinessUtil.execute_command_hex(self._close_controller_command, self._com_serial, self._logger,
                                             is_hex=True)
            time.sleep(0.2)
            # 判断如果继电器是否已经关闭，如果未关闭，做5次关闭操作
            result = BusinessUtil.execute_command_hex(self._state_controller_command, self._com_serial, self._logger,
                                                      is_hex=True)
            result = BusinessUtil.get_int_data_from_serial(result)
            if result == 1:
                for i in range(5):
                    self._logger.get_log().info(f"[UAVController.close_controller]手柄关闭-第二次抬起不成功，重复进行抬起操作，重复第{i + 1}次")
                    BusinessUtil.execute_command_hex(self._close_controller_command, self._com_serial, self._logger,
                                                     is_hex=True)
            # 如果没有ping通遥控器ip说明已经关机
            time.sleep(10)
            if Config.get_controller_ip() != "":
                result = self._pingComputer(2)
                if result == BusinessConstant.ERROR:
                    result = BusinessConstant.SUCCESS
                else:
                    result = BusinessConstant.ERROR
            else:
                result = BusinessConstant.SUCCESS
            self._logger.get_log().info(f"[UAVController.close_controller]手柄关闭-结束,返回值为:{result}")
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[UAVController.close_controller]手柄关闭-异常,异常信息为:{ex}")
            # 异常，做一次继电器关闭操作
            BusinessUtil.execute_command_hex(self._close_controller_command, self._com_serial, self._logger,
                                             is_hex=True)
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def return_controller(self):
        """
        一键返航,长按3秒
        """
        try:
            self._logger.get_log().info(f"[UAVController.return_controller]手柄一键返航-开始")
            result = self._pingComputer(2)
            if result == BusinessConstant.ERROR:  # ping不通遥控器ip
                self._logger.get_log().info(f"[UAVController.return_controller]手柄一键返航,手柄关闭,无法一键返航")
                return BusinessConstant.ERROR
            BusinessUtil.open_serial(self._com_serial, self._logger)
            # 短按一次遥控器开机按钮-按下
            BusinessUtil.execute_command_hex(self._open_return_command, self._com_serial, self._logger, is_hex=True)
            time.sleep(3)
            # 短按一次遥控器开机按钮-抬起
            BusinessUtil.execute_command_hex(self._close_return_command, self._com_serial, self._logger,
                                             is_hex=True)
            # 判断如果继电器是否已经关闭，如果未关闭，做5次关闭操作
            result = BusinessUtil.execute_command_hex(self._state_return_command, self._com_serial, self._logger,
                                                      is_hex=True)
            result = BusinessUtil.get_int_data_from_serial(result)
            if result == "":
                result = BusinessConstant.ERROR
            else:
                result = BusinessConstant.SUCCESS
                if result == 1:
                    for i in range(5):
                        BusinessUtil.execute_command_hex(self._close_return_command, self._com_serial, self._logger,
                                                         is_hex=True)
            self._logger.get_log().info(f"[UAVController.return_controller]手柄一键返航-结束,返回值为:{result}")
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[UAVController.return_controller]手柄一键返航-异常,异常信息为:{ex}")
            # 异常，做一次继电器关闭操作
            BusinessUtil.execute_command_hex(self._close_return_command, self._com_serial, self._logger,
                                             is_hex=True)
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def _pingComputer(self, max_loop_times):
        """
        遥控器ip是否ping通
        """
        host = Config.get_controller_ip()
        # host = '172.16.22.150'
        if host == "":  # 如果IP为空
            self._logger.get_log().info(f"[UAVController.pingComputer]未配置遥控器ip,返回成功")
            return BusinessConstant.SUCCESS
        loop_times = 0
        while loop_times < max_loop_times:
            nowTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            p = os.popen("ping " + host + " -c 2")
            line = p.read()
            print(line)
            if "无法访问目标主机" in line or "100% 包丢失" in line or "100% 丢失" in line:
                print(nowTime, host, BusinessConstant.ERROR)
                self._logger.get_log().info(f"[UAVController.pingComputer]遥控器ip为{host},第{loop_times + 1}次无法ping通")
            else:
                print(nowTime, host, BusinessConstant.SUCCESS)
                self._logger.get_log().info(f"[UAVController.pingComputer]遥控器ip为{host},ping通,返回成功")
                return BusinessConstant.SUCCESS
            time.sleep(1)
            loop_times = loop_times + 1
        return BusinessConstant.ERROR

    def _checkAPPStarted(self):
        """
        确定app是否开启成功
        """
        appstartclient = StartAppClient()
        return appstartclient.check_startup()


if __name__ == "__main__":
    # logger = Logger(__name__)  # 日志记录
    pass
    # wfcstate = WFState()
    # airconstate = AirCondtionState()
    # hangstate = HangarState(wfcstate, airconstate)
    # configini=ConfigIni()
    # stateflag = StateFlag(configini)
    # ws = UAVController(hangstate,logger,configini,stateflag)
    # ws.start_close_controller("open")
    # ws.lift_up()
    # #启用一个线程
    # ws.start_alarm()
    # ws.stop_alarm()
