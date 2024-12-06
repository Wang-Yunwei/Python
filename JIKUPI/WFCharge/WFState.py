# -*- coding: utf-8 -*-
# @Time : 2022/1/5 22:44
# @Author : ZKL
# @File : WFState.py
# 机库当前状态
class WFState():
    def __init__(self):
        self.state = "close"  # 当前无线充电状态，close/charging/standby/takeoff/outage/cool/full
        self.battery_value = "0"  # 电池电量,满电情况下为100
        self.station_state = "close"  # 充电箱或发射端状态
        self.battery_state="normal"#电池状态，normal(正常)/full（满电状态）/cool(降温等待状态)/charging(充电)

    def set_state(self, state):
        self.state = state

    def set_battery_value(self, battery_value):
        self.battery_value = battery_value

    def get_state(self):
        return self.state

    def get_battery_value(self):
        return self.battery_value

    def get_station_state(self):
        return self.station_state

    def set_station_state(self, value):
        self.station_state = value

    def getChargeInfo(self):
        result = f"\"drone_state\": \"{self.state}\",\"battery_value\": \"{self.battery_value}\""
        return "{" + result + "}"
    def get_battery_state(self):
        '''
        设置电池状态
        :return:
        '''
        return self.battery_state
    def set_battery_state(self,value):
        '''
        设置电池状态
        :param value:
        :return:
        '''
        self.battery_state=value
