# -*- coding: utf-8 -*- 
# @Time : 2022/6/12 17:41 
# @Author : ZKL 
# @File : ConfigIni.py
import BASEUtile.Config as Config


# class ConfigIni():
#     def __init__(self):
#         self.charge_version = 'wfc'  # wfc无线充电,wlc有线充电
#         self.wfc_version = "V2.0"  # 无线充电版本
#         self.bar_diff_move = True  # 推杆是否启用不同步夹紧，不同步是先夹前后（参数2），再加左右（参数1）
#         self.GPS = False  # 是否使用GPS
#         self.use_weather = False  # 是否启用天气获取
#         self.weather_485 = True  # 是否使用485通信
#         self.rain = True  # 是否读取雨雪传感器
#         self.rain_num = False  # 是否使用降雨量
#         self.wind = True  # 是否使用风力
#         self.wind_dir = True  # 是否使用风向
#         self.temp_hum = False  # 是否使用温湿度传感器
#         self.smoke = False  # 是否使用烟雾传感器
#         self.down_version = "V2.0"  # 下位机版本，主要取别是几个串口问题
#         self.wfc_double_connect = False  # 无线充电是否使用USB全双工通信，手动配置进去
#         self.wlc_double_connect = True  # 触点充电，使用全双工通信
#         self.need_auto_charge = False  # 是否需要自动充电功能
#         self.need_heartbeat_check = False  # 是否需要心跳检测功能
#         self.indoor_temp = False  # 是否读取机库内的温湿度
#         self.wlc_version = "V2.0"  # 触点充电版本
#         #self.repeat_bar=False #是否充电失败后做推杆夹紧操作
#         self.ini_config()
#
#     def ini_config(self):
#         '''
#         根据数据库配置，读取机库配置信息
#         :return:
#         '''
#         # config_db = Config()
#         result = Config.get_config_info()
#         if result is not None and len(result) == 1:
#             self.charge_version = result[0][1]
#             self.wfc_version = result[0][2]  # 无线充电版本
#             self.wlc_version = result[0][19]
#             if (result[0][3].strip() == "0"):
#                 self.bar_diff_move = False  # 推杆是否启用不同步夹紧，不同步是先夹前后（参数2），再加左右（参数1）
#             else:
#                 self.bar_diff_move = True
#             if (result[0][4].strip() == "0"):
#                 self.GPS = False  # 是否使用GPS
#             else:
#                 self.GPS = True
#
#             if (result[0][5].strip() == "0"):
#                 self.use_weather = False  # # 是否启用天气获取
#             else:
#                 self.use_weather = True
#
#             if (result[0][6].strip() == "0"):
#                 self.weather_485 = False  # # 是否使用485通信
#             else:
#                 self.weather_485 = True
#
#             if (result[0][7].strip() == "0"):
#                 self.rain = False  # # 是否读取雨雪传感器
#             else:
#                 self.rain = True
#
#             if (result[0][8].strip() == "0"):
#                 self.rain_num = False  # #  是否使用降雨量
#             else:
#                 self.rain_num = True
#
#             if (result[0][9].strip() == "0"):
#                 self.wind = False  # 是否使用风力
#             else:
#                 self.wind = True
#
#             if (result[0][10].strip() == "0"):
#                 self.wind_dir = False  # 是否使用风向
#             else:
#                 self.wind_dir = True
#
#             if (result[0][11].strip() == "0"):
#                 self.temp_hum = False  # 是否使用温湿度传感器
#             else:
#                 self.temp_hum = True
#
#             if (result[0][12].strip() == "0"):
#                 self.smoke = False  # 是否使用烟雾传感器
#             else:
#                 self.smoke = True
#             self.down_version = result[0][13]  # 下位机版本
#             # v1.0.1追加字段处理，判断兼容旧版本DB
#             # print(f"len(result[0])={len(result[0])}")
#             if len(result[0]) > 14:
#                 if result[0][14].strip() == "0":
#                     self.wfc_double_connect = False  # 无线充电是否使用USB全双工通信
#                 else:
#                     self.wfc_double_connect = True
#
#                 if result[0][15].strip() == "0":
#                     self.wlc_double_connect = False  # 触点充电，使用全双工通信
#                 else:
#                     self.wlc_double_connect = True
#
#                 if result[0][16].strip() == "0":
#                     self.need_auto_charge = False  # 是否需要自动充电功能
#                 else:
#                     self.need_auto_charge = True
#
#                 if result[0][17].strip() == "0":
#                     self.need_heartbeat_check = False  # 是否使用心跳机制
#                 else:
#                     self.need_heartbeat_check = True
#
#                 if result[0][18].strip() == "0":
#                     self.indoor_temp = False  # 是否使用读取机库内的温湿度操作
#                 else:
#                     self.indoor_temp = True
#
#                 # if result[0][20].strip() == "0":
#                 #     self.repeat_bar = False  # 是否启用充电失败后推杆的夹紧操作
#                 # else:
#                 #     self.repeat_bar = True
#
#     def get_charge_version(self):
#         return self.charge_version
#
#     def set_charge_version(self, value):
#         self.charge_version = value
#
#     def get_wfc_version(self):
#         return self.wfc_version
#
#     def set_wfc_version(self, value):
#         self.wfc_version = value
#
#     def set_bar_diff_move(self, value):
#         self.bar_diff_move = value
#
#     def get_bar_diff_move(self):
#         return self.bar_diff_move
#
#     def set_GPS(self, value):
#         self.GPS = value
#
#     def get_GPS(self):
#         return self.GPS
#
#     def set_weather_485(self, value):
#         self.weather_485 = value
#
#     def get_weather_485(self):
#         return self.weather_485
#
#     def set_rain(self, value):
#         self.rain = value
#
#     def get_rain(self):
#         return self.rain
#
#     def set_rain_num(self, value):
#         self.rain_num = value
#
#     def get_rain_num(self):
#         return self.rain_num
#
#     def set_wind(self, value):
#         self.wind = value
#
#     def get_wind(self):
#         return self.wind
#
#     def set_wind_dir(self, value):
#         self.wind_dir = value
#
#     def get_wind_dir(self):
#         return self.wind_dir
#
#     def set_tem_hum(self, value):
#         self.temp_hum = value
#
#     def get_tem_hum(self):
#         return self.temp_hum
#
#     def set_useweather(self, value):
#         self.use_weather = value
#
#     def get_useweather(self):
#         return self.use_weather
#
#     def set_smoke(self, value):
#         self.smoke = value
#
#     def get_smoke(self):
#         return self.smoke
#
#     def set_down_version(self, value):
#         self.down_version = value
#
#     def get_down_version(self):
#         return self.down_version
#
#     def set_wfc_double_connect(self, value):
#         self.wfc_double_connect = value
#
#     def get_wfc_double_connect(self):
#         return self.wfc_double_connect
#
#     def set_wlc_double_connect(self, value):
#         self.wlc_double_connect = value
#
#     def get_wlc_double_connect(self):
#         return self.wlc_double_connect
#
#     def set_need_auto_charge(self, value):
#         self.need_auto_charge = value
#
#     def get_need_auto_charge(self):
#         return self.need_auto_charge
#
#     def set_need_heartbeat_check(self, value):
#         self.need_heartbeat_check = value
#
#     def get_need_heartbeat_check(self):
#         return self.need_heartbeat_check
#
#     def get_indoor_temp(self):
#         return self.indoor_temp
#
#     def set_indoor_temp(self, value):
#         self.indoor_temp = value
#
#     def get_wlc_version(self):
#         return self.wlc_version
#
#     def set_wlc_version(self, value):
#         self.wlc_version = value
#
#     def get_night_light(self):
#         # config = Config()
#         return Config.get_is_night_light()
#
#     def get_night_light_time_begin(self):
#         # config = Config()
#         return Config.get_night_light_time_begin()
#
#     def get_night_light_time_end(self):
#         # config = Config()
#         return Config.get_night_light_time_end()
#
#     def get_repeat_bar(self):
#         # config = Config()
#         return Config.get_is_repeat_bar()
#
#     def set_repeat_bar(self, value):
#         # config = Config()
#         return Config.set_is_repeat_bar(value)
#     def get_night_charge(self):
#         # config = Config()
#         return Config.get_is_night_charge()
#
#     def set_night_charge(self, value):
#         # config = Config()
#         return Config.set_is_night_charge(value)
#
#     def get_night_light_time(self):
#         # config = Config()
#         return Config.get_is_night_light_time()
#
#     def set_night_light_time(self, value):
#         # config = Config()
#         return Config.set_is_night_light_time(value)
#     def get_signal_battery_charge(self):
#         # config = Config()
#         return Config.get_is_signal_battery_charge()
#
#     def set_signal_battery_charge(self, value):
#         # config = Config()
#         return Config.set_is_signal_battery_charge(value)
#
#     def get_weather_wait_time(self):
#         # config=Config()
#         return Config.get_weather_wait_time()
#     def set_weather_wait_time(self,value):
#         # config=Config()
#         return Config.set_weather_wait_time(value)
#
#     def get_aircon485(self):
#         # config = Config()
#         return Config.get_is_aircon485()
#
#     def set_aircon485(self, value):
#         # config = Config()
#         return Config.set_is_aircon485(value)
#
#     def get_meanopen(self):
#         # config = Config()
#         return Config.get_is_meanopen()
#
#     def set_meanopen(self, value):
#         # config = Config()
#         return Config.set_is_meanopen(value)
#
#     def get_alarm(self):
#         # config = Config()
#         return Config.get_is_alarm()
#
#     def set_alarm(self, value):
#         # config = Config()
#         return Config.set_is_alarm(value)
#     def get_bar_move_style(self):
#         # config = Config()
#         return Config.get_bar_move_style()
#
#     def set_bar_move_style(self, value):
#         # config = Config()
#         return Config.set_bar_move_style(value)
#
#     def get_gps_type(self):
#         # config = Config()
#         return Config.get_gps_type()
#
#     def set_gps_type(self, value):
#         # config = Config()
#         return Config.set_gps_type(value)
#
#     def get_controller_ip(self):
#         # config = Config()
#         return Config.get_controller_ip()
#
#     def set_controller_ip(self, value):
#         # config = Config()
#         return Config.set_controller_ip(value)
#
#     def get_con_server_ip_port(self):
#         # config = Config()
#         return Config.get_con_server_ip_port()
#
#     def set_con_server_ip_port(self, value):
#         # config = Config()
#         return Config.set_con_server_ip_port(value)
#
#     def get_license_code(self):
#         # config = Config()
#         return Config.get_license_code()
#
#     def set_license_code(self, value):
#         # config = Config()
#         return Config.set_license_code(value)
#
#     def get_td_bar(self):
#         # config = Config()
#         return Config.get_is_td_bar()
#
#     def set_td_bar(self, value):
#         # config = Config()
#         return Config.set_is_td_bar(value)
#
#     def get_blance_charge(self):
#         # config = Config()
#         return Config.get_is_blance_charge()
#
#     def set_blance_charge(self, value):
#         # config = Config()
#         return Config.set_is_blance_charge(value)
#
#     # coldstoptem = params['coldstoptem']
#     # coldsenstem = params['coldsenstem']
#     # hotstoptem = params['hotstoptem']
#     # hotsenstem = params['hotsenstem']
#     def get_hotsenstem(self):
#         # config = Config()
#         return Config.get_hotsenstem()
#
#     def set_hotsenstem(self, value):
#         # config = Config()
#         return Config.set_hotsenstem(value)
#     def get_hotstoptem(self):
#         # config = Config()
#         return Config.get_hotstoptem()
#
#     def set_hotstoptem(self, value):
#         # config = Config()
#         return Config.set_hotstoptem(value)
#     def get_coldsenstem(self):
#         # config = Config()
#         return Config.get_coldsenstem()
#
#     def set_coldsenstem(self, value):
#         # config = Config()
#         return Config.set_coldsenstem(value)
#     def get_coldstoptem(self):
#         # config = Config()
#         return Config.get_coldstoptem()
#
#     def set_coldstoptem(self, value):
#         # config = Config()
#         return Config.set_coldstoptem(value)
#
#     def get_hihum(self):
#         # config = Config()
#         return Config.get_hihum()
#
#     def set_hihum(self, value):
#         # config = Config()
#         return Config.set_hihum(value)
#
#     def get_lowhum(self):
#         # config = Config()
#         return Config.get_lowhum()
#
#     def set_lowhum(self, value):
#         # config = Config()
#         return Config.set_lowhum(value)