import BASEUtile.BusinessConstant as BusinessConstant
import USBDevice.ComSerial as ComSerial
import BASEUtile.BusinessUtil as BusinessUtil
import BASEUtile.HangarState as HangarState


class TempHumController:
    """
    温湿度传感器
    """

    def __init__(self, logger):
        self._logger = logger
        self._com_serial = ComSerial.get_com_serial(BusinessConstant.USB_WEATHER)
        self._read_command = "06 03 00 00 00 02 C5 BC"

    def get_temp_hum(self):
        """
        获取温湿度
        """
        try:
            self._logger.get_log().info(f"[TempHumController.get_temp_hum]温湿度获取-开始")
            BusinessUtil.open_serial(self._com_serial, self._logger)
            result = BusinessUtil.execute_command_hex(self._read_command, self._com_serial, self._logger,
                                                      is_hex=True, byte_size=9)
            if result == "":
                result = BusinessConstant.ERROR
                self._logger.get_log().info(f"[TempHumController.get_temp_hum]温湿度获取-结束,未获取到数值")
            else:
                hum = BusinessUtil.hexString_to_int(result[6:10])/10  # 湿度
                temp = BusinessUtil.hexString_to_int(result[10:14])/10  # 温度
                HangarState.set_parking_humidity_value(hum)
                HangarState.set_parking_temperature_value(temp)
                result = BusinessConstant.SUCCESS
                self._logger.get_log().info(f"[TempHumController.get_temp_hum]温湿度获取-结束,返回结果:湿度:{hum},温度:{temp}")
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[TempHumController.get_temp_hum]温湿度获取-异常,异常信息为:{str(ex)}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)
