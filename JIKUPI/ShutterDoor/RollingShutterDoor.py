import BASEUtile.BusinessConstant as BusinessConstant
import BASEUtile.BusinessUtil as BusinessUtil
import time
import USBDevice.USBDeviceConfig as USBDeviceConfig
import USBDevice.ComSerial as ComSerial
import SerialUsedStateFlag as SerialUsedStateFlag

"""
卷帘门控制
"""


class RollingShutterDoor:
    def __init__(self, logger):
        self._logger = logger
        self._usb_used_state = SerialUsedStateFlag
        # self._open_command = "15 06 D0 03 00 01 83 DE"
        # self._open_command = "15 06 00 D3 00 01 BA E7"
        # self._open_command = "15 06 D0 03 00 01 83 DE"
        # self._open_command = "15 06 01 00 D3 01 17 D2"
        self._open_command = "15 06 00 00 00 08 8B 18"

        # self._close_command = "15 06 D0 04 00 01 32 1F"
        # self._close_command = "15 06 00 D4 00 01 0B 26"
        # self._close_command = "15 06 D0 04 00 01 32 1F"
        # self._close_command = "15 06 01 00 D0 04 D7 21"
        # self._close_command = "15 06 01 00 D4 01 15 E2"
        self._close_command = "15 06 00 00 00 10 8B 12"

        # self._is_open_command = "15 03 D1 00 00 01 BE 22"
        # self._is_close_command = "15 03 D1 01 00 01 EF E2"
        self._is_open_command = "15 03 00 D0 00 01 86 E7"
        self._is_close_command = "15 03 00 D1 00 01 D7 27"
        self._state_command = "15 03 00 01 00 01 D6 DE"
        self._com_serial = ComSerial.get_com_serial(BusinessConstant.USB_WEATHER)

    def open(self):
        """
        卷帘门打开
        """
        # if self._usb_used_state.get_is_used_serial_weather() is True:
        #     self._logger.get_log().info(f"[RollingShutterDoor.open]卷帘门打开,端口被占用")
        #     return BusinessConstant.BUSY
        # else:
        #     self._usb_used_state.set_used_serial_weather()
        #     time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
        try:
            self._logger.get_log().info(f"[RollingShutterDoor.open]卷帘门打开-开始")
            BusinessUtil.open_serial(self._com_serial,self._logger)
            result = BusinessUtil.execute_command_hex(self._open_command, self._com_serial, self._logger, is_hex=True)
            print(f"[RollingShutterDoor.open]卷帘门打开,返回结果为:{result}")
            time.sleep(50)
            loop_times = 0
            max_loop_times = 10
            while True:
                try:
                    result = BusinessUtil.execute_command_hex(self._state_command, self._com_serial, self._logger,
                                                              is_hex=True, byte_size=0)
                    result = BusinessUtil.get_int_data_from_serial(result)
                    if result == 1:
                        result = BusinessConstant.SUCCESS
                        break
                    else:
                        loop_times = loop_times + 1
                except Exception as ex:
                    loop_times = loop_times + 1
                    self._logger.get_log().info(f"[RollingShutterDoor.open]卷帘门打开,获取状态值异常,异常信息为:{ex}")
                if loop_times > max_loop_times:
                    result = BusinessConstant.OVERTIME
                    break
                time.sleep(2)
            self._logger.get_log().info(f"[RollingShutterDoor.open]卷帘门打开-结束,打开结果为:{result}")
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[RollingShutterDoor.open]卷帘门打开-异常,异常信息为:{ex}")
        finally:
            BusinessUtil.close_serial(self._com_serial,self._logger)
                # self._usb_used_state.set_used_serial_free_weather()

    def close(self):
        """
        卷帘门关闭
        """
        # if self._usb_used_state.get_is_used_serial_weather() is True:
        #     self._logger.get_log().info(f"[RollingShutterDoor.close]卷帘门关闭,端口被占用")
        #     return BusinessConstant.BUSY
        # else:
        #     self._usb_used_state.set_used_serial_weather()
        #     time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
        try:
            self._logger.get_log().info(f"[RollingShutterDoor.close]卷帘门关闭-开始")
            BusinessUtil.open_serial(self._com_serial,self._logger)
            result = BusinessUtil.execute_command_hex(self._close_command, self._com_serial, self._logger, is_hex=True)
            print(f"[RollingShutterDoor.close]卷帘门关闭,返回结果为:{result}")
            time.sleep(50)
            loop_times = 0
            max_loop_times = 10
            while True:
                try:
                    result = BusinessUtil.execute_command_hex(self._state_command, self._com_serial, self._logger,
                                                              is_hex=True, byte_size=0)
                    result = BusinessUtil.get_int_data_from_serial(result)
                    if result == 6:
                        result = BusinessConstant.SUCCESS
                        break
                    else:
                        loop_times = loop_times + 1
                except Exception as ex:
                    loop_times = loop_times + 1
                    self._logger.get_log().info(f"[RollingShutterDoor.close]卷帘门关闭,获取状态值异常,异常信息为:{ex}")
                if loop_times > max_loop_times:
                    result = BusinessConstant.OVERTIME
                    break
                time.sleep(2)
            self._logger.get_log().info(f"[RollingShutterDoor.close]卷帘门关闭-结束,关闭结果为:{result}")
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[RollingShutterDoor.close]卷帘门关闭-异常,异常信息为:{ex}")
        finally:
            BusinessUtil.close_serial(self._com_serial,self._logger)
                # self._usb_used_state.set_used_serial_free_weather()

    def is_open(self):
        pass

    def is_close(self):
        pass
