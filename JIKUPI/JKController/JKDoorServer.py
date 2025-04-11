# -*- coding: utf-8 -*- 
# @Time : 2021/12/15 14:45 
# @Author : ZKL 
# @File : JKControllerServer.py
# 机库控制端server
import time

import BASEUtile.Config as Config
from weather.AlarmController import AlarmController
import USBDevice.USBDeviceConfig as USBDeviceConfig
import USBDevice.ComSerial as ComSerial
import BASEUtile.BusinessUtil as BusinessUtil
import BASEUtile.BusinessConstant as BusinessConstant


class JKDoorServer:
    def __init__(self, logger):
        self._logger = logger
        self._com_serial = ComSerial.get_com_serial(BusinessConstant.USB_DOOR)

    def open_door(self):
        """
        机库开门
        """
        try:
            self._logger.get_log().info(f"[JKDoorServer.open_door]机库门打开-开始")
            BusinessUtil.open_serial(self._com_serial, self._logger)
            open_door_command = Config.get_operation_command_info()[0][1] + "\r\n"
            result = BusinessUtil.execute_command(open_door_command, self._com_serial, self._logger, is_hex=False,
                                                  byte_size=4)
            result = BusinessUtil.reset_write_result(result)
            self._logger.get_log().info(f"[JKDoorServer.open_door]机库门打开-结束,操作指令{open_door_command},返回值为{result}")
            # 警报灯操控
            if Config.get_is_alarm():
                alarm = AlarmController(self._logger)
                if result.endswith('9140'):
                    alarm.start_red_light_slow()
                    alarm.start_alarm()
                else:
                    alarm.start_yellow_light()
                    alarm.stop_alarm()
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[JKDoorServer.open_door]机库门打开-异常,异常信息:{str(ex)}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def close_door(self):
        """
        机库门关闭
        """
        try:
            self._logger.get_log().info(f"[JKDoorServer.close_door]机库门关闭-开始")
            BusinessUtil.open_serial(self._com_serial, self._logger)
            close_door_command = Config.get_operation_command_info()[0][2] + "\r\n"
            result = BusinessUtil.execute_command(close_door_command, self._com_serial, self._logger, is_hex=False,
                                                  byte_size=4)
            result = BusinessUtil.reset_write_result(result)
            self._logger.get_log().info(f"[JKDoorServer.close_door]机库门关闭-结束,操作指令{close_door_command},返回值为{result}")
            # 警报灯操控
            if Config.get_is_alarm():
                alarm = AlarmController(self._logger)
                alarm.stop_alarm()
                if result.endswith('9150'):
                    alarm.start_green_light()
                else:
                    alarm.start_yellow_light()
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[JKDoorServer.close_door]机库门关闭-异常,异常信息:{str(ex)}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def get_door_state(self):
        """
        获取机库门状态
        """
        try:
            self._logger.get_log().info(f"[JKDoorServer.get_door_state]机库门状态获取-开始")
            BusinessUtil.open_serial(self._com_serial, self._logger)
            close_door_command = "170000" + "\r\n"
            result = BusinessUtil.execute_command(close_door_command, self._com_serial, self._logger, is_hex=False,
                                                  byte_size=4)
            result = BusinessUtil.reset_write_result(result)
            self._logger.get_log().info(
                f"[JKDoorServer.get_door_state]机库门状态获取-结束,操作指令{close_door_command},返回值为{result}")
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[JKDoorServer.get_door_state]机库门状态获取-异常,异常信息:{str(ex)}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)
    # def oper_door(self, commond):
    #     '''
    #     机库门的操作，包括左右门同时开启和关闭
    #     :return:
    #     '''
    #     try:
    #         # 直接调用串口发送命令
    #         self._logger.get_log().info(f"接收到发送过来的命令{commond}")
    #         if len(commond) != 6 and len(commond) != 2:
    #             self._logger.get_log().error(f"接收到端命令{commond}，长度不为6")
    #             return 'error'
    #         if commond.startswith("03"):
    #             result = self.statcom_door.operator_hanger(commond + "\r\n")
    #             return result
    #         # 机库门操作特殊处理
    #         if commond.startswith("14") or commond.startswith("15"):  # 门的开启操作
    #             # 机库门的操作，左右机库门的操作，同时开启
    #             # 先开机库左门，然后再开机库右门（需要确认）
    #             if commond.startswith("14"):
    #                 # 开门操作
    #                 commond = Config.get_operation_command_info()[0][1]
    #             else:
    #                 # 关门操作
    #                 commond = Config.get_operation_command_info()[0][2]
    #             result = self.statcom_door.operator_hanger(commond + "\r\n")
    #             # 判断返回的结果
    #             self._logger.get_log().info(f"机库门--,下位机返回结果：{result}")
    #             if result == "90119021":
    #                 if commond.startswith("14"):
    #                     result = "9141"
    #                 else:
    #                     result = "9151"
    #             time.sleep(0.5)
    #             # 2023-5-8 做灯的判断
    #             if Config.get_is_alarm() == True:
    #                 if result.endswith('1'):
    #                     alarm = AlarmController(self._logger, Config)
    #                     alarm.start_yellow_light()
    #                 elif result.startswith('914'):  # open
    #                     alarm = AlarmController(self._logger, Config)
    #                     alarm.start_red_light_slow()
    #                 elif result.startswith('915'):  # close
    #                     alarm = AlarmController(self._logger, Config)
    #                     alarm.start_green_light()
    #
    #             return result
    #     except Exception as e:
    #         self._logger.get_log().info(f"机库门--，机库门操作异常，{e}")
    #         return "error"

    # def oper_controller(self, commond):  # 操作遥控器
    #     '''
    #     操作无人机遥控器
    #     :return:
    #     '''
    #     # 发送空调操作命令
    #     result = self.statcom_door.operator_hanger(commond + "\r\n")
    #     self._logger.get_log().info(f"遥控器---返回值为：{result}")
    #     if result == "90119021":
    #         if commond.startswith("40"):
    #             result = "9401"
    #             # result = "9400"
    #         elif commond.startswith('41'):
    #             result = "9411"
    #             # result = "9410"
    #     return result

    # def operator_hanger(self, commond):
    #     '''
    #     操作机库
    #     :param commond: 操作命令
    #     :return:
    #     '''
    #     try:
    #         # 直接调用串口发送命令
    #         if len(commond) != 6 and len(commond) != 10 and len(commond) != 8 and len(commond) != 12 and len(
    #                 commond) != 2:
    #             self._logger.get_log().error(f"接收到外部端命令{commond}，长度不为6 or 10")
    #             return 'error'
    #         # 机库门操作特殊处理
    #         if commond.startswith("03"):  # 下位机版本号获取
    #             return self.oper_door(commond)
    #         if commond.startswith("0"):  # 连接状态的操作
    #             return HangarState.get_hangar_state()
    #         elif commond.startswith("1"):  # 门的操作
    #             return self.oper_door(commond)
    #         elif commond.startswith("4"):  # 遥控操作:
    #             return self.oper_controller(commond)
    #     except Exception as e:
    #         self._logger.get_log().info(f"机库操作异常，{e}")
    #         return "error"
