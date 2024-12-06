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


class AirConditionOper():
    '''
    (1)空调的开关机
    (2)空调加热模式开启
    (3)制冷模式开启
    (4)加热停止温度
    (5）制冷停止温度
    (6)空调报警开、关
    '''
    def __init__(self,airstate,state,comconfig,logger):
        self.state=state
        self.comconfig=comconfig
        self.logger=logger
        self.airstate=airstate
        self.open_command = "0D 06 00 2f 00 01 79 0F"
        self.close_commond="0D 06 00 2f 00 00 B8 CF"
        self.system_running_commond = "0D 02 00 07 00 01 08 C7"  # 系统运行状态
        self.hot_stop_tem_high="0D 04"#加热停止温度当前260度(26)
        self.hot_stop_tem_low="0D c4" #-6度
        self.cold_stop_tem_high="0D 18"#制冷停止温度，制冷优先
        self.cold_stop_tem_low = "0D 01"  # 制冷停止温度，制冷优先
        self.hot_start_commond_hot="0D 06 00 02 01 04 28 95"
        self.hot_start_commond_cold="0D 06 00 00 01 18 88 9C"
        self.cold_start_commond_hot="0D 06 00 02 00 c4 29 55"
        self.cold_start_commond_cold = "0D 06 00 00 00 96 09 68"
        self.hot_mode_commond = "0D 02 00 03 00 01 49 06"  # 加热模式是否运行
        self.code_mode_commond = "0D 02 00 02 00 01 18 C6"  # 制冷模式是否运行
        self.alarm_open="0D 06 00 18 00 01 C8 C1" #开警报
        self.close_alarm="0D 06 00 18 00 00 09 01" #关闭警报
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
        try:
            if self.airstate.isused == False:
                self.airstate.isused = True
                time.sleep(3)
            else:
                return "fail"
            #comstate=# 配置串口基本参数并建立通信
            comstate = serial.Serial(
                timeout=self.comconfig.get_aircondition_timeout(),
                port=self.comconfig.get_aircondition_usbname(),
                baudrate=self.comconfig.get_aircondition_bps(),
                parity=serial.PARITY_EVEN,  # 可以不写
                stopbits=serial.STOPBITS_ONE,  # 可以不写
                bytesize=serial.EIGHTBITS) # 可以不写
            self.sendcommond(self.open_command,comstate)
            time.sleep(5)
            self.readCommonFunSingle(self.system_running_commond,comstate)
            self.airstate.isused=False
            if self.airstate.system_running=="1":
                return "success"
            else:
                return "fail"
        except Exception as ex:
            self.airstate.isused = False
            print(f"异常---{ex}")
        finally:
            self.airstate.isused = False
    def closeAircondition(self):
        '''
        关闭空调
        '''
        try:
            if self.airstate.isused == False:
                self.airstate.isused = True
                time.sleep(3)
            else:
                return "fail"
            # comstate=# 配置串口基本参数并建立通信
            comstate = serial.Serial(
                timeout=self.comconfig.get_aircondition_timeout(),
                port=self.comconfig.get_aircondition_usbname(),
                baudrate=self.comconfig.get_aircondition_bps(),
                parity=serial.PARITY_EVEN,  # 可以不写
                stopbits=serial.STOPBITS_ONE,  # 可以不写
                bytesize=serial.EIGHTBITS)  # 可以不写
            self.sendcommond(self.close_commond, comstate)
            time.sleep(5)
            self.readCommonFunSingle(self.system_running_commond, comstate)
            self.airstate.isused = False
            if self.airstate.system_running == "0":
                return "success"
            else:
                return "fail"
        except Exception as ex:
            print(f"{ex}")
        finally:
            self.airstate.isused = False
    def openHotMode(self):
        '''
        开启加热模式
        '''
        try:
            if self.airstate.isused == False:
                self.airstate.isused = True
                time.sleep(3)
            else:
                return "fail"
            # comstate=# 配置串口基本参数并建立通信
            comstate = serial.Serial(
                timeout=self.comconfig.get_aircondition_timeout(),
                port=self.comconfig.get_aircondition_usbname(),
                baudrate=self.comconfig.get_aircondition_bps(),
                parity=serial.PARITY_EVEN,  # 可以不写
                stopbits=serial.STOPBITS_ONE,  # 可以不写
                bytesize=serial.EIGHTBITS)  # 可以不写
            self.sendcommond(self.hot_start_commond_cold, comstate)
            time.sleep(5)
            self.sendcommond(self.hot_start_commond_hot, comstate)
            time.sleep(5)
            self.readCommonFunSingle(self.hot_mode_commond, comstate)
            self.airstate.isused = False
            if self.airstate.hot_mode == "1":
                return "success"
            else:
                return "fail"
        except Exception as ex:
            print(f"{ex}")
        finally:
            self.airstate.isused = False
    def closeHotMode(self):
        '''
        关闭加热模式
        '''
        pass
    def openCodeMode(self):
        '''
        开启制冷模式
        '''
        try:
            if self.airstate.isused == False:
                self.airstate.isused = True
                time.sleep(3)
            else:
                return "fail"
            # comstate=# 配置串口基本参数并建立通信
            comstate = serial.Serial(
                timeout=self.comconfig.get_aircondition_timeout(),
                port=self.comconfig.get_aircondition_usbname(),
                baudrate=self.comconfig.get_aircondition_bps(),
                parity=serial.PARITY_EVEN,  # 可以不写
                stopbits=serial.STOPBITS_ONE,  # 可以不写
                bytesize=serial.EIGHTBITS)  # 可以不写
            self.sendcommond(self.cold_start_commond_cold, comstate)
            time.sleep(5)
            self.sendcommond(self.cold_start_commond_hot, comstate)
            time.sleep(5)
            self.readCommonFunSingle(self.code_mode_commond, comstate)
            self.airstate.isused = False
            time.sleep(50)#强制等待50秒
            if self.airstate.code_mode == "1":
                return "success"
            else:
                return "fail"
        except Exception as ex:
            print(f"{ex}")
        finally:
            self.airstate.isused = False
    def closeCodeMode(self):
        '''
        关闭制冷模式
        '''
        pass
    def setHotStopTem(self,stop_tem):
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
            return "fail"
        commond="0D 06 00 02 "+stop_tem_x
        commond=commond+" "+str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(commond)))
        comm_read="0D 03 00 02 "+stop_tem_x
        comm_read = comm_read + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(comm_read)))
        print(f"hot stop commond {commond},read-commond {comm_read}")
        try:
            if self.airstate.isused == False:
                self.airstate.isused = True
                time.sleep(3)
            else:
                return "fail"
            # comstate=# 配置串口基本参数并建立通信
            comstate = serial.Serial(
                timeout=self.comconfig.get_aircondition_timeout(),
                port=self.comconfig.get_aircondition_usbname(),
                baudrate=self.comconfig.get_aircondition_bps(),
                parity=serial.PARITY_EVEN,  # 可以不写
                stopbits=serial.STOPBITS_ONE,  # 可以不写
                bytesize=serial.EIGHTBITS)  # 可以不写
            self.sendcommond(commond, comstate)
            time.sleep(5)  # 强制等待50秒
            self.sendcommond(comm_read, comstate)
            time.sleep(5)
            self.airstate.isused = False
            #time.sleep(5)  # 强制等待50秒
            return "success"
        except Exception as ex:
            print(f"{ex}")
            return "fail"
        finally:
            self.airstate.isused = False
    def setColdStopTem(self,stop_tem):
        '''
        设置制冷停止温度
        '''
        stop_tem=int(stop_tem)
        stop_tem_x = hex(stop_tem * 10)[2:]
        if len(str(stop_tem_x))==1:
            stop_tem_x="00 0"+stop_tem_x
        elif len(str(stop_tem_x))==2:
            stop_tem_x="00 "+stop_tem_x
        elif len(str(stop_tem_x))==3:
            stop_tem_x="0"+str(stop_tem_x)[:1]+" "+str(stop_tem_x)[1:]
        elif len(str(stop_tem_x))==4:
            stop_tem_x=str(stop_tem_x)[:2]+" "+str(stop_tem_x)[2:]
        else:
            return "fail"
        commond = "0D 06 00 00 " + stop_tem_x
        commond = commond + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(commond)))
        comm_read = "0D 03 00 00 " + stop_tem_x
        comm_read = comm_read + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(comm_read)))
        print(f"code stop commond {commond},read-commond {comm_read}")
        try:
            if self.airstate.isused == False:
                self.airstate.isused = True
                time.sleep(3)
            else:
                return "fail"
            # comstate=# 配置串口基本参数并建立通信
            comstate = serial.Serial(
                timeout=self.comconfig.get_aircondition_timeout(),
                port=self.comconfig.get_aircondition_usbname(),
                baudrate=self.comconfig.get_aircondition_bps(),
                parity=serial.PARITY_EVEN,  # 可以不写
                stopbits=serial.STOPBITS_ONE,  # 可以不写
                bytesize=serial.EIGHTBITS)  # 可以不写
            self.sendcommond(commond, comstate)
            time.sleep(5)  # 强制等待50秒
            self.sendcommond(comm_read, comstate)
            time.sleep(5)  # 强制等待50秒
            self.airstate.isused = False

            return "success"
        except Exception as ex:
            self.logger.get_log().info(f"{ex}")
            return "fail"
        finally:
            self.airstate.isused = False

    def setHotSensitivityTem(self,sens_tem):
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
            return "fail"
        commond = "0D 06 00 03 " + stop_tem_x
        commond = commond + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(commond)))
        comm_read = "0D 03 00 03 " + stop_tem_x
        comm_read = comm_read + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(comm_read)))
        print(f"hot sens commond {commond},read-commond {comm_read}")
        try:
            if self.airstate.isused == False:
                self.airstate.isused = True
                time.sleep(3)
            else:
                return "fail"
            # comstate=# 配置串口基本参数并建立通信
            comstate = serial.Serial(
                timeout=self.comconfig.get_aircondition_timeout(),
                port=self.comconfig.get_aircondition_usbname(),
                baudrate=self.comconfig.get_aircondition_bps(),
                parity=serial.PARITY_EVEN,  # 可以不写
                stopbits=serial.STOPBITS_ONE,  # 可以不写
                bytesize=serial.EIGHTBITS)  # 可以不写
            self.sendcommond(commond, comstate)
            time.sleep(5)  # 强制等待50秒
            self.sendcommond(comm_read, comstate)
            time.sleep(5)  # 强制等待50秒
            self.airstate.isused = False
            return "success"
        except Exception as ex:
            print(f"{ex}")
            return "fail"
        finally:
            self.airstate.isused = False

    def setColdSensitivityTem(self,sens_tem):
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
            return "fail"
        commond = "0D 06 00 01 " + stop_tem_x
        commond = commond + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(commond)))
        comm_read = "0D 03 00 01 " + stop_tem_x
        comm_read = comm_read + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(comm_read)))
        print(f"code sens commond {commond},read-commond {comm_read}")
        try:
            if self.airstate.isused == False:
                self.airstate.isused = True
                time.sleep(3)
            else:
                return "fail"
            # comstate=# 配置串口基本参数并建立通信
            comstate = serial.Serial(
                timeout=self.comconfig.get_aircondition_timeout(),
                port=self.comconfig.get_aircondition_usbname(),
                baudrate=self.comconfig.get_aircondition_bps(),
                parity=serial.PARITY_EVEN,  # 可以不写
                stopbits=serial.STOPBITS_ONE,  # 可以不写
                bytesize=serial.EIGHTBITS)  # 可以不写
            self.sendcommond(commond, comstate)
            time.sleep(5)  # 强制等待50秒
            self.sendcommond(comm_read, comstate)
            time.sleep(5)  # 强制等待50秒
            self.airstate.isused = False
            return "success"
        except Exception as ex:
            print(f"{ex}")
            return "fail"
        finally:
            self.airstate.isused = False

    def setHiHumidityAlarm(self,humidity):
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
            return "fail"
        commond = "0D 06 00 07 " + stop_tem_x
        commond = commond + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(commond)))
        comm_read = "0D 03 00 07 " + stop_tem_x
        comm_read = comm_read + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(comm_read)))
        print(f"code sens commond {commond},read-commond {comm_read}")
        try:
            if self.airstate.isused == False:
                self.airstate.isused = True
                time.sleep(3)
            else:
                return "fail"
            # comstate=# 配置串口基本参数并建立通信
            comstate = serial.Serial(
                timeout=self.comconfig.get_aircondition_timeout(),
                port=self.comconfig.get_aircondition_usbname(),
                baudrate=self.comconfig.get_aircondition_bps(),
                parity=serial.PARITY_EVEN,  # 可以不写
                stopbits=serial.STOPBITS_ONE,  # 可以不写
                bytesize=serial.EIGHTBITS)  # 可以不写
            self.sendcommond(commond, comstate)
            time.sleep(5)  # 强制等待50秒
            self.sendcommond(comm_read, comstate)
            time.sleep(5)  # 强制等待50秒
            self.airstate.isused = False
            return "success"
        except Exception as ex:
            print(f"{ex}")
            return "fail"
        finally:
            self.airstate.isused = False

    def setLowHumidityAlarm(self,humidity):
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
            return "fail"
        commond = "0D 06 00 08 " + stop_tem_x
        commond = commond + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(commond)))
        comm_read = "0D 03 00 08 " + stop_tem_x
        comm_read = comm_read + " " + str(BASEUtile.ModbusUtils.calculate_crc16(bytes.fromhex(comm_read)))
        print(f"code sens commond {commond},read-commond {comm_read}")
        try:
            if self.airstate.isused == False:
                self.airstate.isused = True
                time.sleep(3)
            else:
                return "fail"
            # comstate=# 配置串口基本参数并建立通信
            comstate = serial.Serial(
                timeout=self.comconfig.get_aircondition_timeout(),
                port=self.comconfig.get_aircondition_usbname(),
                baudrate=self.comconfig.get_aircondition_bps(),
                parity=serial.PARITY_EVEN,  # 可以不写
                stopbits=serial.STOPBITS_ONE,  # 可以不写
                bytesize=serial.EIGHTBITS)  # 可以不写
            self.sendcommond(commond, comstate)
            time.sleep(5)  # 强制等待50秒
            self.sendcommond(comm_read, comstate)
            time.sleep(5)  # 强制等待50秒
            self.airstate.isused = False
            return "success"
        except Exception as ex:
            print(f"{ex}")
            return "fail"
        finally:
            self.airstate.isused = False

    def setAirconditonAlarmOpen(self):
        '''
        开启空调报警模式
        '''
        try:
            if self.airstate.isused == False:
                self.airstate.isused = True
                time.sleep(3)
            else:
                return "fail"
            # comstate=# 配置串口基本参数并建立通信
            comstate = serial.Serial(
                timeout=self.comconfig.get_aircondition_timeout(),
                port=self.comconfig.get_aircondition_usbname(),
                baudrate=self.comconfig.get_aircondition_bps(),
                parity=serial.PARITY_EVEN,  # 可以不写
                stopbits=serial.STOPBITS_ONE,  # 可以不写
                bytesize=serial.EIGHTBITS)  # 可以不写
            self.sendcommond(self.alarm_open, comstate)
            self.airstate.isused = False
            time.sleep(5)
            return "success"
        except Exception as ex:
            print(f"{ex}")
        finally:
            self.airstate.isused = False
    def setAirConditionAlarmClose(self):
        '''
        关闭空调报警模式
        '''
        try:
            if self.airstate.isused == False:
                self.airstate.isused = True
                time.sleep(3)
            else:
                return "fail"
            # comstate=# 配置串口基本参数并建立通信
            comstate = serial.Serial(
                timeout=self.comconfig.get_aircondition_timeout(),
                port=self.comconfig.get_aircondition_usbname(),
                baudrate=self.comconfig.get_aircondition_bps(),
                parity=serial.PARITY_EVEN,  # 可以不写
                stopbits=serial.STOPBITS_ONE,  # 可以不写
                bytesize=serial.EIGHTBITS)  # 可以不写
            self.sendcommond(self.close_alarm, comstate)
            self.airstate.isused = False
            time.sleep(5)
            return "success"
        except Exception as ex:
            print(f"{ex}")
        finally:
            self.airstate.isused = False
    def sendcommond(self, commond, comstate):
        '''
        发送命令
        '''
        if comstate.isOpen()==False:
            comstate.open()
        comstate.write(bytes.fromhex(commond))
        time.sleep(0.1)
        count = comstate.inWaiting()
        # 数据的接收
        # 可以根据实际情况做修改，比如：当没有响应传回时，等待+判断
        if count == 0:
            pass
            #print('没有响应传回')
        if count > 0:
            data = comstate.read(count)
            print(f"读取通道返回值为{data}")
        comstate.flushInput()  # 清除缓存区数据,当代码在循环中执行时，不加这句代码会造成count累加
        comstate.close()
    def readCommonFunSingle(self, commond, comstate):
        '''
        通用执行方法
        '''
        if comstate.isOpen()==False:
            comstate.open()
        comstate.write(bytes.fromhex(commond))
        time.sleep(0.1)
        count = comstate.inWaiting()
        # 数据的接收
        # 可以根据实际情况做修改，比如：当没有响应传回时，等待+判断
        result=b''
        if count == 0:
            pass
            #print('没有响应传回')
        if count > 0:
            result = comstate.read(count)
            result = bytes.fromhex(self.hexShow(result))
        comstate.flushInput()  # 清除缓存区数据。当代码在循环中执行时，不加这句代码会造成count累加
        comstate.close()
        #print(f"the result is {result}")
        if result == b'':
            pass
        else:
            if len(result) == 0:
                if commond == self.system_running_commond:
                    self.airstate.set_system_running("0")
                elif commond == self.hot_mode_commond:
                    self.airstate.set_hot_mode("0")
                elif commond == self.code_mode_commond:
                    self.airstate.set_code_mode("0")
            else:
                result = binascii.b2a_hex(result[3:4]).decode('ascii')  #获取状态数据
                result=str(int(result))
                #print(f"the deal result is {result}")
                if commond == self.system_running_commond:
                    self.airstate.set_system_running(result)
                elif commond == self.hot_mode_commond:
                    self.airstate.set_hot_mode(result)
                elif commond == self.code_mode_commond:
                    self.airstate.set_code_mode(result)
