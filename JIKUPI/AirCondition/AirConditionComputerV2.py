import BASEUtile.BusinessConstant as BusinessConstant
import USBDevice.ComSerial as ComSerial
import BASEUtile.BusinessUtil as BusinessUtil
import BASEUtile.ModbusUtils as ModbusUtils
import AirCondition.AirConditionState as AirConditionState
import time

class AirConditionComputerV2:
    """
    (1)空调的开关机
    (2)空调加热模式开启
    (3)制冷模式开启
    (4)加热停止温度
    (5）制冷停止温度
    (6)空调报警开、关
    """

    def __init__(self, logger):
        self._logger = logger
        self._open_command = "0D 06 04 0F 00 00 B8 35"  # 开机
        self._close_command = "0D 06 04 0F 00 01 79 F5"  # 关机
        # self.system_running_commond = "0D 03 00 03 00 00 45 06"  # 系统运行状态,报警状态，待验证
        # self.hot_stop_tem_high="0D 04"#加热停止温度当前260度(26)
        # self.hot_stop_tem_low="0D c4" #-6度
        # self.cold_stop_tem_high="0D 18"#制冷停止温度，制冷优先
        # self.cold_stop_tem_low = "0D 01"  # 制冷停止温度，制冷优先
        # self.hot_start_commond_hot = "0D 06 00 02 01 04 28 95"  # 加热停止温度--制热模式下,没用到
        # self.hot_start_commond_cold = "0D 06 00 00 01 18 88 9C"  # 制冷停止温度--制热模式下，没用到
        # self.cold_start_commond_hot = "0D 06 00 02 00 c4 29 55"  # 加热停止温度--制冷模式下，没用到
        # self.cold_start_commond_cold = "0D 06 00 00 00 96 09 68"  # 制冷停止温度--制冷模式下，没用到
        # self.hot_mode_commond = "0D 03 00 02 00 01 25 06"  # 加热模式是否运行
        # self.code_mode_commond = "0D 03 00 01 00 01 D5 06"  # 制冷模式是否运行
        self._alarm_open = "0D 06 04 12 00 00 28 33"  # 开警报(蜂鸣器)
        self._close_alarm = "0D 06 04 12 00 01 E9 F3"  # 关闭警报(蜂鸣器)

        self._read_humidity = "0D 03 04 0A 00 01 A5 F4"  # 读取设置的除湿值
        self._read_hot_stop_tem_to = "0D 03 04 09 00 01 55 F4"  # 读取加热停止温度上限
        self._read_hot_stop_tem_from = "0D 03 04 08 00 01 04 34"  # 读取加热停止温度下限
        self._read_cold_stop_tem = "0D 04 00 00 01 C9 31"  # 读取制冷停止温度
        self._read_cold_sensitivity_tem = "0D 03 04 04 00 01 C4 37"  # 读取制冷灵敏度、温控回差

        self._com_serial = ComSerial.get_com_serial(BusinessConstant.USB_AIRCONITION)

        # 关机：0D 06 04 0F 00 01 79 F5
        # 开机：0D 06 04 0F 00 00 B8 35
        # 制冷最高温度：0D 06 04 03 温度(占2字节）
        # 制冷最低温度：0D 06 04 02 温度(占2字节）
        # 制热最高温度：0D 06 04 09 温度
        # 制热最低温度：0D 06 04 08 温度

    def openAircondition(self):
        """
        打开空调
        """
        try:
            self._logger.get_log().info(f"[AirConditionComputerV2.openAircondition]空调打开-开始")
            BusinessUtil.open_serial(self._com_serial, self._logger)
            result = BusinessUtil.execute_command_hex(self._open_command, self._com_serial, self._logger,
                                                      is_hex=True, byte_size=8)
            result = BusinessUtil.reset_write_result(result,self._open_command)
            self._logger.get_log().info(f"[AirConditionComputerV2.openAircondition]空调打开-结束,返回结果为:{result}")
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[AirConditionComputerV2.openAircondition]空调打开-异常,异常信息为:{str(ex)}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def closeAircondition(self):
        """
        关闭空调
        """
        try:
            self._logger.get_log().info(f"[AirConditionComputerV2.closeAircondition]空调关闭-开始")
            BusinessUtil.open_serial(self._com_serial, self._logger)
            result = BusinessUtil.execute_command_hex(self._close_command, self._com_serial, self._logger,
                                                      is_hex=True, byte_size=8)
            result = BusinessUtil.reset_write_result(result, self._open_command)
            self._logger.get_log().info(f"[AirConditionComputerV2.closeAircondition]空调关闭-结束,返回结果为:{result}")
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[AirConditionComputerV2.closeAircondition]空调关闭-异常,异常信息为:{str(ex)}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def openHotMode(self):
        """
        开启加热模式
        """
        pass

    def closeHotMode(self):
        """
        关闭加热模式
        """
        pass

    def openCodeMode(self):
        """
        开启制冷模式
        """
        pass

    def closeCodeMode(self):
        """
        关闭制冷模式
        """
        pass

    def setHotStopTem(self, stop_tem):
        pass

    def setHotStopTemTo(self, stop_tem, sens_tem):
        """
        设置加热停止温度上限
        """
        # try:
        #     self._logger.get_log().info(f"[AirConditionComputerV2.setHotStopTemTo]设置空调制热停止温度上限-开始,设置值停止温度为:{stop_tem},灵敏度为:{sens_tem}")
        #     stop_tem = (int(stop_tem) + int(sens_tem)) * 10
        #     stop_tem_x = BusinessUtil.int_to_hexByteString(stop_tem, 2)
        #     commond = "0D 06 04 09 " + stop_tem_x
        #     commond = commond + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(commond)))
        #     # comm_read = "0D 03 04 09 00 01 55 F4"
        #     # comm_read = comm_read + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(comm_read)))
        #     # print(f"hot stop commond {commond},read-commond {comm_read}")
        #     self.sendcommond(commond)
        #     time.sleep(5)  # 强制等待50秒
        #     # 读取加热停止温度 TODO 解析result
        #     result = self.sendcommond(self.read_hot_stop_tem_to)
        #     result = BusinessUtil.reset_read_result(result)
        #     if result == BusinessConstant.ERROR or result == BusinessConstant.BUSY:
        #         self.logger.operate_log(
        #             f"[setHotStopTemTo]设置空调制热停止温度上限-结束,设置值停止温度为:{stop_tem},灵敏度为:{sens_tem},返回值为:{result}")
        #         return result
        #     else:
        #         # self.logger.operate_log(f"[setHotStopTemTo]设置加热停止温度上限-读取制热返回值{result}")
        #         result = BusinessUtil.get_int_data_from_serial(result) / 10
        #         self.airstate.set_hot_stop_tem_to(result)
        #     self.logger.operate_log(
        #         f"[setHotStopTemTo]设置空调制热停止温度上限-结束,设置值停止温度为:{stop_tem},灵敏度为:{sens_tem},返回值为:{result}")
        #     return BusinessConstant.SUCCESS
        # except Exception as ex:
        #     self.logger.fault_log(f"[setHotStopTemTo]设置空调制热停止温度上限-异常，异常信息为:{str(ex)}")
        #     return BusinessConstant.ERROR
        pass

    def setHotStopTemFrom(self, stop_tem, sens_tem):
        """
        设置加热停止温度下限
        """
        # try:
        #     self.logger.operate_log(f"[setHotStopTemFrom]设置空调制热停止温度下限-开始,设置值停止温度为:{stop_tem},灵敏度为:{sens_tem}")
        #     time.sleep(BusinessConstant.COMMAND_WAIT_TIME)
        #     stop_tem = (int(stop_tem) - int(sens_tem)) * 10
        #     stop_tem_x = BusinessUtil.int_to_hexByteString(stop_tem, 2)
        #     commond = "0D 06 04 08 " + stop_tem_x
        #     commond = commond + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(commond)))
        #     # comm_read = "0D 03 04 08 " + stop_tem_x
        #     # comm_read = comm_read + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(comm_read)))
        #     # print(f"hot stop commond {commond},read-commond {comm_read}")
        #     self.sendcommond(commond)
        #     time.sleep(5)  # 强制等待50秒
        #     # 读取加热停止温度 TODO 解析result
        #     result = self.sendcommond(self.read_hot_stop_tem_from)
        #     result = BusinessUtil.reset_read_result(result)
        #     if result == BusinessConstant.ERROR or result == BusinessConstant.BUSY:
        #         self.logger.operate_log(
        #             f"[setHotStopTemFrom]设置空调制热停止温度下限-结束,设置值停止温度为:{stop_tem},灵敏度为:{sens_tem},返回值为:{result}")
        #         return result
        #     else:
        #         # self.logger.operate_log(f"[setHotStopTemFrom]读取制热返回值{result}")
        #         result = BusinessUtil.get_int_data_from_serial(result) / 10
        #         self.airstate.set_hot_stop_tem_from(result)
        #     self.logger.operate_log(
        #             f"[setHotStopTemFrom]设置空调制热停止温度下限-结束,设置值停止温度为:{stop_tem},灵敏度为:{sens_tem},返回值为:{result}")
        #     return BusinessConstant.SUCCESS
        # except Exception as ex:
        #     self.logger.fault_log(f"[setHotStopTemFrom]设置空调制热停止温度下限-异常,异常信息为:{str(ex)}")
        #     return BusinessConstant.ERROR
        pass

    def setColdStopTem(self, stop_tem):
        """
        设置制冷停止温度
        """
        try:
            self._logger.get_log().info(f"[AirConditionComputer.setColdStopTem]空调制冷停止温度设置-开始,设置值为:{stop_tem}")
            BusinessUtil.open_serial(self._com_serial, self._logger)
            stop_tem = int(stop_tem) * 10
            stop_tem_x = BusinessUtil.int_to_hexByteString(stop_tem, 2)
            command = "0D 06 04 00 " + stop_tem_x
            command = command + " " + str(ModbusUtils.calculate_crc16(bytes.fromhex(command)))
            result = BusinessUtil.execute_command_hex(command, self._com_serial, self._logger, is_hex=True,byte_size=8)
            time.sleep(5)  # 强制等待50秒
            # 读取制冷停止温度 TODO 解析result
            result = BusinessUtil.execute_command_hex(self._read_cold_stop_tem, self._com_serial, self._logger, is_hex=True, byte_size=8)
            result = BusinessUtil.reset_read_result(result)
            if result == BusinessConstant.ERROR or result == BusinessConstant.BUSY:
                self._logger.get_log().info(f"[AirConditionComputer.setColdStopTem]空调制冷停止温度设置-结束,设置值为:{stop_tem},返回值{result}")
                return result
            else:
                result = BusinessUtil.get_int_data_from_serial(result) / 10
            self._logger.get_log().info(f"[AirConditionComputer.setColdStopTem]空调制冷停止温度设置-结束,设置值为:{stop_tem},返回值{result}")
            return BusinessConstant.SUCCESS
        except Exception as ex:
            self._logger.get_log().info(f"[AirConditionComputer.setColdStopTem]空调制冷停止温度设置-异常,异常信息为:{str(ex)}")
            return BusinessConstant.ERROR

    def setColdSensitivityTem(self, sens_tem):
        """
        设置制冷灵敏温度
        """
        try:
            self._logger.get_log().info(f"[AirConditionComputer。setColdSensitivityTem]空调制冷灵敏度设置-开始,设置值为:{sens_tem}")
            stop_tem_x = BusinessUtil.int_to_hexByteString(int(sens_tem), 2)
            command = "0D 06 04 04 " + stop_tem_x
            command = command + " " + str(ModbusUtils.calculate_crc16(bytes.fromhex(command)))
            result = BusinessUtil.execute_command_hex(command, self._com_serial, self._logger, is_hex=True,byte_size=8)
            time.sleep(5)  # 强制等待50秒
            # 读取制冷灵敏温度 TODO 解析result
            result = BusinessUtil.execute_command_hex(self._read_cold_sensitivity_tem, self._com_serial, self._logger,
                                                      is_hex=True, byte_size=8)
            result = BusinessUtil.reset_read_result(result)
            if result == BusinessConstant.ERROR or result == BusinessConstant.BUSY:
                self._logger.get_log().info(f"[AirConditionComputer。setColdSensitivityTem]空调制冷灵敏度设置-开始,设置值为:{sens_tem},返回值{result}")
                return result
            else:
                result = BusinessUtil.get_int_data_from_serial(result)/10
            self._logger.get_log().info(f"[AirConditionComputer。setColdSensitivityTem]空调制冷灵敏度设置-开始,设置值为:{sens_tem},返回值{result}")
            return BusinessConstant.SUCCESS
        except Exception as ex:
            self._logger.get_log().info(f"[AirConditionComputer。setColdSensitivityTem]空调制冷灵敏度设置-异常,异常信息为:{str(ex)}")
            return BusinessConstant.ERROR

    def setHumidity(self, humidity):
        """
        设置湿度值
        """
        # try:
        #     self.logger.operate_log(f"[setHumidity]设置空调开始除湿的湿度值-开始,设置值为:{humidity}")
        #     time.sleep(BusinessConstant.COMMAND_WAIT_TIME)
        #     stop_tem_x = BusinessUtil.int_to_hexByteString(int(humidity), 2)
        #     commond = "0D 06 04 0A " + stop_tem_x
        #     commond = commond + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(commond)))
        #     # comm_read = "0D 03 04 04 " + stop_tem_x
        #     # comm_read = comm_read + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(comm_read)))
        #     # print(f"code sens commond {commond},read-commond {comm_read}")
        #     self.sendcommond(commond)
        #     time.sleep(5)  # 强制等待50秒
        #     # 读取制冷灵敏温度 TODO 解析result
        #     result = self.sendcommond(self.read_humidity)
        #     result = BusinessUtil.reset_read_result(result)
        #     if result == BusinessConstant.ERROR or result == BusinessConstant.BUSY:
        #         self.logger.operate_log(f"[setHumidity]设置空调开始除湿的湿度值-开始,设置值为:{humidity},返回值{result}")
        #         return result
        #     else:
        #         result = BusinessUtil.get_int_data_from_serial(result)/10
        #         self.airstate.set_open_humidity(result)
        #     self.logger.operate_log(f"[setHumidity]设置空调开始除湿的湿度值-开始,设置值为:{humidity},返回值{result}")
        #     return BusinessConstant.SUCCESS
        # except Exception as ex:
        #     self.logger.fault_log(f"[setHumidity]设置空调开始除湿的湿度值-异常,异常信息为:{str(ex)}")
        #     return BusinessConstant.ERROR
        pass

    def setHotSensitivityTem(self, sens_tem):
        pass

    def setHiHumidityAlarm(self, humidity):
        """
        设置高湿度报警湿度
        """
        pass

    def setLowHumidityAlarm(self, humidity):
        """
        设置低湿度报警湿度
        """
        pass

    def setAirconditonAlarmOpen(self):
        """
        开启空调报警模式
        """
        # try:
        #     self.logger.operate_log(f"[setAirconditonAlarmOpen]开启报警-开始")
        #     result = self.sendcommond(self.alarm_open)
        #     result = BusinessUtil.reset_write_result(result, self.alarm_open)
        #     self.logger.operate_log(f"[setAirconditonAlarmOpen]开启报警-结束,返回结果为:{result}")
        #     return result
        # except Exception as ex:
        #     self.logger.operate_log(f"[setAirconditonAlarmOpen]开启报警-异常,异常信息为:{str(ex)}")
        #     return BusinessConstant.ERROR
        pass

    def setAirConditionAlarmClose(self):
        """
        关闭空调报警模式
        """
        # try:
        #     self.logger.operate_log(f"[setAirConditionAlarmClose]关闭报警-开始")
        #     time.sleep(BusinessConstant.COMMAND_WAIT_TIME)
        #     result = self.sendcommond(self.close_alarm)
        #     result = BusinessUtil.reset_write_result(result, self.alarm_open)
        #     self.logger.operate_log(f"[setAirConditionAlarmClose]关闭报警-结束,返回结果为:{result}")
        #     return result
        # except Exception as ex:
        #     self.logger.operate_log(f"[setAirConditionAlarmClose]开启报警-异常,异常信息为:{str(ex)}")
        #     return BusinessConstant.ERROR
        pass


if __name__ == '__main__':
    commond = "0D 06 00 2f 00 01 79 0F"
    print(bytes.fromhex(commond))
