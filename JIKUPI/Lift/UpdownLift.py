import BASEUtile.BusinessConstant as BusinessConstant
import BASEUtile.BusinessUtil as BusinessUtil
import USBDevice.USBDeviceConfig as USBDeviceConfig
import USBDevice.ComSerial as ComSerial
import time

"""
升降台控制
"""


class UpdownLift:
    def __init__(self, logger):
        self._logger = logger
        self._auto_up_command = "12 05 00 02 FF 00 2F 59"  # 自动上升
        self._auto_down_command = "12 05 00 03 FF 00 7E 99"  # 自动下降
        self._reset_command = "12 05 00 05 FF 00 9E 98"  # 复位
        self._down_target_state_command = "12 04 00 01 00 02 22 A8"  # 下降到位信号
        self._down_distance = 430  # 门关闭到位距离判断标准：小于该值，判断门关闭(实际到位距离为410)
        self._up_distance = 940  # 门打开到位距离判断标准：大于该值，判断门打(实际到位距离为960)
        self._move_target_door_command = "12 05 00 06 FF 00 6E 98"  # 向目标移动
        self._target_door_para_command = "12 06 00 02 "
        self._com_serial = ComSerial.get_com_serial(BusinessConstant.USB_WEATHER)

    def up_lift(self):
        """
        升降台上升
        """
        try:
            self._logger.get_log().info(f"[UpdownLift.up_lift]升降台上升开始")
            BusinessUtil.open_serial(self._com_serial, self._logger)
            result = BusinessUtil.execute_command_hex(self._auto_up_command, self._com_serial, self._logger,
                                                      is_hex=True)
            print(f"[UpdownLift.up_lift]升降台上升,返回结果为:{result}")
            time.sleep(20)
            loop_times = 0
            max_loop_times = 10
            while True:
                try:
                    result = BusinessUtil.execute_command_hex(self._down_target_state_command, self._com_serial,
                                                              self._logger,
                                                              is_hex=True, byte_size=0)
                    distance = BusinessUtil.hexString_to_int(result[-8:-4])
                    print(f"[UpdownLift.up_lift]升降台上升距离计算,返回结果为:{result}，转换为10机制后为:{distance}")
                    if distance is None or distance == "":
                        loop_times = loop_times + 1
                    else:
                        if distance >= self._up_distance:
                            result = BusinessConstant.SUCCESS
                            break
                        else:
                            loop_times = loop_times + 1
                except Exception as ex:
                    loop_times = loop_times + 1
                    self._logger.get_log().info(f"[UpdownLift.up_lift]升降台上升计算距离异常,异常信息为:{ex}")
                if loop_times > max_loop_times:
                    result = BusinessConstant.OVERTIME
                    break
                time.sleep(2)
            self._logger.get_log().info(f"[UpdownLift.up_lift]升降台上升结束,打开结果为:{result}")
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[UpdownLift.up_lift]升降台上升异常,异常信息为:{ex}")
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def down_lift(self):
        """
        升降台下降
        """
        try:
            self._logger.get_log().info(f"[UpdownLift.down_lift]升降台下降开始")
            BusinessUtil.open_serial(self._com_serial, self._logger)
            result = BusinessUtil.execute_command_hex(self._auto_down_command, self._com_serial, self._logger,
                                                      is_hex=True)
            print(f"[UpdownLift.down_lift]升降台下降,返回结果为:{result}")
            time.sleep(20)
            loop_times = 0
            max_loop_times = 10
            while True:
                try:
                    result = BusinessUtil.execute_command_hex(self._down_target_state_command, self._com_serial,
                                                              self._logger,
                                                              is_hex=True, byte_size=0)
                    distance = BusinessUtil.hexString_to_int(result[-8:-4])
                    print(f"[UpdownLift.down_lift]升降台下降距离计算,返回结果为:{result}，转换为10机制后为:{distance}")
                    if distance is None or distance == "":
                        loop_times = loop_times + 1
                    elif distance <= self._down_distance:
                        result = BusinessConstant.SUCCESS
                        break
                    else:
                        loop_times = loop_times + 1
                except Exception as ex:
                    loop_times = loop_times + 1
                    self._logger.get_log().info(f"[UpdownLift.down_lift]升降台下降计算距离异常,异常信息为:{ex}")
                if loop_times > max_loop_times:
                    result = BusinessConstant.OVERTIME
                    break
                time.sleep(2)
            self._logger.get_log().info(f"[UpdownLift.down_lift]升降台下降结束,下降结果为:{result}")
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[UpdownLift.down_lift]升降台下降异常,异常信息为:{ex}")
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def reset_lift(self):
        """
        复位操作
        """
        try:
            self._logger.get_log().info(f"[UpdownLift.rest_lift]升降台复位开始")
            BusinessUtil.open_serial(self._com_serial, self._logger)
            result = BusinessUtil.execute_command_hex(self._reset_command, self._com_serial, self._logger,
                                                      is_hex=True)
            print(f"[UpdownLift.rest_lift]升降台复位,返回结果为:{result}")
            time.sleep(50)
            loop_times = 0
            max_loop_times = 10
            while True:
                try:
                    result = BusinessUtil.execute_command_hex(self._down_target_state_command, self._com_serial,
                                                              self._logger,
                                                              is_hex=True, byte_size=0)
                    distance = BusinessUtil.hexString_to_int(result[-8:-4])
                    print(f"[UpdownLift.rest_lift]升降台复位距离计算,返回结果为:{result}，转换为10机制后为:{distance}")
                    if distance is None or distance == "":
                        loop_times = loop_times + 1
                    elif distance <= self._down_distance:
                        result = BusinessConstant.SUCCESS
                        break
                    else:
                        loop_times = loop_times + 1
                except Exception as ex:
                    loop_times = loop_times + 1
                    self._logger.get_log().info(f"[UpdownLift.rest_lift]升降台复位计算距离异常,异常信息为:{ex}")
                if loop_times > max_loop_times:
                    result = BusinessConstant.OVERTIME
                    break
                time.sleep(1)
            self._logger.get_log().info(f"[UpdownLift.rest_lift]升降台复位结束,下降结果为:{result}")
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[UpdownLift.rest_lift]升降台复位下降异常,异常信息为:{ex}")
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def is_up_lift(self):
        pass

    def is_down_lift(self):
        pass
