# -*- coding: utf-8 -*- 
# @Time : 2021/12/15 14:45 
# @Author : ZKL 
# @File : JKControllerServer.py
# 机库控制端server
import time
import BASEUtile.Config as Config
import BASEUtile.HangarState as HangarState
import USBDevice.USBDeviceConfig as USBDeviceConfig
import USBDevice.ComSerial as ComSerial
import BASEUtile.BusinessUtil as BusinessUtil
import BASEUtile.BusinessConstant as BusinessConstant


class JKBarServer:
    def __init__(self, logger):
        self._logger = logger
        self._com_serial = ComSerial.get_com_serial(BusinessConstant.USB_BAR)

    def open_bar(self):
        """
        推杆打开
        """
        try:
            self._logger.get_log().info(f"[JKBarServer.open_bar]推杆打开-开始")
            BusinessUtil.open_serial(self._com_serial, self._logger)
            if HangarState.get_hangar_bar_state() == BusinessConstant.OPENING_STATE and HangarState.get_hangar_td_bar_state() == BusinessConstant.OPEN_STATE:
                # 前后推杆已经打开，只需打开左右推杆即可
                close_command = Config.get_operation_command_info()[0][4]
                self._logger.get_log().info(f"[JKBarServer.open_bar]推杆打开-单独打开左右推杆")
                if Config.get_down_version() == "V2.0":
                    self._logger.get_log().info(f"[JKBarServer.open_bar]推杆打开-单独打开左右推杆，版本V2.0")
                    # open_command = "2f1" + close_command[3:6] + "2000"
                    open_command = "500000"
                else:
                    self._logger.get_log().info(f"[JKBarServer.open_bar]推杆打开-单独打开左右推杆，版本{Config.get_down_version()}")
                    open_command = "2f10002000"
            else:
                self._logger.get_log().info(f"[JKBarServer.open_bar]推杆打开-全部打开,bar_state:{HangarState.get_hangar_bar_state()},td_bar_state:{HangarState.get_hangar_td_bar_state()}")
                open_command = Config.get_operation_command_info()[0][3]
            result = BusinessUtil.execute_command(open_command + "\r\n", self._com_serial, self._logger, is_hex=False,
                                                  byte_size=4)
            self._logger.get_log().info(f"[JKBarServer.open_bar]推杆打开-结束,返回值为{result}")
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[JKBarServer.open_bar]推杆打开-异常,异常信息:{str(ex)}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def open_td_bar(self):
        """
        前后推杆打开
        """
        try:
            self._logger.get_log().info(f"[JKBarServer.open_td_bar]前后推杆打开-开始")
            close_command = Config.get_operation_command_info()[0][4]  # 距离参考夹紧距离
            if Config.get_down_version() == "V2.0":
                # 下位机V2.0距离以当时所在点为远点，然后根据距离移动，例如：300，则向边框方向移动距离为300
                command = "2f10002" + close_command[7:]
            else:
                # 下位机V3.0距离以机库边框最远点为远点,例如：0，则离边框为0，所以推杆会打开到机库边框
                command = "2f1" + close_command[3:6] + "2000"
            result = BusinessUtil.execute_command(command + "\r\n", self._com_serial, self._logger, is_hex=False,
                                                  byte_size=4)
            self._logger.get_log().info(f"[JKBarServer.open_td_bar]前后推杆打开-结束,返回值为{result}")
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[JKBarServer.open_td_bar]前后推杆打开-异常,异常信息:{str(ex)}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def close_bar(self):
        """
        夹紧推杆
        """
        try:
            self._logger.get_log().info(f"[JKBarServer.close_bar]推杆夹紧-开始")
            command = Config.get_operation_command_info()[0][4]
            BusinessUtil.open_serial(self._com_serial, self._logger)
            if Config.get_bar_move_style() == 'TDF':  # 先推前后，再推左右
                # 夹紧前后之前，先做一下短距离的左右夹紧
                command_td = command[:3] + "0002" + command[7:]
                result_td = BusinessUtil.execute_command(command_td + "\r\n", self._com_serial, self._logger,
                                                         is_hex=False, byte_size=4)
                self._logger.get_log().info(f"[JKBarServer.close_bar]推杆夹紧,前后推杆返回值为{result_td}")
                time.sleep(2)
                if result_td != "92e0":
                    return "92e1"
                if Config.get_down_version() == "V2.0":
                    command_lr = command[:7] + "000"
                else:
                    command_lr = command
                result_lr = BusinessUtil.execute_command(command_lr + "\r\n", self._com_serial, self._logger,
                                                         is_hex=False, byte_size=4)
                self._logger.get_log().info(f"[JKBarServer.close_bar]推杆夹紧,左右推杆返回值为{result_lr}")
                if result_lr == "92e0" and result_td == "92e0":
                    result = "92e0"
                else:
                    result = "92e1"
            elif Config.get_bar_move_style() == 'LRF':  # 先推左右再前后
                command_lr = command[:7] + "000"
                result_lr = BusinessUtil.execute_command(command_lr + "\r\n", self._com_serial, self._logger,
                                                         is_hex=False, byte_size=4)
                self._logger.get_log().info(f"[JKBarServer.close_bar]推杆夹紧,左右推杆返回值为{result_lr}")
                time.sleep(2)
                if result_lr != "92e0":
                    return "92e1"
                if Config.get_down_version() == "V2.0":
                    command_td = command[:3] + "0002" + command[7:]
                else:
                    command_td = command
                result_td = BusinessUtil.execute_command(command_td + "\r\n", self._com_serial, self._logger,
                                                         is_hex=False, byte_size=4)
                self._logger.get_log().info(f"[JKBarServer.close_bar]推杆夹紧,前后推杆返回值为{result_td}")
                if result_lr == "92e0" and result_td == "92e0":
                    result = "92e0"
                else:
                    result = "92e1"
            else:  # 同时夹紧
                result = BusinessUtil.execute_command(command + "\r\n", self._com_serial, self._logger, is_hex=False,
                                                      byte_size=4)
                self._logger.get_log().info(f"[JKBarServer.close_bar]推杆夹紧,同时夹紧推杆返回值为{result}")
            # 2023-9-13 如果有夹紧后打开前后推杆配置
            if Config.get_is_td_bar():
                # 如果配置了前后打开操作
                command = Config.get_operation_command_info()[0][3]  # 2f10002000
                if Config.get_down_version() == "V2.0":
                    command = "2f10002" + command[7:] + "\r\n"
                    result1 = BusinessUtil.execute_command(command, self._com_serial, self._logger, is_hex=False,
                                                           byte_size=4)
                    self._logger.get_log().info(f"[JKBarServer.close_bar]推杆夹紧,前后推杆打开的返回值{result1}")
                    # HangarState.set_hangar_bar_state("close")
                    # HangarState.set_hangar_td_bar_state("open")
                elif Config.get_down_version() == "V3.0":
                    command_close = Config.get_operation_command_info()[0][4]
                    command = "2f1" + command_close[3:6] + "2000" + "\r\n"
                    result1 = BusinessUtil.execute_command(command, self._com_serial, self._logger, is_hex=False,
                                                           byte_size=4)
                    self._logger.get_log().info(f"[JKBarServer.close_bar]推杆夹紧,前后推杆打开的返回值{result1}")
                    # HangarState.set_hangar_bar_state("close")
                    # HangarState.set_hangar_td_bar_state("open")
            self._logger.get_log().info(f"[JKBarServer.close_bar]推杆夹紧-结束,操作指令为{command},返回值为{result}")
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[JKBarServer.close_bar]推杆夹紧-异常,异常信息:{str(ex)}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def reset_bar(self):
        """
        推杆复位
        """
        try:
            self._logger.get_log().info(f"[JKBarServer.reset_bar]推杆复位-开始")
            command = "500000" + "\r\n"
            BusinessUtil.open_serial(self._com_serial, self._logger)
            result = BusinessUtil.execute_command(command, self._com_serial, self._logger, is_hex=False,
                                                  byte_size=4)
            self._logger.get_log().info(f"[JKBarServer.reset_bar]推杆复位-结束,返回值为{result}")
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[JKBarServer.reset_bar]推杆复位-异常,异常信息:{str(ex)}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def get_bar_state(self):
        """
        获取推杆状态
        """
        try:
            self._logger.get_log().info(f"[JKBarServer.get_bar_state]推杆状态获取-开始")
            command = "2g0000" + "\r\n"
            BusinessUtil.open_serial(self._com_serial, self._logger)
            result = BusinessUtil.execute_command(command, self._com_serial, self._logger, is_hex=False,
                                                  byte_size=4)
            self._logger.get_log().info(f"[JKBarServer.get_bar_state]推杆状态获取-结束,返回值为{result}")
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[JKBarServer.get_bar_state]推杆状态获取-异常,异常信息:{str(ex)}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    # def oper_bar(self, commond):
    #     '''
    #     推拉杠的操作，包括推拉杠同时开启和关闭
    #     :return:
    #     '''
    #     try:
    #         # 直接调用串口发送命令
    #         self._logger.get_log().info(f"推拉杆--接收到发送过来的命令{commond}")
    #         if len(commond) != 6 and len(commond) != 10 and len(commond) != 8 and len(commond) != 12:
    #             self._logger.get_log().error(f"接收到外部端命令{commond}，长度不为6 or 10")
    #             return 'error'
    #         # 机库门操作特殊处理
    #         result = ""
    #         if commond.startswith("2a") or commond.startswith("2b") or commond.startswith("2c") or commond.startswith(
    #                 "2d") or commond.startswith("2e") or commond.startswith("2f"):  # 左右推杆打开
    #             if commond.startswith("2e"):
    #                 # close
    #                 commond = Config.get_operation_command_info()[0][4]
    #                 if Config.get_bar_move_style() == 'TDF':  # 先推前后，再推左右
    #                     # 夹紧前后之前，先做一下短距离的左右夹紧
    #                     commond_td = commond[:3] + "0002" + commond[7:]
    #                     result_td = self.statcom_bar.operator_hanger(commond_td + "\r\n")
    #                     self._logger.get_log().info(f"前后推杆的返回值{result_td}")
    #                     time.sleep(2)
    #                     if result_td != "92e0":
    #                         return "92e1"
    #                     if Config.get_down_version() == "V2.0":
    #                         commond_lr = commond[:7] + "000"
    #                     else:
    #                         commond_lr = commond
    #                     result_lr = self.statcom_bar.operator_hanger(commond_lr + "\r\n")  # 左右推杆动
    #                     self._logger.get_log().info(f"左右推杆的返回值{result_lr}")
    #                     if result_lr == "92e0" and result_td == "92e0":
    #                         result = "92e0"
    #                     else:
    #                         result = "92e1"
    #                         # time.sleep(20)
    #                         # result = "92e0"
    #                 elif Config.get_bar_move_style() == 'LRF':  # 先推左右再前后
    #                     commond_lr = commond[:7] + "000"
    #                     result_lr = self.statcom_bar.operator_hanger(commond_lr + "\r\n")  # 左右推杆动
    #                     self._logger.get_log().info(f"左右推杆的返回值{result_lr}")
    #                     time.sleep(2)
    #                     if result_lr != "92e0":
    #                         return "92e1"
    #                     if Config.get_down_version() == "V2.0":
    #                         commond_td = commond[:3] + "0002" + commond[7:]
    #                     else:
    #                         commond_td = commond
    #                     result_td = self.statcom_bar.operator_hanger(commond_td + "\r\n")  # 前后推杆动作
    #                     self._logger.get_log().info(f"前后推杆的返回值{result_td}")
    #                     if result_lr == "92e0" and result_td == "92e0":
    #                         result = "92e0"
    #                     else:
    #                         result = "92e1"
    #                         # time.sleep(20)
    #                         # result = "92e0"
    #                 else:  # 同时夹紧
    #                     result = self.statcom_bar.operator_hanger(commond + "\r\n")
    #                 # 2023-9-13 如果有夹紧后打开前后推杆配置
    #                 if Config.get_is_td_bar() == True:
    #                     # 如果配置了前后打开操作
    #                     commond = Config.get_operation_command_info()[0][3]  # 2f10002000
    #                     if Config.get_down_version() == "V2.0":
    #                         commond = "2f10002" + commond[7:]
    #                         result1 = self.statcom_bar.operator_hanger(commond + "\r\n")
    #                         self._logger.get_log().info(f"前后推杆打开的返回值{result1}")
    #                         HangarState.set_hangar_bar_state("close")
    #                         HangarState.set_hangar_td_bar_state("open")
    #                     elif Config.get_down_version() == "V3.0":
    #                         commond_close = Config.get_operation_command_info()[0][4]
    #                         commond = "2f1" + commond_close[3:6] + "2000"
    #                         result1 = self.statcom_bar.operator_hanger(commond + "\r\n")
    #                         self._logger.get_log().info(f"前后推杆打开的返回值{result1}")
    #                         HangarState.set_hangar_bar_state("close")
    #                         HangarState.set_hangar_td_bar_state("open")
    #             elif commond.startswith("2f"):
    #                 # open
    #                 commond = Config.get_operation_command_info()[0][3]
    #                 result = self.statcom_bar.operator_hanger(commond + "\r\n")
    #                 # 判断返回的结果
    #             self._logger.get_log().info(f"推拉杆--下位机返回结果：{result}")
    #             if not result.startswith("92"):
    #                 self._logger.get_log().info(f"推杆操作---返回值错误，为：{result}")
    #                 if commond.startswith("2f"):
    #                     return "92f1"
    #                 if commond.startswith("2e"):
    #                     return "92e1"
    #             if result == "90119021":
    #                 if commond.startswith("2f"):
    #                     if HangarState.get_hangar_bar_state() == "open":  # 2023-04-24加状态判断，如果下位机返回空，但是当前机库推杆为打开则返回正确值
    #                         result = '92f0'
    #                     else:
    #                         result = "92f1"
    #                 elif commond.startswith("2e"):
    #                     result = "92e1"
    #                 elif commond.startswith("2a"):
    #                     result = "92a1"
    #                 elif commond.startswith("2b"):
    #                     result = "92b1"
    #                 elif commond.startswith("2c"):
    #                     result = "92c1"
    #                 elif commond.startswith("2d"):
    #                     result = "92d1"
    #             return result
    #     except Exception as e:
    #         self._logger.get_log().info(f"推拉杆--机库操作异常，{e}")
    #         return "error"
    #
    # def oper_aircondition(self, commond):  # 操作空调
    #     '''
    #     操作空调
    #     :return:
    #     '''
    #     # 发送空调操作命令
    #     result = self.statcom_bar.operator_hanger(commond + "\r\n")
    #     self._logger.get_log().info(f"空调---返回值为：{result}")
    #     if result == "90119021":
    #         if commond.startswith("30"):
    #             result = "9301"
    #         else:
    #             result = "9311"
    #     return result
    #
    # def oper_reset_bar(self, commond):  # 推杆复位
    #     '''
    #     推杆复位打开
    #     :return:
    #     '''
    #     result = self.statcom_bar.operator_hanger(commond + "\r\n")
    #     time.sleep(1)  # 偶尔出现上下推杆不一致的情况，需要做一下等待
    #     self._logger.get_log().info(f"推杆复位---返回值为：{result}")
    #     if not result.startswith("95"):
    #         self._logger.get_log().info(f"推杆复位---返回值错误，为：{result}")
    #         return "9501"
    #     if result == "90119021":
    #         if commond.startswith("50"):
    #             if HangarState.get_hangar_bar_state() == "open":  # 2023-04-24加状态判断，如果下位机返回空，但是当前机库推杆为打开则返回正确值
    #                 result = "9500"
    #                 self._logger.get_log().info(f"推杆复位：下位机返回空null,但是推杆是打开的，则修改返回结果为9500")
    #             else:
    #                 result = "9501"
    #         else:
    #             result = "9511"
    #
    #     return result
    #
    # def operator_hanger(self, commond):
    #     '''
    #     操作机库
    #     :param commond: 操作命令
    #     :return:
    #     '''
    #     try:
    #         # 直接调用串口发送命令
    #         if len(commond) != 6 and len(commond) != 10 and len(commond) != 8 and len(commond) != 12:
    #             self._logger.get_log().error(f"接收到外部端命令{commond}，长度不为6 or 10")
    #             return 'error'
    #         # 机库门操作特殊处理
    #         if commond.startswith("0"):  # 连接状态的操作
    #             return HangarState.get_hangar_state()
    #         elif commond.startswith("2"):  # 推杆操作:
    #             return self.oper_bar(commond)
    #         elif commond.startswith("3"):  # 空调操作:
    #             return self.oper_aircondition(commond)
    #         elif commond.startswith("5"):  # 推杆:
    #             return self.oper_reset_bar(commond)
    #     except Exception as e:
    #         self._logger.get_log().info(f"机库操作异常，{e}")
    #         return "error"
