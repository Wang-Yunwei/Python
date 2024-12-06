# -*- coding: utf-8 -*- 
# @Time : 2022/6/13 1:25 
# @Author : ZKL 
# @File : JCCListerner.py
import threading
import time

from BASEUtile.logger import Logger
from ConfigIni import ConfigIni
from SATA.SerialUtils import SerialUtils
from weather.AlarmController import AlarmController


class WFCV2Listerner():
    '''
    触点充电，全双工监听充电状态信息
    '''
    def __init__(self,logger,wfstate,comconfig):
        self.logger=logger
        self.state=wfstate
        self.sleeptime=90#90秒读取信息的积累
        #构建一个充电串口对象，进行数据接收
        self.charge_com=SerialUtils(comconfig)
        self.value="" #接收到的数据
        self.thread_read=None


    def check_state(self):
        '''
        根据读取到的值，不停的check当前无人机和充电状态
        :return:
        '''
        if "Standby Order Received" in self.value and not ("ConnectError" in self.value or "PositionError" in self.value or "ConnectBreak" in self.value or "VrecError" in self.value or "InputCurrentError" in self.value):
            self.state.set_state("standby")
            self.logger.get_log().info(f"充电设置 standby;{self.value}")
            self.charge_com.clear_read_value()  # 清空获取到的数据
        elif "ChargeStart" in self.value:
            self.state.set_state("charging")
            self.logger.get_log().info(f"充电设置 charging;{self.value}")
            if "BatteryFull" in self.value:
                self.logger.get_log().info(f"充电设置 close 充满电;{self.value}")
                self.state.set_state("close")
                self.state.set_battery_value("100")
            self.charge_com.clear_read_value()  # 清空获取到的数据
        elif "TakeOffSuccess" in self.value:
            self.logger.get_log().info(f"充电设置 takeoff;{self.value}")
            self.state.set_state("takeoff")
            self.charge_com.clear_read_value()  # 清空获取到的数据
        elif "OffSuccess" in self.value:
            self.logger.get_log().info(f"充电设置 close;{self.value}")
            self.state.set_state("close")
            self.charge_com.clear_read_value()  # 清空获取到的数据
        elif "BatteryFull" in self.value:
            self.logger.get_log().info(f"充电设置 满电 close;{self.value}")
            self.state.set_state("close")
            self.state.set_battery_value("100")
            self.charge_com.clear_read_value()  # 清空获取到的数据
        elif "BatteryCooling" in self.value:
            self.logger.get_log().info(f"充电设置 电池降温 cool;{self.value}")
            self.state.set_state("cool")#电池需要降温，等待中
            self.charge_com.clear_read_value()  # 清空获取到的数据
        elif "Busy" in self.value or "BatteryLowVoltage" in self.value or "InputVoltageError" in self.value or  "ConnectError"  in self.value or "PositionError"  in self.value or "ConnectBreak"  in self.value or "VrecError"  in self.value or "InputCurrentError"  in self.value or "Error" in self.value or "TakeOffFail"  in self.value or "OffFail"  in self.value or "ChargeFail"  in self.value :
            self.logger.get_log().info(f"充电设置 chargeerror ;{self.value}")
            self.state.set_state("chargeerror")  # 充电操作错误
            self.charge_com.clear_read_value()  # 清空获取到的数据
        elif "Station:OFF" in self.value:  # 充电箱关
            self.logger.get_log().info(f"充电设置 OFF ;{self.value}")
            self.state.set_station_state("OFF")
            # 判断是否为充满电关闭
            if self.state.get_state() == "charging" and self.state.get_battery_value() == "4":  # 上一个时刻还是充电，这个时刻已经是关机状态，则判定为充满关机
                self.logger.get_log().info(f"充电设置 电量100 ;{self.value}")
                self.state.set_battery_value("100")
            if "Drone:OFF" in self.value:
                self.state.set_state("close")
            elif "Drone:ON" in self.value:
                self.state.set_state("takeoff")
            self.charge_com.clear_read_value()  # 清空获取到的数据
        elif "Station:ON" in self.value:  # 充电箱开
            self.logger.get_log().info(f"充电设置 ON ;{self.value}")
            self.state.set_station_state("ON")
            if "Drone:OFF" in self.value:
                # 判断是否为充满电关闭
                if self.state.get_state() == "charging" and self.state.get_battery_value() == "4":  # 上一个时刻还是充电，这个时刻已经是关机状态，则判定为充满关机
                    self.logger.get_log().info(f"充电设置 电量100 ;{self.value}")
                    self.state.set_battery_value("100")
                    self.state.set_state("close")
            elif "Drone:ON" in self.value:
                # 判断是否为充满电关闭
                if self.state.get_state() == "charging" and self.state.get_battery_value() == "4":  # 上一个时刻还是充电，这个时刻即将关机状态，则判定为充满关机
                    self.logger.get_log().info(f"充电设置 电量100 ;{self.value}")
                    self.state.set_battery_value("100")
                    self.state.set_state("takeoff")
            elif "Drone:Charge" in self.value:#充电中状态
                self.logger.get_log().info(f"充电设置 充电中 设置电量{self.value} ;{self.value}")
                self.state.set_state("charging")
                if "Cap:0~25%" in self.value:
                    self.state.set_battery_value("1")
                elif "Cap:25~50%" in self.value:
                    self.state.set_battery_value("2")
                elif "Cap:50~75%" in self.value:
                    self.state.set_battery_value("3")
                elif "Cap:75~100%" in self.value:
                    self.state.set_battery_value("4")
                if "BatteryFull" in self.value:
                    self.state.set_battery_value("100")
            self.charge_com.clear_read_value()  # 清空获取到的数据
            self.startAlarm() #开启警报
            #没有处理的字符串
        elif self.value!="":
            print(f"当前没有可识别的返回结果，当前串口数据为{self.value}")
    def startAlarm(self):
        '''
        判断是否启用警报设置
        '''
        configini=ConfigIni()
        if configini.get_alarm()==True:
            if self.state.get_state()=="charging":
                alarm=AlarmController(None,self.logger,configini)
                alarm.start_green_light_slow()
            elif self.state.get_state()=="close":
                alarm=AlarmController(None,self.logger,configini)
                alarm.start_green_light()
            elif self.state.get_state()=="takeoff":
                alarm=AlarmController(None,self.logger,configini)
                alarm.start_red_light()

    def start_Listern(self):
        self.init_com()
        times = 1
        last_content = ""
        current_content = ""
        while True:
            try:
                time.sleep(1)  # 等待1秒
                self.value = self.charge_com.get_read_value()  # 串口数据有累加
                current_content = self.value
                if current_content == last_content:
                    # print(times)
                    times += 1
                else:
                    times = 1
                if times >= self.sleeptime:
                    self.init_com()
                    times = 1
                if self.value != "":
                    self.check_state()
                last_content = current_content
            except Exception as ex:
                self.init_com()
                continue

    def init_com(self):
        try:
            self.charge_com.start()
            self.charge_com.clear_read_value()
            self.thread_read = threading.Thread(target=self.charge_com.read)#需要启动一个线程不停的去读取数据
            self.thread_read.setDaemon(True)
            self.thread_read.start()
        except Exception as connect_error:
            print(f"充电串口启动错误,{connect_error}")

if __name__=="__main__":
     logger = Logger(__name__)#日志记录
     #listern=JCCListerner()