# -*- coding: utf-8 -*-
# @Time : 2022/1/5 22:44
# @Author : ZKL
# @File : WFState.py
# 机库当前状态
import WFCharge.WFStateConstant as WFStateConstant


# class WFState():
#     def __init__(self):
#         self.state = "close"  # 当前无线充电状态，close/charging/standby/takeoff/outage/cool/full
#         self.battery_value = "0"  # 电池电量,满电情况下为100
#         self.station_state = "close"  # 充电箱或发射端状态
#         self.battery_state="normal"#电池状态，normal(正常)/full（满电状态）/cool(降温等待状态)/charging(充电)

def get_battery_state():
    return WFStateConstant.BATTERY_STATE


def set_battery_state(value):
    WFStateConstant.BATTERY_STATE = value


def get_battery_value():
    return WFStateConstant.BATTERY_VALUE


def set_battery_value(value):
    WFStateConstant.BATTERY_VALUE = value


def get_station_state():
    return WFStateConstant.STATION_STATE


def set_station_state(value):
    WFStateConstant.STATION_STATE = value


def get_av_list():
    return WFStateConstant.AV_LIST


def set_av_list(value):
    WFStateConstant.AV_LIST = value


def get_charge_info():
    result = f"\"drone_state\": \"{get_battery_state()}\",\"battery_value\": \"{get_battery_value()}\""
    return "{" + result + "}"

