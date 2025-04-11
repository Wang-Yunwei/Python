# -*- coding: utf-8 -*- 
# @Time : 2022/5/17 9:09 
# @Author : ZKL 
# @File : GPSCompute.py
'''
外置机库升降台控制
'''

import time
import struct

from BASEUtile.logger import Logger
import USBDevice.ComSerial as ComSerial
import BASEUtile.BusinessUtil as BusinessUtil
import BASEUtile.BusinessConstant as BusinessConstant


class OutLiftController():
    '''
    控制升降台升和降
    通过RS485协议获取
    '''

    # def __init__(self,state,log):
    #     self.state=state
    #     self._logger=log
    #     self.wait_time=30#等待30秒获取一次GPS数据

    def __init__(self, log):
        # self.state = state
        self._logger = log
        self._com_serial = ComSerial.get_com_serial(BusinessConstant.USB_WEATHER)

    def lift_up(self):
        '''
        升降台抬升
        '''
        try:
            # self.stateflag.set_used_serial_weather()
            self._logger.get_log().info(f"[OutLiftController.lift_up]外挂升降台上升-开始")
            # statCom_wea = JKSATACOM(USBDeviceConfig.get_serial_usb_weather(), USBDeviceConfig.get_serial_bps_weather(),
            #                         USBDeviceConfig.get_serial_timeout_weather(),
            #                         self._logger, None)
            BusinessUtil.open_serial(self._com_serial, self._logger)
            # 下降触点关闭
            commond_down_close = "0B 06 00 01 00 00 D8 A0"
            result = BusinessUtil.execute_command_hex(commond_down_close, self._com_serial, self._logger, is_hex=True)
            result = BusinessUtil.reset_write_result(result, commond_down_close)
            # statCom_wea.engine.Open_Engine()  # 打开串口
            # statCom_wea.engine.Send_data(bytes.fromhex(commond_down_close))
            # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
            # commond_down_result = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
            # statCom_wea.engine.Close_Engine()
            self._logger.get_log().info(f"[OutLiftController.lift_up]外挂升降台上升-下降触点关闭,返回结果为:{result}")
            # self._logger.get_log().info(f"---begin lift up commond_down_result is {commond_down_result}----")
            time.sleep(3)
            # 升降台上升命令
            commond_up = "0B 06 00 00 00 01 48 A0"
            result = BusinessUtil.execute_command_hex(commond_up, self._com_serial, self._logger, is_hex=True)
            # statCom_wea.engine.Open_Engine()  # 打开串口
            # statCom_wea.engine.Send_data(bytes.fromhex(commond_up))
            # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
            # result_up = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
            # statCom_wea.engine.Close_Engine()
            # result_up = bytes.fromhex(self.hexShow(result_up))
            result = BusinessUtil.reset_write_result(result, commond_up)
            self._logger.get_log().info(f"[OutLiftController.lift_up]外挂升降台上升-结束,返回结果为:{result}")
            return result
            # HangarState.set_out_lift_state('up')
            # self.stateflag.set_used_serial_free_weather()
        except Exception as ex:
            # self.stateflag.set_used_serial_free_weather()
            self._logger.get_log().info(f"[OutLiftController.lift_up]外挂升降台上升-异常,异常信息为:{ex}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)

    def lift_down(self):
        '''
        升降台降低
        '''
        try:
            # self.stateflag.set_used_serial_weather()
            # self._logger.get_log().info(f"---begin lift down----")
            # statCom_wea = JKSATACOM(USBDeviceConfig.get_serial_usb_weather(), USBDeviceConfig.get_serial_bps_weather(),
            #                         USBDeviceConfig.get_serial_timeout_weather(),
            #                         self._logger, None)
            self._logger.get_log().info(f"[OutLiftController.lift_down]外挂升降台下降-开始")
            BusinessUtil.open_serial(self._com_serial, self._logger)
            # 上升触点关闭
            commond_up_close = "0B 06 00 00 00 00 89 60"
            result = BusinessUtil.execute_command_hex(commond_up_close, self._com_serial, self._logger, is_hex=True)
            result = BusinessUtil.reset_write_result(result, commond_up_close)
            self._logger.get_log().info(f"[OutLiftController.lift_down]外挂升降台下降-上升触点关闭,返回结果为:{result}")
            # statCom_wea.engine.Open_Engine()  # 打开串口
            # statCom_wea.engine.Send_data(bytes.fromhex(commond_up_close))
            # # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
            # commond_up_result = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
            # statCom_wea.engine.Close_Engine()
            # self._logger.get_log().info(f"---begin lift down commond_up_result is {commond_up_result}----")
            time.sleep(3)
            # 升降台降低指令
            commond_down_open = "0B 06 00 01 00 01 19 60"  #
            result = BusinessUtil.execute_command_hex(commond_down_open, self._com_serial, self._logger, is_hex=True)
            result = BusinessUtil.reset_write_result(result, commond_down_open)
            self._logger.get_log().info(f"[OutLiftController.lift_down]外挂升降台下降-结束,返回结果为:{result}")
            return result
            # statCom_wea.engine.Open_Engine()  # 打开串口
            # statCom_wea.engine.Send_data(bytes.fromhex(commond_down_open))
            # # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
            # commond_down = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
            # statCom_wea.engine.Close_Engine()
            # commond_down = bytes.fromhex(self.hexShow(commond_down))
            # self._logger.get_log().info(f"Lift down result is {commond_down}")
            # HangarState.set_out_lift_state('down')
            # self.stateflag.set_used_serial_free_weather()
        except Exception as ex:
            # self.stateflag.set_used_serial_free_weather()
            self._logger.get_log().info(f"[OutLiftController.lift_down]外挂升降台下降-异常,异常信息为:{ex}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)


if __name__ == "__main__":
    # logger = Logger(__name__)  # 日志记录
    pass
    # wfcstate = WFState()
    # airconstate = AirCondtionState()
    # hangstate = HangarState(wfcstate, airconstate)
    # configini=ConfigIni()
    # ws = OutLiftController(hangstate,logger,configini)
    # ws.lift_up()
    # #启用一个线程
    # ws.start_alarm()
    # ws.stop_alarm()
