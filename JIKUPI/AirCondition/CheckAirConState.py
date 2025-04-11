# -*- coding: utf-8 -*- 
# @Time : 2023/3/21 18:17 
# @Author : ZKL 
# @File : CheckAirConState.py
'''
定时检测空调状态，并将结果写入到空调状态中
'''
import binascii
import threading
import time
import USBDevice.USBDeviceConfig as USBDeviceConfig
import serial

from SATA.SATACom import JKSATACOM
import SerialUsedStateFlag as SerialUsedStateFlag
import AirCondition.AirConditionState as AirConditionState


class CheckAirConState():
    def __init__(self, logger):
        # self.comconfig = comconfig
        # self.state = state
        self.logger = logger
        # self.airstate = airstate
        self.comstate_flag = SerialUsedStateFlag
        self.waittime = 60
        self.system_running_commond = "0D 02 00 07 00 01 08 C7"  # 系统运行状态
        self.inner_tem_commond = "0D 04 00 00 00 02 71 07"  # 柜内温度
        self.inner_hum_commond = "0D 04 00 03 00 02 81 07"  # 柜内湿度
        self.out_tem_commond = "0D 04 00 01 00 02 20 C7"  # 柜外温度
        self.out_hum_commond = "0D 04 00 04 00 02 30 C6"  # 柜外湿度
        self.hot_mode_commond = "0D 02 00 03 00 01 49 06"  # 加热模式是否运行
        self.code_mode_commond = "0D 02 00 02 00 01 18 C6"  # 制冷模式是否运行
        self.innerMachineRun_commond = "0D 02 00 00 00 01 B9 06"  # 柜内风机运行状态
        self.codeArefaction_commond = "0D 02 00 04 00 01 F8 C7"  # 制冷除湿模式是否运行
        self.hotArefaction_commond = "0D 02 00 05 00 01 A9 07"  # 加热除湿模式是否运行
        self.alarmState_commond = "0D 02 00 08 00 01 38 C4"  # 报警状态
        self.innerHotAlarm_commond = "0D 02 00 10 00 01 B8 C3"  # 柜内高温报警状态
        self.innerCodeAlarm_commond = "0D 02 00 11 00 01 E9 03"  # 柜内低温报价状态
        self.innerTemperatureError_commond = "0D 02 00 09 00 01 69 04"  # 柜内温感故障
        self.codeInvalid_commond = "0D 02 00 17 00 01 09 02"  # 柜内制冷失效告警
        self.hotInvalid_commond = "0D 02 00 18 00 01 39 01"  # 制热失效告警

    def hexShow(self, argv):
        '''
        十六进制去除特殊字符
        '''
        hLen = len(argv)
        out_s = ''
        for i in range(hLen):
            out_s = out_s + '{:02X}'.format(argv[i]) + ' '
        return out_s

    def checkAirState(self):
        '''
        启动一个线程，根据读取的状态，修改空调状态
        '''
        threading.Thread(target=self.checkconditon, args=()).start()

    def hex_to_dec(self, hex_str):
        # 把16进制字符串转成带符号10进制
        if hex_str[0] in '0123456789':
            dec_data = int(hex_str, 16)
        else:
            # 负数算法
            width = 32  # 16进制数所占位数
            d = 'FFFF' + hex_str
            dec_data = int(d, 16)
            if dec_data > 2 ** (width - 1) - 1:
                dec_data = 2 ** width - dec_data
                dec_data = 0 - dec_data
        return dec_data

    def checkconditon(self):
        comstate = None
        try:
            # comstate=# 配置串口基本参数并建立通信
            comstate = serial.Serial(
                timeout=USBDeviceConfig.get_serial_timeout_aircondition(),
                port=USBDeviceConfig.get_serial_usb_aircondition(),
                baudrate=USBDeviceConfig.get_serial_bps_aircondition(),
                parity=USBDeviceConfig.get_serial_parity_aircondition(),  # 可以不写
                stopbits=USBDeviceConfig.get_serial_stopbits_aircondition(),  # 可以不写
                bytesize=USBDeviceConfig.get_serial_bytesize_aircondition())  # 可以不写
        except Exception as ex:
            print(ex)
        while True:
            if self.comstate_flag.get_is_used_serial_weather() is False:
                if comstate == None:
                    # comstate=# 配置串口基本参数并建立通信
                    try:
                        # comstate=# 配置串口基本参数并建立通信
                        comstate = serial.Serial(
                            timeout=USBDeviceConfig.get_serial_timeout_aircondition(),
                            port=USBDeviceConfig.get_serial_usb_aircondition(),
                            baudrate=USBDeviceConfig.get_serial_bps_aircondition(),
                            parity=USBDeviceConfig.get_serial_parity_aircondition(),  # 可以不写
                            stopbits=USBDeviceConfig.get_serial_stopbits_aircondition(),  # 可以不写
                            bytesize=USBDeviceConfig.get_serial_bytesize_aircondition())  # 可以不写
                    except Exception as ex:
                        print(ex)
                try:
                    # _________ system_running _________
                    self.commonFunSingle(self.system_running_commond, comstate)
                    # _________ inner_tem_commond _________
                    self.commonFunMul(self.inner_tem_commond, comstate)
                    # _________ inner_hum _________
                    self.commonFunMul(self.inner_hum_commond, comstate)
                    # _________ out_tem _________
                    self.commonFunMul(self.out_tem_commond, comstate)
                    # _________ out_hum _________
                    self.commonFunMul(self.out_hum_commond, comstate)
                    # _________ hot_mode _________
                    self.commonFunSingle(self.hot_mode_commond, comstate)
                    # _________ code_mode _________
                    self.commonFunSingle(self.code_mode_commond, comstate)
                    # _________ innerMachineRun _________
                    self.commonFunSingle(self.innerMachineRun_commond, comstate)
                    # _________ codeArefaction _________
                    self.commonFunSingle(self.codeArefaction_commond, comstate)
                    # _________ hotArefaction _________
                    self.commonFunSingle(self.hotArefaction_commond, comstate)
                    # _________ alarmState _________
                    self.commonFunSingle(self.alarmState_commond, comstate)
                    # _________ innerHotAlarm _________
                    self.commonFunSingle(self.innerHotAlarm_commond, comstate)
                    # _________ innerCodeAlarm _________
                    self.commonFunSingle(self.innerCodeAlarm_commond, comstate)
                    # _________ innerTemperatureError _________
                    self.commonFunSingle(self.innerTemperatureError_commond, comstate)
                    # _________ codeInvalid _________
                    self.commonFunSingle(self.codeInvalid_commond, comstate)
                    # _________ hotInvalid _________
                    self.commonFunSingle(self.hotInvalid_commond, comstate)

                except Exception as ex:
                    comstate = None
                    # time.sleep(self.waittime)
                    print(ex)
            time.sleep(self.waittime)  # 等待后再获取

    def commonFunSingle(self, commond, comstate):
        '''
        通用执行方法
        '''
        if self.comstate_flag.get_is_used_serial_weather():
            comstate.close()
            return
        if comstate.isOpen() == False:
            comstate.open()
        comstate.write(bytes.fromhex(commond))
        time.sleep(0.1)
        count = comstate.inWaiting()
        # 数据的接收
        # 可以根据实际情况做修改，比如：当没有响应传回时，等待+判断
        result = b''
        if count == 0:
            pass
            # print('没有响应传回1')
        if count > 0:
            result = comstate.read(count)
            result = bytes.fromhex(self.hexShow(result))
        comstate.flushInput()  # 清除缓存区数据。当代码在循环中执行时，不加这句代码会造成count累加
        comstate.close()
        if result == b'':
            pass
        else:
            if len(result) == 0:
                if commond == self.system_running_commond:
                    AirConditionState.set_is_system_running("0")
                elif commond == self.hot_mode_commond:
                    AirConditionState.set_is_hot_mode("0")
                elif commond == self.code_mode_commond:
                    AirConditionState.set_is_cold_mode("0")
                elif commond == self.innerMachineRun_commond:
                    AirConditionState.set_is_inner_machine_run("0")
                elif commond == self.codeArefaction_commond:
                    AirConditionState.set_is_cold_arefaction("0")
                elif commond == self.hotArefaction_commond:
                    AirConditionState.set_is_hot_arefaction("0")
                elif commond == self.alarmState_commond:
                    AirConditionState.set_is_alarm_state("0")
                elif commond == self.innerHotAlarm_commond:
                    AirConditionState.set_is_inner_hot_alarm("0")
                elif commond == self.innerCodeAlarm_commond:
                    AirConditionState.set_is_inner_code_alarm("0")
                elif commond == self.innerTemperatureError_commond:
                    AirConditionState.set_is_inner_temperature_error("0")
                elif commond == self.codeInvalid_commond:
                    AirConditionState.set_is_code_invalid("0")
                elif commond == self.hotInvalid_commond:
                    AirConditionState.set_is_hot_invalid("0")
            else:
                result = binascii.b2a_hex(result[3:4]).decode('ascii')  # 获取是否在运行
                result = str(int(result))
                # print(f"{commond} the deal result is {result}")
                if commond == self.system_running_commond:
                    AirConditionState.set_is_system_running(result)
                elif commond == self.hot_mode_commond:
                    AirConditionState.set_is_hot_mode(result)
                elif commond == self.code_mode_commond:
                    AirConditionState.set_is_cold_mode(result)
                elif commond == self.innerMachineRun_commond:
                    AirConditionState.set_is_inner_machine_run(result)
                elif commond == self.codeArefaction_commond:
                    AirConditionState.set_is_cold_arefaction(result)
                elif commond == self.hotArefaction_commond:
                    AirConditionState.set_is_hot_arefaction(result)
                elif commond == self.alarmState_commond:
                    AirConditionState.set_is_alarm_state(result)
                elif commond == self.innerHotAlarm_commond:
                    AirConditionState.set_is_inner_hot_alarm(result)
                elif commond == self.innerCodeAlarm_commond:
                    AirConditionState.set_is_inner_code_alarm(result)
                elif commond == self.innerTemperatureError_commond:
                    AirConditionState.set_is_inner_temperature_error(result)
                elif commond == self.codeInvalid_commond:
                    AirConditionState.set_is_code_invalid(result)
                elif commond == self.hotInvalid_commond:
                    AirConditionState.set_is_hot_invalid(result)

    def commonFunMul(self, commond, comstate):
        '''
        通用执行方法
        '''
        if self.comstate_flag.get_is_used_serial_weather():
            comstate.close()
            return
        if comstate.isOpen() == False:
            comstate.open()
        comstate.write(bytes.fromhex(commond))
        time.sleep(0.1)
        count = comstate.inWaiting()
        # 数据的接收
        # 可以根据实际情况做修改，比如：当没有响应传回时，等待+判断
        result = b''
        if count == 0:
            pass
            # print('没有响应传回2')
        if count > 0:
            result = comstate.read(count)
            result = bytes.fromhex(self.hexShow(result))
        comstate.flushInput()  # 清除缓存区数据。当代码在循环中执行时，不加这句代码会造成count累加
        comstate.close()
        if result == b'':
            pass
        else:
            if len(result) == 0:
                if commond == self.inner_tem_commond:
                    AirConditionState.set_inner_tem("0")
                elif commond == self.inner_hum_commond:
                    AirConditionState.set_inner_hum("0")
                elif commond == self.out_tem_commond:
                    AirConditionState.set_out_tem("0")
                elif commond == self.out_hum_commond:
                    AirConditionState.set_out_hum("0")
            else:
                # print(f"*************{result}")
                if len(result) != 9:
                    # print("---长度不够---")
                    return
                result = binascii.b2a_hex(result[3:5]).decode('ascii')
                if result in ['7FFF', 'FFFF', '7fff', 'ffff', 'c2c1']:
                    # print("---无效---")
                    return
                result = self.hex_to_dec(result) / 10  # 获取柜内温度,注意正负值
                # print(f"---the deal result is {result}----")
                if commond == self.inner_tem_commond:
                    AirConditionState.set_inner_tem(result)
                elif commond == self.inner_hum_commond:
                    AirConditionState.set_inner_hum(result)
                elif commond == self.out_tem_commond:
                    AirConditionState.set_out_tem(result)
                elif commond == self.out_hum_commond:
                    AirConditionState.set_out_hum(result)
