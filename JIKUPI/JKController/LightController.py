# -*- coding: utf-8 -*- 
# @Time : 2023/1/3 14:54 
# @Author : ZKL 
# @File : LightController.py
# @Des : 夜航灯的打开和关闭
import time

import BASEUtile.Config as Config
import USBDevice.USBDeviceConfig as USBDeviceConfig
import USBDevice.ComSerial as ComSerial
import BASEUtile.BusinessUtil as BusinessUtil
import BASEUtile.BusinessConstant as BusinessConstant


class LightController:
    def __init__(self, logger):
        self._logger = logger
        self._com_serial = ComSerial.get_com_serial(BusinessConstant.USB_DOOR)

    def open_light(self):
        '''
        打开夜航灯
        '''
        #  夜灯流程进入判断
        recv_text = "400000" + "\r\n"
        result = ""
        # config = Config()
        night_light = Config.get_is_night_light()  # 是否启动夜灯功能
        night_light_time = Config.get_is_night_light_time()  # 是否判断夜灯时间段
        hour = int(time.strftime("%H", time.localtime()))  # 当前系统时间小时数
        night_light_time_begin = int(Config.get_night_light_time_begin())
        night_light_time_end = int(Config.get_night_light_time_end())
        #  运行夜灯功能，且当前小时在业务配置的时间段内d
        self._logger.get_log().info(f"[LightController.open_light]机库夜灯打开-开始")
        if (night_light and (night_light_time_begin <= hour or night_light_time_end >= hour)) or (
                night_light and night_light_time == False):
            try:
                # 打开夜灯判断
                self._logger.get_log().info(
                    f"[LightController.open_light]机库夜灯打开,开始时间:{night_light_time_begin},结束时间:{night_light_time_end},当前时间:{hour}")
                self._logger.get_log().info(
                    f"[LightController.open_light]机库夜灯打开,是否启动夜灯:{night_light},是否开启夜灯时间段:{night_light_time}")
                # result = self.step_scene_night_light_open_400000()
                BusinessUtil.open_serial(self._com_serial, self._logger)
                result = BusinessUtil.execute_command(recv_text, self._com_serial, self._logger, is_hex=False,
                                                      byte_size=4)
                self._logger.get_log().info(f"[LightController.open_light]机库夜灯打开-结束,返回值为:{result}")
                # if not result.endswith("0"):
                #     # 末尾不为0，返回拼装8位错误码
                #     result = recv_text + result
                #     self._logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                #     return result
                # else:
                #     HangarState.set_night_light_state("open")
            except Exception as ex:
                self._logger.get_log().info(f"[LightController.open_light]机库夜灯打开-异常,异常信息:{str(ex)}")
                return BusinessConstant.ERROR
            finally:
                BusinessUtil.close_serial(self._com_serial, self._logger)
        else:
            self._logger.get_log().info(f"[LightController.open_light]机库夜灯打开-结束,根据配置,无需打开夜灯")
        return result

    def close_light(self):
        '''
        关闭夜航灯
        '''
        #  夜灯流程进入判断
        recv_text = "410000" + "\r\n"
        result = ""
        night_light = Config.get_is_night_light()  # 是否启动夜灯功能
        #  运行夜灯功能，且当前小时在业务配置的时间段内
        self._logger.get_log().info(f"[LightController.close_light]机库夜灯关闭-开始")
        if night_light:
            try:
                # result = self.step_scene_night_light_open_400000()
                BusinessUtil.open_serial(self._com_serial, self._logger)
                result = BusinessUtil.execute_command(recv_text, self._com_serial, self._logger, is_hex=False,
                                                      byte_size=4)
                self._logger.get_log().info(f"[LightController.close_light]机库夜灯关闭-结束,返回值为:{result}")
                # if not result.endswith("0"):
                #     # 末尾不为0，返回拼装8位错误码
                #     result = recv_text + result
                #     self._logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                #     return result
                # else:
                #     HangarState.set_night_light_state("open")
            except Exception as ex:
                self._logger.get_log().info(f"[LightController.close_light]机库夜灯关闭-异常,异常信息:{str(ex)}")
                return BusinessConstant.ERROR
            finally:
                BusinessUtil.close_serial(self._com_serial, self._logger)
        else:
            self._logger.get_log().info(f"[LightController.close_light]机库夜灯关闭-结束,根据配置,无需关闭夜灯")
        return result
