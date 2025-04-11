# -*- coding: utf-8 -*- 
# @Time : 2024/2/18 11:41 
# @Author : ZKL 
# @File : JKDownVersion.py
'''
获取下位机版本号
'''
import BASEUtile.BusinessUtil as BusinessUtil
import USBDevice.USBDeviceConfig as USBDeviceConfig
import USBDevice.ComSerial as ComSerial
import BASEUtile.BusinessConstant as BusinessConstant


class DownVersion:
    def __init__(self, logger):
        self._logger = logger
        self._com_serial = ComSerial.get_com_serial(BusinessConstant.USB_DOOR)

    def get_down_version(self):
        '''
        获取下位机版本号
        '''
        #  常量/参数部分
        recv_text = "03"  # 下发指令
        result = "unknown"
        try:
            self._logger.get_log().info(f"[DownVersion.get_down_version]下位机版本获取-开始")
            #  对下位机进行操作
            # statCom_door = JKSATACOM(USBDeviceConfig.get_serial_usb_door(),
            #                          USBDeviceConfig.get_serial_bps_door(), USBDeviceConfig.get_serial_timeout_door(),
            #                          self.logger,
            #                          0)  # 操作的实例
            # self.jkdoor = JKDoorServer(statCom_door, self.logger)  # 控制对象
            # result = self.jkdoor.operator_hanger(recv_text)  # 执行命令
            # self.comstate_flag.set_door_free()  # 串口设置没有在使用
            BusinessUtil.open_serial(self._com_serial, self._logger)
            down_command = recv_text + "\r\n"
            result = BusinessUtil.execute_command(down_command, self._com_serial, self._logger, is_hex=False,
                                                  byte_size=4)
        except Exception as e:
            # self.comstate_flag.set_door_free()  # 串口设置没有在使用
            self._logger.get_log().info(f"执行命令{recv_text}发生异常，{e}")
            result = "unknown"
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)
        self._logger.get_log().info(f"[DownVersion.get_down_version]下位机版本获取-结束,返回结果为:{result}")
        return result
