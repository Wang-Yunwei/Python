# -*- coding: utf-8 -*-
# @Time : 2024/3/14 17:50
# @Author : luxd
import BASEUtile.BusinessConstant as BusinessConstant
import USBDevice.ComSerial as ComSerial
import BASEUtile.BusinessUtil as BusinessUtil
import time

"""
两个继电器升降判断
1.上升继电器关闭（常亮），升降台上升，上升到位，下降继电器打开（不亮）
2.下降继电器关闭（常亮），升降台下降，下降到位，上升继电器打开（不亮）
3.当升降台在中间位置时，上升和下降继电器都关闭（常亮）
"""


class UpdownLiftV2:
    def __init__(self, logger):
        self._logger = logger
        self._com_serial = ComSerial.get_com_serial(BusinessConstant.USB_WEATHER)
        self._up_command_start = "12 06 00 00 00 01 4A A9"
        self._up_command_end = "12 06 00 00 00 00 8B 69"
        self._down_command_start = "12 06 00 01 00 01 1B 69"
        self._down_command_end = "12 06 00 01 00 00 DA A9"
        self._is_up_command = "12 02 00 00 00 01 BB 69"
        self._is_down_command = "12 02 00 01 00 01 EA A9"

    def up_lift(self):
        """
        升降机-上升
        """
        try:
            self._logger.get_log().info(f"[UpdownLiftV2.up_lift]升降台上升-开始")
            BusinessUtil.open_serial(self._com_serial, self._logger)
            # 结束下降
            result = BusinessUtil.execute_command_hex(self._down_command_end, self._com_serial, self._logger,
                                                      is_hex=True, byte_size=8)
            time.sleep(0.5)
            # 开始上升
            result = BusinessUtil.execute_command_hex(self._up_command_start, self._com_serial, self._logger,
                                                      is_hex=True, byte_size=8)
            # time.sleep(6)
            is_up_result = BusinessConstant.ERROR
            for loop in range(3000):
                result = BusinessUtil.execute_command_hex(self._is_up_command, self._com_serial, self._logger,
                                                          is_hex=True, byte_size=6, is_log_time=True)
                result = BusinessUtil.get_int_data_from_serial(result)
                if result != BusinessConstant.ERROR:
                    if result == 1:
                        is_up_result = BusinessConstant.SUCCESS
                        break
                time.sleep(0.01)
                # time.sleep(2)
            # 结束上升
            result = BusinessUtil.execute_command_hex(self._up_command_end, self._com_serial, self._logger,
                                                      is_hex=True, byte_size=8)
            self._logger.get_log().info(f"[UpdownLiftV2.up_lift]升降台上升-结束,返回结果：{is_up_result}")
            return is_up_result
        except Exception as ex:
            self._logger.get_log().info(f"[UpdownLiftV2.up_lift]升降机上升-异常,异常信息为:{str(ex)}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def down_lift(self):
        """
        升降机-下降
        """
        try:
            self._logger.get_log().info(f"[UpdownLiftV2.down_lift]升降台下降-开始")
            BusinessUtil.open_serial(self._com_serial, self._logger)
            # 结束上升
            result = BusinessUtil.execute_command_hex(self._up_command_end, self._com_serial, self._logger,
                                                      is_hex=True, byte_size=8)
            time.sleep(0.5)
            # 开始下降
            result = BusinessUtil.execute_command_hex(self._down_command_start, self._com_serial, self._logger,
                                                      is_hex=True, byte_size=8)
            # time.sleep(6)
            is_down_result = BusinessConstant.ERROR
            for loop in range(3000):
                result = BusinessUtil.execute_command_hex(self._is_down_command, self._com_serial, self._logger,
                                                          is_hex=True, byte_size=6, is_log_time=True)
                result = BusinessUtil.get_int_data_from_serial(result)
                if result != BusinessConstant.ERROR:
                    if result == 1:
                        is_down_result = BusinessConstant.SUCCESS
                        break
                time.sleep(0.01)
                # time.sleep(2)
            # 结束下降
            result = BusinessUtil.execute_command_hex(self._down_command_end, self._com_serial, self._logger,
                                                      is_hex=True, byte_size=8)
            self._logger.get_log().info(f"[UpdownLiftV2.down_lift]升降台下降-结束,返回结果：{is_down_result}")
            return is_down_result
        except Exception as ex:
            self._logger.get_log().info(f"[UpdownLiftV2.down_lift]升降机下降-异常,异常信息为:{str(ex)}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def reset_lift(self):
        """
        升降机-复位,复位和下降相同
        """
        try:
            self._logger.get_log().info(f"[UpdownLiftV2.reset_lift]升降台复位-开始")
            BusinessUtil.open_serial(self._com_serial, self._logger)
            # 结束上升
            result = BusinessUtil.execute_command_hex(self._up_command_end, self._com_serial, self._logger,
                                                      is_hex=True, byte_size=8)
            time.sleep(0.5)
            # 开始下降
            result = BusinessUtil.execute_command_hex(self._down_command_start, self._com_serial, self._logger,
                                                      is_hex=True, byte_size=8)
            # time.sleep(6)
            is_down_result = BusinessConstant.ERROR
            for loop in range(3000):
                result = BusinessUtil.execute_command_hex(self._is_down_command, self._com_serial, self._logger,
                                                          is_hex=True, byte_size=6)
                result = BusinessUtil.get_int_data_from_serial(result)
                if result == 1:
                    is_down_result = BusinessConstant.SUCCESS
                    break
                time.sleep(0.01)
                # time.sleep(2)
            # 结束下降
            result = BusinessUtil.execute_command_hex(self._down_command_end, self._com_serial, self._logger,
                                                      is_hex=True, byte_size=8)
            self._logger.get_log().info(f"[UpdownLiftV2.reset_lift]升降台复位-结束,返回结果：{is_down_result}")
            return is_down_result
        except Exception as ex:
            self._logger.get_log().info(f"[UpdownLiftV2.reset_lift]升降台复位-异常,异常信息为:{str(ex)}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def get_lift_state(self):
        """
        获取升降台状态
        """
        try:
            self._logger.get_log().info(f"[UpdownLiftV2.get_lift_state]获取升降台状态-开始")
            BusinessUtil.open_serial(self._com_serial, self._logger)
            result = BusinessUtil.execute_command_hex(self._is_up_command, self._com_serial, self._logger,
                                                      is_hex=True, byte_size=6)
            result = BusinessUtil.get_int_data_from_serial(result)
            if result == 1:
                result = "9734"  # 上升状态
            else:
                result = BusinessUtil.execute_command_hex(self._is_down_command, self._com_serial, self._logger,
                                                          is_hex=True, byte_size=6)
                result = BusinessUtil.get_int_data_from_serial(result)
                if result == 1:
                    result = "9735"  # 下降状态
            self._logger.get_log().info(f"[UpdownLiftV2.get_lift_state]获取升降台状态-结束,返回结果：{result}")
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[UpdownLiftV2.get_lift_state]获取升降台状态-异常,异常信息为:{str(ex)}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)
