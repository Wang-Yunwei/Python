# -*- coding: utf-8 -*- 
# @Time : 2023/3/21 17:50 
# @Author : ZKL 
# @File : AirConditionComputer.py
'''
做空调的基础操作部分
'''
import binascii
import time

import serial

import BASEUtile.ModbusUtils
from SATA.SATACom import JKSATACOM
import SerialUsedStateFlag as SerialUsedStateFlag
import AirCondition.AirConditionState as AirConditionState
import USBDevice.USBDeviceConfig as USBDeviceConfig
import USBDevice.ComSerial as ComSerial
import BASEUtile.BusinessUtil as BusinessUtil
import BASEUtile.BusinessConstant as BusinessConstant


class AirConditionComputer:
    '''
    (1)空调的开关机
    (2)空调加热模式开启
    (3)制冷模式开启
    (4)加热停止温度
    (5）制冷停止温度
    (6)空调报警开、关
    '''

    def __init__(self, logger):
        # self.state=state
        # self.comconfig = comconfig
        self._logger = logger
        # self.airstate=airstate
        self.open_command = "0D 06 00 2f 00 01 79 0F"
        self.close_commond = "0D 06 00 2f 00 00 B8 CF"
        self.system_running_commond = "0D 02 00 07 00 01 08 C7"  # 系统运行状态
        self.hot_stop_tem_high = "0D 04"  # 加热停止温度当前260度(26)
        self.hot_stop_tem_low = "0D c4"  # -6度
        self.cold_stop_tem_high = "0D 18"  # 制冷停止温度，制冷优先
        self.cold_stop_tem_low = "0D 01"  # 制冷停止温度，制冷优先
        self.hot_start_commond_hot = "0D 06 00 02 01 04 28 95"
        self.hot_start_commond_cold = "0D 06 00 00 01 18 88 9C"
        self.cold_start_commond_hot = "0D 06 00 02 00 c4 29 55"
        self.cold_start_commond_cold = "0D 06 00 00 00 96 09 68"
        self.hot_mode_commond = "0D 02 00 03 00 01 49 06"  # 加热模式是否运行
        self.code_mode_commond = "0D 02 00 02 00 01 18 C6"  # 制冷模式是否运行
        self.alarm_open = "0D 06 00 18 00 01 C8 C1"  # 开警报
        self.close_alarm = "0D 06 00 18 00 00 09 01"  # 关闭警报
        self.comstate = None
        # self._init_comstate()
        self._com_serial = ComSerial.get_com_serial(BusinessConstant.USB_AIRCONITION)

    # def _init_comstate(self):
    #     try:
    #         self.comstate = serial.Serial(
    #             timeout=USBDeviceConfig.get_serial_timeout_aircondition(),
    #             port=USBDeviceConfig.get_serial_usb_aircondition(),
    #             baudrate=USBDeviceConfig.get_serial_bps_aircondition(),
    #             parity=USBDeviceConfig.get_serial_parity_aircondition(),  # 可以不写
    #             stopbits=USBDeviceConfig.get_serial_parity_aircondition(),  # 可以不写
    #             bytesize=USBDeviceConfig.get_serial_bytesize_aircondition())  # 可以不写
    #     except Exception as ex:
    #         self._logger.get_log().info(f"[AirConditionOper._init_comstate]初始化串口异常,异常信息为:{ex}")

    def hexShow(self, argv):
        '''
        十六进制去除特殊字符
        '''
        hLen = len(argv)
        out_s = ''
        for i in range(hLen):
            out_s = out_s + '{:02X}'.format(argv[i]) + ' '
        return out_s

    def openAircondition(self):
        '''
        打开空调
        '''
        # if not SerialUsedStateFlag.get_is_used_serial_weather():
        #     SerialUsedStateFlag.set_used_serial_weather()
        #     time.sleep(3)
        # else:
        #     return "busy"
        try:
            # comstate=# 配置串口基本参数并建立通信
            # comstate = serial.Serial(
            #     timeout=USBDeviceConfig.get_serial_timeout_aircondition(),
            #     port=USBDeviceConfig.get_serial_usb_aircondition(),
            #     baudrate=USBDeviceConfig.get_serial_bps_aircondition(),
            #     parity=USBDeviceConfig.get_serial_parity_aircondition(),  # 可以不写
            #     stopbits=USBDeviceConfig.get_serial_parity_aircondition(),  # 可以不写
            #     bytesize=USBDeviceConfig.get_serial_bytesize_aircondition())  # 可以不写
            self.sendcommand(self.open_command)
            time.sleep(5)
            result = self.readCommonFunSingle(self.system_running_commond)
            if result == BusinessConstant.ERROR:
                return BusinessConstant.ERROR
            if AirConditionState.get_is_system_running() == "1":
                return BusinessConstant.SUCCESS
            else:
                return BusinessConstant.ERROR
        except Exception as ex:
            self._logger.get_log().info(f"[AirConditionComputer.openAircondition]空调打开-异常,异常信息:{str(ex)}")
            return BusinessConstant.ERROR
            # SerialUsedStateFlag.set_used_serial_free_weather()
            # print(f"异常---{ex}")
        # finally:
        #     SerialUsedStateFlag.set_used_serial_free_weather()

    def closeAircondition(self):
        '''
        关闭空调
        '''
        # if not SerialUsedStateFlag.get_is_used_serial_weather():
        #     SerialUsedStateFlag.set_used_serial_weather()
        #     time.sleep(3)
        # else:
        #     return "busy"
        try:
            # comstate=# 配置串口基本参数并建立通信
            # comstate = serial.Serial(
            #     timeout=self.comconfig.get_serial_timeout_aircondition(),
            #     port=self.comconfig.get_serial_usb_aircondition(),
            #     baudrate=self.comconfig.get_serial_bps_aircondition(),
            #     parity=serial.PARITY_EVEN,  # 可以不写
            #     stopbits=serial.STOPBITS_ONE,  # 可以不写
            #     bytesize=serial.EIGHTBITS)  # 可以不写
            self.sendcommand(self.close_commond)
            time.sleep(5)
            result = self.readCommonFunSingle(self.system_running_commond)
            if result == BusinessConstant.ERROR:
                return BusinessConstant.ERROR
            if AirConditionState.get_is_system_running() == "0":
                return BusinessConstant.SUCCESS
            else:
                return BusinessConstant.ERROR
        except Exception as ex:
            self._logger.get_log().info(f"[AirConditionComputer.closeAircondition]空调关闭-异常,异常信息:{str(ex)}")
            return BusinessConstant.ERROR
        # finally:
        #     SerialUsedStateFlag.set_used_serial_free_weather()

    def openHotMode(self):
        '''
        开启加热模式
        '''
        if not SerialUsedStateFlag.get_is_used_serial_weather():
            SerialUsedStateFlag.set_used_serial_weather()
            time.sleep(3)
        else:
            return BusinessConstant.BUSY
        try:
            # comstate=# 配置串口基本参数并建立通信
            # comstate = serial.Serial(
            #     timeout=self.comconfig.get_serial_timeout_aircondition(),
            #     port=self.comconfig.get_serial_usb_aircondition(),
            #     baudrate=self.comconfig.get_serial_bps_aircondition(),
            #     parity=serial.PARITY_EVEN,  # 可以不写
            #     stopbits=serial.STOPBITS_ONE,  # 可以不写
            #     bytesize=serial.EIGHTBITS)  # 可以不写
            self.sendcommand(self.hot_start_commond_cold)
            time.sleep(5)
            self.sendcommand(self.hot_start_commond_hot)
            time.sleep(5)
            self.readCommonFunSingle(self.hot_mode_commond)
            if AirConditionState.get_is_hot_mode() == "1":
                return BusinessConstant.SUCCESS
            else:
                return BusinessConstant.ERROR
        except Exception as ex:
            print(f"{ex}")
        finally:
            SerialUsedStateFlag.set_used_serial_free_weather()

    def closeHotMode(self):
        '''
        关闭加热模式
        '''
        pass

    def openCodeMode(self):
        '''
        开启制冷模式
        '''
        if not SerialUsedStateFlag.get_is_used_serial_weather():
            SerialUsedStateFlag.set_used_serial_weather()
            time.sleep(3)
        else:
            return BusinessConstant.BUSY
        try:
            # comstate=# 配置串口基本参数并建立通信
            # comstate = serial.Serial(
            #     timeout=self.comconfig.get_serial_timeout_aircondition(),
            #     port=self.comconfig.get_serial_usb_aircondition(),
            #     baudrate=self.comconfig.get_serial_bps_aircondition(),
            #     parity=serial.PARITY_EVEN,  # 可以不写
            #     stopbits=serial.STOPBITS_ONE,  # 可以不写
            #     bytesize=serial.EIGHTBITS)  # 可以不写
            self.sendcommand(self.cold_start_commond_cold)
            time.sleep(5)
            self.sendcommand(self.cold_start_commond_hot)
            time.sleep(5)
            self.readCommonFunSingle(self.code_mode_commond)
            time.sleep(50)  # 强制等待50秒
            if AirConditionState.get_is_cold_mode() == "1":
                return BusinessConstant.SUCCESS
            else:
                return BusinessConstant.ERROR
        except Exception as ex:
            print(f"{ex}")
        finally:
            SerialUsedStateFlag.set_used_serial_free_weather()

    def closeCodeMode(self):
        '''
        关闭制冷模式
        '''
        pass

    def setHotStopTem(self, stop_tem):
        '''
        设置加热停止温度
        '''
        stop_tem = int(stop_tem)
        stop_tem_x = hex(stop_tem * 10)[2:]
        if len(str(stop_tem_x)) == 1:
            stop_tem_x = "00 0" + stop_tem_x
        elif len(str(stop_tem_x)) == 2:
            stop_tem_x = "00 " + stop_tem_x
        elif len(str(stop_tem_x)) == 3:
            stop_tem_x = "0" + str(stop_tem_x)[:1] + " " + str(stop_tem_x)[1:]
        elif len(str(stop_tem_x)) == 4:
            stop_tem_x = str(stop_tem_x)[:2] + " " + str(stop_tem_x)[2:]
        else:
            return BusinessConstant.ERROR
        commond = "0D 06 00 02 " + stop_tem_x
        commond = commond + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(commond)))
        comm_read = "0D 03 00 02 " + stop_tem_x
        comm_read = comm_read + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(comm_read)))
        print(f"hot stop commond {commond},read-commond {comm_read}")
        if not SerialUsedStateFlag.get_is_used_serial_weather():
            SerialUsedStateFlag.set_used_serial_weather()
            time.sleep(3)
        else:
            return BusinessConstant.BUSY
        try:
            # comstate=# 配置串口基本参数并建立通信
            # comstate = serial.Serial(
            #     timeout=self.comconfig.get_serial_timeout_aircondition(),
            #     port=self.comconfig.get_serial_usb_aircondition(),
            #     baudrate=self.comconfig.get_serial_bps_aircondition(),
            #     parity=serial.PARITY_EVEN,  # 可以不写
            #     stopbits=serial.STOPBITS_ONE,  # 可以不写
            #     bytesize=serial.EIGHTBITS)  # 可以不写
            self.sendcommand(commond)
            time.sleep(5)  # 强制等待50秒
            self.sendcommand(comm_read)
            time.sleep(5)
            # time.sleep(5)  # 强制等待50秒
            return BusinessConstant.SUCCESS
        except Exception as ex:
            print(f"{ex}")
            return BusinessConstant.ERROR
        finally:
            SerialUsedStateFlag.set_used_serial_free_weather()

    def setColdStopTem(self, stop_tem):
        '''
        设置制冷停止温度
        '''
        stop_tem = int(stop_tem)
        stop_tem_x = hex(stop_tem * 10)[2:]
        if len(str(stop_tem_x)) == 1:
            stop_tem_x = "00 0" + stop_tem_x
        elif len(str(stop_tem_x)) == 2:
            stop_tem_x = "00 " + stop_tem_x
        elif len(str(stop_tem_x)) == 3:
            stop_tem_x = "0" + str(stop_tem_x)[:1] + " " + str(stop_tem_x)[1:]
        elif len(str(stop_tem_x)) == 4:
            stop_tem_x = str(stop_tem_x)[:2] + " " + str(stop_tem_x)[2:]
        else:
            return BusinessConstant.ERROR
        commond = "0D 06 00 00 " + stop_tem_x
        commond = commond + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(commond)))
        comm_read = "0D 03 00 00 " + stop_tem_x
        comm_read = comm_read + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(comm_read)))
        print(f"code stop commond {commond},read-commond {comm_read}")
        if not SerialUsedStateFlag.get_is_used_serial_weather():
            SerialUsedStateFlag.set_used_serial_weather()
            time.sleep(3)
        else:
            return BusinessConstant.BUSY
        try:
            # comstate=# 配置串口基本参数并建立通信
            # comstate = serial.Serial(
            #     timeout=self.comconfig.get_serial_timeout_aircondition(),
            #     port=self.comconfig.get_serial_usb_aircondition(),
            #     baudrate=self.comconfig.get_serial_bps_aircondition(),
            #     parity=serial.PARITY_EVEN,  # 可以不写
            #     stopbits=serial.STOPBITS_ONE,  # 可以不写
            #     bytesize=serial.EIGHTBITS)  # 可以不写
            self.sendcommand(commond)
            time.sleep(5)  # 强制等待50秒
            self.sendcommand(comm_read)
            time.sleep(5)  # 强制等待50秒

            return BusinessConstant.SUCCESS
        except Exception as ex:
            self._logger.get_log().info(f"{ex}")
            return BusinessConstant.ERROR
        finally:
            SerialUsedStateFlag.set_used_serial_free_weather()

    def setHotSensitivityTem(self, sens_tem):
        '''
        设置加热灵敏温度
        '''
        sens_tem = int(sens_tem)
        stop_tem_x = hex(sens_tem * 10)[2:]
        if len(str(stop_tem_x)) == 1:
            stop_tem_x = "00 0" + stop_tem_x
        elif len(str(stop_tem_x)) == 2:
            stop_tem_x = "00 " + stop_tem_x
        elif len(str(stop_tem_x)) == 3:
            stop_tem_x = "0" + str(stop_tem_x)[:1] + " " + str(stop_tem_x)[1:]
        elif len(str(stop_tem_x)) == 4:
            stop_tem_x = str(stop_tem_x)[:2] + " " + str(stop_tem_x)[2:]
        else:
            return BusinessConstant.ERROR
        commond = "0D 06 00 03 " + stop_tem_x
        commond = commond + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(commond)))
        comm_read = "0D 03 00 03 " + stop_tem_x
        comm_read = comm_read + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(comm_read)))
        print(f"hot sens commond {commond},read-commond {comm_read}")
        if not SerialUsedStateFlag.get_is_used_serial_weather():
            SerialUsedStateFlag.set_used_serial_weather()
            time.sleep(3)
        else:
            return BusinessConstant.BUSY
        try:
            # comstate=# 配置串口基本参数并建立通信
            # comstate = serial.Serial(
            #     timeout=self.comconfig.get_serial_timeout_aircondition(),
            #     port=self.comconfig.get_serial_usb_aircondition(),
            #     baudrate=self.comconfig.get_serial_bps_aircondition(),
            #     parity=serial.PARITY_EVEN,  # 可以不写
            #     stopbits=serial.STOPBITS_ONE,  # 可以不写
            #     bytesize=serial.EIGHTBITS)  # 可以不写
            self.sendcommand(commond)
            time.sleep(5)  # 强制等待50秒
            self.sendcommand(comm_read)
            time.sleep(5)  # 强制等待50秒
            return BusinessConstant.SUCCESS
        except Exception as ex:
            print(f"{ex}")
            return BusinessConstant.ERROR
        finally:
            SerialUsedStateFlag.set_used_serial_free_weather()

    def setColdSensitivityTem(self, sens_tem):
        '''
        设置制冷灵敏温度
        '''
        sens_tem = int(sens_tem)
        stop_tem_x = hex(sens_tem * 10)[2:]
        if len(str(stop_tem_x)) == 1:
            stop_tem_x = "00 0" + stop_tem_x
        elif len(str(stop_tem_x)) == 2:
            stop_tem_x = "00 " + stop_tem_x
        elif len(str(stop_tem_x)) == 3:
            stop_tem_x = "0" + str(stop_tem_x)[:1] + " " + str(stop_tem_x)[1:]
        elif len(str(stop_tem_x)) == 4:
            stop_tem_x = str(stop_tem_x)[:2] + " " + str(stop_tem_x)[2:]
        else:
            return BusinessConstant.ERROR
        commond = "0D 06 00 01 " + stop_tem_x
        commond = commond + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(commond)))
        comm_read = "0D 03 00 01 " + stop_tem_x
        comm_read = comm_read + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(comm_read)))
        print(f"code sens commond {commond},read-commond {comm_read}")
        if not SerialUsedStateFlag.get_is_used_serial_weather():
            SerialUsedStateFlag.set_used_serial_weather()
            time.sleep(3)
        else:
            return BusinessConstant.BUSY
        try:
            # comstate=# 配置串口基本参数并建立通信
            # comstate = serial.Serial(
            #     timeout=self.comconfig.get_serial_timeout_aircondition(),
            #     port=self.comconfig.get_serial_usb_aircondition(),
            #     baudrate=self.comconfig.get_serial_bps_aircondition(),
            #     parity=serial.PARITY_EVEN,  # 可以不写
            #     stopbits=serial.STOPBITS_ONE,  # 可以不写
            #     bytesize=serial.EIGHTBITS)  # 可以不写
            self.sendcommand(commond)
            time.sleep(5)  # 强制等待50秒
            self.sendcommand(comm_read)
            time.sleep(5)  # 强制等待50秒
            return BusinessConstant.SUCCESS
        except Exception as ex:
            print(f"{ex}")
            return BusinessConstant.ERROR
        finally:
            SerialUsedStateFlag.set_used_serial_free_weather()

    def setHiHumidityAlarm(self, humidity):
        '''
        设置高湿度报警湿度
        '''
        sens_tem = int(humidity)
        stop_tem_x = hex(sens_tem * 10)[2:]
        if len(str(stop_tem_x)) == 1:
            stop_tem_x = "00 0" + stop_tem_x
        elif len(str(stop_tem_x)) == 2:
            stop_tem_x = "00 " + stop_tem_x
        elif len(str(stop_tem_x)) == 3:
            stop_tem_x = "0" + str(stop_tem_x)[:1] + " " + str(stop_tem_x)[1:]
        elif len(str(stop_tem_x)) == 4:
            stop_tem_x = str(stop_tem_x)[:2] + " " + str(stop_tem_x)[2:]
        else:
            return BusinessConstant.ERROR
        commond = "0D 06 00 07 " + stop_tem_x
        commond = commond + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(commond)))
        comm_read = "0D 03 00 07 " + stop_tem_x
        comm_read = comm_read + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(comm_read)))
        print(f"code sens commond {commond},read-commond {comm_read}")
        if not SerialUsedStateFlag.get_is_used_serial_weather():
            SerialUsedStateFlag.set_used_serial_weather()
            time.sleep(3)
        else:
            return BusinessConstant.BUSY
        try:
            # comstate=# 配置串口基本参数并建立通信
            # comstate = serial.Serial(
            #     timeout=self.comconfig.get_serial_timeout_aircondition(),
            #     port=self.comconfig.get_serial_usb_aircondition(),
            #     baudrate=self.comconfig.get_serial_bps_aircondition(),
            #     parity=serial.PARITY_EVEN,  # 可以不写
            #     stopbits=serial.STOPBITS_ONE,  # 可以不写
            #     bytesize=serial.EIGHTBITS)  # 可以不写
            self.sendcommand(commond)
            time.sleep(5)  # 强制等待50秒
            self.sendcommand(comm_read)
            time.sleep(5)  # 强制等待50秒
            return BusinessConstant.SUCCESS
        except Exception as ex:
            print(f"{ex}")
            return BusinessConstant.ERROR
        finally:
            SerialUsedStateFlag.set_used_serial_free_weather()

    def setLowHumidityAlarm(self, humidity):
        '''
        设置低湿度报警湿度
        '''
        sens_tem = int(humidity)
        stop_tem_x = hex(sens_tem * 10)[2:]
        if len(str(stop_tem_x)) == 1:
            stop_tem_x = "00 0" + stop_tem_x
        elif len(str(stop_tem_x)) == 2:
            stop_tem_x = "00 " + stop_tem_x
        elif len(str(stop_tem_x)) == 3:
            stop_tem_x = "0" + str(stop_tem_x)[:1] + " " + str(stop_tem_x)[1:]
        elif len(str(stop_tem_x)) == 4:
            stop_tem_x = str(stop_tem_x)[:2] + " " + str(stop_tem_x)[2:]
        else:
            return BusinessConstant.ERROR
        commond = "0D 06 00 08 " + stop_tem_x
        commond = commond + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(commond)))
        comm_read = "0D 03 00 08 " + stop_tem_x
        comm_read = comm_read + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(comm_read)))
        print(f"code sens commond {commond},read-commond {comm_read}")
        if not SerialUsedStateFlag.get_is_used_serial_weather():
            SerialUsedStateFlag.set_used_serial_weather()
            time.sleep(3)
        else:
            return BusinessConstant.BUSY
        try:
            # comstate=# 配置串口基本参数并建立通信
            # comstate = serial.Serial(
            #     timeout=self.comconfig.get_serial_timeout_aircondition(),
            #     port=self.comconfig.get_serial_usb_aircondition(),
            #     baudrate=self.comconfig.get_serial_bps_aircondition(),
            #     parity=serial.PARITY_EVEN,  # 可以不写
            #     stopbits=serial.STOPBITS_ONE,  # 可以不写
            #     bytesize=serial.EIGHTBITS)  # 可以不写
            self.sendcommand(commond)
            time.sleep(5)  # 强制等待50秒
            self.sendcommand(comm_read)
            time.sleep(5)  # 强制等待50秒
            return BusinessConstant.SUCCESS
        except Exception as ex:
            print(f"{ex}")
            return BusinessConstant.ERROR
        finally:
            SerialUsedStateFlag.set_used_serial_free_weather()

    def setAirconditonAlarmOpen(self):
        '''
        开启空调报警模式
        '''
        if not SerialUsedStateFlag.get_is_used_serial_weather():
            SerialUsedStateFlag.set_used_serial_weather()
            time.sleep(3)
        else:
            return BusinessConstant.BUSY
        try:
            # comstate=# 配置串口基本参数并建立通信
            # comstate = serial.Serial(
            #     timeout=self.comconfig.get_serial_timeout_aircondition(),
            #     port=self.comconfig.get_serial_usb_aircondition(),
            #     baudrate=self.comconfig.get_serial_bps_aircondition(),
            #     parity=serial.PARITY_EVEN,  # 可以不写
            #     stopbits=serial.STOPBITS_ONE,  # 可以不写
            #     bytesize=serial.EIGHTBITS)  # 可以不写
            self.sendcommand(self.alarm_open)
            time.sleep(5)
            return BusinessConstant.SUCCESS
        except Exception as ex:
            print(f"{ex}")
        finally:
            SerialUsedStateFlag.set_used_serial_free_weather()

    def setAirConditionAlarmClose(self):
        '''
        关闭空调报警模式
        '''
        if not SerialUsedStateFlag.get_is_used_serial_weather():
            SerialUsedStateFlag.set_used_serial_weather()
            time.sleep(3)
        else:
            return BusinessConstant.BUSY
        try:
            # comstate=# 配置串口基本参数并建立通信
            # comstate = serial.Serial(
            #     timeout=self.comconfig.get_serial_timeout_aircondition(),
            #     port=self.comconfig.get_serial_usb_aircondition(),
            #     baudrate=self.comconfig.get_serial_bps_aircondition(),
            #     parity=serial.PARITY_EVEN,  # 可以不写
            #     stopbits=serial.STOPBITS_ONE,  # 可以不写
            #     bytesize=serial.EIGHTBITS)  # 可以不写
            self.sendcommand(self.close_alarm)
            time.sleep(5)
            return BusinessConstant.SUCCESS
        except Exception as ex:
            print(f"{ex}")
        finally:
            SerialUsedStateFlag.set_used_serial_free_weather()

    def sendcommand(self, command):
        '''
        发送命令
        '''
        # if self.comstate.isOpen() == False:
        #     self.comstate.open()
        # self.comstate.write(bytes.fromhex(commond))
        # time.sleep(0.1)
        # count = self.comstate.inWaiting()
        # self._logger.get_log().info(f"[AirConditionOper.sendcommond]设置状态,command:{commond},字节数为:{count}")
        # # 数据的接收
        # # 可以根据实际情况做修改，比如：当没有响应传回时，等待+判断
        # if count == 0:
        #     pass
        #     # print('没有响应传回')
        # if count > 0:
        #     data = self.comstate.read(count)
        #     self._logger.get_log().info(f"[AirConditionOper.sendcommond]设置状态,command:{commond},读取结果为:{data}")
        # self.comstate.flushInput()  # 清除缓存区数据,当代码在循环中执行时，不加这句代码会造成count累加
        # self.comstate.close()
        try:
            BusinessUtil.open_serial(self._com_serial, self._logger)
            result = BusinessUtil.execute_command_hex(command, self._com_serial, self._logger, is_hex=True,
                                                      byte_size=0)
            return result
        except Exception as ex:
            self._logger.get_log().info(f"[AirConditionComputer.sendcommand]命令执行-异常,异常信息:{str(ex)}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)


    def readCommonFunSingle(self, command):
        '''
        通用执行方法
        '''
        # if self.comstate.isOpen() == False:
        #     self.comstate.open()
        # self.comstate.write(bytes.fromhex(commond))
        # time.sleep(0.1)
        # count = self.comstate.inWaiting()
        # self._logger.get_log().info(f"[AirConditionOper.readCommonFunSingle]读取状态,command:{commond},字节数为:{count}")
        # # 数据的接收
        # # 可以根据实际情况做修改，比如：当没有响应传回时，等待+判断
        # result = b''
        # if count == 0:
        #     pass
        #     # print('没有响应传回')
        # if count > 0:
        #     result = self.comstate.read(count)
        #     result = bytes.fromhex(self.hexShow(result))
        # self.comstate.flushInput()  # 清除缓存区数据。当代码在循环中执行时，不加这句代码会造成count累加
        # self.comstate.close()
        # self._logger.get_log().info(f"[AirConditionOper.readCommonFunSingle]读取状态,command:{commond},读取结果为:{result}")
        # # print(f"the result is {result}")
        # if result == b'':
        #     pass
        # else:
        #     if len(result) == 0:
        #         if commond == self.system_running_commond:
        #             AirConditionState.set_is_system_running("0")
        #         elif commond == self.hot_mode_commond:
        #             AirConditionState.set_is_hot_mode("0")
        #         elif commond == self.code_mode_commond:
        #             AirConditionState.set_is_cold_mode("0")
        #     else:
        #         result = binascii.b2a_hex(result[3:4]).decode('ascii')  # 获取状态数据
        #         result = str(int(result))
        #         # print(f"the deal result is {result}")
        #         if commond == self.system_running_commond:
        #             AirConditionState.set_is_system_running(result)
        #         elif commond == self.hot_mode_commond:
        #             AirConditionState.set_is_hot_mode(result)
        #         elif commond == self.code_mode_commond:
        #             AirConditionState.set_is_cold_mode(result)
        try:
            BusinessUtil.open_serial(self._com_serial, self._logger)
            result = BusinessUtil.execute_command_hex(command, self._com_serial, self._logger, is_hex=True,
                                                      byte_size=0)
            self._logger.get_log().info(f"[AirConditionComputer.readCommonFunSingle]读取空调状态,command:{command},读取结果为:{result}")
            if result == "":
                pass
            else:
                if len(result) == 0:
                    if command == self.system_running_commond:
                        AirConditionState.set_is_system_running("0")
                    elif command == self.hot_mode_commond:
                        AirConditionState.set_is_hot_mode("0")
                    elif command == self.code_mode_commond:
                        AirConditionState.set_is_cold_mode("0")
                else:
                    result = result[6:8]  # 获取状态数据
                    result = str(int(result))
                    # print(f"the deal result is {result}")
                    if command == self.system_running_commond:
                        AirConditionState.set_is_system_running(result)
                    elif command == self.hot_mode_commond:
                        AirConditionState.set_is_hot_mode(result)
                    elif command == self.code_mode_commond:
                        AirConditionState.set_is_cold_mode(result)
        except Exception as ex:
            self._logger.get_log().info(f"[AirConditionComputer.readCommonFunSingle]命令执行-异常,异常信息:{str(ex)}")
            return BusinessConstant.ERROR
        finally:
            BusinessUtil.close_serial(self._com_serial, self._logger)
