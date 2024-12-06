# -*- coding: utf-8 -*- 
# @Time : 2023/3/21 17:50 
# @Author : ZKL 
# @File : AirConditionState.py
'''
空调的状态数据，固定时间检测一次
（1）系统运行状态，0停止、1运行
（2）柜内温度
（3）柜内湿度
（4）柜外温度
（5）柜外湿度
（6）加热模式，0停止、1运行
（7）制冷模式，0停止、1运行
（8）内风机运转状态，0停止、1运行
（9）制冷除湿状态：0停止、1运行
（10）加热除湿状态：0停止、1运行
（11）报警状态：0打开，1关闭
（12）柜内高温告警。0正常、1故障
（13）柜内低温告警，0正常、1故障
（14）柜内温感故障：0正常、1故障
（15）制冷失效告警，0正常，1告警
（16）制热失效告警，0正常，1告警
'''
class AirCondtionState():
    def __init__(self):
        self.system_running=0 #系统运行状态
        self.inner_tem=0 #柜内温度
        self.inner_hum=0 #柜内湿度
        self.out_tem=0 #柜外温度
        self.out_hum=0 #柜外湿度
        self.hot_mode=0 #加热模式是否运行
        self.code_mode=0 #制冷模式是否运行
        self.innerMachineRun=0 #柜内风机运行状态
        self.codeArefaction=0 #制冷除湿模式是否运行
        self.hotArefaction=0 #加热除湿模式是否运行
        self.alarmState=0 #报警状态
        self.innerHotAlarm=0 #柜内加热报警状态
        self.innerCodeAlarm=0 #柜内制冷报价状态
        self.innerTemperatureError=0 #柜内温感故障
        self.codeInvalid=0 #柜内制冷失效告警
        self.hotInvalid=0 #制热失效告警
        self.isused=False #串口是否被占用
    def getAirConditonState(self):
        result = f"\"system_running\": \"{self.system_running}\",\"inner_tem\": \"{self.inner_tem}\",\"inner_hum\": \"{self.inner_hum}\",\"out_tem\": \"{self.out_tem}\",\"out_hum\": \"{self.out_hum}\"," \
                 f"\"hot_mode\": \"{self.hot_mode}\",\"code_mode\": \"{self.code_mode}\",\"innerMachineRun\": \"{self.innerMachineRun}\",\"codeArefaction\": \"{self.codeArefaction}\",\"hotArefaction\": \"{self.hotArefaction}\"," \
                 f"\"alarmState\": \"{self.alarmState}\",\"innerHotAlarm\": \"{self.innerHotAlarm}\",\"innerCodeAlarm\": \"{self.innerCodeAlarm}\",\"innerTemperatureError\": \"{self.innerTemperatureError}\",\"codeInvalid\": \"{self.codeInvalid}\",\"hotInvalid\": \"{self.hotInvalid}\""
        return "{" + result + "}"
    def set_system_running(self,value):
        self.system_running=value
    def set_inner_tem(self,value):
        self.inner_tem=value
    def set_inner_hum(self,value):
        self.inner_hum=value
    def set_out_tem(self,value):
        self.out_tem=value
    def set_out_hum(self,value):
        self.out_hum=value
    def set_hot_mode(self,value):
        self.hot_mode=value
    def set_code_mode(self,value):
        self.code_mode=value
    def set_innerMachineRun(self,value):
        self.innerMachineRun=value
    def set_codeArefaction(self,value):
        self.codeArefaction=value
    def set_hotArefaction(self,value):
        self.hotArefaction=value
    def set_alarmState(self,value):
        self.alarmState=value
    def set_innerHotAlarm(self,value):
        self.innerHotAlarm=value
    def set_innerCodeAlarm(self,value):
        self.innerCodeAlarm=value
    def set_innerTemperatureError(self,value):
        self.innerTemperatureError=value
    def set_codeInvalid(self,value):
        self.codeInvalid=value
    def set_hotInvalid(self,value):
        self.hotInvalid=value


