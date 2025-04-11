# -*- coding: utf-8 -*- 
# @Time : 2022/09/19 22:41
# @Author : ZKL 
# @File : JCCServerM300.py
# 黑砂触点充电
'''
处理充电过程中有压差、或者电池有高温等待的时候，要求两个电池能同时充电
'''
import binascii
import math
import threading
import time

# from BASEUtile.loggerColl import LoggerColl
import BASEUtile.Config as Config
from JKController.BarRepeat.JKBarRepeatCharge import JKBarRepeatCharge
from SATA.SATACom import Communication
from SATA.SerialHelp import SerialHelper
import USBDevice.USBDeviceConfig as USBDeviceConfig
from WFCharge.M300VolFit import M300VolFit
import WFCharge.WFState as WFState
import BASEUtile.HangarState as HangarState
from BASEUtile.logger import Logger


class JCCServerV4M350:  # 定义接触充电服务端
    """
    A路开
    01 06 80 00 00 01 61 CA
    A路关
    01 06 80 00 00 02 21 CB

    B路开
    01 06 80 00 00 04 A1 C9
    B路关
    01 06 80 00 00 08 A1 CC

    开机
    01 06 80 00 00 10 A1 C6
    关机
    01 06 80 00 00 20 A1 D2
    读取
    01 04 00 00 00 06 70 08
-------------------------------------------------------
    地址	0x01

    支持04读取指令，如后面3为100 标识有输入，A、B关；后3位为101为B路关，A路开
    0	状态	"bit0: 0 A路充电关 1： A路充电开
    bit1: 0 B路充电关 1： B路充电开
    bit2: 0 IO3输入0   1：IO3输入1
    bit4-bit3: 0,3:未知 1:开机 2:关机  "
    1	模块在线	"bit0: 0 A路采样离线 1： A路采样在线
    bit1: 0 B路采样离线 1： B路采样在线"
    2	A路电压	X100
    3	B路电压	X100
    4	A路电流	X100
    5	B路电流	X100

    支持03读，06，16写指令
    0x8000	命令	"bit1-bit0:1开始A 2停止A  0,3：无动作
    bit1-bit0:1开始B 2停止B  0,3：无动作
    bit1-bit0:1开机   2关机A  0,3：无动作"
    0x8001	RS485地址	0~255，地址默认0x01
    0x8002	RS485波特率	12，24，48，96波特率默认：96
    9600

    """

    def __init__(self,logger):
        # self.hangstate = hangstate
        # self.state = state  # 充电箱当前状态信息
        self.logger = logger
        # self.comconfig = USBDeviceConfig()
        self.engine = Communication(USBDeviceConfig.get_serial_usb_charge(), USBDeviceConfig.get_serial_bps_charge(), 10,
                                    self.logger, None)  # 串口初始化:
        self.iniconfig = Config
        self.pre_model = M300VolFit()
        self.A_waiting = False
        self.B_waiting = False
        self.lowA_times=0 #低电流的次数
        # self.loggercoll=LoggerColl("JCCSERVER2")
        # self.engine = SerialHelper(Port=USBDeviceConfig.get_device_info_chargeV2(), BaudRate=USBDeviceConfig.get_bps_chargeV2(), ByteSize=USBDeviceConfig.get_charge_bytesize_chargeV2(), Parity=USBDeviceConfig.get_charge_parityV2(), Stopbits=USBDeviceConfig.get_charge_stopbitsV2(),
        #                           thresholdValue=1)

    def hex2bin(self, string_num):
        '''
        十六进制字符串转二进制
        :return:10111
        '''
        return bin(int(string_num, 16))[2:].rjust(5, '0')

    def operator_charge(self, commond):
        """
        无线充电操作
        :param commond:
        :return:
        """
        try:
            result = "error"
            if commond == "Standby" or commond == "standby":
                result = self.standby()
            elif commond == "Charge":
                result = self.charge()
                print(f"The first charge result is {result}")
                if self.iniconfig.get_is_repeat_bar() == True:
                    if result == "chargeerror" or result == "error" or result == "chargeerror(null)":  # 充电失败情况下，要重新做一下推杆的打开和失败操作
                        jkbarRepeat = JKBarRepeatCharge(self.logger)
                        if jkbarRepeat.repeat_bar() == False:
                            self.logger.get_log().info(f"充电失败，推杆复位再夹紧失败，充电返回失败")
                            result = "chargeerror"
                        else:  # 夹紧了，可以进行充电操作了
                            result = self.charge()
            elif commond == "TakeOff":
                result = self.takeoff()
            elif commond == "DroneOff":
                result = self.droneoff()
            elif commond == "Check":
                result = self.Check()
            else:
                self.logger.get_log().info(f"输入命令不正确{commond}")
                return 'commond-error'
        except Exception as ex:
            self.logger.get_log().info(f"充电操作异常，{ex}")
            WFState.set_battery_state("unknown")  # 未知状态
            return "exception-error(获取不到下位机充电信息；请确认为2.0版本充电，检查充电硬件设备)"
        # time.sleep(20)
        # result="success"
        return result

    def charge_A(self):
        '''
        开启A电池充电
        commond:"01 06 80 00 00 01 61 CA "
        '''
        commond = "01 06 80 00 00 01 61 CA "
        self.logger.get_log().info(f"发送开启A电池充电指令")
        self.engine = Communication(USBDeviceConfig.get_serial_usb_charge(), USBDeviceConfig.get_serial_bps_charge(),
                                    10, self.logger, None)
        self.engine.Open_Engine()
        self.engine.Send_data(bytes.fromhex(commond))
        time.sleep(5)
        self.engine.Close_Engine()

    def charge_B(self):
        '''
        开启B电池充电
        commond:"01 06 80 00 00 04 A1 C9"
        '''
        commond = "01 06 80 00 00 04 A1 C9"
        self.logger.get_log().info(f"发送开启B电池充电指令")
        self.engine = Communication(USBDeviceConfig.get_serial_usb_charge(), USBDeviceConfig.get_serial_bps_charge(),
                                    10, self.logger, None)
        self.engine.Open_Engine()
        self.engine.Send_data(bytes.fromhex(commond))
        time.sleep(5)
        self.engine.Close_Engine()

    def standby_A(self):
        '''
        停止A电池充电
        commond: "01 06 80 00 00 02 21 CB"
        '''
        commond = "01 06 80 00 00 02 21 CB"
        self.logger.get_log().info(f"发送停止A电池充电指令")
        self.engine = Communication(USBDeviceConfig.get_serial_usb_charge(), USBDeviceConfig.get_serial_bps_charge(),
                                    10, self.logger, None)
        self.engine.Open_Engine()
        self.engine.Send_data(bytes.fromhex(commond))
        time.sleep(5)
        self.engine.Close_Engine()

    def standby_B(self):
        '''
        停止B电池充电
        commond:"01 06 80 00 00 08 A1 CC"
        '''
        commond = "01 06 80 00 00 08 A1 CC "
        self.logger.get_log().info(f"发送停止B电池充电指令")
        self.engine = Communication(USBDeviceConfig.get_serial_usb_charge(), USBDeviceConfig.get_serial_bps_charge(),
                                    10, self.logger, None)
        self.engine.Open_Engine()
        self.engine.Send_data(bytes.fromhex(commond))
        time.sleep(5)
        self.engine.Close_Engine()

    def read_current_bin(self):
        '''
        读取当前状态，二进制返回
        commond:"01 04 00 00 00 06 70 08"
        其中[3:3]为0标识A充电关闭；1标识A充电开启
        其中[4:4]为0标识B充电关闭；1标识B充电开启
        [6:7]为00或者11 标识未知；为01标识开机；为10标识关机
        [7:9]标识A路电压，[9:11]标识B路电压；[11:13]A路电流，[13:15]B路电流
        '''
        commond = "01 04 00 00 00 06 70 08 "
        self.logger.get_log().info(f"发送读取当前充电状态指令")
        self.engine = Communication(USBDeviceConfig.get_serial_usb_charge(), USBDeviceConfig.get_serial_bps_charge(),
                                    10, self.logger, None)
        self.engine.Open_Engine()
        self.engine.Send_data(bytes.fromhex(commond))
        time.sleep(2)
        result = self.engine.Read_Size(17)  # 读取一行数据
        self.engine.Close_Engine()
        showresult = self.hexShow(result)  # 16进制乱码转换
        result = bytes.fromhex(showresult)  # 16进制转成b''
        value = binascii.b2a_hex(result).decode('ascii')  # b''转成ascii码的
        value = self.hex2bin(value)  # 16进制转成2进制
        return value

    def check_charging(self, result):
        '''
        result= bytes.fromhex(showresult)
        每次确定是否在充电，以及如果在充电的时候是否需要等待或待机操作
        [3:4]为11双边充，10A充，01B充
        '''
        value = binascii.b2a_hex(result[3:5]).decode('ascii')  # b''转成ascii码的
        value = self.hex2bin(value)  # 16进制转成2进制
        valueAV = binascii.b2a_hex(result[7:9]).decode('ascii')  # A路电压
        valueBV = binascii.b2a_hex(result[9:11]).decode('ascii')  # B路电压
        valueAA = binascii.b2a_hex(result[11:13]).decode('ascii')  # A路电流
        valueBA = binascii.b2a_hex(result[13:15]).decode('ascii')  # B路电流

        valueAV10 = str(int(valueAV.upper(), 16))  # 10进制表示
        valueBV10 = str(int(valueBV.upper(), 16))  # 10进制表示
        valueAA10 = str(int(valueAA.upper(), 16))  # 10进制表示
        valueBA10 = str(int(valueBA.upper(), 16))  # 10进制表示
        self.logger.get_log().info(
            f"check充电状态，电压、电流值AV is {int(valueAV10) / 100},BV is {int(valueBV10) / 100}，AA is {int(valueAA10) / 100},BA is {int(valueBA10) / 100}")
        # 2023-06-21如果检测到电压值不在有效范围内则舍弃
        if (int(valueAV10) / 100 < 45 or int(valueAV10) / 100 > 53 or int(valueBV10) / 100 < 45 or int(
                valueBV10) / 100 > 53) and int(valueAV10) / 100 != 0 and int(valueBV10) / 100 != 0:
            self.logger.get_log().info(f"获取到的电流电压值不准确，本次丢弃检测")
            return
        # （1）如果是双边充电，需要预测电量，如果电量偏差大，有压差，则终止其中一个充电
        if value[3:5] == "11":  # 双充电
            # (1)如果两边均有电流
            if int(valueAA10) > 0 and int(valueBA10) > 0:
                pre_A = self.pre_model.pre_vol(int(valueAV10) / 100, int(valueAA10) / 100)
                pre_B = self.pre_model.pre_vol(int(valueBV10) / 100, int(valueBA10) / 100)
                #2023-9-27 如果两个电流都很小，则认为满电
                if int(valueAA10)/100<0.5 and int(valueBA10)/100<0.5:#如果预测出的A、B电流都小于0.5则认为满电，断开充电
                    self.logger.get_log().info(
                        f"check充电状态，预测出A、B均满电或降温，{pre_A},{pre_B}")
                    if WFState.get_battery_state() == "charging":  # 如果是充电
                        WFState.set_battery_state("full")
                        WFState.set_battery_value("100")
                        self.standby()  # 2023-9-27 断开操作
                    else:
                        WFState.set_battery_state("full or waiting")
                if pre_A >= pre_B and pre_A != -1 and pre_B != -1:
                    if (pre_A - pre_B) > 8 and pre_A < 65:  # 只有电量小于65的时候才可以断，大于65再启动充电可能无法启动
                        # A、B电量偏差太大，需要断掉A电池充电
                        if self.iniconfig.get_is_blance_charge()== True:
                            self.standby_A()
                            self.A_waiting = True
                            self.logger.get_log().info(
                                f"check充电状态，预测出电量压差过大，{pre_A}，{pre_B},停止A充电")
                        else:
                            self.logger.get_log().info(
                                f"check充电状态，预测出电量压差过大，{pre_A}，{pre_B},没有启用均衡充电，继续双充电")
                    elif (pre_A - pre_B) > 8 and pre_A >= 65:
                        self.logger.get_log().info(
                            f"check充电状态，预测出电量压差过大，A电量大，A电量预测为{pre_A}，但是A电量已经超过65，不断开A充电")
                    WFState.set_battery_value(f"{pre_B}")
                elif pre_A < pre_B and pre_A != -1 and pre_B != -1:
                    if (pre_B - pre_A) > 8 and pre_B < 65:
                        # A、B电量偏差太大，需要断掉B电池充电
                        if self.iniconfig.get_is_blance_charge() == True:
                            self.standby_B()
                            self.B_waiting = True
                            self.logger.get_log().info(
                                f"check充电状态，预测出电量压差过大，{pre_A}，{pre_B},停止B充电")
                        else:
                            self.logger.get_log().info(
                                f"check充电状态，预测出电量压差过大，{pre_A}，{pre_B},没有启用均衡充电，继续双充电")
                    elif (pre_B - pre_A) > 8 and pre_B >= 65:
                        self.logger.get_log().info(
                            f"check充电状态，预测出电量压差过大，A电量大，B电量预测为{pre_B}，但是B电量已经超过65，不断开B充电")
                    WFState.set_battery_value(f"{pre_A}")
                self.logger.get_log().info(
                    f"check充电状态，预测电量为{pre_A},{pre_B},当前电量为{WFState.get_battery_value()}")
                WFState.set_battery_state("charging")
            elif int(valueAA10) > 0:  # 如果只有A充电
                # 预测B电量，如果B不为满电，则B为降温模式，这个时候要断掉A充电，等待B
                pre_A = self.pre_model.pre_vol(int(valueAV10) / 100, int(valueAA10) / 100)
                pre_B = self.pre_model.pre_vol(int(valueBV10) / 100, int(valueBA10) / 100)  # 有可能满电，有可能高温等待
                # if pre_B<100:#B不为满电，断掉A充电
                if WFState.get_battery_state() == "charging":  # B电池满电
                    # self.logger.get_log().info(f"check充电状态，预测出B满电，{pre_B},A继续充电")
                    # WFState.set_battery_state("charging")
                    # WFState.set_battery_value(f"{pre_A}")
                    if int(valueAA10) / 100 < 0.5:  # 如果预测出的A电流都小于0.5则认为满电，断开充电
                        self.logger.get_log().info(
                            f"check充电状态，预测出B满电或降温，A电流小，{pre_A},{pre_B}")
                        if WFState.get_battery_state() == "charging":  # 如果是充电
                            WFState.set_battery_state("full")
                            WFState.set_battery_value("100")
                            self.standby()  # 2023-9-27 断开操作
                        else:
                            WFState.set_battery_state("full or waiting")
                    else:
                        self.logger.get_log().info(f"check充电状态，预测出B满电，{pre_B},A继续充电")
                        WFState.set_battery_state("charging")
                        WFState.set_battery_value(f"{pre_A}")
                elif pre_A < 80 and pre_A != -1:  # 当A电量不满80的时候，认为B是在高温等待；B不为满电，断掉A充电
                    if self.iniconfig.get_is_blance_charge() == True:
                        self.standby_A()
                        self.A_waiting = True
                        self.logger.get_log().info(f"check充电状态，预测出B在等待降温，{pre_B},停止A充电")
                        WFState.set_battery_state("waiting")
                        WFState.set_battery_value(f"{pre_A}")
                    else:
                        WFState.set_battery_state("charging")
                        self.logger.get_log().info(f"check充电状态，预测出B在等待降温，{pre_B},没有启用均衡充电，继续双充电")
                else:  # B为满电
                    # 2023-9-27 如果两个电流都很小，则认为满电
                    if int(valueAA10) / 100 < 0.5:  # 如果预测出的A电流都小于0.5则认为满电，断开充电
                        self.logger.get_log().info(
                            f"check充电状态，预测出B满电或降温，A电流小，{pre_A},{pre_B}")
                        if WFState.get_battery_state() == "charging":  # 如果是充电
                            WFState.set_battery_state("full")
                            WFState.set_battery_value("100")
                            self.standby()  # 2023-9-27 断开操作
                        else:
                            WFState.set_battery_state("full or waiting")
                    else:
                        self.logger.get_log().info(f"check充电状态，预测出B满电，{pre_B},A继续充电")
                        WFState.set_battery_state("charging")
                        WFState.set_battery_value(f"{pre_A}")
            elif int(valueBA10) > 0:  # 如果只有B充电
                # 预测A电量，如果A不为满电，则A为降温模式，这个时候要断掉B充电，等待A
                pre_A = self.pre_model.pre_vol(int(valueAV10) / 100, int(valueAA10) / 100)  # 有可能满电，有可能高温等待
                pre_B = self.pre_model.pre_vol(int(valueBV10) / 100, int(valueBA10) / 100)
                # if pre_A<100:#A不为满电，断掉A充电
                # 如果上个状态是在充电的状态，这个时候有一个电池断掉了，那这个电池认定为满电状态
                if WFState.get_battery_state() == "charging":  # A电池满电
                    # self.logger.get_log().info(
                    #     f"check充电状态，预测出A满电，{pre_A},B继续充电")
                    # WFState.set_battery_state("charging")
                    # WFState.set_battery_value(f"{pre_B}")
                    if int(valueBA10) / 100 < 0.5:  # 如果预测出的B电流都小于0.5则认为满电，断开充电
                        self.logger.get_log().info(
                            f"check充电状态，预测出B满电或降温，B电流小，{pre_A},{pre_B}")
                        if WFState.get_battery_state() == "charging":  # 如果是充电
                            WFState.set_battery_state("full")
                            WFState.set_battery_value("100")
                            self.standby()  # 2023-9-27 断开操作
                        else:
                            WFState.set_battery_state("full or waiting")
                    else:
                        self.logger.get_log().info(
                            f"check充电状态，预测出A满电，{pre_A},B继续充电")
                        WFState.set_battery_state("charging")
                        WFState.set_battery_value(f"{pre_B}")
                elif pre_B < 80 and pre_B != -1:  # A不为满电，断掉A充电
                    if self.iniconfig.get_is_blance_charge() == True:
                        self.standby_B()
                        self.B_waiting = True
                        self.logger.get_log().info(
                            f"check充电状态，预测出A在等待降温，{pre_A},停止B充电")
                        WFState.set_battery_state("waiting")
                        WFState.set_battery_value(f"{pre_B}")
                    else:
                        WFState.set_battery_state("charging")
                        self.logger.get_log().info(f"check充电状态，预测出B在等待降温，{pre_A},没有启用均衡充电，继续双充电")
                else:  # A为满电
                    # 2023-9-27 如果两个电流都很小，则认为满电
                    if int(valueBA10) / 100 < 0.5:  # 如果预测出的B电流都小于0.5则认为满电，断开充电
                        self.logger.get_log().info(
                            f"check充电状态，预测出B满电或降温，B电流小，{pre_A},{pre_B}")
                        if WFState.get_battery_state() == "charging":  # 如果是充电
                            WFState.set_battery_state("full")
                            WFState.set_battery_value("100")
                            self.standby()  # 2023-9-27 断开操作
                        else:
                            WFState.set_battery_state("full or waiting")
                    else:
                        self.logger.get_log().info(
                            f"check充电状态，预测出A满电，{pre_A},B继续充电")
                        WFState.set_battery_state("charging")
                        WFState.set_battery_value(f"{pre_B}")
            else:  # 双边均没电流
                # 预测A/B电量
                pre_A = self.pre_model.pre_vol(int(valueAV10) / 100, int(valueAA10) / 100)
                pre_B = self.pre_model.pre_vol(int(valueBV10) / 100, int(valueBA10) / 100)
                if pre_A == 100 and pre_B == 100:  # 如果都是满电，或者都是高温等待
                    self.logger.get_log().info(
                        f"check充电状态，预测出A、B均满电或降温，{pre_A},{pre_B}")
                    if WFState.get_battery_state() == "charging":  # 如果是充电
                        WFState.set_battery_state("full")
                        WFState.set_battery_value("100")
                        self.standby()  # 2023-5-22 断开操作
                    else:
                        WFState.set_battery_state("full or waiting")
                if pre_A < 100 and pre_B < 100:  # 均不为满电，那就是双方均在等待
                    self.logger.get_log().info(
                        f"check充电状态，预测出A、B均在等待，{pre_A},{pre_B}，cooling 或加热中")
                    WFState.set_battery_state("waiting")
                if pre_A < 100:  # 如果只有A不满电
                    self.logger.get_log().info(
                        f"check充电状态，预测出A在等待，{pre_A},B满电，{pre_B}，cooling 或加热中")
                    WFState.set_battery_state("waiting")
                    WFState.set_battery_value(f"{pre_A}")
                if pre_B < 100:  # 如果只有B不满电
                    self.logger.get_log().info(
                        f"check充电状态，预测出A满电，{pre_A},B在等待，{pre_B}，cooling 或加热中")
                    WFState.set_battery_state("waiting")
                    WFState.set_battery_value(f"{pre_B}")
        elif value[3:5] == "01":  # A充，B不充（A开，B不开）
            # 说明前面，B处于等待的状态，被断掉了充电，前面A处于降温或者低电压情况
            # （1）A有电流，说明A处于充电中，这个时候A不降温
            pre_A = self.pre_model.pre_vol(int(valueAV10) / 100, int(valueAA10) / 100)
            if int(valueAA10) / 100 > 0:  # A有电流
                self.logger.get_log().info(
                    f"check充电状态，只有A在充电，此时启动B充电")
                WFState.set_battery_state("charging")
                self.charge_B()  # 启动B充电
                WFState.set_battery_value(f"{pre_A}")
            else:  # 如果A没有电流，说明A没在充电，可能A还在降温
                self.logger.get_log().info(
                    f"check充电状态，A仍然没有充电，A继续等待")
                WFState.set_battery_state("waiting")
                WFState.set_battery_value(f"-1")
        elif value[3:5] == "10":  # B充，A不充(B开A不开)
            # 说明前面，A处于等待的状态，被断掉了充电，前面B处于降温或者低电压情况
            # （1）B有电流，说明B处于充电中，这个时候B不降温
            pre_B = self.pre_model.pre_vol(int(valueBV10) / 100, int(valueBA10) / 100)
            if int(valueBA10) / 100 > 0:  # B有电流
                self.logger.get_log().info(
                    f"check充电状态，只有B在充电，此时启动A充电")
                WFState.set_battery_state("charging")
                self.charge_A()  # 启动A充电
                WFState.set_battery_value(f"{pre_B}")
            else:  # 如果B没有电流，说明B没在充电，可能B还在降温
                self.logger.get_log().info(
                    f"check充电状态，B仍然没有充电，B继续等待")
                WFState.set_battery_state("waiting")
                WFState.set_battery_value(f"-1")
        self.logger.get_log().info(f"当前电池电量为：{WFState.get_battery_value()}")

    def standby(self):
        '''
        无线充电standby 操作
        关闭A电源，关闭B电源
        :return:
        '''
        try:
            result = ""
            # 发送命令
            self.logger.get_log().info(f"发送待机命令--Standby")
            self.engine = Communication(USBDeviceConfig.get_serial_usb_charge(), USBDeviceConfig.get_serial_bps_charge(),
                                        10, self.logger, None)
            self.engine.Open_Engine()
            # A路关
            # 01 06 80 00 00 02 21 CB
            # B路关
            # 01 06 80 00 00 08 A1 CC
            command_close_A = "01 06 80 00 00 02 21 CB"
            command_close_B = "01 06 80 00 00 08 A1 CC"
            command_read = "01 04 00 00 00 06 70 08"
            self.engine.Send_data(bytes.fromhex(command_close_A))
            time.sleep(2)
            self.engine.Close_Engine()
            # 等待5秒后启动B路关
            self.engine = Communication(USBDeviceConfig.get_serial_usb_charge(), USBDeviceConfig.get_serial_bps_charge(),
                                        10, self.logger, None)
            self.engine.Send_data(bytes.fromhex(command_close_B))
            # 等待10秒读取状态
            time.sleep(2)
            # self.engine.Send_data(bytes.fromhex(command_read))
            # result = self.engine.Read_Size(17)  # 读取一行数据
            self.engine.Close_Engine()
            # 等待最长时间为10秒
            waittimes = 5
            begintimes = waittimes
            empty_times = 0
            while waittimes > 0:
                if len(result) == 0:
                    self.engine = Communication(USBDeviceConfig.get_serial_usb_charge(),
                                                USBDeviceConfig.get_serial_bps_charge(),
                                                10, self.logger, None)
                    self.engine.Open_Engine()
                    self.engine.Send_data(bytes.fromhex(command_read))
                    result = self.engine.Read_Size(17)  # 读取一行数据
                    self.engine.Close_Engine()
                waittimes = waittimes - 1
                time.sleep(2)  # 等待2秒
                if len(result) == 0:
                    empty_times = empty_times + 1
                    self.logger.get_log().info(f"充电获取不到下位机值（null），第{empty_times}次失败")
                    if empty_times >= 2:
                        return "chargeerror(null)"
                    continue
                showresult = self.hexShow(result)  # 16进制乱码转换
                result = bytes.fromhex(showresult)
                self.logger.get_log().info(f"第{begintimes - waittimes}次，Standby result: {showresult}")
                value = binascii.b2a_hex(result[3:5]).decode('ascii')
                value = self.hex2bin(value)
                self.logger.get_log().info(f"第{begintimes - waittimes}次，Standby deal result is {value}")
                if value[3:] == "00":
                    WFState.set_battery_state("standby")
                    result = "success"
                    break
                result = ""
            if waittimes <= 0:
                result = "chargeerror"
            return result
        except Exception as e:
            self.logger.get_log().info(f"待机命令异常，{e}")
            return 'error'

    def charge(self):
        """
        无线充电充电操作
        :return:
        """
        try:
            WFState.set_battery_state("unknown")
            WFState.set_battery_value("0")
            result = ""
            # 发送命令
            self.logger.get_log().info(f"发送充电命令--Charge")
            self.engine = Communication(USBDeviceConfig.get_serial_usb_charge(), USBDeviceConfig.get_serial_bps_charge(),
                                        10, self.logger, None)
            self.engine.Open_Engine()
            command_open_A = "01 06 80 00 00 01 61 CA "
            command_open_B = "01 06 80 00 00 04 A1 C9"
            command_read = "01 04 00 00 00 06 70 08"
            self.engine.Send_data(bytes.fromhex(command_open_A))
            time.sleep(5)
            self.engine.Close_Engine()
            self.engine = Communication(USBDeviceConfig.get_serial_usb_charge(), USBDeviceConfig.get_serial_bps_charge(),
                                        10, self.logger, None)
            # 等待5秒后启动B路
            self.engine.Open_Engine()
            self.engine.Send_data(bytes.fromhex(command_open_B))
            # 等待10秒读取状态
            time.sleep(5)
            self.engine.Close_Engine()
            # 等待最长时间为30秒
            waittimes = 15
            begintimes = waittimes
            fail_times = 0
            empty_times = 0
            success_wait_times = 0
            while waittimes > 0:
                if len(result) == 0:
                    self.engine = Communication(USBDeviceConfig.get_serial_usb_charge(),
                                                USBDeviceConfig.get_serial_bps_charge(),
                                                10, self.logger, None)
                    self.engine.Open_Engine()
                    self.engine.Send_data(bytes.fromhex(command_read))
                    result = self.engine.Read_Size(17)  # 读取一行数据
                    self.engine.Close_Engine()
                waittimes = waittimes - 1
                time.sleep(2)  # 等待2秒
                if len(result) == 0:
                    empty_times = empty_times + 1
                    self.logger.get_log().info(f"充电获取不到下位机值（null），第{empty_times}次失败")
                    if empty_times >= 2:
                        return "chargeerror(null)"
                    continue
                showresult = self.hexShow(result)  # 16进制乱码转换
                result = bytes.fromhex(showresult)
                self.logger.get_log().info(f"第{begintimes - waittimes}次，charge result: {showresult}")
                value = binascii.b2a_hex(result[3:5]).decode('ascii')
                value = self.hex2bin(value)
                self.logger.get_log().info(f"第{begintimes - waittimes}次，charge deal result is {value}")
                valueAV = binascii.b2a_hex(result[7:9]).decode('ascii')  # A路电压
                valueBV = binascii.b2a_hex(result[9:11]).decode('ascii')  # B路电压
                valueAA = binascii.b2a_hex(result[11:13]).decode('ascii')  # A路电流
                valueBA = binascii.b2a_hex(result[13:15]).decode('ascii')  # B路电流

                valueAV10 = str(int(valueAV.upper(), 16))  # 10进制表示
                valueBV10 = str(int(valueBV.upper(), 16))  # 10进制表示
                valueAA10 = str(int(valueAA.upper(), 16))  # 10进制表示
                valueBA10 = str(int(valueBA.upper(), 16))  # 10进制表示
                self.logger.get_log().info(
                    f"充电命令发送，第{begintimes - waittimes}次，电压、电流值AV is {int(valueAV10) / 100},BV is {int(valueBV10) / 100}，AA is {int(valueAA10) / 100},BA is {int(valueBA10) / 100}")
                if value[2:] == "111":  # 双充电，标记位B位A位
                    # 2023-3-23新增，充电成功后强制等待充电状态,等待两次，10秒；以防充电状态，电压电流还没有更新成功
                    if success_wait_times <= 1:  # 2次
                        success_wait_times = success_wait_times + 1
                        time.sleep(5)
                        result = ""
                        waittimes = waittimes + 1
                        continue
                    if int(valueAA10) > 0 or int(valueBA10) > 0:  # 有可能出现单边充电情况
                        if int(valueAA10) == 0 or int(valueBA10) == 0:
                            self.logger.get_log().info("---------充电启动的时候，单边充电---------------")
                            # 单边充电要做的一些处理，是否做成一个配置，单边充电不启动充电
                            if self.iniconfig.get_is_signal_battery_charge() == True:  # 配置了单边充电，不启动充电
                                self.standby()  # 待机操作，停止充电
                                return "chargeerror"
                        WFState.set_battery_state("charging")
                        result = "success"
                        break
                    elif int(valueAV10) / 100 > 30 and int(valueBV10) / 100 > 30:  # 无人机不在或者充满了,双电池都不在充电
                        if fail_times <= 2:
                            fail_times = fail_times + 1
                            time.sleep(3)
                            result = ""
                            continue
                        if WFState.get_battery_state() == "charging" or WFState.get_battery_state() == "full":
                            WFState.set_battery_value("100")
                            WFState.set_battery_state("full")
                        else:
                            # 充电,满电或高温等待
                            if self.pre_model.pre_vol(int(valueAV10) / 100, 0) == 100 or self.pre_model.pre_vol(
                                    int(valueBV10) / 100, 0) == 100:  # 冷却的时候电量预测和满电的时候情况类似，开始的时候没有电量
                                # WFState.set_battery_value("100")
                                WFState.set_battery_state("full or waiting")
                                if self.iniconfig.get_is_blance_charge()==True:
                                    # 断开B，打开A,解决满电的时候自动断电的情况，只有一个开的时候不自动断开
                                    self.standby_B()
                                    self.charge_A()
                                result = "chargeerror"
                            else:  # 带电压,状态未知
                                WFState.set_battery_state("unknown")
                                result = "chargeerror"
                        break
                    else:
                        result = "chargeerror"  # 无人机不在位
                result = ""
            if waittimes <= 0:
                result = "chargeerror"
            return result
        except Exception as e:
            self.logger.get_log().info(f"充电命令异常，{e}")
            return 'error'

    def takeoff(self):
        """
        无人机启动操作;
        解决充电时，待机后开机操作；经常出现充电情况下，待机，然后启动开机，提示开机成功，实际没成功
        :return:
        """
        try:
            result = ""
            is_charging = False
            # 发送命令
            self.logger.get_log().info(f"接收到开机命令--TakeOff")
            self.engine = Communication(USBDeviceConfig.get_serial_usb_charge(), USBDeviceConfig.get_serial_bps_charge(),
                                        20, self.logger, None)
            self.engine.Open_Engine()
            command_open = "01 06 80 00 00 10 A1 C6"
            command_read = "01 04 00 00 00 06 70 08"
            # 先读取一下命令，如果当前在充电，则先进行待机操作
            self.engine.Send_data(bytes.fromhex(command_read))
            result_standby = self.engine.Read_Size(17)
            if len(result_standby) != 0:
                value_standby = binascii.b2a_hex(result_standby[3:5]).decode('ascii')
                value_standby = self.hex2bin(value_standby)
                if value_standby[3:5] in ("11", '10', '01'):  # 双充电
                    is_charging = True
            self.engine.Close_Engine()
            if is_charging:  # 如果在充电
                self.logger.get_log().info('开机操作，开机之前无人机在充电，先待机')
                self.standby()
                time.sleep(2)
            else:  # 如果没有在充电
                self.logger.get_log().info('开机操作，开机之前无人机非充电')
                # 等待10秒读取状态.2023-5-10,必须强制等待5秒，否则立即standby情况下，开机返回结果正确，但是实际开机失败
                # 2023-7-21
                if WFState.get_battery_state() == "standby":
                    time.sleep(3)
                # time.sleep(3)#必须要等待，否则马上下开机指令，提示开机成功，实际没有成功
            # 做命令读取操作，2023-2-11
            self.engine = Communication(USBDeviceConfig.get_serial_usb_charge(),
                                        USBDeviceConfig.get_serial_bps_charge(),
                                        20, self.logger, None)
            self.engine.Open_Engine()
            self.engine.Send_data(bytes.fromhex(command_read))
            # 等待10秒读取状态
            self.logger.get_log().info('开机操作，开机之前等待2秒')
            time.sleep(2)
            self.engine.Close_Engine()

            # 然后进行第二次开机操作
            self.logger.get_log().info('开机操作，发送开机动作')
            self.engine = Communication(USBDeviceConfig.get_serial_usb_charge(),
                                        USBDeviceConfig.get_serial_bps_charge(),
                                        20, self.logger, None)
            self.engine.Open_Engine()
            self.engine.Send_data(bytes.fromhex(command_open))
            # 等待10秒读取状态
            time.sleep(5)
            self.engine.Close_Engine()
            self.logger.get_log().info('开机操作，开始读取状态数据')
            # 等待最长时间为30秒
            waittimes = 10
            begintimes = waittimes
            empty_times = 0
            while waittimes > 0:
                if len(result) == 0:
                    self.engine = Communication(USBDeviceConfig.get_serial_usb_charge(),
                                                USBDeviceConfig.get_serial_bps_charge(),
                                                10, self.logger, None)
                    self.engine.Open_Engine()
                    self.engine.Send_data(bytes.fromhex(command_read))
                    result = self.engine.Read_Size(17)  # 读取一行数据
                    self.engine.Close_Engine()
                waittimes = waittimes - 1
                time.sleep(2)  # 等待2秒
                if len(result) == 0:
                    empty_times = empty_times + 1
                    self.logger.get_log().info(f"充电获取不到下位机值（null），第{empty_times}次失败")
                    if empty_times >= 2:
                        return "chargeerror(null)"
                    continue
                showresult = self.hexShow(result)  # 16进制乱码转换
                result = bytes.fromhex(showresult)
                self.logger.get_log().info(f"第{begintimes - waittimes}次，takeoff result: {showresult}")
                value = binascii.b2a_hex(result[3:5]).decode('ascii')
                value = self.hex2bin(value)
                self.logger.get_log().info(f"第{begintimes - waittimes}次，takeoff deal result is {value}")

                # 2023-7-28 开机成功除了前面的标识位置为01外，还要判断检测到的电压有一个>0
                valueAV = binascii.b2a_hex(result[7:9]).decode('ascii')  # A路电压
                valueBV = binascii.b2a_hex(result[9:11]).decode('ascii')  # B路电压
                if value[:2] == "01" and (int(valueAV.upper(), 16) > 0 or int(valueBV.upper(), 16) > 0):
                    WFState.set_battery_state("takeoff")
                    WFState.set_battery_value("-1")  # 2023-06-16电量预测
                    result = "success"
                    break
                result = ""
            if waittimes <= 0:
                result = "chargeerror"
            # time.sleep(5)
            self.logger.get_log().info(f'开机操作，最终返回结果为{result}')
            return result
        except Exception as e:
            self.logger.get_log().info(f"TakeOff--开机命令异常，{e}")
            return 'error'

    def droneoff(self):
        """
        关闭无人机
        :return:
        """
        try:
            result = ""
            is_charging = False
            # 发送命令
            self.logger.get_log().info(f"发送关机命令--DroneOff")
            self.engine = Communication(USBDeviceConfig.get_serial_usb_charge(), USBDeviceConfig.get_serial_bps_charge(),
                                        10, self.logger, None)
            self.engine.Open_Engine()
            command_close = "01 06 80 00 00 20 A1 D2"
            command_read = "01 04 00 00 00 06 70 08"
            # 先读取一下命令，如果当前在充电，则先进行待机操作
            self.engine.Send_data(bytes.fromhex(command_read))
            result_standby = self.engine.Read_Size(17)
            if len(result_standby) != 0:
                value_standby = binascii.b2a_hex(result_standby[3:5]).decode('ascii')
                value_standby = self.hex2bin(value_standby)
                if value_standby[2:] == "111":  # 双充电
                    is_charging = True
            self.engine.Close_Engine()

            if is_charging:  # 如果是充电
                self.standby()
                time.sleep(10)

            self.engine = Communication(USBDeviceConfig.get_serial_usb_charge(), USBDeviceConfig.get_serial_bps_charge(),
                                        10, self.logger, None)
            self.engine.Open_Engine()
            # 发送关机指令
            self.engine.Send_data(bytes.fromhex(command_close))
            # 等待30秒读取状态
            time.sleep(10)
            self.engine.Close_Engine()
            # 等待最长时间为30秒
            waittimes = 15
            begintimes = waittimes
            empty_times = 0
            while waittimes > 0:
                if len(result) == 0:
                    self.engine = Communication(USBDeviceConfig.get_serial_usb_charge(),
                                                USBDeviceConfig.get_serial_bps_charge(),
                                                10, self.logger, None)
                    self.engine.Open_Engine()
                    self.engine.Send_data(bytes.fromhex(command_read))
                    result = self.engine.Read_Size(17)  # 读取一行数据
                    self.engine.Close_Engine()
                waittimes = waittimes - 1
                time.sleep(2)  # 等待2秒
                if len(result) == 0:
                    empty_times = empty_times + 1
                    self.logger.get_log().info(f"充电获取不到下位机值（null），第{empty_times}次失败")
                    if empty_times >= 2:
                        return "chargeerror(null)"
                    continue
                showresult = self.hexShow(result)  # 16进制乱码转换
                result = bytes.fromhex(showresult)
                self.logger.get_log().info(f"第{begintimes - waittimes}次，droneoff result: {showresult}")
                value = binascii.b2a_hex(result[3:5]).decode('ascii')
                value = self.hex2bin(value)
                self.logger.get_log().info(f"第{begintimes - waittimes}次，droneoff deal result is {value}")
                if value[:2] == "10":
                    WFState.set_battery_state("close")
                    result = "success"
                    break
                result = ""
            if waittimes <= 0:
                result = "chargeerror"
            return result
        except Exception as e:
            self.logger.get_log().info(f"DroneOff--关机指令异常，{e}")
            return 'error'

    def Check(self):
        """
        状态检查
        :return:
        """
        try:
            result = "error"
            # 发送命令
            self.logger.get_log().info(
                f"发送命令--Check,before checking, current battery value is {WFState.get_battery_value()},state is {WFState.get_battery_state()}")
            self.engine = Communication(USBDeviceConfig.get_serial_usb_charge(), USBDeviceConfig.get_serial_bps_charge(),
                                        10, self.logger, None)
            self.engine.Open_Engine()
            command_read = "01 04 00 00 00 06 70 08"
            self.engine.Send_data(bytes.fromhex(command_read))
            result = self.engine.Read_Size(17)
            self.engine.Close_Engine()
            if len(result) == 0:
                self.engine = Communication(USBDeviceConfig.get_serial_usb_charge(),
                                            USBDeviceConfig.get_serial_bps_charge(),
                                            10, self.logger, None)
                self.engine.Open_Engine()
                self.engine.Send_data(bytes.fromhex(command_read))
                result = self.engine.Read_Size(17)  # 读取一行数据
                self.engine.Close_Engine()
            if len(result) == 0:
                return "chargeerror(null)"
            showresult = self.hexShow(result)  # 16进制乱码转换
            result = bytes.fromhex(showresult)

            # self.logger.get_log().info(f"Check result: {result}")
            valueAV = binascii.b2a_hex(result[7:9]).decode('ascii')  # A路电压
            valueBV = binascii.b2a_hex(result[9:11]).decode('ascii')  # B路电压
            valueAA = binascii.b2a_hex(result[11:13]).decode('ascii')  # A路电流
            valueBA = binascii.b2a_hex(result[13:15]).decode('ascii')  # B路电流

            valueAV10 = str(int(valueAV.upper(), 16))  # 10进制表示
            valueBV10 = str(int(valueBV.upper(), 16))  # 10进制表示
            valueAA10 = str(int(valueAA.upper(), 16))  # 10进制表示
            valueBA10 = str(int(valueBA.upper(), 16))  # 10进制表示

            value = binascii.b2a_hex(result[3:5]).decode('ascii')
            value = self.hex2bin(value)
            self.logger.get_log().info(
                f"check指令获取到的值，value is {value},value[3:5] is {value[3:5]}，电压、电流值AV is {int(valueAV10) / 100},BV is {int(valueBV10) / 100}，AA is {int(valueAA10) / 100},BA is {int(valueBA10) / 100}，当前电量为{WFState.get_battery_value()}")

            # 根据状态值做逻辑处理
            if value[3:5] in ("11", "10", "01"):
                self.logger.get_log().info(f"检查到结果在charging检测范围内，需要进行charging检查")
                self.check_charging(result)
            elif value == "10100" and WFState.get_battery_state() == "charging":
                print("standby")
                self.standby()
                WFState.set_battery_state("close")
                WFState.set_battery_value("100")
                result = "close"
            elif value[:2] == "01":
                valueAV = int(valueAV.upper(), 16)  # A路电压
                valueBV = int(valueBV.upper(), 16)  # B路电压
                if valueBV > 0 or valueAV > 0:
                    # 2023-7-28 开机成功除了前面的标识位置为01外，还要判断检测到的电压有一个>0
                    WFState.set_battery_state("takeoff")
                    WFState.set_battery_value("-1")  # 2023-06-16电量预测
                    result = "takeoff"
                elif value[3:] == "00":
                    WFState.set_battery_state("standby")
                    result = "standby"
            elif value[:2] == "10":
                if "open" in HangarState.get_hangar_bar_state():
                    WFState.set_battery_state("standby")
                    result = "standby"
                else:
                    WFState.set_battery_state("close")
                    result = "close"
            elif value[3:] == "00":
                WFState.set_battery_state("standby")
                result = "standby"
            else:
                self.logger.get_log().info(f"Check result +++ UNKNOWN: {result}")
                WFState.set_battery_state("unknown")
            self.logger.get_log().info(f"Check deal result is {result}")
            if 'error' in str(result):
                return result
            else:
                return 'success'
        except Exception as e:
            self.logger.get_log().info(f"check状态检查命令异常，{e}")
            return 'error'

    def exe_commond(self, commond):
        """
        读取指定命令的状态
         '''
         读取
         01 04 00 00 00 06 70 08  #状态
         01 04 01 00 00 00 F1 F6  #模块在线 bit0: 0 A路采样离线 1： A路采样在线
                                     bit1: 0 B路采样离线 1： B路采样在线

         01 04 02 00 00 00 F1 B2 A路电压 有电压没电流就是充满了；没电压没电流就是处于离线状态，无人机没接触上
         01 04 03 00 00 00 F0 4E B路电压
         01 04 04 00 00 00 F1 3A A电流 有电流就是在充电
         01 04 05 00 00 00 F0C6  B电流
        '''
        :return:
        """
        try:
            result = "false"
            # 发送命令
            self.logger.get_log().info(f"发送待机命令--Check")
            self.engine = Communication(USBDeviceConfig.get_serial_usb_charge(), USBDeviceConfig.get_serial_bps_charge(),
                                        10, self.logger, None)
            self.engine.Open_Engine()
            command_read = commond
            self.engine.Send_data(bytes.fromhex(command_read))
            result = self.engine.Read_Size(17)
            self.engine.Close_Engine()
            if len(result) == 0:
                self.engine = Communication(USBDeviceConfig.get_serial_usb_charge(),
                                            USBDeviceConfig.get_serial_bps_charge(),
                                            10, self.logger, None)
                self.engine.Open_Engine()
                self.engine.Send_data(bytes.fromhex(command_read))
                result = self.engine.Read_Size(17)  # 读取一行数据
                self.engine.Close_Engine()
            showresult = self.hexShow(result)  # 16进制乱码转换
            result = bytes.fromhex(showresult)
            return result
        except Exception as e:
            self.logger.get_log().info(f"待机命令异常，{e}")
            return 'error'

    def hexShow(self, argv):
        hLen = len(argv)
        out_s = ''
        for i in range(hLen):
            out_s = out_s + '{:02X}'.format(argv[i]) + ' '
        return out_s

    def printstate(self):
        for i in range(10):
            print(WFState.get_hangar_state())

    def readData(self, times):
        commond = "01 04 00 00 00 06 70 08"
        for i in range(times):
            self.engine = Communication(USBDeviceConfig.get_serial_usb_charge(), USBDeviceConfig.get_serial_bps_charge(),
                                        10, self.logger, None)
            self.engine.Open_Engine()
            command_read = commond
            self.engine.Send_data(bytes.fromhex(command_read))
            result = self.engine.Read_Size(17)
            self.engine.Close_Engine()
            showresult = self.hexShow(result)  # 16进制乱码转换
            result = bytes.fromhex(showresult)
            self.logger.get_log().info(f"第{i + 1}次，结果为 {result}")


def hexShow(self, argv):
    hLen = len(argv)
    out_s = ''
    for i in range(hLen):
        out_s = out_s + '{:02X}'.format(argv[i]) + ' '
    return out_s


if __name__ == "__main__":
    logger = Logger(__name__)  # 日志记录
    # # ---------------无线充电操作
    # wf_state = WFState()  # 创建对象
    # configini = ConfigIni()  # 初始配置信息
    # hangestate=
    # chargeServer = M300JCCServerV2(wf_state, logger, configini)
    # chargeServer.printstate()
    # chargeServer.operator_charge("DroneOff")
    # print(f"the result is {chargeServer.hex2bin('0017').rjust(5,'0')}")
    '''
        A路开
        01 06 80 00 00 01 61 CA 
        A路关
        01 06 80 00 00 02 21 CB

        B路开
        01 06 80 00 00 04 A1 C9
        B路关
        01 06 80 00 00 08 A1 CC

        开机
        01 06 80 00 00 10 A1 C6
        关机
        01 06 80 00 00 20 A1 D2
     读取
     01 04 00 00 00 06 70 08  #状态
     01 04 00 00 00 01 31 CA  #模块在线 bit0: 0 A路采样离线 1： A路采样在线
                                 bit1: 0 B路采样离线 1： B路采样在线

     01 04 00 00 00 02 71 CB A路电压 有电压没电流就是充满了；没电压没电流就是处于离线状态，无人机没接触上
     01 04 00 00 00 03 B0 0B B路电压
     01 04 00 00 00 04 F1 C9 A电流 有电流就是在充电
     01 04 00 00 00 05 30 09  B电流
     '''
    # commond = "01 04 00 00 00 06 70 08"
    # result = chargeServer.exe_commond(commond)
    # showresult = chargeServer.hexShow(result)  # 16进制乱码转换
    # showresult = hexShow(result)  # 16进制乱码转换
    # showresult =b'\x01\x04\x0c\x00\x17\x00\x03\x14\x14\x14\x1e\x00\x00\x00\x000\x1b'
    #
    #
    # valueAV = binascii.b2a_hex(showresult[7:9]).decode('ascii')  # A路电压
    # valueBV = binascii.b2a_hex(showresult[9:11]).decode('ascii')  # B路电压
    # valueAA = binascii.b2a_hex(showresult[11:13]).decode('ascii')  # A路电流
    # valueBA = binascii.b2a_hex(showresult[13:15]).decode('ascii')  # B路电流
    #
    # valueAV10 = str(int(valueAV.upper(), 16))  # 10
    # valueBV10 = str(int(valueBV.upper(), 16))  # 10
    # valueAA10 = str(int(valueAA.upper(), 16))  # 10
    # valueBA10 = str(int(valueBA.upper(), 16))  # 10
    #
    # print(f"the result is ,the showresult is {showresult} \n,the AV is {int(valueAV10) / 100} V;the BV is {int(valueBV10) / 100} V;AA is {int(valueAA10)} A;BA is {int(valueBA10)} A")

    # 测试停止A充电
