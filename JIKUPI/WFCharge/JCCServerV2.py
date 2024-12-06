# -*- coding: utf-8 -*- 
# @Time : 2022/09/19 22:41
# @Author : ZKL 
# @File : JCCServer.py
# 黑砂触点充电
import binascii
import math
import threading
import time

#from BASEUtile.loggerColl import LoggerColl
from ConfigIni import ConfigIni
from JKController.BarRepeat.JKBarRepeatCharge import JKBarRepeatCharge
from SATA.SATACom import Communication
from SATA.SerialHelp import SerialHelper
from USBDevice.USBDeviceConfig import USBDeviceConfig
from WFCharge.M300VolFit import M300VolFit
from WFCharge.WFState import WFState
from BASEUtile.logger import Logger


class M300JCCServerV2():  # 定义接触充电服务端
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

    支持04读取指令
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

    def __init__(self,hangstate, state, logger, configini):
        self.hangstate=hangstate
        self.state = state  # 充电箱当前状态信息
        self.logger = logger
        self.comconfig = USBDeviceConfig(configini)
        self.engine = Communication(self.comconfig.get_device_info_chargeV2(), self.comconfig.get_bps_chargeV2(), 10,
                                    self.logger, None)  # 串口初始化:
        self.iniconfig=configini
        self.pre_model=M300VolFit()
        #self.loggercoll=LoggerColl("JCCSERVER2")
        # self.engine = SerialHelper(Port=self.comconfig.get_device_info_chargeV2(), BaudRate=self.comconfig.get_bps_chargeV2(), ByteSize=self.comconfig.get_charge_bytesize_chargeV2(), Parity=self.comconfig.get_charge_parityV2(), Stopbits=self.comconfig.get_charge_stopbitsV2(),
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
            if commond == "Standby" or commond=="standby":
                result = self.standby()
            elif commond == "Charge":
                result = self.charge()
                print(f"The first charge result is {result}")
                if self.iniconfig.get_repeat_bar() == True:
                    if result == "chargeerror" or result=="error" or result=="chargeerror(null)":  # 充电失败情况下，要重新做一下推杆的打开和失败操作
                        jkbarRepeat = JKBarRepeatCharge(self.hangstate, self.logger,self.comconfig)
                        if jkbarRepeat.repeat_bar() == False:
                            self.logger.get_log().info(f"充电失败，推杆复位再夹紧失败，充电返回失败")
                            result = "chargeerror"
                        else:# 夹紧了，可以进行充电操作了
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
            self.state.set_state("unknown")  # 未知状态
            return "exception-error(获取不到下位机充电信息；请确认为2.0版本充电，检查充电硬件设备)"
        # time.sleep(20)
        # result="success"
        return result

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
            self.engine = Communication(self.comconfig.get_device_info_chargeV2(), self.comconfig.get_bps_chargeV2(),
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
            self.engine = Communication(self.comconfig.get_device_info_chargeV2(), self.comconfig.get_bps_chargeV2(),
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
            empty_times=0
            while waittimes > 0:
                if len(result) == 0:
                    self.engine = Communication(self.comconfig.get_device_info_chargeV2(),
                                                self.comconfig.get_bps_chargeV2(),
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
                    self.state.set_state("standby")
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
            self.state.set_state("unknown")
            self.state.set_battery_value("0")
            result = ""
            # 发送命令
            self.logger.get_log().info(f"发送充电命令--Charge")
            self.engine = Communication(self.comconfig.get_device_info_chargeV2(), self.comconfig.get_bps_chargeV2(),
                                        10, self.logger, None)
            self.engine.Open_Engine()
            command_open_A = "01 06 80 00 00 01 61 CA "
            command_open_B = "01 06 80 00 00 04 A1 C9"
            command_read = "01 04 00 00 00 06 70 08"
            self.engine.Send_data(bytes.fromhex(command_open_A))
            time.sleep(5)
            self.engine.Close_Engine()
            self.engine = Communication(self.comconfig.get_device_info_chargeV2(), self.comconfig.get_bps_chargeV2(),
                                        10, self.logger, None)
            # 等待5秒后启动B路
            self.engine.Open_Engine()
            self.engine.Send_data(bytes.fromhex(command_open_B))
            # 等待10秒读取状态
            time.sleep(5)
            # self.engine.Send_data(bytes.fromhex(command_read))
            # result = self.engine.Read_Size(17)
            self.engine.Close_Engine()
            # 等待最长时间为30秒
            waittimes = 15
            begintimes = waittimes
            fail_times=0
            empty_times=0
            while waittimes > 0:
                if len(result) == 0:
                    self.engine = Communication(self.comconfig.get_device_info_chargeV2(),
                                                self.comconfig.get_bps_chargeV2(),
                                                10, self.logger, None)
                    self.engine.Open_Engine()
                    self.engine.Send_data(bytes.fromhex(command_read))
                    result = self.engine.Read_Size(17)  # 读取一行数据
                    self.engine.Close_Engine()
                waittimes = waittimes - 1
                time.sleep(2)  # 等待2秒
                if len(result) == 0:
                    empty_times=empty_times+1
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
                self.logger.get_log().info(f"充电命令发送，第{begintimes - waittimes}次，电压、电流值AV is {int(valueAV10)/100},BV is {int(valueBV10)/100}，AA is {int(valueAA10)/100},BA is {int(valueBA10)/100}")
                if value[2:] == "111":  # 双充电
                    if int(valueAA10) > 0 or int(valueBA10) > 0:#有可能出现单边充电情况
                        if int(valueAA10)==0 or int(valueBA10)==0:
                            self.logger.get_log().info("---------充电启动的时候，单边充电---------------")
                            #单边充电要做的一些处理，是否做成一个配置，单边充电不启动充电
                            if self.iniconfig.get_signal_battery_charge()==True:#配置了单边充电，不启动充电
                                self.standby()#待机操作，停止充电
                                return "chargeerror"
                        self.state.set_state("charging")
                        result = "success"
                        break
                    elif int(valueAV10) / 100 > 30 and int(valueBV10) / 100 > 30:  # 无人机不在或者充满了
                        if self.state.get_state()=="charging" or self.state.get_state()=="full":
                            if fail_times == 0:
                                fail_times = fail_times + 1
                                time.sleep(3)
                                result = ""
                                continue
                            self.state.set_battery_value("100")
                            self.state.set_state("full")
                            self.standby()
                        else:
                            if fail_times==0:
                                fail_times=fail_times+1
                                time.sleep(3)
                                result=""
                                continue
                            #充电,满电
                            if self.pre_model.pre_vol(int(valueAV10) / 100,0)==100:
                                self.state.set_battery_value("100")
                                self.state.set_state("full")
                                result="full"
                            else:#带电压,状态未知
                                self.state.set_state("unknown")
                                result = "检测到电压，没有电流，并且不是满电，状态未知（unknown）"
                            # self.state.set_state("unknown")
                            # result = "检测到电压，没有电流，并且不是满电，状态未知（unknown）"
                            # self.standby()#2023-07-06取消做一次待机操作
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
            is_charging=False
            # 发送命令
            self.logger.get_log().info(f"接收到开机命令--TakeOff")
            self.engine = Communication(self.comconfig.get_device_info_chargeV2(), self.comconfig.get_bps_chargeV2(),
                                        20, self.logger, None)
            self.engine.Open_Engine()
            command_open = "01 06 80 00 00 10 A1 C6"
            command_read = "01 04 00 00 00 06 70 08"
            #先读取一下命令，如果当前在充电，则先进行待机操作
            self.engine.Send_data(bytes.fromhex(command_read))
            result_standby = self.engine.Read_Size(17)
            if len(result_standby)!=0:
                value_standby = binascii.b2a_hex(result_standby[3:5]).decode('ascii')
                value_standby = self.hex2bin(value_standby)
                if value_standby[2:] == "111":  # 双充电
                    is_charging=True
            self.engine.Close_Engine()
            if is_charging:#如果在充电
                self.logger.get_log().info('开机操作，开机之前无人机在充电，先待机')
                self.standby()
            else:#如果没有在充电
                self.logger.get_log().info('开机操作，开机之前无人机非充电')
            time.sleep(5)
            #做命令读取操作，2023-2-11
            self.engine = Communication(self.comconfig.get_device_info_chargeV2(),
                                        self.comconfig.get_bps_chargeV2(),
                                        20, self.logger, None)
            self.engine.Open_Engine()
            self.engine.Send_data(bytes.fromhex(command_read))
            # 等待10秒读取状态
            self.logger.get_log().info('开机操作，开机之前等待5秒')
            time.sleep(2)
            self.engine.Close_Engine()
            # 等待10秒读取状态
            time.sleep(5)
            # 然后进行第二次开机操作
            self.logger.get_log().info('开机操作，发送开机动作')
            self.engine = Communication(self.comconfig.get_device_info_chargeV2(),
                                        self.comconfig.get_bps_chargeV2(),
                                        20, self.logger, None)
            self.engine.Open_Engine()
            self.engine.Send_data(bytes.fromhex(command_open))
            # 等待10秒读取状态
            time.sleep(15)
            self.engine.Close_Engine()
            self.logger.get_log().info('开机操作，15秒等待结束后，读取状态数据')
            # 等待最长时间为30秒
            waittimes = 15
            begintimes = waittimes
            empty_times=0
            while waittimes > 0:
                if len(result) == 0:
                    self.engine = Communication(self.comconfig.get_device_info_chargeV2(),
                                                self.comconfig.get_bps_chargeV2(),
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
                if value[:2] == "01":
                    self.state.set_state("takeoff")
                    result = "success"
                    break
                result=""
            if waittimes <= 0:
                result = "chargeerror"
            time.sleep(5)
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
            is_charging=False
            # 发送命令
            self.logger.get_log().info(f"发送关机命令--DroneOff")
            self.engine = Communication(self.comconfig.get_device_info_chargeV2(), self.comconfig.get_bps_chargeV2(),
                                        10, self.logger, None)
            self.engine.Open_Engine()
            command_close = "01 06 80 00 00 20 A1 D2"
            command_read = "01 04 00 00 00 06 70 08"
            # 先读取一下命令，如果当前在充电，则先进行待机操作
            self.engine.Send_data(bytes.fromhex(command_read))
            result_standby = self.engine.Read_Size(17)
            if len(result_standby)!=0:
                value_standby = binascii.b2a_hex(result_standby[3:5]).decode('ascii')
                value_standby = self.hex2bin(value_standby)
                if value_standby[2:] == "111":  # 双充电
                    is_charging=True
            self.engine.Close_Engine()

            if is_charging:#如果是充电
                self.standby()
                time.sleep(10)

            self.engine=Communication(self.comconfig.get_device_info_chargeV2(), self.comconfig.get_bps_chargeV2(),
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
            empty_times=0
            while waittimes > 0:
                if len(result) == 0:
                    self.engine = Communication(self.comconfig.get_device_info_chargeV2(),
                                                self.comconfig.get_bps_chargeV2(),
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
                    self.state.set_state("close")
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
            result = "false"
            # 发送命令
            self.logger.get_log().info(f"发送待机命令--Check")
            self.engine = Communication(self.comconfig.get_device_info_chargeV2(), self.comconfig.get_bps_chargeV2(),
                                        10, self.logger, None)
            self.engine.Open_Engine()
            command_read = "01 04 00 00 00 06 70 08"
            self.engine.Send_data(bytes.fromhex(command_read))
            result = self.engine.Read_Size(17)
            self.engine.Close_Engine()
            if len(result) == 0:
                self.engine = Communication(self.comconfig.get_device_info_chargeV2(),
                                            self.comconfig.get_bps_chargeV2(),
                                            10, self.logger, None)
                self.engine.Open_Engine()
                self.engine.Send_data(bytes.fromhex(command_read))
                result = self.engine.Read_Size(17)  # 读取一行数据
                self.engine.Close_Engine()
            if len(result)==0:
                return "chargeerror(null)"
            showresult = self.hexShow(result)  # 16进制乱码转换
            result = bytes.fromhex(showresult)

            self.logger.get_log().info(f"Check result: {result}")
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
            self.logger.get_log().info(f"Check deal result bin is {value}")
            self.logger.get_log().info(f"check指令获取到的值，电压、电流值AV is {int(valueAV10) / 100},BV is {int(valueBV10) / 100}，AA is {int(valueAA10) / 100},BA is {int(valueBA10) / 100}，当前电量为{self.state.get_battery_value()}")

            # 根据状态值做逻辑处理
            if value[2:] == "111":
                if int(valueAA10) > 0 or int(valueBA10) > 0:
                    pre_A=self.pre_model.pre_vol(int(valueAV10) / 100,int(valueAA10) / 100)
                    pre_B=self.pre_model.pre_vol(int(valueBV10) / 100,int(valueBA10) / 100)
                    self.logger.get_log().info(
                        f"check指令获取到的值，电压、电流值AV is {int(valueAV10) / 100},BV is {int(valueBV10) / 100}，AA is {int(valueAA10) / 100},BA is {int(valueBA10) / 100};"
                        f"A预测电量为{pre_A},B预测电量为{pre_B}")
                    if pre_A>=pre_B:
                        self.state.set_battery_value(f"{pre_B}")
                    else:
                        self.state.set_battery_value(f"{pre_A}")
                    #如果两个电量差相差超过10，就赋值-1
                    if math.fabs(pre_B-pre_A)>10:
                        self.logger.get_log().info(
                            f"A、B电池压差过大，压差为{pre_B-pre_A}")
                        self.state.set_battery_value(f"-1")
                    self.state.set_state("charging")
                    result = "charging"
                elif int(valueAV10) / 100 > 30 and int(valueBV10) / 100 > 30:  # 无人机不在或者充满了
                    self.logger.get_log().info(f"Check deal result VAV is {valueAV10},VBV is {valueBV10}")
                    if self.state.get_state()=="charging" or self.state.get_state()=="full":
                        self.state.set_battery_value("100")
                        self.state.set_state("full")
                        self.standby()
                    else:
                        self.standby()
                        self.state.set_state("close")
                        result = "full or cooling or drone out of range"
                else:#在充电，一个有电压或者都没有电压
                    self.state.set_state("close")  # 无人机不在位
                    result = "无人机没连接"
            elif value == "10100" and self.state.get_state() == "charging":
                self.standby()
                self.state.set_state("close")
                self.state.set_battery_value("100")
                result = "close"
            elif value[:2] == "01":
                self.state.set_state("takeoff")
                result = "takeoff"
            elif value[:2] == "10":
                self.state.set_state("close")
                result = "close"
            elif value[3:] == "00":
                self.state.set_state("standby")
                result = "standby"
            else:
                self.logger.get_log().info(f"Check result +++ UNKNOWN: {result}")
                self.state.set_state("unkonwn")
            self.logger.get_log().info(f"Check deal result is {result}")
            return result
        except Exception as e:
            self.logger.get_log().info(f"待机命令异常，{e}")
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
            self.engine = Communication(self.comconfig.get_device_info_chargeV2(), self.comconfig.get_bps_chargeV2(),
                                        10, self.logger, None)
            self.engine.Open_Engine()
            command_read = commond
            self.engine.Send_data(bytes.fromhex(command_read))
            result = self.engine.Read_Size(17)
            self.engine.Close_Engine()
            if len(result) == 0:
                self.engine = Communication(self.comconfig.get_device_info_chargeV2(),
                                            self.comconfig.get_bps_chargeV2(),
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
            print(self.state.getHangerState())

def hexShow(self, argv):
    hLen = len(argv)
    out_s = ''
    for i in range(hLen):
        out_s = out_s + '{:02X}'.format(argv[i]) + ' '
    return out_s
if __name__ == "__main__":
    # logger = Logger(__name__)  # 日志记录
    # # ---------------无线充电操作
    # wf_state = WFState()  # 创建对象
    # configini = ConfigIni()  # 初始配置信息
    # chargeServer = M300JCCServerV2(wf_state, logger, configini)
    #chargeServer.printstate()
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
    #showresult = hexShow(result)  # 16进制乱码转换
    showresult =b'\x01\x04\x0c\x00\x17\x00\x03\x14\x14\x14\x1e\x00\x00\x00\x000\x1b'


    valueAV = binascii.b2a_hex(showresult[7:9]).decode('ascii')  # A路电压
    valueBV = binascii.b2a_hex(showresult[9:11]).decode('ascii')  # B路电压
    valueAA = binascii.b2a_hex(showresult[11:13]).decode('ascii')  # A路电流
    valueBA = binascii.b2a_hex(showresult[13:15]).decode('ascii')  # B路电流

    valueAV10 = str(int(valueAV.upper(), 16))  # 10
    valueBV10 = str(int(valueBV.upper(), 16))  # 10
    valueAA10 = str(int(valueAA.upper(), 16))  # 10
    valueBA10 = str(int(valueBA.upper(), 16))  # 10

    print(f"the result is ,the showresult is {showresult} \n,the AV is {int(valueAV10) / 100} V;the BV is {int(valueBV10) / 100} V;AA is {int(valueAA10)} A;BA is {int(valueBA10)} A")
