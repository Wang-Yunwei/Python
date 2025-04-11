# -*- coding: utf-8 -*- 
# @Time : 2021/12/13 11:02 
# @Author : ZKL 
# @File : HangarState.py
# 对机库的状态进行记录，程序初始状态为机库门关闭，推杆打开，空调关闭
import json
# from BASEUtile.logger import Logger
import BASEUtile.HangarStateConstant as HangarStateConstant
import WFCharge.WFState as WFState
import AirCondition.AirConditionState as AirConditionState
import BASEUtile.Config as Config
import uuid


# class HangarState():
#     def __init__(self):
#         self.hanger_door = 'close'  # 机库门状态为打开（open）、关闭(close)、异常（error）
#         self.hanger_td_bar = 'close'  # 上下推拉杠状态，打开为open,关闭为close,异常为error
#         self.hanger_lr_bar = 'close'  # 左右推拉杠状态，打开为open,关闭为close，异常为error
#         self.hanger_bar = 'close'  # 初始状态推拉杆为打开状态
#         self.air_condition = 'close'  # 空调状态，打开为open,关闭为close，异常为error
#         self.stat_connet_state = 'close'  # 当前设备串口连接状态
#         self.wfcstate = wfcstate  # 无线充电当前状态
#         self.uav_controller = 'close'  # 无人机手柄初始状态为关机
#         self.rain = '0'
#         self.windspeed = '0'
#         self.winddirection = '北风'
#
#         self.temperature = 0.0  # 温度
#         self.humidity = 0.0  # 湿度
#         self.rainfall = 0.0  # 降雨量
#         self.smoke = 0  # 无烟
#         self.GPS_VALUE = "0.0,0.0"
#         self.UPS = 0  # 市电正常
#         self.indoor_tem = 0.0  # 机库内温度
#         self.indoor_hum = 0.0  # 机库内湿度
#         self.night_light_state = 'close'  # 夜间灯状态，默认close
#         self.pressure = 100  # 外部大气压
#         self.alarm = "close"  # 警报灯是否开启
#         self.airstate = airstate
#         self.out_lift = "unknown"
#         self.updown_lift_state = "up"
#         self.shutter_door_state = "close"
#         self.shade_window_state = "close"
#         self.logger = Logger(__name__)

def get_updown_lift_state():
    '''
    获取升降台状态
    '''
    return HangarStateConstant.UPDOWN_LIFT_STATE


def set_updown_lift_state(value):
    '''
    设置升降台状态
    '''
    HangarStateConstant.UPDOWN_LIFT_STATE = value
    Config.set_updown_lift_state(value)


def get_turn_lift_state():
    '''
    获取旋转台状态
    '''
    return HangarStateConstant.TURN_LIFT_STATE


def set_turn_lift_state(value):
    '''
    设置旋转台状态
    '''
    HangarStateConstant.TURN_LIFT_STATE = value
    Config.set_turn_lift_state(value)


def get_shade_window_state():
    '''
    获取百叶窗状态
    '''
    return HangarStateConstant.SHADE_WINDOW_STATE


def set_shade_window_state(value):
    '''
    设置百叶窗状态
    '''
    HangarStateConstant.SHADE_WINDOW_STATE = value


# def get_airstate(self):
#     '''
#     获取空调状态
#     '''
#     return self.airstate
#
# def set_airstate(self, value):
#     '''
#     设置空调状态
#     '''
#     self.airstate = value

def set_hangar_door_state(value):
    '''
    设置机库门的状态
    :param value:
    '''
    HangarStateConstant.HANGAR_DOOR_STATE = value
    Config.set_hangar_door_state(value)


def get_hangar_door_state():
    '''
    获取机库门的状态
    '''
    return HangarStateConstant.HANGAR_DOOR_STATE


def set_hangar_td_bar_state(value):
    '''
    设置机库上下推杆的状态
    :param value:
    '''
    # if hanger_td_bar != 'open' and hanger_td_bar != 'close' and hanger_td_bar != 'error':
    #     self.logger.get_log().info(f"机库上下推杆，传递参数值错误，传递参数值为{hanger_td_bar}")
    #     return 'para_error'
    # self.logger.get_log().info(f"设置机库上下推杆状态，传递参数值为{hanger_td_bar}")
    HangarStateConstant.HANGAR_TD_BAR_STATE = value


def get_hangar_td_bar_state():
    '''
    获取机库上下推杆的状态
    :return:
    '''
    return HangarStateConstant.HANGAR_TD_BAR_STATE


def set_hangar_bar_state(value):
    '''
    设置机库推杆的状态
    :param value:
    '''
    # if hanger_bar != 'open' and hanger_bar != 'close' and hanger_bar != 'error':
    #     self.logger.get_log().info(f"机库推杆，传递参数值错误，传递参数值为{hanger_bar}")
    #     return 'para_error'
    # self.logger.get_log().info(f"设置机库推杆状态，传递参数值为{hanger_bar}")
    # self.hanger_bar = hanger_bar
    HangarStateConstant.HANGAR_BAR_STATE = value
    Config.set_hangar_bar_state(value)


def get_hangar_bar_state():
    '''
    获取机库推杆的状态
    :return:
    '''
    return HangarStateConstant.HANGAR_BAR_STATE


def set_hangar_lr_bar_state(value):
    '''
    设置机库左右推杆的状态
    :param value:
    :return:
    '''
    # if hanger_lr_bar != 'open' and hanger_lr_bar != 'close' and hanger_lr_bar != 'error':
    #     self.logger.get_log().info(f"机库左右推杆，传递参数值错误，传递参数值为{hanger_lr_bar}")
    #     return 'para_error'
    # self.logger.get_log().info(f"设置机库左右推杆状态，传递参数值为{hanger_lr_bar}")
    # self.hanger_lr_bar = hanger_lr_bar
    HangarStateConstant.HANGAR_LR_BAR_STATE = value


def get_hangar_lr_bar_state():
    '''
    获取机库左右推杆的状态
    :return:
    '''
    return HangarStateConstant.HANGAR_LR_BAR_STATE


def set_air_condition_state(value):
    '''
    设置机库空调的状态
    :param value:
    :return:
    '''
    # if air_condition != 'open' and air_condition != 'close' and air_condition != 'error':
    #     self.logger.get_log().info(f"机库空调设置，传递参数值错误，传递参数值为{air_condition}")
    #     return 'para_error'
    # self.logger.get_log().info(f"设置机库空调状态，传递参数值为{air_condition}")
    # self.air_condition = air_condition
    HangarStateConstant.AIR_CONDITION_STATE = value


def get_air_condition_state():
    '''
    获取机库空调的状态
    :return:
    '''
    return HangarStateConstant.AIR_CONDITION_STATE


def set_uav_controller_state(value):
    '''
    设置无人机手柄的状态
    :param air_condition:
    :return:
    '''
    # if uav_controller != 'open' and uav_controller != 'close' and uav_controller != 'error':
    #     self.logger.get_log().info(f"无人机手柄设置，传递参数值错误，传递参数值为{uav_controller}")
    #     return 'para_error'
    # self.logger.get_log().info(f"设置无人机手柄状态，传递参数值为{uav_controller}")
    # self.uav_controller = uav_controller
    HangarStateConstant.UAV_CONTROLLER_STATE = value


def get_uav_controller_state():
    '''
    获取机库空调的状态
    :return:
    '''
    return HangarStateConstant.UAV_CONTROLLER_STATE


def set_stat_connect_state(value):
    '''
    设置串口连接状态，如果连接超时，则认为连接异常
    :param value:
    :return:
    '''
    HangarStateConstant.STAT_CONNECT_STATE = value


def get_stat_connect_state():
    '''
    获取机库串口的状态
    :return:
    '''
    return HangarStateConstant.STAT_CONNECT_STATE


def set_gps_value(value):
    '''
    设置GPS信息
    :param value:
    '''
    HangarStateConstant.GPS_VALUE = value


def get_gps_value():
    return HangarStateConstant.GPS_VALUE


def get_wind_speed_value():
    return HangarStateConstant.WIND_SPEED_VALUE


def set_wind_speed_value(value):
    HangarStateConstant.WIND_SPEED_VALUE = value


def get_wind_direction_value():
    return HangarStateConstant.WIND_DIRECTION_VALUE


def set_wind_direction_value(value):
    HangarStateConstant.WIND_DIRECTION_VALUE = value


def get_is_rain_state():
    return HangarStateConstant.IS_RAIN_STATE


def set_is_rain_state(value):
    HangarStateConstant.IS_RAIN_STATE = value


def get_temperature_value():
    return HangarStateConstant.TEMPERATURE_VALUE


def set_temperature_value(value):
    '''
    设置温度值
    :param tem_value:
    :return:
    '''
    HangarStateConstant.TEMPERATURE_VALUE = value


def get_humidity_value():
    '''
    设置湿度值
    :param value:
    :return:
    '''
    return HangarStateConstant.HUMIDITY_VALUE


def set_humidity_value(value):
    '''
    设置湿度值
    :param value:
    :return:
    '''
    HangarStateConstant.HUMIDITY_VALUE = value


def get_parking_temperature_value():
    return HangarStateConstant.PARKING_TEMPERATURE_VALUE


def set_parking_temperature_value(value):
    '''
    设置温度值
    :param tem_value:
    :return:
    '''
    HangarStateConstant.PARKING_TEMPERATURE_VALUE = value


def get_parking_humidity_value():
    '''
    设置湿度值
    :param value:
    :return:
    '''
    return HangarStateConstant.PARKING_HUMIDITY_VALUE


def set_parking_humidity_value(value):
    '''
    设置湿度值
    :param value:
    :return:
    '''
    HangarStateConstant.PARKING_HUMIDITY_VALUE = value


def get_pressure_value():
    '''
    获取大气压
    '''
    return HangarStateConstant.PRESSURE_VALUE


def set_pressure_value(value):
    '''
    设置大气压
    :param value:
    :return:
    '''
    HangarStateConstant.PRESSURE_VALUE = value


def get_alarm_state():
    '''
    获取警报灯状态
    '''
    return HangarStateConstant.ALARM_STATE


def set_alarm_state(value):
    '''
    设置警报灯状态
    :param value:
    :return:
    '''
    HangarStateConstant.ALARM_STATE = value


def get_out_lift_state():
    '''
    设置外置升降台状态
    :param value:
    :return:
    '''
    return HangarStateConstant.OUT_LIFT_STATE


def set_out_lift_state(value):
    '''
    设置外置升降台状态
    :param value:
    :return:
    '''
    HangarStateConstant.OUT_LIFT_STATE = value


def get_rain_fall_value():
    '''
    获取降雨量
    '''
    return HangarStateConstant.RAIN_FALL_VALUE


def set_rain_fall_value(value):
    '''
    设置降雨量
    :param value:
    :return:
    '''
    HangarStateConstant.RAIN_FALL_VALUE = value


def get_smoke_value():
    '''
    获取烟雾值
    '''
    return HangarStateConstant.SMOKE_VALUE


def set_smoke_value(value):
    '''
    设置烟雾值
    :param value:
    :return:
    '''
    HangarStateConstant.SMOKE_VALUE = value


def get_is_ups_state():
    '''
    获取UPS值
    :param value:
    :return:
    '''
    return HangarStateConstant.IS_UPS_STATE


def set_is_ups_state(value):
    '''
    设置UPS值
    :param value:
    :return:
    '''
    HangarStateConstant.IS_UPS_STATE = value


def get_indoor_tem_value():
    return HangarStateConstant.INDOOR_TEM_VALUE


def set_indoor_tem_value(value):
    '''
    设置机库内温度
    :param value:
    :return:
    '''
    HangarStateConstant.INDOOR_TEM_VALUE = value


def get_indoor_hum_value():
    return HangarStateConstant.INDOOR_HUM_VALUE


def set_indoor_hum_value(value):
    '''
    设置机库内湿度
    :param value:
    :return:
    '''
    HangarStateConstant.INDOOR_HUM_VALUE = value


def set_night_light_state(value):
    '''
    设置机库夜灯状态
    :param value:
    :return:
    '''
    HangarStateConstant.NIGHT_LIGHT_STATE = value


def get_night_light_state():
    '''
    获取机库夜灯状态
    :return:
    '''
    return HangarStateConstant.NIGHT_LIGHT_STATE


def get_hangar_version():
    '''
    获取机库版本
    '''
    return HangarStateConstant.HANGAR_VERSION


def set_hangar_version(value):
    '''
    设置机库版本
    '''
    HangarStateConstant.HANGAR_VERSION = value
    Config.set_hangar_version(value)


def open_auto_charge():
    """
    开启自动充电,重置充电配置项
    """
    set_run_auto_charge(1)
    set_charge_uuid(str(uuid.uuid4()))
    set_charge_num(0)
    WFState.set_battery_value("unknown")


def close_auto_charge():
    """
    关闭自动充电
    """
    set_run_auto_charge(0)
    set_charge_num(0)


def get_run_auto_charge():
    return HangarStateConstant.RUN_AUTO_CHARGE


def set_run_auto_charge(value):
    HangarStateConstant.RUN_AUTO_CHARGE = value


def get_charge_uuid():
    return HangarStateConstant.CHARGE_UUID


def set_charge_uuid(value):
    HangarStateConstant.CHARGE_UUID = value


def get_charge_num():
    return HangarStateConstant.CHARGE_NUM


def set_charge_num(value):
    HangarStateConstant.CHARGE_NUM = value


def add_charge_num_error():
    set_charge_num(get_charge_num() + 1)


# def get_wfcstate():  # 获取充电状态
#     return self.wfcstate.get_battery_state()
#
# def get_wfc_battery_value(self):  # 获取充电电量
#     return self.wfcstate.get_battery_value()

def get_hangar_state():
    '''
    获取当前机库的状态json格式
    :return:
    '''
    result = f"\"hanger_door\": \"{get_hangar_door_state()}\",\"hanger_td_bar\": \"{get_hangar_td_bar_state()}\",\"air_condition\": \"{get_air_condition_state()}\"," \
             f"\"STAT_connet_state\": \"{get_stat_connect_state()}\",\"hanger_lr_bar\": \"{get_hangar_lr_bar_state()}\"," \
             f"\"charge_state\": \"{WFState.get_battery_state()}\",\"hanger_bar\": \"{get_hangar_bar_state()}\",\"uav_controller\": \"{get_uav_controller_state()}\"," \
             f"\"windspeed\": \"{get_wind_speed_value()}\",\"winddirction\": \"{get_wind_direction_value()}\",\"rain\": \"{get_is_rain_state()}\"," \
             f"\"GPS\": \"{get_gps_value()}\",\"temperature\": \"{get_temperature_value()}\",\"humidity\": \"{get_humidity_value()}\",\"rainfall\": \"{get_rain_fall_value()}\"," \
             f"\"smoke\": \"{get_smoke_value()}\",\"ups\": \"{get_is_ups_state()}\",\"battery_value\": \"{WFState.get_battery_value()}\"," \
             f"\"indoor_tem\": \"{get_indoor_tem_value()}\",\"indoor_hum\": \"{get_indoor_hum_value()}\",\"night_light_state\": \"{get_night_light_state()}\"," \
             f"\"pressure\": \"{get_pressure_value()}\",\"alarm\": \"{get_alarm_state()}\",\"out_lift\": \"{get_out_lift_state()}\"," \
             f"\"hotmodel\": \"{AirConditionState.get_is_hot_mode()}\",\"codemodel\": \"{AirConditionState.get_is_cold_mode()}\"," \
             f"\"updown_lift\":\"{get_updown_lift_state()}\",\"turn_lift\":\"{get_turn_lift_state()}\",\"hangar_version\":\"{get_hangar_version()}\"," \
             f"\"parking_humidity_value\":\"{get_parking_humidity_value()}\",\"parking_temperature_value\":\"{get_parking_temperature_value()}\" "
    return "{" + result + "}"


def get_hangar_state_dict(self):
    response = {"hanger_door": get_hangar_door_state(), "hanger_td_bar": get_hangar_td_bar_state(),
                "hanger_lr_bar": get_hangar_lr_bar_state(), "hanger_bar": get_hangar_bar_state(),
                "air_condition": get_air_condition_state(), "STAT_connet_state": get_stat_connect_state(),
                "uav_controller": get_uav_controller_state(), "rain": get_is_rain_state(),
                "rainfall": get_rain_fall_value(), "windspeed": get_wind_speed_value(),
                "winddirction": get_wind_direction_value(), "temperature": get_temperature_value(),
                "humidity": get_humidity_value(), "smoke": get_smoke_value(), "GPS": get_gps_value(),
                "ups": get_is_ups_state(), "charge_state": WFState.get_battery_state(),
                "battery_value": WFState.get_battery_value(), "night_light_state": get_night_light_state(),
                "pressure": get_pressure_value(), "alarm": get_alarm_state()}

    return response
