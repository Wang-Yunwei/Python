# -*- coding: utf-8 -*- 
# @Time : 2022/6/12 15:58 
# @Author : ZKL 
# @File : StateFlag.py
class StateFlag():
    '''
    机库各个串口是否使用状态标记，利用此标记，做串口访问；如果串口被占用，则返回失败结果
    '''
    def __init__(self,configini):
        self.door_isused=False
        self.bar_isused=False
        self.charge_isused=False
        self.bar_iswaiting=False #是否有推拉杆在等待，默认情况，推拉杆命令可以等待5秒
        self.weather_isused = False
        self.configini=configini

    def set_door_used(self):
        self.door_isused=True
    def set_door_free(self):
        self.door_isused=False

    def set_bar_used(self):
        if self.configini.get_down_version()=="V2.0" or self.configini.get_down_version()=="V3.0":
            #下位机2.0
            self.door_isused=True
        else:
            self.bar_isused=True
    def set_bar_free(self):
        if self.configini.get_down_version() == "V2.0" or self.configini.get_down_version()=="V3.0":
            self.door_isused=False
        else:
            self.bar_isused=False

    def set_bar_waiting(self):
        self.bar_iswaiting=True

    def set_bar_waiting_free(self):
        self.bar_iswaiting=False

    def get_bar_waiting(self):
        return self.bar_iswaiting

    def set_charge_used(self):
        self.charge_isused=True

    def set_charge_free(self):
        self.charge_isused=False

    def get_door_isused(self):
        return self.door_isused

    def get_bar_isused(self):
        if self.configini.get_down_version() == "V2.0" or self.configini.get_down_version()=="V3.0":
            return self.door_isused
        else:
            return self.bar_isused

    def get_charge_isused(self):
        return self.charge_isused

    def set_weather_used(self):
        self.weather_isused=True

    def set_weather_free(self):
        self.weather_isused=False

    def get_weather_isused(self):
        return self.weather_isused