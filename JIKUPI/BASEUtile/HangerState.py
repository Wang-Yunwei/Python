# -*- coding: utf-8 -*- 
# @Time : 2021/12/13 11:02 
# @Author : ZKL 
# @File : HangerState.py
# 对机库的状态进行记录，程序初始状态为机库门关闭，推杆打开，空调关闭
import json
from BASEUtile.logger import Logger


class HangerState():
    def __init__(self, wfcstate,airstate):
        self.hanger_door = 'close'  # 机库门状态为打开（open）、关闭(close)、异常（error）
        self.hanger_td_bar = 'close'  # 上下推拉杠状态，打开为open,关闭为close,异常为error
        self.hanger_lr_bar = 'close'  # 左右推拉杠状态，打开为open,关闭为close，异常为error
        self.hanger_bar = 'close'  # 初始状态推拉杆为打开状态
        self.air_condition = 'close'  # 空调状态，打开为open,关闭为close，异常为error
        self.STAT_connet_state = 'close'  # 当前设备串口连接状态
        self.wfcstate = wfcstate  # 无线充电当前状态
        self.uav_controller = 'close'  # 无人机手柄初始状态为关机
        self.rain = '0'
        self.windspeed = '0'
        self.winddirection = '北风'

        self.temperature = 0.0  # 温度
        self.humidity = 0.0  # 湿度
        self.rainfall = 0.0  # 降雨量
        self.smoke = 0  # 无烟
        self.GPS_VALUE = "0.0,0.0"
        self.UPS = 0  # 市电正常
        self.indoor_tem = 0.0  # 机库内温度
        self.indoor_hum = 0.0  # 机库内湿度
        self.night_light_state = 'close'  # 夜间灯状态，默认close
        self.pressure=100 #外部大气压
        self.alarm="close" #警报灯是否开启
        self.airstate=airstate
        self.out_lift="unknown"
        self.logger = Logger(__name__)

    def get_airstate(self):
        '''
        获取空调状态
        '''
        return self.airstate
    def set_airstate(self,value):
        '''
        设置空调状态
        '''
        self.airstate=value
    def set_hanger_door(self, hanger_door):
        '''
        设置机库门的状态
        :param hanger_door:
        :return:
        '''
        if hanger_door != 'open' and hanger_door != 'close' and hanger_door != 'error':
            self.logger.get_log().info(f"机库门，传递参数值错误，传递参数值为{hanger_door}")
            return 'para_error'
        self.logger.get_log().info(f"设置机库门状态，传递参数值为{hanger_door}")
        self.hanger_door = hanger_door

    def get_hanger_door(self):
        '''
        获取机库门的状态
        :return:
        '''
        return self.hanger_door

    def set_hanger_td_bar(self, hanger_td_bar):
        '''
        设置机库上下推杆的状态
        :param hanger_td_bar:
        :return:
        '''
        if hanger_td_bar != 'open' and hanger_td_bar != 'close' and hanger_td_bar != 'error':
            self.logger.get_log().info(f"机库上下推杆，传递参数值错误，传递参数值为{hanger_td_bar}")
            return 'para_error'
        self.logger.get_log().info(f"设置机库上下推杆状态，传递参数值为{hanger_td_bar}")
        self.hanger_td_bar = hanger_td_bar

    def get_hanger_td_bar(self):
        '''
        获取机库上下推杆的状态
        :return:
        '''
        return self.hanger_td_bar

    def set_hanger_bar(self, hanger_bar):
        '''
        设置机库推杆的状态
        :param hanger_td_bar:
        :return:
        '''
        if hanger_bar != 'open' and hanger_bar != 'close' and hanger_bar != 'error':
            self.logger.get_log().info(f"机库推杆，传递参数值错误，传递参数值为{hanger_bar}")
            return 'para_error'
        self.logger.get_log().info(f"设置机库推杆状态，传递参数值为{hanger_bar}")
        self.hanger_bar = hanger_bar

    def get_hanger_bar(self):
        '''
        获取机库推杆的状态
        :return:
        '''
        return self.hanger_bar

    def set_hanger_lr_bar(self, hanger_lr_bar):
        '''
        设置机库左右推杆的状态
        :param hanger_lr_bar:
        :return:
        '''
        if hanger_lr_bar != 'open' and hanger_lr_bar != 'close' and hanger_lr_bar != 'error':
            self.logger.get_log().info(f"机库左右推杆，传递参数值错误，传递参数值为{hanger_lr_bar}")
            return 'para_error'
        self.logger.get_log().info(f"设置机库左右推杆状态，传递参数值为{hanger_lr_bar}")
        self.hanger_lr_bar = hanger_lr_bar

    def get_hanger_lr_bar(self):
        '''
        获取机库左右推杆的状态
        :return:
        '''
        return self.hanger_lr_bar

    def set_air_condition(self, air_condition):
        '''
        设置机库空调的状态
        :param air_condition:
        :return:
        '''
        if air_condition != 'open' and air_condition != 'close' and air_condition != 'error':
            self.logger.get_log().info(f"机库空调设置，传递参数值错误，传递参数值为{air_condition}")
            return 'para_error'
        self.logger.get_log().info(f"设置机库空调状态，传递参数值为{air_condition}")
        self.air_condition = air_condition

    def get_air_condition(self):
        '''
        获取机库空调的状态
        :return:
        '''
        return self.air_condition

    def set_uav_controller(self, uav_controller):
        '''
        设置无人机手柄的状态
        :param air_condition:
        :return:
        '''
        if uav_controller != 'open' and uav_controller != 'close' and uav_controller != 'error':
            self.logger.get_log().info(f"无人机手柄设置，传递参数值错误，传递参数值为{uav_controller}")
            return 'para_error'
        self.logger.get_log().info(f"设置无人机手柄状态，传递参数值为{uav_controller}")
        self.uav_controller = uav_controller

    def get_uav_controller(self):
        '''
        获取机库空调的状态
        :return:
        '''
        return self.uav_controller

    def set_STAT_connet_state(self, STAT_connet_state):
        '''
        设置串口连接状态，如果连接超时，则认为连接异常
        :param STAT_connet_state:
        :return:
        '''
        self.STAT_connet_state = STAT_connet_state

    def get_STAT_connet_state(self):
        '''
        获取机库串口的状态
        :return:
        '''
        return self.STAT_connet_state

    def set_GPS(self, gps_vlue):
        '''
        设置GPS信息
        :param gps_vlue:
        :return:
        '''
        self.GPS_VALUE = gps_vlue

    # ---------------天气操作-------------------------
    def set_windspeed(self, windspeed):
        self.windspeed = windspeed

    def set_winddirection(self, winddirection):
        self.winddirection = winddirection

    def set_rain(self, rain):
        self.rain = rain

    def set_temperature(self, tem_value):
        '''
        设置温度值
        :param tem_value:
        :return:
        '''
        self.temperature = tem_value

    def set_humidity(self, value):
        '''
        设置湿度值
        :param value:
        :return:
        '''
        self.humidity = value

    def set_pressure(self, value):
        '''
        设置大气压
        :param value:
        :return:
        '''
        self.pressure = value

    def set_alarm(self, value):
        '''
        设置警报灯状态
        :param value:
        :return:
        '''
        self.alarm = value

    def set_out_lift(self, value):
        '''
        设置外置升降台状态
        :param value:
        :return:
        '''
        self.out_lift = value

    def set_rainfall(self, value):
        '''
        设置降雨量
        :param value:
        :return:
        '''
        self.rainfall = value

    def set_smoke(self, value):
        '''
        设置烟雾值
        :param value:
        :return:
        '''
        self.smoke = value

    def set_UPS(self, value):
        '''
        设置UPS值
        :param value:
        :return:
        '''
        self.UPS = value

    def set_indoor_tem(self, value):
        '''
        设置机库内温度
        :param value:
        :return:
        '''
        self.indoor_tem = value

    def set_indoor_hum(self, value):
        '''
        设置机库内湿度
        :param value:
        :return:
        '''
        self.indoor_hum = value

    def set_night_light_state(self, value):
        '''
        设置机库夜灯状态
        :param value:
        :return:
        '''
        self.night_light_state = value

    def get_night_light_state(self):
        '''
        获取机库夜灯状态
        :return:
        '''
        return self.night_light_state

    def getHangerState(self):
        '''
        获取当前机库的状态json格式
        :return:
        '''
        result = f"\"hanger_door\": \"{self.hanger_door}\",\"hanger_td_bar\": \"{self.hanger_td_bar}\",\"air_condition\": \"{self.air_condition}\",\"STAT_connet_state\": \"{self.STAT_connet_state}\",\"hanger_lr_bar\": \"{self.hanger_lr_bar}\"," \
                 f"\"charge_state\": \"{self.wfcstate.get_state()}\",\"hanger_bar\": \"{self.hanger_bar}\",\"uav_controller\": \"{self.uav_controller}\",\"windspeed\": \"{self.windspeed}\",\"winddirction\": \"{self.winddirection}\"," \
                 f"\"rain\": \"{self.rain}\",\"GPS\": \"{self.GPS_VALUE}\",\"temperature\": \"{self.temperature}\",\"humidity\": \"{self.humidity}\",\"rainfall\": \"{self.rainfall}\",\"smoke\": \"{self.smoke}\",\"ups\": \"{self.UPS}\",\"battery_value\": \"{self.wfcstate.get_battery_value()}\"," \
                 f"\"indoor_tem\": \"{self.indoor_tem}\",\"indoor_hum\": \"{self.indoor_hum}\",\"night_light_state\": \"{self.night_light_state}\",\"pressure\": \"{self.pressure}\",\"alarm\": \"{self.alarm}\",\"out_lift\": \"{self.out_lift}\",\"hotmodel\": \"{self.airstate.hot_mode}\",\"codemodel\": \"{self.airstate.code_mode}\""
        return "{" + result + "}"

    def get_state_dict(self):
        response = {}
        response["hanger_door"] = self.hanger_door
        response["hanger_td_bar"] = self.hanger_td_bar
        response["hanger_lr_bar"] = self.hanger_lr_bar
        response["hanger_bar"] = self.hanger_bar
        response["air_condition"] = self.air_condition
        response["STAT_connet_state"] = self.STAT_connet_state
        response["uav_controller"] = self.uav_controller
        response["rain"] = self.rain
        response["rainfall"] = self.rainfall
        response["windspeed"] = self.windspeed
        response["winddirction"] = self.winddirection  # 这里特意保持一致改为winddirction
        response["temperature"] = self.temperature
        response["humidity"] = self.humidity
        response["smoke"] = self.smoke
        response["GPS"] = self.GPS_VALUE
        response["ups"] = self.UPS

        response["charge_state"] = self.wfcstate.get_state()  # 这里特意保持一致改为charge_state
        response["battery_value"] = self.wfcstate.get_battery_value()

        response["night_light_state"] = self.night_light_state

        response["pressure"] = self.pressure
        response["alarm"] = self.alarm
        return response

    def get_wfcstate(self):  # 获取充电状态
        return self.wfcstate.get_state()

    def get_wfc_battery_value(self):  # 获取充电电量
        return self.wfcstate.get_battery_value()

    def get_temperature(self):
        return self.temperature

    def get_indoor_tem(self):
        return self.indoor_tem

    def get_indoor_hum(self):
        return self.indoor_hum

    def get_windspeed(self):
        return self.windspeed

    def get_winddirection(self):
        return self.winddirection
