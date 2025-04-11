# -*- coding: utf-8 -*-
'''
机库配置说明，主要做机库的服务端socket ip设置，站点9位ID绑定（服务端生成后）
全部改为INI配置 by pang.hy
'''
import os
import sqlite3
import sys

import BASEUtile.InitFileTool


def get_websocket_config_info():
    # socket_ip = BASEUtile.InitFileTool.get_str_value("websocket_info", "socket_ip")
    # socket_port = BASEUtile.InitFileTool.get_str_value("websocket_info", "socket_port")
    station_id = BASEUtile.InitFileTool.get_str_value("websocket_info", "station_id")
    web_socket_url = BASEUtile.InitFileTool.get_str_value("websocket_info", "web_socket_url")
    web_socket_heart = BASEUtile.InitFileTool.get_str_value("websocket_info", "web_socket_heart")
    tup = 1, station_id, web_socket_url, web_socket_heart
    list_res = [tup]
    return list_res


def set_websocket_config_info(station_id, web_socket_url, web_socket_heart, logger):
    logger.get_log().info(
        f"[Config Ini]设置链接配置信息: station_id={station_id},web_socket_url={web_socket_url},web_socket_heart={web_socket_heart}")
    # BASEUtile.InitFileTool.set_value("websocket_info", "socket_ip", ip)
    # BASEUtile.InitFileTool.set_value("websocket_info", "socket_port", socket)
    BASEUtile.InitFileTool.set_value("websocket_info", "station_id", station_id)
    BASEUtile.InitFileTool.set_value("websocket_info", "web_socket_url", web_socket_url)
    BASEUtile.InitFileTool.set_value("websocket_info", "web_socket_heart", web_socket_heart)


def get_operation_command_info():  # command应该误写成commond，修改害怕有问题，先保持原样。
    open_door = BASEUtile.InitFileTool.get_str_value("command_info", "open_door")
    close_door = BASEUtile.InitFileTool.get_str_value("command_info", "close_door")
    open_bar = BASEUtile.InitFileTool.get_str_value("command_info", "open_bar")
    close_bar = BASEUtile.InitFileTool.get_str_value("command_info", "close_bar")
    open_air = BASEUtile.InitFileTool.get_str_value("command_info", "open_air")
    close_air = BASEUtile.InitFileTool.get_str_value("command_info", "close_air")
    open_uav = BASEUtile.InitFileTool.get_str_value("command_info", "open_uav")
    close_uav = BASEUtile.InitFileTool.get_str_value("command_info", "close_uav")
    up_lift = BASEUtile.InitFileTool.get_str_value("command_info", "up_lift")
    down_lift = BASEUtile.InitFileTool.get_str_value("command_info", "down_lift")
    turn_lift = BASEUtile.InitFileTool.get_str_value("command_info", "turn_lift")
    back_lift = BASEUtile.InitFileTool.get_str_value("command_info", "back_lift")
    tup = 1, open_door, close_door, open_bar, close_bar, open_air, close_air, open_uav, close_uav, up_lift, down_lift, turn_lift, back_lift
    list_res = [tup]
    return list_res


def set_operation_command_info_sign(logger, **kw):
    for key, value in kw.items():
        logger.get_log().info(f"[Config Ini]设置指令配置信息: {key}={value}")
        print(f"{key}='{value}'")
        if key == "opendoor":
            BASEUtile.InitFileTool.set_value("command_info", "open_door", value)
        elif key == "closedoor":
            BASEUtile.InitFileTool.set_value("command_info", "close_door", value)
        elif key == "openbar":
            BASEUtile.InitFileTool.set_value("command_info", "open_bar", value)
        elif key == "closebar":
            BASEUtile.InitFileTool.set_value("command_info", "close_bar", value)
        elif key == "openair":
            BASEUtile.InitFileTool.set_value("command_info", "open_air", value)
        elif key == "closeair":
            BASEUtile.InitFileTool.set_value("command_info", "close_air", value)
        elif key == "openuav":
            BASEUtile.InitFileTool.set_value("command_info", "open_uav", value)
        elif key == "closeuav":
            BASEUtile.InitFileTool.set_value("command_info", "close_uav", value)
        elif key == "uplift":
            BASEUtile.InitFileTool.set_value("command_info", "up_lift", value)
        elif key == "downlift":
            BASEUtile.InitFileTool.set_value("command_info", "down_lift", value)
        elif key == "turnlift":
            BASEUtile.InitFileTool.set_value("command_info", "turn_lift", value)
        elif key == "backlift":
            BASEUtile.InitFileTool.set_value("command_info", "back_lift", value)


def set_config_info(charge_version, wfc_version, bar_diff_move, GPS, use_weather, weather_485, rain,
                    rain_num, wind, wind_dir, temp_hum, smoke, down_version, wfc_double_connect,
                    wlc_double_connect, need_auto_charge, need_heartbeat_check, indoor_temp, wlc_version, logger):
    logger.get_log().info(
        f"[Config Ini]设置开关等配置信息: charge_version={charge_version},wfc_version={wfc_version},bar_diff_move={bar_diff_move},GPS={GPS},use_weather={use_weather},weather_485={weather_485},rain={rain}"
        f",rain_num={rain_num},wind={wind},wind_dir={wind_dir},temp_hum={temp_hum},smoke={smoke},down_version={down_version},wfc_double_connect={wfc_double_connect}"
        f",wlc_double_connect={wlc_double_connect},need_auto_charge={need_auto_charge},need_heartbeat_check={need_heartbeat_check},indoor_temp={indoor_temp},wlc_version={wlc_version}")
    BASEUtile.InitFileTool.set_value("config_info", "charge_version", charge_version)
    BASEUtile.InitFileTool.set_value("config_info", "wfc_version", wfc_version)
    BASEUtile.InitFileTool.set_value("config_info", "bar_diff_move", bar_diff_move)
    BASEUtile.InitFileTool.set_value("config_info", "GPS", GPS)
    BASEUtile.InitFileTool.set_value("config_info", "use_weather", use_weather)
    BASEUtile.InitFileTool.set_value("config_info", "weather_485", weather_485)
    BASEUtile.InitFileTool.set_value("config_info", "rain", rain)
    BASEUtile.InitFileTool.set_value("config_info", "rain_num", rain_num)
    BASEUtile.InitFileTool.set_value("config_info", "wind", wind)
    BASEUtile.InitFileTool.set_value("config_info", "wind_dir", wind_dir)
    BASEUtile.InitFileTool.set_value("config_info", "temp_hum", temp_hum)
    BASEUtile.InitFileTool.set_value("config_info", "smoke", smoke)
    BASEUtile.InitFileTool.set_value("config_info", "down_version", down_version)
    BASEUtile.InitFileTool.set_value("config_info", "wfc_double_connect", wfc_double_connect)
    BASEUtile.InitFileTool.set_value("config_info", "wlc_double_connect", wlc_double_connect)
    BASEUtile.InitFileTool.set_value("config_info", "need_auto_charge", need_auto_charge)
    BASEUtile.InitFileTool.set_value("config_info", "need_heartbeat_check", need_heartbeat_check)
    BASEUtile.InitFileTool.set_value("config_info", "indoor_temp", indoor_temp)
    BASEUtile.InitFileTool.set_value("config_info", "wlc_version", wlc_version)


def get_config_info():
    charge_version = BASEUtile.InitFileTool.get_str_value("config_info", "charge_version")
    wfc_version = BASEUtile.InitFileTool.get_str_value("config_info", "wfc_version")
    bar_diff_move = BASEUtile.InitFileTool.get_str_value("config_info", "bar_diff_move")
    GPS = BASEUtile.InitFileTool.get_str_value("config_info", "GPS")
    use_weather = BASEUtile.InitFileTool.get_str_value("config_info", "use_weather")
    weather_485 = BASEUtile.InitFileTool.get_str_value("config_info", "weather_485")
    rain = BASEUtile.InitFileTool.get_str_value("config_info", "rain")
    rain_num = BASEUtile.InitFileTool.get_str_value("config_info", "rain_num")
    wind = BASEUtile.InitFileTool.get_str_value("config_info", "wind")
    wind_dir = BASEUtile.InitFileTool.get_str_value("config_info", "wind_dir")
    temp_hum = BASEUtile.InitFileTool.get_str_value("config_info", "temp_hum")
    smoke = BASEUtile.InitFileTool.get_str_value("config_info", "smoke")
    down_version = BASEUtile.InitFileTool.get_str_value("config_info", "down_version")
    wfc_double_connect = BASEUtile.InitFileTool.get_str_value("config_info", "wfc_double_connect")
    wlc_double_connect = BASEUtile.InitFileTool.get_str_value("config_info", "wlc_double_connect")
    need_auto_charge = BASEUtile.InitFileTool.get_str_value("config_info", "need_auto_charge")
    need_heartbeat_check = BASEUtile.InitFileTool.get_str_value("config_info", "need_heartbeat_check")
    indoor_temp = BASEUtile.InitFileTool.get_str_value("config_info", "indoor_temp")
    wlc_version = BASEUtile.InitFileTool.get_str_value("config_info", "wlc_version")
    repeat_bar = BASEUtile.InitFileTool.get_str_value("config_info", "repeat_bar")
    night_charge = BASEUtile.InitFileTool.get_str_value("config_info", "night_charge")
    tup = 1, charge_version, wfc_version, bar_diff_move, GPS, use_weather, weather_485, rain, rain_num, wind, wind_dir, temp_hum, smoke, down_version, wfc_double_connect, wlc_double_connect, need_auto_charge, need_heartbeat_check, indoor_temp, wlc_version, repeat_bar, night_charge
    list_res = [tup]
    return list_res


def set_minio_config_info(minio_ip, minio_username, minio_password, minio_dir, logger):
    logger.get_log().info(
        f"[Config Ini]设置MINIO配置信息: minio_ip={minio_ip},minio_username={minio_username},minio_password={minio_password},minio_dir={minio_dir}")
    BASEUtile.InitFileTool.set_value("minio_info", "minio_ip", minio_ip)
    BASEUtile.InitFileTool.set_value("minio_info", "minio_username", minio_username)
    BASEUtile.InitFileTool.set_value("minio_info", "minio_password", minio_password)
    BASEUtile.InitFileTool.set_value("minio_info", "minio_dir", minio_dir)
    # BASEUtile.InitFileTool.set_value("minio_info", "minio_suffix", minio_suffix)


def get_minio_config_info():
    minio_ip = BASEUtile.InitFileTool.get_str_value("minio_info", "minio_ip")
    minio_username = BASEUtile.InitFileTool.get_str_value("minio_info", "minio_username")
    minio_password = BASEUtile.InitFileTool.get_str_value("minio_info", "minio_password")
    minio_dir = BASEUtile.InitFileTool.get_str_value("minio_info", "minio_dir")
    # minio_suffix = BASEUtile.InitFileTool.get_str_value("minio_info", "minio_suffix")
    tup = 1, minio_ip, minio_username, minio_password, minio_dir
    list_res = [tup]
    return list_res


"""
配置信息
"""


def get_charge_version():
    return BASEUtile.InitFileTool.get_str_value("config_info", "charge_version")


def set_charge_version(value):
    BASEUtile.InitFileTool.set_value("config_info", "charge_version", value)


def get_wfc_version():
    return BASEUtile.InitFileTool.get_str_value("config_info", "wfc_version")


def set_wfc_version(value):
    BASEUtile.InitFileTool.set_value("config_info", "wfc_version", value)


def get_is_wfc_double_connect():
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "wfc_double_connect")


def set_is_wfc_double_connect(value):
    BASEUtile.InitFileTool.set_value("config_info", "wfc_double_connect", value)


def get_wlc_version():
    return BASEUtile.InitFileTool.get_str_value("config_info", "wlc_version")


def set_wlc_version(value):
    BASEUtile.InitFileTool.set_value("config_info", "wlc_version", value)


def get_is_wlc_double_connect():
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "wlc_double_connect")


def set_is_wlc_double_connect(value):
    BASEUtile.InitFileTool.set_value("config_info", "wlc_double_connect", value)


def get_is_bar_diff_move():
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "bar_diff_move")


def set_is_bar_diff_move(value):
    BASEUtile.InitFileTool.set_value("config_info", "bar_diff_move", value)


def get_is_gps():
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "gps")


def set_is_gps(value):
    BASEUtile.InitFileTool.set_value("config_info", "gps", value)


def get_is_use_weather():
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "use_weather")


def set_is_use_weather(value):
    BASEUtile.InitFileTool.set_value("config_info", "use_weather", value)


def get_is_weather_485():
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "weather_485")


def set_is_weather_485(value):
    BASEUtile.InitFileTool.set_value("config_info", "weather_485", value)


def get_is_rain():
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "rain")


def set_is_rain(value):
    BASEUtile.InitFileTool.set_value("config_info", "rain", value)


def get_is_rain_num():
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "rain_num")


def set_is_rain_num(value):
    BASEUtile.InitFileTool.set_value("config_info", "rain_num", value)


def get_is_wind():
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "wind")


def set_is_wind(value):
    BASEUtile.InitFileTool.set_value("config_info", "wind", value)


def get_is_wind_dir():
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "wind_dir")


def set_is_wind_dir(value):
    BASEUtile.InitFileTool.set_value("config_info", "wind_dir", value)


def get_is_temp_hum():
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "temp_hum")


def set_is_temp_hum(value):
    BASEUtile.InitFileTool.set_value("config_info", "temp_hum", value)


def get_is_parking_temp_hum():
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "is_parking_temp_hum")


def set_is_parking_temp_hum(value):
    BASEUtile.InitFileTool.set_value("config_info", "is_parking_temp_hum", value)


def get_is_smoke():
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "smoke")


def set_is_smoke(value):
    BASEUtile.InitFileTool.set_value("config_info", "smoke", value)


def get_down_version():
    """
    下位机版本号获取
    """
    return BASEUtile.InitFileTool.get_str_value("config_info", "down_version")


def set_down_version(value):
    """
    下位机版本号设置
    """
    BASEUtile.InitFileTool.set_value("config_info", "down_version", value)


def get_is_need_auto_charge():
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "need_auto_charge")


def set_is_need_auto_charge(value):
    BASEUtile.InitFileTool.set_value("config_info", "need_auto_charge", value)


def get_is_need_heartbeat_check():
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "need_heartbeat_check")


def set_is_need_heartbeat_check(value):
    BASEUtile.InitFileTool.set_value("config_info", "need_heartbeat_check", value)


def get_is_indoor_temp():
    """
    获取是否读取机库内的温湿度
    """
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "indoor_temp")


def set_is_indoor_temp(value):
    BASEUtile.InitFileTool.set_value("config_info", "indoor_temp", value)


def get_is_night_light():
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "night_light")


def set_is_night_light(value):
    BASEUtile.InitFileTool.set_value("config_info", "night_light", value)


def get_is_night_light_time():
    '''
    是否开启夜灯开启时间段有效
    '''
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "night_light_time")


def set_is_night_light_time(value):
    '''
    是否开启夜灯开启时间段有效
    '''
    BASEUtile.InitFileTool.set_value("config_info", "night_light_time", value)


def get_night_light_time_begin():
    return BASEUtile.InitFileTool.get_str_value("config_info", "night_light_time_begin")


def set_night_light_time_begin(value):
    BASEUtile.InitFileTool.set_value("config_info", "night_light_time_begin", value)


def get_night_light_time_end():
    return BASEUtile.InitFileTool.get_str_value("config_info", "night_light_time_end")


def set_night_light_time_end(value):
    BASEUtile.InitFileTool.set_value("config_info", "night_light_time_end", value)


def get_is_repeat_bar():
    """
    充电失败后，推杆重复夹紧配置
    """
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "repeat_bar")


def set_is_repeat_bar(value):
    """
    充电失败后，推杆重复夹紧配置设置
    """
    BASEUtile.InitFileTool.set_value("config_info", "repeat_bar", value)


def get_is_night_charge():
    '''
    是否开启夜间自动充电功能
    '''
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "night_charge")


def set_is_night_charge(value):
    '''
    是否开启夜间自动充电功能
    '''
    BASEUtile.InitFileTool.set_value("config_info", "night_charge", value)


def get_is_signal_battery_charge():
    '''
    是否开启单电池充电停止充电配置
    '''
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "signal_battery_charge")


def set_is_signal_battery_charge(value):
    '''
    是否开启单电池充电停止充电配置
    '''
    BASEUtile.InitFileTool.set_value("config_info", "signal_battery_charge", value)


def get_weather_wait_time():
    '''
    获取天气等待时间
    '''
    return BASEUtile.InitFileTool.get_str_value("config_info", "weather_wait_time")


def set_weather_wait_time(value):
    '''
    获取天气等待时间
    '''
    return BASEUtile.InitFileTool.set_value("config_info", "weather_wait_time", value)


def get_is_aircon485():
    """
    是否使用485控制空调信息
    """
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "aircon485")


def set_is_aircon485(value):
    """
    是否使用485控制空调信息
    """
    BASEUtile.InitFileTool.set_value("config_info", "aircon485", value)


def get_is_meanopen():
    """
    大场景中是否使用同时开机、开门操作
    """
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "meanopen")


def set_is_meanopen(value):
    """
    大场景中是否使用同时开机、开门操作
    """
    BASEUtile.InitFileTool.set_value("config_info", "meanopen", value)


def get_is_alarm():
    """
    是否使用警示灯装置
    """
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "alarm")


def set_is_alarm(value):
    """
    是否使用警示灯装置
    """
    BASEUtile.InitFileTool.set_value("config_info", "alarm", value)


def get_is_alarm_light():
    """
    是否使用警示灯装置
    """
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "alarm_light")


def set_is_alarm_light(value):
    """
    是否使用警示灯装置
    """
    BASEUtile.InitFileTool.set_value("config_info", "alarm_light", value)


def get_bar_move_style():
    """
    获取推杆打开方式
    """
    return BASEUtile.InitFileTool.get_str_value("config_info", "bar_move_style")


def set_bar_move_style(value):
    """
    保存推杆打开方式
    """
    return BASEUtile.InitFileTool.set_value("config_info", "bar_move_style", value)


def get_gps_type():
    """
    gps方式
    """
    return BASEUtile.InitFileTool.get_str_value("config_info", "GPS_type")


def set_gps_type(value):
    """
    gps方式
    """
    return BASEUtile.InitFileTool.set_value("config_info", "GPS_type", value)


def get_is_td_bar():
    '''
    获取推杆夹紧后前后推杆是否打开
    '''
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "td_bar")


def set_is_td_bar(value):
    '''
    设置推杆夹紧后前后推杆是否打开
    '''
    return BASEUtile.InitFileTool.set_value("config_info", "td_bar", value)


def get_is_blance_charge():
    '''
    获取是否启用均衡充电
    '''
    return BASEUtile.InitFileTool.get_boolean_value("config_info", "blance_charge")


def set_is_blance_charge(value):
    '''
    设置是否启用均衡充电
    '''
    return BASEUtile.InitFileTool.set_value("config_info", "blance_charge", value)


"""
手柄配置
"""


def get_controller_ip():
    '''
    获取遥控器IP地址
    '''
    return BASEUtile.InitFileTool.get_str_value("controller_ip", "controller_ip")


def set_controller_ip(value):
    '''
    设置遥控器IP地址
    '''
    return BASEUtile.InitFileTool.set_value("controller_ip", "controller_ip", value)


def get_con_server_ip_port():
    '''
    获取启动APP上位机地址和端口
    '''
    return BASEUtile.InitFileTool.get_str_value("controller_ip", "con_server_ip_port")


def set_con_server_ip_port(value):
    '''
    设置启动APP上位机地址和端口
    '''
    return BASEUtile.InitFileTool.set_value("controller_ip", "con_server_ip_port", value)


"""
license信息
"""


def get_license_code():
    '''
    获取激活码
    '''
    return BASEUtile.InitFileTool.get_str_value("license_info", "license_code")


def set_license_code(value):
    '''
    设置激活码
    '''
    return BASEUtile.InitFileTool.set_value("license_info", "license_code", value)


"""
空调配置信息
"""


def get_hotsenstem():
    '''
    获取加热敏感温度
    '''
    return BASEUtile.InitFileTool.get_int_value("aircondition_info", "hotsenstem")


def set_hotsenstem(value):
    '''
    设置加热敏感温度
    '''
    return BASEUtile.InitFileTool.set_value("aircondition_info", "hotsenstem", value)


def get_hotstoptem():
    '''
    获取加热停止温度
    '''
    return BASEUtile.InitFileTool.get_int_value("aircondition_info", "hotstoptem")


def set_hotstoptem(value):
    '''
    设置加热停止温度
    '''
    return BASEUtile.InitFileTool.set_value("aircondition_info", "hotstoptem", value)


def get_coldstoptem():
    '''
    获取制冷停止温度
    '''
    return BASEUtile.InitFileTool.get_int_value("aircondition_info", "coldstoptem")


def set_coldstoptem(value):
    '''
    设置制冷停止温度
    '''
    return BASEUtile.InitFileTool.set_value("aircondition_info", "coldstoptem", value)


def get_coldsenstem():
    '''
    获取制冷敏感温度
    '''
    return BASEUtile.InitFileTool.get_int_value("aircondition_info", "coldsenstem")


def set_coldsenstem(value):
    '''
    设置制冷敏感温度
    '''
    return BASEUtile.InitFileTool.set_value("aircondition_info", "coldsenstem", value)


def get_hihum():
    '''
    获取高湿湿度
    '''
    return BASEUtile.InitFileTool.get_int_value("aircondition_info", "hihum")


def set_hihum(value):
    '''
    设置高湿湿度
    '''
    return BASEUtile.InitFileTool.set_value("aircondition_info", "hihum", value)


def get_lowhum():
    '''
    获取低湿湿度
    '''
    return BASEUtile.InitFileTool.get_int_value("aircondition_info", "lowhum")


def set_lowhum(value):
    '''
    设置低湿湿度
    '''
    return BASEUtile.InitFileTool.set_value("aircondition_info", "lowhum", value)


def get_hangar_version():
    '''
    获取机库版本
    '''
    return BASEUtile.InitFileTool.get_str_value("config_info", "hangar_version")


def set_hangar_version(value):
    '''
    设置机库版本
    '''
    return BASEUtile.InitFileTool.set_value("config_info", "hangar_version", value)


def get_hangar_door_state():
    '''
    获取门状态
    '''
    return BASEUtile.InitFileTool.get_str_value("hangar_state_history", "hangar_door_state")


def set_hangar_door_state(value):
    '''
    设置门状态
    '''
    return BASEUtile.InitFileTool.set_value("hangar_state_history", "hangar_door_state", value)


def get_hangar_bar_state():
    '''
    获取夹杆状态
    '''
    return BASEUtile.InitFileTool.get_str_value("hangar_state_history", "hangar_bar_state")


def set_hangar_bar_state(value):
    '''
    设置夹杆状态
    '''
    return BASEUtile.InitFileTool.set_value("hangar_state_history", "hangar_bar_state", value)


def get_updown_lift_state():
    '''
    获取升降台状态
    '''
    return BASEUtile.InitFileTool.get_str_value("hangar_state_history", "updown_lift_state")


def set_updown_lift_state(value):
    '''
    设置升降台状态
    '''
    return BASEUtile.InitFileTool.set_value("hangar_state_history", "updown_lift_state", value)


def get_turn_lift_state():
    '''
    获取旋转台状态
    '''
    return BASEUtile.InitFileTool.get_str_value("hangar_state_history", "turn_lift_state")


def set_turn_lift_state(value):
    '''
    设置旋转台状态
    '''
    return BASEUtile.InitFileTool.set_value("hangar_state_history", "turn_lift_state", value)


def get_updown_lift_version():
    '''
    获取升降台版本
    '''
    return BASEUtile.InitFileTool.get_str_value("config_info", "updown_lift_version")


def set_updown_lift_version(value):
    '''
    设置升降台版本
    '''
    return BASEUtile.InitFileTool.set_value("config_info", "updown_lift_version", value)


def get_air_condition_computer_version():
    '''
    获取空调版本
    '''
    return BASEUtile.InitFileTool.get_str_value("config_info", "air_condition_computer_version")


def set_air_condition_computer_version(value):
    '''
    设置空调版本
    '''
    return BASEUtile.InitFileTool.set_value("config_info", "air_condition_computer_version", value)


def get_web_socket_heart():
    '''
    获取websocket心跳
    '''
    return BASEUtile.InitFileTool.get_int_value("websocket_info", "web_socket_heart")


def set_web_socket_heart(value):
    '''
    设置websocket心跳
    '''
    return BASEUtile.InitFileTool.set_value("websocket_info", "web_socket_heart", value)


def get_upload_log_url():
    '''
    获取上传日志接口
    '''
    return BASEUtile.InitFileTool.get_str_value("config_info", "upload_log_url")


def set_upload_log_url(value):
    '''
    设置上传日志接口
    '''
    return BASEUtile.InitFileTool.set_value("config_info", "upload_log_url", value)


# class Config:
#     def __init__(self):
#         self.logger = None
#         self.db_path = ""
#         # self.db_path = "E:\python_jk_mqtt\JIKUPI\JK.db"
#         # 改为用于参数初始化，兼容旧版本，新版本启动时判断老版本是否有该配置，没有给设定一个默认值
#         BASEUtile.InitFileTool.init_section_option_value("demo_info", "demo01", "demo_show_value")  # 例子，首次版本增加的样例
#         pass
#
#     '''
#     因为MINIO中引入log对象，又引入Config对象，造成直接创建logger会报循环引用异常，而改造引用结构风险太高，故采用外部设置，内部判断
#     '''
#
#     def init_logger(self, out_logger):
#         self.logger = out_logger
#
#     def get_websocket_config_info(self):
#         socket_ip = BASEUtile.InitFileTool.get_str_value("websocket_info", "socket_ip")
#         socket_port = BASEUtile.InitFileTool.get_str_value("websocket_info", "socket_port")
#         station_id = BASEUtile.InitFileTool.get_str_value("websocket_info", "station_id")
#         web_socket_url = BASEUtile.InitFileTool.get_str_value("websocket_info", "web_socket_url")
#         tup = 1, socket_ip, socket_port, station_id, web_socket_url
#         list_res = [tup]
#         return list_res
#
#     def getconfiginfo_db(self):
#         '''
#         获取数据库中配置信息，返回列表的形式（内容为字典）
#         :return:
#         '''
#         try:
#             with sqlite3.connect(self.db_path) as conn:
#                 cursor = conn.cursor()
#                 # 如果已经存在一条数据则进行更新，否则直接插入
#                 select_sql = f"select * from config"
#                 result = cursor.execute(select_sql).fetchall()
#                 # print(f"the result is {result}")
#                 cursor.close()
#                 conn.commit()
#                 return result
#         except Exception as ex:
#             print(f"配置存储异常，{ex}")
#             return None
#
#     def set_websocket_config_info(self, ip, socket, station_id, web_socket_url):
#         if self.logger is not None:
#             self.logger.get_log().info(
#                 f"[Config Ini]设置链接配置信息: socket_ip={ip},socket_port={socket},station_id={station_id},web_socket_url={web_socket_url}")
#         BASEUtile.InitFileTool.set_value("websocket_info", "socket_ip", ip)
#         BASEUtile.InitFileTool.set_value("websocket_info", "socket_port", socket)
#         BASEUtile.InitFileTool.set_value("websocket_info", "station_id", station_id)
#         BASEUtile.InitFileTool.set_value("websocket_info", "web_socket_url", web_socket_url)
#
#     def setconfiginfo_db(self, ip, socket, station_id, web_socket_url):
#         '''
#         数据库中设置机库的信息
#         :param ip:服务器ip地址
#         :param socket:端口号
#         :param station_id:站点ID值，服务端生成后配置
#         :param web_socket_url:完整的websocket访问地址，当其不为空时，直接使用它作为链接地址
#         :return:
#         '''
#         try:
#             with sqlite3.connect(self.db_path) as conn:
#                 cursor = conn.cursor()
#                 # 如果已经存在一条数据则进行更新，否则直接插入
#                 select_sql = f"select * from config"
#                 result = cursor.execute(select_sql).fetchall()
#                 # print(f"the result is {result}")
#                 if len(result) < 1:
#                     self.createConfigTabe()
#                     cursor.execute(
#                         f"insert into config (ip,socket,station_id,web_socket_url) values (\'{ip}\', \'{socket}\', \'{station_id}\', \'{web_socket_url}\')")
#                 else:
#                     if len(result[0]) == 5:
#                         cursor.execute(
#                             f"update config set ip=\'{ip}\',socket=\'{socket}\',station_id=\'{station_id}\',web_socket_url=\'{web_socket_url}\'")
#                     else:
#                         self.createConfigTabe()
#                         cursor.execute(
#                             f"insert into config (ip,socket,station_id,web_socket_url) values (\'{ip}\', \'{socket}\', \'{station_id}\', \'{web_socket_url}\')")
#                 cursor.close()
#                 conn.commit()
#         except Exception as ex:
#             print(f"配置存储异常，{ex}")
#
#     def createConfigTabe(self):
#         #  改为ini，无需创建表，初始化交由init完成
#         pass
#
#     def createConfigTabe_db(self):
#         '''
#         创建数据库config表格
#         :return:
#         '''
#         with sqlite3.connect(self.db_path) as conn:
#             # with sqlite3.connect('/JK.db') as conn:
#             cursor = conn.cursor()
#             cursor.execute("drop table config")
#             cursor.execute(
#                 "CREATE TABLE config(id  integer PRIMARY KEY autoincrement,ip  varchar(50) NOT NULL,socket  varchar(10) NOT NULL,station_id varchar(10) NOT NULL,web_socket_url varchar(256) );")
#             cursor.close()
#             conn.commit()
#
#     def createConfigInfoTabe(self):
#         #  改为ini，无需创建表，初始化交由init完成
#         pass
#
#     def createConfigInfoTabe_db(self):
#         '''
#         创建数据库config表格
#         :return:
#         '''
#         # print("createConfigInfoTabe")
#         with sqlite3.connect(self.db_path) as conn:
#             # with sqlite3.connect('/JK.db') as conn:
#             cursor = conn.cursor()
#             cursor.execute("drop table config_info")
#             cursor.execute(
#                 "CREATE TABLE config_info(id  integer PRIMARY KEY autoincrement,charge_version  varchar(20) NOT NULL,wfc_version  varchar(20) NOT NULL,bar_diff_move  varchar(2) NOT NULL,GPS  varchar(2) NOT NULL,use_weather  varchar(2) NOT NULL,weather_485  varchar(2) NOT NULL,rain  varchar(2) NOT NULL,rain_num  varchar(2) NOT NULL,"
#                 "wind  varchar(2) NOT NULL,wind_dir  varchar(2) NOT NULL,temp_hum  varchar(2) NOT NULL,smoke  varchar(2) NOT NULL,down_version  varchar(10) NOT NULL,wfc_double_connect  varchar(2) NOT NULL,wlc_double_connect  varchar(2) NOT NULL,need_auto_charge  varchar(2) NOT NULL,need_heartbeat_check  varchar(2) NOT NULL,indoor_temp varchar(2) NOT NULL,wlc_version varchar(20) NOT NULL);")
#             cursor.close()
#             conn.commit()
#
#     def createTable(self):
#         #  改为ini，无需创建表，初始化交由init完成
#         pass
#
#     def createTable_db(self):
#         '''
#         创建数据库表格
#         :return:
#         '''
#         # with sqlite3.connect('/home/pi/JIKUPI/JK.db') as conn:
#         #     cursor = conn.cursor()
#         #     cursor.execute("CREATE TABLE config(id  integer PRIMARY KEY autoincrement,ip  varchar(50) NOT NULL,socket  varchar(10) NOT NULL,station_id varchar(10) NOT NULL);")
#         #     cursor.close()
#         #     conn.commit()
#         # with sqlite3.connect(self.db_path) as conn:
#         # #with sqlite3.connect('/JK.db') as conn:
#         #     cursor = conn.cursor()
#         #     cursor.execute("drop table commond")
#         #     cursor.execute(
#         #         "CREATE TABLE commond(id  integer PRIMARY KEY autoincrement,opendoor  varchar(20) NOT NULL,closedoor  varchar(20) NOT NULL,openbar  varchar(50) NOT NULL,closebar  varchar(50) NOT NULL,openair  varchar(20) NOT NULL,closeair  varchar(20) NOT NULL,openuav  varchar(20) NOT NULL,closeuav  varchar(20) NOT NULL);")
#         #     cursor.close()
#         #     conn.commit()
#         with sqlite3.connect(self.db_path) as conn:
#             # with sqlite3.connect('/JK.db') as conn:
#             cursor = conn.cursor()
#             cursor.execute("drop table config_info")
#             cursor.execute(
#                 "CREATE TABLE config_info(id  integer PRIMARY KEY autoincrement,charge_version  varchar(20) NOT NULL,wfc_version  varchar(20) NOT NULL,bar_diff_move  varchar(2) NOT NULL,GPS  varchar(2) NOT NULL,use_weather  varchar(2) NOT NULL,weather_485  varchar(2) NOT NULL,rain  varchar(2) NOT NULL,rain_num  varchar(2) NOT NULL,"
#                 "wind  varchar(2) NOT NULL,wind_dir  varchar(2) NOT NULL,temp_hum  varchar(2) NOT NULL,smoke  varchar(2) NOT NULL,down_version  varchar(10) NOT NULL,wlc_version  varchar(20) NOT NULL);")
#             cursor.close()
#             conn.commit()
#         # with sqlite3.connect(self.db_path) as conn:
#         #     # with sqlite3.connect('/JK.db') as conn:
#         #     cursor = conn.cursor()
#         #     #cursor.execute("drop table config_minio")
#         #     cursor.execute(
#         #         "CREATE TABLE config_minio(id  integer PRIMARY KEY autoincrement,minio_ip  varchar(50) NOT NULL,minio_username  varchar(30) NOT NULL,minio_password  varchar(30) NOT NULL,minio_dir  varchar(20) NOT NULL);")
#         #     cursor.close()
#         #     conn.commit()
#
#     def get_operation_command_info(self):  # command应该误写成commond，修改害怕有问题，先保持原样。
#         open_door = BASEUtile.InitFileTool.get_str_value("command_info", "open_door")
#         close_door = BASEUtile.InitFileTool.get_str_value("command_info", "close_door")
#         open_bar = BASEUtile.InitFileTool.get_str_value("command_info", "open_bar")
#         close_bar = BASEUtile.InitFileTool.get_str_value("command_info", "close_bar")
#         open_air = BASEUtile.InitFileTool.get_str_value("command_info", "open_air")
#         close_air = BASEUtile.InitFileTool.get_str_value("command_info", "close_air")
#         open_uav = BASEUtile.InitFileTool.get_str_value("command_info", "open_uav")
#         close_uav = BASEUtile.InitFileTool.get_str_value("command_info", "close_uav")
#         tup = 1, open_door, close_door, open_bar, close_bar, open_air, close_air, open_uav, close_uav
#         list_res = [tup]
#         return list_res
#
#     def getcommond_db(self):
#         '''
#         获取数据库中命令信息，返回列表的形式（内容为字典）
#         :return:
#         '''
#         try:
#             with sqlite3.connect(self.db_path) as conn:
#                 # with sqlite3.connect('/JK.db') as conn:
#                 cursor = conn.cursor()
#                 # 如果已经存在一条数据则进行更新，否则直接插入
#                 select_sql = f"select * from commond"
#                 result = cursor.execute(select_sql).fetchall()
#                 # print(f"the result is {result}")
#                 cursor.close()
#                 conn.commit()
#                 return result
#         except Exception as ex:
#             print(f"命令读取异常，{ex}")
#             return None
#
#     def set_operation_command_info(self, opendoor, closedoor, openbar, closebar, openair, closeair, openuav, closeuav):
#         if self.logger is not None:
#             self.logger.get_log().info(
#                 f"[Config Ini]设置指令配置信息: open_door={opendoor},close_door={closedoor},open_bar={openbar},close_bar={closebar},open_air={openair},close_air={closeair},open_uav={openuav},close_uav={closeuav}")
#         BASEUtile.InitFileTool.set_value("command_info", "open_door", opendoor)
#         BASEUtile.InitFileTool.set_value("command_info", "close_door", closedoor)
#         BASEUtile.InitFileTool.set_value("command_info", "open_bar", openbar)
#         BASEUtile.InitFileTool.set_value("command_info", "close_bar", closebar)
#         BASEUtile.InitFileTool.set_value("command_info", "open_air", openair)
#         BASEUtile.InitFileTool.set_value("command_info", "close_air", closeair)
#         BASEUtile.InitFileTool.set_value("command_info", "open_uav", openuav)
#         BASEUtile.InitFileTool.set_value("command_info", "close_uav", closeuav)
#
#     def setcommon_db(self, opendoor, closedoor, openbar, closebar, openair, closeair, openuav, closeuav):
#         '''
#         :param opendoor: 开门命令
#         :param closedoor: 关门命令
#         :param openbar: 推杆打开命令
#         :param closebar: 推杆关闭命令
#         :param openair: 空调打开命令
#         :param closeair: 空调关闭命令
#         :param openuav: 手柄打开命令
#         :param closeuav: 手柄关闭命令
#         :return:
#         '''
#         try:
#             with sqlite3.connect(self.db_path) as conn:
#                 # with sqlite3.connect('/JK.db') as conn:
#                 cursor = conn.cursor()
#                 # 如果已经存在一条数据则进行更新，否则直接插入
#                 select_sql = f"select * from commond"
#                 result = cursor.execute(select_sql).fetchall()
#                 # print(f"the result is {result}")
#                 if len(result) < 1:
#                     cursor.execute(
#                         f"insert into commond (opendoor,closedoor,openbar,closebar,openair,closeair,openuav,closeuav) values (\'{opendoor}\', \'{closedoor}\', \'{openbar}\', \'{closebar}\', \'{openair}\', \'{closeair}\', \'{openuav}\', \'{closeuav}\')")
#                 else:
#                     cursor.execute(
#                         f"update commond set opendoor=\'{opendoor}\',closedoor=\'{closedoor}\',openbar=\'{openbar}\',closebar=\'{closebar}\',openair=\'{openair}\',closeair=\'{closeair}\',openuav=\'{openuav}\',closeuav=\'{closeuav}\'")
#                 cursor.close()
#                 conn.commit()
#         except Exception as ex:
#             print(f"命令存储异常，{ex}")
#
#     def set_operation_command_info_sign(self, **kw):
#         for key, value in kw.items():
#             if self.logger is not None:
#                 self.logger.get_log().info(
#                     f"[Config Ini]设置指令配置信息: {key}={value}")
#             print(f"{key}='{value}'")
#             if key == "opendoor":
#                 BASEUtile.InitFileTool.set_value("command_info", "open_door", value)
#             elif key == "closedoor":
#                 BASEUtile.InitFileTool.set_value("command_info", "close_door", value)
#             elif key == "openbar":
#                 BASEUtile.InitFileTool.set_value("command_info", "open_bar", value)
#             elif key == "closebar":
#                 BASEUtile.InitFileTool.set_value("command_info", "close_bar", value)
#             elif key == "openair":
#                 BASEUtile.InitFileTool.set_value("command_info", "open_air", value)
#             elif key == "closeair":
#                 BASEUtile.InitFileTool.set_value("command_info", "close_air", value)
#             elif key == "openuav":
#                 BASEUtile.InitFileTool.set_value("command_info", "open_uav", value)
#             elif key == "closeuav":
#                 BASEUtile.InitFileTool.set_value("command_info", "close_uav", value)
#
#     def setcommon_sign_db(self, **kw):
#         try:
#             with sqlite3.connect(self.db_path) as conn:
#                 # with sqlite3.connect('/JK.db') as conn:
#                 cursor = conn.cursor()
#                 # 如果已经存在一条数据则进行更新，否则直接插入
#                 # select_sql=f"select * from commond"
#                 # print(f"the result is {result}")
#                 sqlstr = "update commond set "
#                 for key, value in kw.items():
#                     sqlstr += f"{key}='{value}'"
#                 cursor.execute(sqlstr)
#                 cursor.close()
#                 conn.commit()
#         except Exception as ex:
#             print(f"命令存储异常，{ex}")
#
#     def set_config_info(self, charge_version, wfc_version, bar_diff_move, GPS, use_weather, weather_485, rain,
#                         rain_num, wind, wind_dir, temp_hum, smoke, down_version, wfc_double_connect,
#                         wlc_double_connect, need_auto_charge, need_heartbeat_check, indoor_temp, wlc_version):
#         if self.logger is not None:
#             self.logger.get_log().info(
#                 f"[Config Ini]设置开关等配置信息: charge_version={charge_version},wfc_version={wfc_version},bar_diff_move={bar_diff_move},GPS={GPS},use_weather={use_weather},weather_485={weather_485},rain={rain}"
#                 f",rain_num={rain_num},wind={wind},wind_dir={wind_dir},temp_hum={temp_hum},smoke={smoke},down_version={down_version},wfc_double_connect={wfc_double_connect}"
#                 f",wlc_double_connect={wlc_double_connect},need_auto_charge={need_auto_charge},need_heartbeat_check={need_heartbeat_check},indoor_temp={indoor_temp},wlc_version={wlc_version}")
#         BASEUtile.InitFileTool.set_value("config_info", "charge_version", charge_version)
#         BASEUtile.InitFileTool.set_value("config_info", "wfc_version", wfc_version)
#         BASEUtile.InitFileTool.set_value("config_info", "bar_diff_move", bar_diff_move)
#         BASEUtile.InitFileTool.set_value("config_info", "GPS", GPS)
#         BASEUtile.InitFileTool.set_value("config_info", "use_weather", use_weather)
#         BASEUtile.InitFileTool.set_value("config_info", "weather_485", weather_485)
#         BASEUtile.InitFileTool.set_value("config_info", "rain", rain)
#         BASEUtile.InitFileTool.set_value("config_info", "rain_num", rain_num)
#         BASEUtile.InitFileTool.set_value("config_info", "wind", wind)
#         BASEUtile.InitFileTool.set_value("config_info", "wind_dir", wind_dir)
#         BASEUtile.InitFileTool.set_value("config_info", "temp_hum", temp_hum)
#         BASEUtile.InitFileTool.set_value("config_info", "smoke", smoke)
#         BASEUtile.InitFileTool.set_value("config_info", "down_version", down_version)
#         BASEUtile.InitFileTool.set_value("config_info", "wfc_double_connect", wfc_double_connect)
#         BASEUtile.InitFileTool.set_value("config_info", "wlc_double_connect", wlc_double_connect)
#         BASEUtile.InitFileTool.set_value("config_info", "need_auto_charge", need_auto_charge)
#         BASEUtile.InitFileTool.set_value("config_info", "need_heartbeat_check", need_heartbeat_check)
#         BASEUtile.InitFileTool.set_value("config_info", "indoor_temp", indoor_temp)
#         BASEUtile.InitFileTool.set_value("config_info", "wlc_version", wlc_version)
#
#     def setDetailConfiginfo_db(self, charge_version, wfc_version, bar_diff_move, GPS, use_weather, weather_485, rain,
#                                rain_num, wind, wind_dir, temp_hum, smoke, down_version, wfc_double_connect,
#                                wlc_double_connect, need_auto_charge, need_heartbeat_check, indoor_temp, wlc_version):
#         try:
#             with sqlite3.connect(self.db_path) as conn:
#                 # with sqlite3.connect('/JK.db') as conn:
#                 cursor = conn.cursor()
#                 # 如果已经存在一条数据则进行更新，否则直接插入
#                 select_sql = f"select * from config_info"
#                 result = cursor.execute(select_sql).fetchall()
#                 # print(f"the result is {result}")
#                 if len(result) < 1:
#                     self.createConfigInfoTabe()
#                     cursor.execute(
#                         f"insert into config_info (charge_version,wfc_version,bar_diff_move,GPS,use_weather,weather_485,rain,rain_num,wind,wind_dir,temp_hum,smoke,down_version, wfc_double_connect, wlc_double_connect, need_auto_charge, need_heartbeat_check,indoor_temp,wlc_version) values (\'{charge_version}\', \'{wfc_version}\', \'{bar_diff_move}\', \'{GPS}\', \'{use_weather}\', \'{weather_485}\', \'{rain}\', \'{rain_num}\', \'{wind}\', \'{wind_dir}\', \'{temp_hum}\', \'{smoke}\', \'{down_version}\', \'{wfc_double_connect}\', \'{wlc_double_connect}\', \'{need_auto_charge}\', \'{need_heartbeat_check}\', \'{indoor_temp}\', \'{wlc_version}\')")
#                 else:
#                     if len(result[0]) == 20:
#                         cursor.execute(
#                             f"update config_info set charge_version=\'{charge_version}\',wfc_version=\'{wfc_version}\',bar_diff_move=\'{bar_diff_move}\',GPS=\'{GPS}\',use_weather=\'{use_weather}\',weather_485=\'{weather_485}\',rain=\'{rain}\',rain_num=\'{rain_num}\',wind=\'{wind}\',wind_dir=\'{wind_dir}\',temp_hum=\'{temp_hum}\',smoke=\'{smoke}\',down_version=\'{down_version}\',wfc_double_connect=\'{wfc_double_connect}\',wlc_double_connect=\'{wlc_double_connect}\',need_auto_charge=\'{need_auto_charge}\',need_heartbeat_check=\'{need_heartbeat_check}\',indoor_temp=\'{indoor_temp}\',wlc_version=\'{wlc_version}\' ")
#                     else:
#                         self.createConfigInfoTabe()
#                         cursor.execute(
#                             f"insert into config_info (charge_version,wfc_version,bar_diff_move,GPS,use_weather,weather_485,rain,rain_num,wind,wind_dir,temp_hum,smoke,down_version, wfc_double_connect, wlc_double_connect, need_auto_charge, need_heartbeat_check,indoor_temp,wlc_version) values (\'{charge_version}\', \'{wfc_version}\', \'{bar_diff_move}\', \'{GPS}\', \'{use_weather}\', \'{weather_485}\', \'{rain}\', \'{rain_num}\', \'{wind}\', \'{wind_dir}\', \'{temp_hum}\', \'{smoke}\', \'{down_version}\', \'{wfc_double_connect}\', \'{wlc_double_connect}\', \'{need_auto_charge}\', \'{need_heartbeat_check}\',\'{indoor_temp}\',\'{wlc_version}\')")
#                 cursor.close()
#                 conn.commit()
#         except Exception as ex:
#             print(f"命令存储异常，{ex}")
#
#     def get_config_info(self):
#         charge_version = BASEUtile.InitFileTool.get_str_value("config_info", "charge_version")
#         wfc_version = BASEUtile.InitFileTool.get_str_value("config_info", "wfc_version")
#         bar_diff_move = BASEUtile.InitFileTool.get_str_value("config_info", "bar_diff_move")
#         GPS = BASEUtile.InitFileTool.get_str_value("config_info", "GPS")
#         use_weather = BASEUtile.InitFileTool.get_str_value("config_info", "use_weather")
#         weather_485 = BASEUtile.InitFileTool.get_str_value("config_info", "weather_485")
#         rain = BASEUtile.InitFileTool.get_str_value("config_info", "rain")
#         rain_num = BASEUtile.InitFileTool.get_str_value("config_info", "rain_num")
#         wind = BASEUtile.InitFileTool.get_str_value("config_info", "wind")
#         wind_dir = BASEUtile.InitFileTool.get_str_value("config_info", "wind_dir")
#         temp_hum = BASEUtile.InitFileTool.get_str_value("config_info", "temp_hum")
#         smoke = BASEUtile.InitFileTool.get_str_value("config_info", "smoke")
#         down_version = BASEUtile.InitFileTool.get_str_value("config_info", "down_version")
#         wfc_double_connect = BASEUtile.InitFileTool.get_str_value("config_info", "wfc_double_connect")
#         wlc_double_connect = BASEUtile.InitFileTool.get_str_value("config_info", "wlc_double_connect")
#         need_auto_charge = BASEUtile.InitFileTool.get_str_value("config_info", "need_auto_charge")
#         need_heartbeat_check = BASEUtile.InitFileTool.get_str_value("config_info", "need_heartbeat_check")
#         indoor_temp = BASEUtile.InitFileTool.get_str_value("config_info", "indoor_temp")
#         wlc_version = BASEUtile.InitFileTool.get_str_value("config_info", "wlc_version")
#         repeat_bar = BASEUtile.InitFileTool.get_str_value("config_info", "repeat_bar")
#         night_charge = BASEUtile.InitFileTool.get_str_value("config_info", "night_charge")
#         tup = 1, charge_version, wfc_version, bar_diff_move, GPS, use_weather, weather_485, rain, rain_num, wind, wind_dir, temp_hum, smoke, down_version, wfc_double_connect, wlc_double_connect, need_auto_charge, need_heartbeat_check, indoor_temp, wlc_version, repeat_bar, night_charge
#         list_res = [tup]
#         return list_res
#
#     def getdetail_config_db(self):
#         '''
#         获取数据库中命令信息，返回列表的形式（内容为字典）
#         :return:
#         '''
#         try:
#             with sqlite3.connect(self.db_path) as conn:
#                 # with sqlite3.connect('/JK.db') as conn:
#                 cursor = conn.cursor()
#                 # 如果已经存在一条数据则进行更新，否则直接插入
#                 select_sql = f"select * from config_info"
#                 result = cursor.execute(select_sql).fetchall()
#                 # print(f"the result is {result}")
#                 cursor.close()
#                 conn.commit()
#                 return result
#         except Exception as ex:
#             print(f"命令读取异常，{ex}")
#             return None
#
#     def setdetail_config_sign(self, **kw):
#         for key, value in kw.items():
#             if self.logger is not None:
#                 self.logger.get_log().info(
#                     f"[Config Ini]设置开关等配置信息: {key}={value}")
#             print(f"{key}='{value}'")
#             if key == "charge_version":
#                 BASEUtile.InitFileTool.set_value("config_info", "charge_version", value)
#             elif key == "wfc_version":
#                 BASEUtile.InitFileTool.set_value("config_info", "wfc_version", value)
#             elif key == "bar_diff_move":
#                 BASEUtile.InitFileTool.set_value("config_info", "bar_diff_move", value)
#             elif key == "GPS":
#                 BASEUtile.InitFileTool.set_value("config_info", "GPS", value)
#             elif key == "use_weather":
#                 BASEUtile.InitFileTool.set_value("config_info", "use_weather", value)
#             elif key == "weather_485":
#                 BASEUtile.InitFileTool.set_value("config_info", "weather_485", value)
#             elif key == "rain":
#                 BASEUtile.InitFileTool.set_value("config_info", "rain", value)
#             elif key == "rain_num":
#                 BASEUtile.InitFileTool.set_value("config_info", "rain_num", value)
#             elif key == "wind":
#                 BASEUtile.InitFileTool.set_value("config_info", "wind", value)
#             elif key == "wind_dir":
#                 BASEUtile.InitFileTool.set_value("config_info", "wind_dir", value)
#             elif key == "temp_hum":
#                 BASEUtile.InitFileTool.set_value("config_info", "temp_hum", value)
#             elif key == "smoke":
#                 BASEUtile.InitFileTool.set_value("config_info", "smoke", value)
#             elif key == "down_version":
#                 BASEUtile.InitFileTool.set_value("config_info", "down_version", value)
#             elif key == "wfc_double_connect":
#                 BASEUtile.InitFileTool.set_value("config_info", "wfc_double_connect", value)
#             elif key == "wlc_double_connect":
#                 BASEUtile.InitFileTool.set_value("config_info", "wlc_double_connect", value)
#             elif key == "need_auto_charge":
#                 BASEUtile.InitFileTool.set_value("config_info", "need_auto_charge", value)
#             elif key == "need_heartbeat_check":
#                 BASEUtile.InitFileTool.set_value("config_info", "need_heartbeat_check", value)
#             elif key == "indoor_temp":
#                 BASEUtile.InitFileTool.set_value("config_info", "indoor_temp", value)
#             elif key == "wlc_version":
#                 BASEUtile.InitFileTool.set_value("config_info", "wlc_version", value)
#             elif key == "repeat_bar":
#                 BASEUtile.InitFileTool.set_value("config_info", "repeat_bar", value)
#             elif key == "night_charge":
#                 BASEUtile.InitFileTool.set_value("config_info", "night_charge", value)
#             elif key == "signal_battery_charge":
#                 BASEUtile.InitFileTool.set_value("config_info", "signal_battery_charge", value)
#             elif key == "weather_wait_time":
#                 BASEUtile.InitFileTool.set_value("config_info", "weather_wait_time", value)
#             elif key == "aircon485":
#                 BASEUtile.InitFileTool.set_value("config_info", "aircon485", value)
#             elif key == "meanopen":
#                 BASEUtile.InitFileTool.set_value("config_info", "meanopen", value)
#             elif key == "alarm":
#                 BASEUtile.InitFileTool.set_value("config_info", "alarm", value)
#             elif key == "bar_move_style":
#                 BASEUtile.InitFileTool.set_value("config_info", "bar_move_style", value)
#
#     def setdetail_config_sign_db(self, **kw):
#         try:
#             with sqlite3.connect(self.db_path) as conn:
#                 # with sqlite3.connect('/JK.db') as conn:
#                 cursor = conn.cursor()
#                 # 如果已经存在一条数据则进行更新，否则直接插入
#                 # select_sql=f"select * from commond"
#                 # print(f"the result is {result}")
#                 sqlstr = "update config_info set "
#                 for key, value in kw.items():
#                     sqlstr += f"{key}='{value}'"
#                 cursor.execute(sqlstr)
#                 cursor.close()
#                 conn.commit()
#         except Exception as ex:
#             print(f"配置存储异常，{ex}")
#
#     def set_minio_config_info(self, minio_ip, minio_username, minio_password, minio_dir):
#         if self.logger is not None:
#             self.logger.get_log().info(
#                 f"[Config Ini]设置MINIO配置信息: minio_ip={minio_ip},minio_username={minio_username},minio_password={minio_password},minio_dir={minio_dir}")
#         BASEUtile.InitFileTool.set_value("minio_info", "minio_ip", minio_ip)
#         BASEUtile.InitFileTool.set_value("minio_info", "minio_username", minio_username)
#         BASEUtile.InitFileTool.set_value("minio_info", "minio_password", minio_password)
#         BASEUtile.InitFileTool.set_value("minio_info", "minio_dir", minio_dir)
#
#     def set_minio_config_db(self, minio_ip, minio_username, minio_password, minio_dir):
#         '''
#         设置minio配置
#         :param ip:
#         :param username:
#         :param password:
#         :param dirname:
#         :return:
#         '''
#         try:
#             with sqlite3.connect(self.db_path) as conn:
#                 # with sqlite3.connect('/JK.db') as conn:
#                 cursor = conn.cursor()
#                 # 如果已经存在一条数据则进行更新，否则直接插入
#                 select_sql = f"select * from config_minio"
#                 result = cursor.execute(select_sql).fetchall()
#                 # print(f"the result is {result}")
#                 if len(result) < 1:
#                     self.createConfigInfoTabe()
#                     cursor.execute(
#                         f"insert into config_minio (minio_ip,minio_username,minio_password,minio_dir) values (\'{minio_ip}\', \'{minio_username}\', \'{minio_password}\', \'{minio_dir}\')")
#                 else:
#                     cursor.execute(
#                         f"update config_minio set minio_ip=\'{minio_ip}\',minio_username=\'{minio_username}\',minio_password=\'{minio_password}\',minio_dir=\'{minio_dir}\'")
#                 cursor.close()
#                 conn.commit()
#         except Exception as ex:
#             print(f"命令存储异常，{ex}")
#
#     def get_minio_config_info(self):
#         minio_ip = BASEUtile.InitFileTool.get_str_value("minio_info", "minio_ip")
#         minio_username = BASEUtile.InitFileTool.get_str_value("minio_info", "minio_username")
#         minio_password = BASEUtile.InitFileTool.get_str_value("minio_info", "minio_password")
#         minio_dir = BASEUtile.InitFileTool.get_str_value("minio_info", "minio_dir")
#         tup = 1, minio_ip, minio_username, minio_password, minio_dir
#         list_res = [tup]
#         return list_res
#
#     def get_minio_config_db(self):
#         try:
#             with sqlite3.connect(self.db_path) as conn:
#                 # with sqlite3.connect('/JK.db') as conn:
#                 cursor = conn.cursor()
#                 # 如果已经存在一条数据则进行更新，否则直接插入
#                 select_sql = f"select * from config_minio"
#                 result = cursor.execute(select_sql).fetchall()
#                 # print(f"the result is {result}")
#                 cursor.close()
#                 conn.commit()
#                 return result
#         except Exception as ex:
#             print(f"命令读取异常，{ex}")
#             return None
#
#     def get_night_light(self):
#         return BASEUtile.InitFileTool.get_boolean_value("config_info", "night_light")
#
#     def set_night_light(self, value):
#         BASEUtile.InitFileTool.set_value("config_info", "night_light", value)
#
#     def get_aircon485(self):
#         return BASEUtile.InitFileTool.get_boolean_value("config_info", "aircon485")
#
#     def set_aircon485(self, value):
#         BASEUtile.InitFileTool.set_value("config_info", "aircon485", value)
#
#     def get_meanopen(self):
#         return BASEUtile.InitFileTool.get_boolean_value("config_info", "meanopen")
#
#     def set_meanopen(self, value):
#         BASEUtile.InitFileTool.set_value("config_info", "meanopen", value)
#
#     def get_alarm(self):
#         return BASEUtile.InitFileTool.get_boolean_value("config_info", "alarm")
#
#     def set_alarm(self, value):
#         BASEUtile.InitFileTool.set_value("config_info", "alarm", value)
#
#     def get_night_light_time_begin(self):
#         return BASEUtile.InitFileTool.get_str_value("config_info", "night_light_time_begin")
#
#     def set_night_light_time_begin(self, value):
#         BASEUtile.InitFileTool.set_value("config_info", "night_light_time_begin", value)
#
#     def get_night_light_time_end(self):
#         return BASEUtile.InitFileTool.get_str_value("config_info", "night_light_time_end")
#
#     def set_night_light_time_end(self, value):
#         BASEUtile.InitFileTool.set_value("config_info", "night_light_time_end", value)
#
#     def get_repeat_bar(self):
#         '''
#         充电失败后，推杆重复夹紧配置
#         '''
#         return BASEUtile.InitFileTool.get_boolean_value("config_info", "repeat_bar")
#
#     def set_repeat_bar(self, value):
#         '''
#         充电失败后，推杆重复夹紧配置设置
#         '''
#         BASEUtile.InitFileTool.set_value("config_info", "repeat_bar", value)
#
#     def get_night_charge(self):
#         '''
#         是否开启夜间自动充电功能
#         '''
#         return BASEUtile.InitFileTool.get_boolean_value("config_info", "night_charge")
#
#     def set_night_charge(self, value):
#         '''
#         是否开启夜间自动充电功能
#         '''
#         BASEUtile.InitFileTool.set_value("config_info", "night_charge", value)
#
#     def get_night_light_time(self):
#         '''
#         是否开启夜灯开启时间段有效
#         '''
#         return BASEUtile.InitFileTool.get_boolean_value("config_info", "night_light_time")
#
#     def set_night_light_time(self, value):
#         '''
#         是否开启夜灯开启时间段有效
#         '''
#         BASEUtile.InitFileTool.set_value("config_info", "night_light_time", value)
#
#     def get_down_version(self):
#         '''
#         下位机版本号获取
#         '''
#         return BASEUtile.InitFileTool.get_str_value("config_info", "down_version")
#
#     def set_down_version(self, value):
#         '''
#         下位机版本号设置
#         '''
#         BASEUtile.InitFileTool.set_value("config_info", "down_version", value)
#
#     def get_signal_battery_charge(self):
#         '''
#         是否开启单电池充电停止充电配置
#         '''
#         return BASEUtile.InitFileTool.get_boolean_value("config_info", "signal_battery_charge")
#
#     def set_signal_battery_charge(self, value):
#         '''
#         是否开启单电池充电停止充电配置
#         '''
#         BASEUtile.InitFileTool.set_value("config_info", "signal_battery_charge", value)
#
#     def get_weather_wait_time(self):
#         '''
#         获取天气等待时间
#         '''
#         return BASEUtile.InitFileTool.get_str_value("config_info", "weather_wait_time")
#
#     def set_weather_wait_time(self, value):
#         '''
#         获取天气等待时间
#         '''
#         return BASEUtile.InitFileTool.set_value("config_info", "weather_wait_time", value)
#
#     def get_bar_move_style(self):
#         '''
#         获取推杆打开方式
#         '''
#         return BASEUtile.InitFileTool.get_str_value("config_info", "bar_move_style")
#
#     def set_bar_move_style(self, value):
#         '''
#         保存推杆打开方式
#         '''
#         return BASEUtile.InitFileTool.set_value("config_info", "bar_move_style", value)
#
#     def get_gps_type(self):
#         '''
#         获取推杆打开方式
#         '''
#         return BASEUtile.InitFileTool.get_str_value("config_info", "GPS_type")
#
#     def set_gps_type(self, value):
#         '''
#         保存推杆打开方式
#         '''
#         return BASEUtile.InitFileTool.set_value("config_info", "GPS_type", value)
#
#     def get_controller_ip(self):
#         '''
#         获取遥控器IP地址
#         '''
#         return BASEUtile.InitFileTool.get_str_value("controller_ip", "controller_ip")
#
#     def set_controller_ip(self, value):
#         '''
#         设置遥控器IP地址
#         '''
#         return BASEUtile.InitFileTool.set_value("controller_ip", "controller_ip", value)
#
#     def get_con_server_ip_port(self):
#         '''
#         获取启动APP上位机地址和端口
#         '''
#         return BASEUtile.InitFileTool.get_str_value("controller_ip", "con_server_ip_port")
#
#     def set_con_server_ip_port(self, value):
#         '''
#         设置启动APP上位机地址和端口
#         '''
#         return BASEUtile.InitFileTool.set_value("controller_ip", "con_server_ip_port", value)
#
#     def get_license_code(self):
#         '''
#         获取激活码
#         '''
#         return BASEUtile.InitFileTool.get_str_value("license_info", "license_code")
#
#     def set_license_code(self, value):
#         '''
#         设置激活码
#         '''
#         return BASEUtile.InitFileTool.set_value("license_info", "license_code", value)
#
#     def get_td_bar(self):
#         '''
#         获取推杆夹紧后前后推杆是否打开
#         '''
#         return BASEUtile.InitFileTool.get_boolean_value("config_info", "td_bar")
#
#     def set_td_bar(self, value):
#         '''
#         设置推杆夹紧后前后推杆是否打开
#         '''
#         return BASEUtile.InitFileTool.set_value("config_info", "td_bar", value)
#
#     def get_blance_charge(self):
#         '''
#         获取是否启用均衡充电
#         '''
#         return BASEUtile.InitFileTool.get_boolean_value("config_info", "blance_charge")
#
#     def set_blance_charge(self, value):
#         '''
#         设置是否启用均衡充电
#         '''
#         return BASEUtile.InitFileTool.set_value("config_info", "blance_charge", value)
#
#     # coldstoptem = params['coldstoptem']
#     # coldsenstem = params['coldsenstem']
#     # hotstoptem = params['hotstoptem']
#     # hotsenstem = params['hotsenstem']
#     def get_hotsenstem(self):
#         '''
#         获取加热敏感温度
#         '''
#         return BASEUtile.InitFileTool.get_int_value("aircondition_info", "hotsenstem")
#
#     def set_hotsenstem(self, value):
#         '''
#         设置加热敏感温度
#         '''
#         return BASEUtile.InitFileTool.set_value("aircondition_info", "hotsenstem", value)
#
#     def get_hotstoptem(self):
#         '''
#         获取加热停止温度
#         '''
#         return BASEUtile.InitFileTool.get_int_value("aircondition_info", "hotstoptem")
#
#     def set_hotstoptem(self, value):
#         '''
#         设置加热停止温度
#         '''
#         return BASEUtile.InitFileTool.set_value("aircondition_info", "hotstoptem", value)
#
#     def get_coldstoptem(self):
#         '''
#         获取制冷停止温度
#         '''
#         return BASEUtile.InitFileTool.get_int_value("aircondition_info", "coldstoptem")
#
#     def set_coldstoptem(self, value):
#         '''
#         设置制冷停止温度
#         '''
#         return BASEUtile.InitFileTool.set_value("aircondition_info", "coldstoptem", value)
#
#     def get_coldsenstem(self):
#         '''
#         获取制冷敏感温度
#         '''
#         return BASEUtile.InitFileTool.get_int_value("aircondition_info", "coldsenstem")
#
#     def set_coldsenstem(self, value):
#         '''
#         设置制冷敏感温度
#         '''
#         return BASEUtile.InitFileTool.set_value("aircondition_info", "coldsenstem", value)
#
#     def get_hihum(self):
#         '''
#         获取高湿湿度
#         '''
#         return BASEUtile.InitFileTool.get_int_value("aircondition_info", "hihum")
#
#     def set_hihum(self, value):
#         '''
#         设置高湿湿度
#         '''
#         return BASEUtile.InitFileTool.set_value("aircondition_info", "hihum", value)
#
#     def get_lowhum(self):
#         '''
#         获取低湿湿度
#         '''
#         return BASEUtile.InitFileTool.get_int_value("aircondition_info", "lowhum")
#
#     def set_lowhum(self, value):
#         '''
#         设置低湿湿度
#         '''
#         return BASEUtile.InitFileTool.set_value("aircondition_info", "lowhum", value)


# 测试见testConfig.py
if __name__ == "__main__":
    pass
