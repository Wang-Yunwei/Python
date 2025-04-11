# -*- coding: utf-8 -*- 
# @Time : 2024/07/08
# @Author : Luxd
# 御三关机充电
import time
import serial
import BASEUtile.BusinessConstant as BusinessConstant
import BASEUtile.BusinessUtil as BusinessUtil
import WFCharge.WFState as WFState
import BASEUtile.Config as Config
import USBDevice.ComSerial as ComSerial
from JKController.BarRepeat.JKBarRepeatCharge import JKBarRepeatCharge


class JCCServerV5:  # 定义接触充电服务端
    """
    御三关机充电:如果飞机电压低于16.2伏(大概电量66%)飞机会自动充电,无法关闭充电
    """

    def __init__(self, logger):
        # self.hangstate = hangstate
        # WFState = state  # 充电箱当前状态信息
        self._logger = logger
        # self._open_power_command = "16 06 80 00 00 03 E3 2C"  # 开机
        # self._close_power_command = "16 06 80 00 00 04 A2 EE"  # 关机
        # self._open_charge_command = "16 06 80 00 00 01 62 ED"  # 开启充电
        # self._close_charge_command = "16 06 80 00 00 02 22 EC"  # 结束充电
        # self._check_command = "16 04 00 00 00 03 B3 2C"  # 电池状态
        self._open_power_command = "01 06 80 00 00 03 E0 0B"  # 开机
        self._close_power_command = "01 06 80 00 00 04 A1 C9"  # 关机
        self._open_charge_command = "01 06 80 00 00 01 61 CA"  # 开启充电
        self._close_charge_command = "01 06 80 00 00 02 21 CB"  # 结束充电
        self._check_command = "01 04 00 00 00 03 B0 0B"  # 电池状态
        self._com_serial = None
        self._charge_state_list = ["未充电","充电准备","关机充电","开机充电","充电完成","故障"]
        self._battery_state_list = ["未知", "检测到电池", "未检测到电池"]
        self._uav_state_list = ["未知", "无人机开机", "无人机关机"]
        # 初始化串口信息
        self._init_serial()

    def _init_serial(self):
        try:
            # self._com_serial = serial.Serial(BusinessConstant.SERIAL_USB_CHARGE, BusinessConstant.SERIAL_BPS_9600,
            #                                  timeout=BusinessConstant.SERIAL_TIMEOUT,
            #                                  bytesize=BusinessConstant.SERIAL_BYTE_SIZE_8,
            #                                  parity=serial.PARITY_NONE,
            #                                  stopbits=BusinessConstant.SERIAL_STOP_BITS_1)
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
                print(f"The first charge result is {result}")
                if Config.get_is_repeat_bar():
                    if result == "chargeerror" or result == "error" or result == "chargeerror(null)":  # 充电失败情况下，要重新做一下推杆的打开和失败操作
                        jkbarRepeat = JKBarRepeatCharge(self.logger)
                        if not jkbarRepeat.repeat_bar():
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
            else:
                self._logger.get_log().info(f"输入命令不正确{commond}")
                return 'commond-error'
        except Exception as ex:
            self._logger.get_log().info(f"充电操作异常，{ex}")
            WFState.set_battery_state("unknown")  # 未知状态
            return "exception-error(获取不到下位机充电信息；请确认为2.0版本充电，检查充电硬件设备)"
        # time.sleep(20)
        # result="success"
        return result

    def standby(self):
        '''
        触电充电standby 操作,结束充电，电压低于16.2伏(电量66%)左右，关闭充电无效
        :return:
        '''
        try:
            # 发送命令
            self._logger.get_log().info(f"[JCCServerV5.standby]执行待机命令-开始")
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            BusinessUtil.open_serial(self._com_serial, self._logger)
            max_loop_times = 3
            loop_time = 0
            result = BusinessConstant.ERROR
            while True:
                BusinessUtil.execute_command_hex(self._close_charge_command, self._com_serial, self._logger,
                                                 is_hex=True)
                time.sleep(10)
                result = BusinessUtil.execute_command_hex(self._check_command, self._com_serial, self._logger,
                                                          is_hex=True,
                                                          byte_size=11)
                # 16进制结果转换为2进制
                sub_result = BusinessUtil.hex_str_to_bin_str(result[6:10])
                # Bit0~Bit3十进制,0:未充电；1:充电准备；2:关机充电；3:开机充电；4:充电完成；8:故障
                charge_state = BusinessUtil.bin_str_to_int(sub_result[4:])
                if charge_state == 0 or charge_state == 4:
                    WFState.set_battery_state("standby")
                    result = BusinessConstant.SUCCESS
                    break
                else:
                    self._logger.get_log().info(
                        f"[JCCServerV5.standby]执行待机命令,第{loop_time + 1}次尝试待机失败,状态值为:{charge_state}")
                loop_time = loop_time + 1
                if loop_time >= max_loop_times:
                    self._logger.get_log().info(f"[JCCServerV5.standby]执行待机命令,待机失败")
                    result = BusinessConstant.ERROR
                    break
            self._logger.get_log().info(f"[JCCServerV5.standby]执行待机命令-结束,返回结果为:{result}")
            return result
        except Exception as e:
            self._logger.get_log().info(f"[JCCServerV5.standby]执行待机命令-异常,异常信息为:{e}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def charge(self):
        """
        触电充电充电操作,关机充电
        :return:
        """
        try:
            # 发送命令
            self._logger.get_log().info(f"[JCCServerV5.charge]执行充电命令-开始")
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            BusinessUtil.open_serial(self._com_serial, self._logger)
            # 关机
            BusinessUtil.execute_command_hex(self._close_power_command, self._com_serial, self._logger,
                                             is_hex=True)
            max_loop_times = 3
            loop_time = 0
            result = BusinessConstant.ERROR
            jump_out = False
            while True:
                time.sleep(10)
                result = BusinessUtil.execute_command_hex(self._check_command, self._com_serial, self._logger,
                                                          is_hex=True, byte_size=11)
                # 16进制结果转换为2进制
                sub_result = BusinessUtil.hex_str_to_bin_str(result[6:10])
                # 无人机状态BIT6~BIT7,0:未知;1:无人机开机;2:无人机关机
                power_state = BusinessUtil.bin_str_to_int(sub_result[:2])
                if power_state == 2:
                    self._logger.get_log().info(f"[JCCServerV5.charge]执行充电命令,关机成功")
                    # 充电
                    result = BusinessUtil.execute_command_hex(self._open_charge_command, self._com_serial, self._logger,
                                                              is_hex=True)
                    for i in range(3):
                        time.sleep(10)
                        # 如果是关机充电状态，则返回成功
                        result = BusinessUtil.execute_command_hex(self._check_command, self._com_serial, self._logger,
                                                                  is_hex=True, byte_size=11)
                        sub_result = BusinessUtil.hex_str_to_bin_str(result[6:10])
                        charge_state = BusinessUtil.bin_str_to_int(sub_result[4:])
                        # BIT0~BIT3 0x00：未充电 0x01：充电准备 0x02：关机充电 0x03：开机充电 0x04：充电完成 0x08： 故障
                        if charge_state == 2 or charge_state == 4:
                            WFState.set_battery_state("charging")
                            result = BusinessConstant.SUCCESS
                            self._logger.get_log().info(
                                f"[JCCServerV5.charge]执行充电命令,第{i + 1}次尝试充电成功,状态为:{charge_state}")
                            break
                        else:
                            result = BusinessConstant.ERROR
                            self._logger.get_log().info(
                                f"[JCCServerV5.charge]执行充电命令,第{i + 1}次尝试充电失败,状态为:{charge_state}")
                    # 充电状态为获取到,结束循环
                    jump_out = True
                else:
                    self._logger.get_log().info(
                        f"[JCCServerV5.charge]执行充电命令,第{loop_time + 1}次无人机关机失败,状态为:{power_state}")
                loop_time = loop_time + 1
                if jump_out:
                    break
                elif loop_time >= max_loop_times:
                    self._logger.get_log().info(f"[JCCServerV5.charge]执行充电命令,充电失败")
                    result = BusinessConstant.ERROR
                    break
            self._logger.get_log().info(f"[JCCServerV5.charge]执行充电命令-结束,返回结果为:{result}")
            return result
        except Exception as e:
            self._logger.get_log().info(f"[JCCServerV5.charge]执行充电命令-异常，异常信息为:{e}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def takeoff(self):
        """
        无人机启动操作;开机,结束充电
        :return:
        """
        try:
            # 发送命令
            self._logger.get_log().info(f"[JCCServerV5.takeoff]执行开机命令-开始")
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            BusinessUtil.open_serial(self._com_serial, self._logger)
            # 开机
            BusinessUtil.execute_command_hex(self._open_power_command, self._com_serial, self._logger,
                                             is_hex=True)
            max_loop_times = 3
            loop_time = 0
            result = BusinessConstant.ERROR
            while True:
                time.sleep(10)
                result = BusinessUtil.execute_command_hex(self._check_command, self._com_serial, self._logger,
                                                          is_hex=True, byte_size=11)
                # 16进制结果转换为2进制
                sub_result = BusinessUtil.hex_str_to_bin_str(result[6:10])
                # 无人机状态BIT6~BIT7,0:未知;1:无人机开机;2:无人机关机
                power_state = BusinessUtil.bin_str_to_int(sub_result[:2])
                if power_state == 1:
                    self._logger.get_log().info(f"[JCCServerV5.takeoff]执行开机命令,开机成功")
                    result = BusinessConstant.SUCCESS
                    WFState.set_battery_state('takeoff')
                    break
                    # # 结束充电
                    # result = BusinessUtil.execute_command_hex(self._close_charge_command, self._com_serial, self._logger,
                    #                                           is_hex=True)
                    # time.sleep(10)
                    # # 如果是关机充电状态，则返回成功
                    # result = BusinessUtil.execute_command_hex(self._check_command, self._com_serial, self._logger,
                    #                                           is_hex=True, byte_size=11)
                    # sub_result = BusinessUtil.hex_str_to_bin_str(result[6:10])
                    # charge_state = BusinessUtil.bin_str_to_int(sub_result[4:])
                    # if charge_state == 0 or charge_state == 4:
                    #     WFState.set_battery_state('takeoff')
                    #     result = BusinessConstant.SUCCESS
                    #     self._logger.get_log().info(f"[JCCServerV5.takeoff]发送开机命令--takeoff-第{loop_time + 1}次尝试结束充电成功,状态值为:{charge_state}")
                    #     break
                    # else:
                    #     self._logger.get_log().info(f"[JCCServerV5.takeoff]发送开机命令--takeoff-第{loop_time + 1}次尝试结束充电失败,状态值为:{charge_state}")
                else:
                    self._logger.get_log().info(
                        f"[JCCServerV5.takeoff]执行开机命令,第{loop_time + 1}次尝试开机失败,状态值为:{power_state}")
                loop_time = loop_time + 1
                if loop_time >= max_loop_times:
                    self._logger.get_log().info(f"[JCCServerV5.takeoff]执行开机命令,开机失败")
                    result = BusinessConstant.ERROR
                    break
            self._logger.get_log().info(f"[JCCServerV5.takeoff]执行开机命令-结束,返回结果为:{result}")
            return result
        except Exception as e:
            self._logger.get_log().info(f"[JCCServerV5.takeoff]执行开机命令-异常，异常信息为:{e}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def droneoff(self):
        """
        关闭无人机,关机,结束充电
        :return:
        """
        try:
            # 发送命令
            self._logger.get_log().info(f"[JCCServerV5.droneoff]执行关机命令-开始")
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            BusinessUtil.open_serial(self._com_serial, self._logger)
            # 关机
            BusinessUtil.execute_command_hex(self._close_power_command, self._com_serial, self._logger,
                                             is_hex=True)
            max_loop_times = 3
            loop_time = 0
            result = BusinessConstant.ERROR
            while True:
                time.sleep(10)
                result = BusinessUtil.execute_command_hex(self._check_command, self._com_serial, self._logger,
                                                          is_hex=True,
                                                          byte_size=11)
                # 16进制结果转换为2进制
                sub_result = BusinessUtil.hex_str_to_bin_str(result[6:10])
                # 无人机状态BIT6~BIT7,0:未知;1:无人机开机;2:无人机关机
                power_state = BusinessUtil.bin_str_to_int(sub_result[:2])
                if power_state == 2:
                    self._logger.get_log().info(f"[JCCServerV5.droneoff]执行关机命令,关机成功")
                    WFState.set_battery_state('close')
                    result = BusinessConstant.SUCCESS
                    break
                    # # 结束充电
                    # result = BusinessUtil.execute_command_hex(self._close_charge_command, self._com_serial, self._logger,
                    #                                           is_hex=True)
                    # time.sleep(10)
                    # # 如果是关机充电状态，则返回成功
                    # result = BusinessUtil.execute_command_hex(self._check_command, self._com_serial, self._logger,
                    #                                           is_hex=True, byte_size=11)
                    # sub_result = BusinessUtil.hex_str_to_bin_str(result[6:10])
                    # charge_state = BusinessUtil.bin_str_to_int(sub_result[4:])
                    # if charge_state == 0 or charge_state == 4:
                    #     WFState.set_battery_state('close')
                    #     result = BusinessConstant.SUCCESS
                    #     self._logger.get_log().info(f"[JCCServerV5.droneoff]发送关机命令--DroneOff-第{loop_time + 1}次尝试结束充电成功,状态值为:{charge_state}")
                    #     break
                    # else:
                    #     self._logger.get_log().info(f"[JCCServerV5.droneoff]发送关机命令--DroneOff-第{loop_time + 1}次尝试结束充电失败,状态值为:{charge_state}")
                else:
                    self._logger.get_log().info(
                        f"[JCCServerV5.droneoff]执行关机命令,第{loop_time + 1}次尝试关机失败,状态值为:{power_state}")
                loop_time = loop_time + 1
                if loop_time >= max_loop_times:
                    self._logger.get_log().info(f"[JCCServerV5.droneoff]执行关机命令,关机失败")
                    result = BusinessConstant.ERROR
                    break
            self._logger.get_log().info(f"[JCCServerV5.droneoff]执行关机命令-结束,返回结果为:{result}")
            return result
        except Exception as e:
            self._logger.get_log().info(f"[JCCServerV5.droneoff]执行关机命令-异常,异常信息为:{e}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def Check(self):
        """
        状态检查
        :return:
        """
        try:
            # 发送命令
            self._logger.get_log().info(f"[JCCServerV5.Check]执行状态命令-开始")
            BusinessUtil.open_serial(self._com_serial, self._logger)
            result = BusinessUtil.execute_command_hex(self._check_command, self._com_serial, self._logger, is_hex=True,
                                                      byte_size=11)
            # 16进制结果转换为2进制
            sub_result = BusinessUtil.hex_str_to_bin_str(result[6:10])
            charge_state = BusinessUtil.bin_str_to_int(sub_result[4:])  # 充电状态
            battery_state = BusinessUtil.bin_str_to_int(sub_result[2:4])  # 电池状态
            uav_state = BusinessUtil.bin_str_to_int(sub_result[0:2])  # 开关机状态
            self._logger.get_log().info(
                f"[JCCServerV5.Check]执行状态命令-电流:16进制{result[14:18]},10进制{BusinessUtil.hexString_to_int(result[14:18])},"
                f"电压:16进制{result[10:14]},10进制{BusinessUtil.hexString_to_int(result[10:14])}")
            self._logger.get_log().info(f"[JCCServerV5.Check]执行状态命令-充电状态:{charge_state},{self._charge_state_list[charge_state]}."
                                        f"电池状态:{battery_state},{self._battery_state_list[battery_state]}.开关机状态:{uav_state},{self._uav_state_list[uav_state]}")
            # 如果充电完成,进行结束充电操作
            if charge_state == 4:
                self._logger.get_log().info(f"[JCCServerV5.Check]执行状态命令,已经满电")
                WFState.set_av_list([])
                if WFState.get_battery_state() == 'charging':
                    result = BusinessUtil.execute_command_hex(self._close_charge_command, self._com_serial,
                                                              self._logger,
                                                              is_hex=True)
                    time.sleep(10)
                    result = BusinessUtil.execute_command_hex(self._check_command, self._com_serial, self._logger,
                                                              is_hex=True, byte_size=11)
                    # 16进制结果转换为2进制
                    sub_result = BusinessUtil.hex_str_to_bin_str(result[6:10])
                    charge_state = BusinessUtil.bin_str_to_int(sub_result[4:])
                    # 结束充电成功，设置飞机状态
                    if charge_state == 0 or charge_state == 4:
                        WFState.set_battery_state('close')
                        WFState.set_battery_value("100")
                        self._logger.get_log().info(
                            f"[JCCServerV5.Check]执行状态命令,已经满电,设置电池状态:{WFState.get_battery_state()},电量:{WFState.get_battery_value()}")
            else:
                WFState.set_battery_value("unknown")
                # 2：关机充电，3：开机充电
                if charge_state == 2 or charge_state == 3:
                    # 电流
                    av = BusinessUtil.hexString_to_int(result[14:18])
                    av_result = self._is_stop_charge(av)
                    if av_result:
                        result = BusinessUtil.execute_command_hex(self._close_charge_command, self._com_serial,
                                                                  self._logger, is_hex=True)
                        WFState.set_battery_state('close')
                        WFState.set_battery_value("100")
                        self._logger.get_log().info(
                            f"[JCCServerV5.Check]执行状态命令,已经满电,设置电池状态:{WFState.get_battery_state()},电量:{WFState.get_battery_value()},电流:{WFState.get_av_list()},根据电流判断满电,有偏差")
                else:
                    WFState.set_av_list([])
            self._logger.get_log().info(f"[JCCServerV5.Check]执行状态命令-结束,返回充电状态结果为:{charge_state}")
            return BusinessConstant.SUCCESS
        except Exception as e:
            self._logger.get_log().info(f"[JCCServerV5.Check]执行状态命令-异常,异常信息为:{e}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def _is_stop_charge(self, av):
        """
        根据连续5次电流值小于1A，则判断结束充电，电量大概在98%左右，如果是电流1.5A，则电量在95%左右
        """
        av_list = WFState.get_av_list()
        result = True
        if len(WFState.get_av_list()) < 5:
            av_list.append(av)
            result = False
        else:
            av_list.pop(0)
            av_list.append(av)
            # 循环电流列表，如果有大于1A的，则不结束冲i但，如果都不大于1A，则结束充电
            for temp_av in av_list:
                if temp_av > 1000:
                    result = False
                    break
        return result


if __name__ == "__main__":
    pass
