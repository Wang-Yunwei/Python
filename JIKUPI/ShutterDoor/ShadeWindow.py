import BASEUtile.BusinessConstant as BusinessConstant
import BASEUtile.BusinessUtil as BusinessUtil
import USBDevice.ComSerial as ComSerial
import SerialUsedStateFlag as SerialUsedStateFlag
"""
百叶窗控制
"""


class ShadeWindow:
    def __init__(self, logger):
        self._logger = logger
        self._usb_used_state = SerialUsedStateFlag
        self._open_command = "0E 06 00 00 00 01 48 F5"
        self._close_command = "0E 06 00 00 00 00 89 35"
        self._com_serial = ComSerial.get_com_serial(BusinessConstant.USB_WEATHER)

    def open(self):
        """
        百叶窗代开
        """
        # if self._usb_used_state.get_is_used_serial_weather() is True:
        #     self._logger.get_log().info(f"[ShadeWindow.open]百叶窗打开,端口被占用")
        #     return BusinessConstant.BUSY
        # else:
        #     self._usb_used_state.set_used_serial_weather()
        #     time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
        try:
            self._logger.get_log().info(f"[ShadeWindow.open]百叶窗打开-开始")
            BusinessUtil.open_serial(self._com_serial,self._logger)
            result = BusinessUtil.execute_command_hex(self._open_command, self._com_serial, self._logger, is_hex=True)
            result = BusinessUtil.reset_write_result(result,self._open_command)
            self._logger.get_log().info(f"[ShadeWindow.open]百叶窗打开-结束,打开结果为:{result}")
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[ShadeWindow.open]百叶窗打开-异常,异常信息为:{ex}")
        finally:
            BusinessUtil.close_serial(self._com_serial,self._logger)
                # self._usb_used_state.set_used_serial_free_weather()

    def close(self):
        """
        百叶窗关闭
        """
        # if self._usb_used_state.get_is_used_serial_weather() is True:
        #     self._logger.get_log().info(f"[ShadeWindow.close]百叶窗关闭,端口被占用")
        #     return BusinessConstant.BUSY
        # else:
        #     self._usb_used_state.set_used_serial_weather()
        #     time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
        try:
            self._logger.get_log().info(f"[ShadeWindow.close]百叶窗关闭-开始")
            BusinessUtil.open_serial(self._com_serial,self._logger)
            result = BusinessUtil.execute_command_hex(self._close_command, self._com_serial, self._logger, is_hex=True)
            result = BusinessUtil.reset_write_result(result, self._close_command)
            self._logger.get_log().info(f"[ShadeWindow.close]百叶窗关闭-结束,打开结果为:{result}")
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[ShadeWindow.close]百叶窗关闭-异常,异常信息为:{ex}")
        finally:
            BusinessUtil.close_serial(self._com_serial,self._logger)
                # self._usb_used_state.set_used_serial_free_weather()
