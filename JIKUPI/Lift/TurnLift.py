import serial
import BASEUtile.BusinessConstant as BusinessConstant
import time
from SATA.SATACom import JKSATACOM
import serial
import BASEUtile.Config as Config
import BASEUtile.BusinessUtil as BusinessUtil
import USBDevice.USBDeviceConfig as USBDeviceConfig
import USBDevice.ComSerial as ComSerial


class TurnLift:
    def __init__(self, logger):
        self._logger = logger
        self._com_serial = ComSerial.get_com_serial(BusinessConstant.USB_DOOR)

    def turn_lift(self):
        """
        旋转旋转台
        """
        try:
            self._logger.get_log().info(f"[TurnLift.turn_lift]旋转台旋转-开始")
            BusinessUtil.open_serial(self._com_serial, self._logger)
            # 直接调用串口发送命令
            turn_lift_command = Config.get_operation_command_info()[0][11] + "\r\n"
            self._logger.get_log().info(f"[TurnLift.turn_lift]旋转台旋转,旋转命令为{turn_lift_command}")
            result = BusinessUtil.execute_command(turn_lift_command, self._com_serial, self._logger, is_hex=False,
                                                  byte_size=4)
            result = BusinessUtil.reset_write_result(result)
            self._logger.get_log().info(f"[TurnLift.turn_lift]旋转台旋转-结束,返回值为{result}")
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[TurnLift.turn_lift]旋转台旋转-异常,异常信息:{str(ex)}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def turn_lift_wind(self):
        try:
            self._logger.get_log().info(f"[TurnLift.turn_lift_wind]旋转台旋转-开始")
            BusinessUtil.open_serial(self._com_serial, self._logger)
            # 直接调用串口发送命令
            turn_lift_command = self._get_auto_turn_command()
            if turn_lift_command == BusinessConstant.ERROR or turn_lift_command == "":
                self._logger.get_log().info(f"[TurnLift.turn_lift_wind]旋转台风向未获取，无法旋转")
                return BusinessConstant.ERROR
            else:
                turn_lift_command = turn_lift_command + "\r\n"
            self._logger.get_log().info(f"[TurnLift.turn_lift_wind]旋转台旋转,旋转命令为{turn_lift_command}")
            result = BusinessUtil.execute_command(turn_lift_command, self._com_serial, self._logger, is_hex=False,
                                                  byte_size=4)
            result = BusinessUtil.reset_write_result(result)
            self._logger.get_log().info(f"[TurnLift.turn_lift_wind]旋转台旋转,返回值为{result}")
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[TurnLift.turn_lift_wind]旋转台旋转-异常,异常信息:{str(ex)}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def _get_auto_turn_command(self):
        """
        旋转旋转台,根据风向自动旋转
        """
        try:
            self._logger.get_log().info(f"[TurnLift._get_auto_turn_command]根据风向计算旋转角度-开始")
            # 根据风向机选旋转角度，机头需要朝向逆风方向;北向为原点零点,机头方向在北向右测为正，左侧为负
            north_turn_angle = self._config.get_north_turn_angle()
            if self._config.get_wind_dir():
                # wind_direction = self._hangerState.get_winddirection()
                wind_direction = self._hangerState.get_winddirection_turn()
                angle = 0
                if wind_direction == BusinessConstant.WIND_DIRECTION_EAST_NORTH:  # 东北风,右转
                    angle = 45
                elif wind_direction == BusinessConstant.WIND_DIRECTION_EAST:  # 东风，右转
                    angle = 90
                elif wind_direction == BusinessConstant.WIND_DIRECTION_EAST_SOUTH:  # 东南风，右转
                    angle = 135
                elif wind_direction == BusinessConstant.WIND_DIRECTION_SOUTH:  # 南风，右转
                    angle = 180
                elif wind_direction == BusinessConstant.WIND_DIRECTION_WEST_SOUTH:  # 西南风，左转
                    angle = -135
                elif wind_direction == BusinessConstant.WIND_DIRECTION_WEST:  # 西风，左转
                    angle = -90
                elif wind_direction == BusinessConstant.WIND_DIRECTION_WEST_NORTH:  # 西北风，左转
                    angle = -45
                elif wind_direction == BusinessConstant.WIND_DIRECTION_NORTH:  # 北风，不转
                    angle = 0
                turn_angle = angle - north_turn_angle
                if turn_angle >= 0:
                    if turn_angle <= 180:
                        if len(str(turn_angle)) == 1:
                            result = "80100" + str(turn_angle)
                        elif len(str(turn_angle)) == 2:
                            result = "8010" + str(turn_angle)
                        elif len(str(turn_angle)) == 3:
                            result = "801" + str(turn_angle)
                    else:
                        turn_angle = 360 - turn_angle
                        if len(str(turn_angle)) == 1:
                            result = "80200" + str(turn_angle)
                        elif len(str(turn_angle)) == 2:
                            result = "8020" + str(turn_angle)
                        elif len(str(turn_angle)) == 3:
                            result = "802" + str(turn_angle)
                else:
                    if turn_angle >= -180:
                        if len(str(turn_angle)) == 2:
                            result = "80200" + str(abs(turn_angle))
                        elif len(str(turn_angle)) == 3:
                            result = "8020" + str(abs(turn_angle))
                        elif len(str(turn_angle)) == 4:
                            result = "802" + str(abs(turn_angle))
                    else:
                        turn_angle = 360 + turn_angle
                        if len(str(turn_angle)) == 1:
                            result = "80100" + str(turn_angle)
                        elif len(str(turn_angle)) == 2:
                            result = "8010" + str(turn_angle)
                        elif len(str(turn_angle)) == 3:
                            result = "801" + str(turn_angle)
                self._logger.get_log().info(
                    f"[TurnLift._get_auto_turn_command]根据风向计算旋转角度-结束,北向夹角为:{north_turn_angle},风向为:{wind_direction},计算结果：{result}")
                return result
            else:
                self._logger.get_log().info(f"[TurnLift._get_auto_turn_command]旋转台风向开关未打开，无法旋转")
                return BusinessConstant.ERROR
        except Exception as e:
            self._logger.get_log().info(f"[TurnLift._get_auto_turn_command]获取风向-异常,异常信息:{str(e)}")
            return BusinessConstant.ERROR

    def back_lift(self):
        """
        复位旋转旋转台
        """
        try:
            self._logger.get_log().info(f"[TurnLift.back_lift]旋转台回位-开始")
            BusinessUtil.open_serial(self._com_serial, self._logger)
            # 直接调用串口发送命令
            back_lift_command = Config.get_operation_command_info()[0][12] + "\r\n"
            self._logger.get_log().info(f"[TurnLift.back_lift]旋转台回位,旋转命令为{back_lift_command}")
            result = BusinessUtil.execute_command(back_lift_command, self._com_serial, self._logger, is_hex=False,
                                                  byte_size=4)
            result = BusinessUtil.reset_write_result(result)
            self._logger.get_log().info(f"[TurnLift.back_lift]旋转台回位-结束,返回值为{result}")
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[TurnLift.back_lift]旋转台回位-异常,异常信息:{str(ex)}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def get_lift_state(self):
        """
        获取旋转台状态
        """
        try:
            self._logger.get_log().info(f"[TurnLift.get_lift_state]获取旋转台状态-开始")
            BusinessUtil.open_serial(self._com_serial, self._logger)
            # 直接调用串口发送命令
            back_lift_command = "830000" + "\r\n"
            result = BusinessUtil.execute_command(back_lift_command, self._com_serial, self._logger, is_hex=False,
                                                  byte_size=4)
            result = BusinessUtil.reset_write_result(result)
            self._logger.get_log().info(f"[TurnLift.get_lift_state]获取旋转台状态-结束,返回值为{result}")
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[TurnLift.get_lift_state]获取旋转台状态-异常,异常信息:{str(ex)}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)
