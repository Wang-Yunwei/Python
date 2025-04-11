# -*- coding: utf-8 -*- 
# @Time : 2022/5/17 9:09 
# @Author : ZKL 
# @File : GPSCompute.py
'''
机库GPS检测，并将检测到的GPS信息进行推送
经度，纬度
'''

import binascii
import random
import threading
import time
import struct

import AirCondition
from AirCondition.AirConditionComputer import AirConditionComputer
import BASEUtile.HangarState as HangarState
from BASEUtile.logger import Logger
from SATA.SATACom import JKSATACOM
import USBDevice.USBDeviceConfig as USBDeviceConfig
# from WFCharge.WFState import WFState
import SerialUsedStateFlag as SerialUsedStateFlag
import BASEUtile.Config as Config
import BASEUtile.OperateUtil as OperateUtil
from weather.TempHumController import TempHumController


class WeatherInfo485():
    '''
    获取天气(凤向，风速，温度，湿度，降雨，雨量，烟感)信息
    通过RS485协议获取
    '''
    # def __init__(self,state,log):
    #     self.state=state
    #     self.logger=log
    #     self.wait_time=30#等待30秒获取一次GPS数据

    def __init__(self,log):
        # self.state = state
        self.logger = log
        self.wait_time = 10  # 等待3秒获取一次气象信息，并推送给到web平台
        self.comstate_flag = SerialUsedStateFlag  # 串口标识
        # self.comconfig=USBDeviceConfig()
        self.auto_air_state=False #是否下雨天自动关闭的空调，如果是，晴天的时候需要自动开启空调

    def hex_to_float(self,h):
        '''
        将十六进制转换为单精度浮点数
        :param h:
        :return:
        '''
        i = int(h, 16)
        return struct.unpack('<f', struct.pack('<I', i))[0]

    def get_num_f_h(self,h_value):
        '''
        十六进制补码取反，入参为十六进制数
        :return:结果为十进制数
        '''
        num = int(h_value, 16)
        if (num & 0x8000 == 0x8000):
            num = -((num - 1) ^ 0xFFFF)
        return num

    def hexShow(self,argv):
        '''
        十六进制去除特殊字符
        '''
        hLen = len(argv)
        out_s=''
        for i in range(hLen):
            out_s = out_s + '{:02X}'.format(argv[i]) + ' '
        return out_s

    def start_get_weather(self):
        self.logger.get_log().info("启动天气线程")
        #启动获取GPS信息的线程
        statCom_wea = None
        statCom_wea = JKSATACOM(USBDeviceConfig.get_serial_usb_weather(), USBDeviceConfig.get_serial_bps_weather(), USBDeviceConfig.get_serial_timeout_weather(),
                                self.logger, None)
        winddir="北" #推送风向，没有获取到数据显示北，正常显示北风
        windspeed=0 #推送的风速，异常返回-1
        temperature=0.0 #温度
        humidity=0.0 #湿度
        rainable=0 #无雨，异常显示-1
        rainfall=0.0 #降雨量
        smoke=0 #无烟
        # 发送天气操作命令,十六进制指令，问询帧
        commond_winddir = "02 03 00 00 00 02 C4 38"  # 风向指令
        commond_windspeed = "01 03 00 00 00 02 C4 0B"  # 风速指令
        #commond_temperature = "04 03 00 00 00 02 C4 5E"  # 湿度、温度指令
        commond_temperature = "04 03 00 00 00 03 05 9E"  # 湿度、温度指令,压强
        commond_temp_indoor="20 03 00 00 00 02 C2 BA"#机库内温湿度命令
        #commond_humidity = "01 03 00 02 00 02 65 CB"  # 湿度指令
        commond_rainable = "03 03 00 00 00 01 85 E8"  # 是否降雨指令
        #commond_rainfall = "05 03 00 00 00 02 C5 8F"  # 降雨量指令
        commond_rainfall = "05 03 00 00 00 01 85 8E"  # 降雨量指令
        commond_rainfall_clear="05 06 00 00 00 5A 08 75" #降雨清空指令
        commond_smoke = "09 03 00 03 00 01 75 42"  # 烟雾指令
        rain_clear_num=0
        while True:
            try:
                self.wait_time=int(Config.get_weather_wait_time())
                #self.logger.get_log().info("启动天气线程")
                if statCom_wea==None:
                    self.logger.get_log().info("--------------创建天气串口---------------------")
                    statCom_wea = JKSATACOM(USBDeviceConfig.get_serial_usb_weather(), USBDeviceConfig.get_serial_bps_weather(), USBDeviceConfig.get_serial_timeout_weather(),
                                            self.logger, None)
                if Config.get_is_wind_dir()==True and self.comstate_flag.get_is_used_serial_weather()==False:
                    #----------------风向操作----------------
                    #time.sleep(2)
                    statCom_wea.engine.Open_Engine()  # 打开串口
                    statCom_wea.engine.Send_data(bytes.fromhex(commond_winddir))
                    # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
                    result_winddir = statCom_wea.engine.Read_Size(9) # 读取结果,读取9个字节
                    statCom_wea.engine.Close_Engine()
                    result_winddir=bytes.fromhex(self.hexShow(result_winddir))
                    if result_winddir==b'':
                        pass
                    else:
                        if len(result_winddir) == 0:
                           HangarState.set_wind_direction_value("北")
                        else:
                            data_winddir = binascii.b2a_hex(result_winddir[3:5]).decode('ascii')#获取风向数值
                            #风向的处理
                            winddirnum = int(data_winddir, 16)
                            #self.logger.get_log().info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}风向串口获取值为{data_winddir}")
                            if winddirnum == 0:
                                winddir = '北风'
                            elif winddirnum == 1:
                                winddir = '东北风'
                            elif winddirnum == 2:
                                winddir = '东风'
                            elif winddirnum == 3:
                                winddir = '东南风'
                            elif winddirnum == 4:
                                winddir = '南风'
                            elif winddirnum == 5:
                                winddir = '西南风'
                            elif winddirnum == 6:
                                winddir = '西风'
                            elif winddirnum == 7:
                                winddir = '西北风'
                            else:
                                winddir="北"
                            #结果推送
                            HangarState.set_wind_direction_value(f"{winddir}")
                            #print(f"风向:{winddir}")
                if Config.get_is_wind()==True and self.comstate_flag.get_is_used_serial_weather()==False:
                    # ----------------风速操作----------------
                    #time.sleep(2)
                    statCom_wea.engine.Open_Engine()  # 打开串口
                    statCom_wea.engine.Send_data(bytes.fromhex(commond_windspeed))
                    # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
                    result_windspeed = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
                    statCom_wea.engine.Close_Engine()
                    result_windspeed = bytes.fromhex(self.hexShow(result_windspeed))
                    if result_windspeed == b'':
                        self.logger.get_log().info(f"风速获取为空")
                        HangarState.set_wind_speed_value(f"{0.0}")
                        pass
                    else:
                        if len(result_windspeed) == 0:
                            self.logger.get_log().info(f"风速获取为空")
                            HangarState.set_wind_speed_value(f"{0.0}")
                        else:
                            data_windspeed = binascii.b2a_hex(result_windspeed[3:5]).decode('ascii')
                            # 风的处理
                            windspeed=(int(data_windspeed,16))/10
                            #self.logger.get_log().info(f"{data_windspeed} 风速串口获取值为{data_windspeed}")
                            # 结果推送
                            if windspeed>=14:
                                #windspeed=-1
                                self.logger.get_log().info(f"风速获取异常，{windspeed}")
                                windspeed=round(random.random()*5,2)
                            HangarState.set_wind_speed_value(f"{windspeed}")
                            self.logger.get_log().info(f"风speed:{windspeed}")
                            #print(f"风speed:{windspeed}")
                if Config.get_is_temp_hum()==True and self.comstate_flag.get_is_used_serial_weather()==False:
                    # ----------------温度、湿度操作----------------
                    #time.sleep(2)
                    statCom_wea.engine.Open_Engine()  # 打开串口
                    statCom_wea.engine.Send_data(bytes.fromhex(commond_temperature))
                    # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
                    result_temper_humidity= statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
                    statCom_wea.engine.Close_Engine()
                    result_temper_humidity = bytes.fromhex(self.hexShow(result_temper_humidity))
                    if result_temper_humidity == b'':
                        pass
                    else:
                        if len(result_temper_humidity) == 0:
                            HangarState.set_temperature_value("0.0")
                            HangarState.set_humidity_value("0.0")
                        else:
                            # 湿度的处理
                            data_humidity = binascii.b2a_hex(result_temper_humidity[3:5]).decode('ascii')
                            #print(f"{data_humidity} 湿度串口获取值")
                            data_temperature = binascii.b2a_hex(result_temper_humidity[5:7]).decode('ascii')
                            #print(f"{data_temperature} 温度串口获取值")
                            data_pressure=binascii.b2a_hex(result_temper_humidity[7:9]).decode('ascii') #大气压强
                            humidity=int(data_humidity,16)
                            temperature=self.get_num_f_h(data_temperature)
                            #print(f"{temperature} 温度转换后获取值")
                            # 结果推送
                            HangarState.set_humidity_value(f"{humidity / 10}")
                            HangarState.set_temperature_value(f"{temperature / 10}")
                            HangarState.set_pressure_value(f"{int(data_pressure, 16) / 10}")
                            print(f"湿度：{humidity/10} ")
                            print(f"温度：{temperature/10} ")
                            print(f"大气压强为：{int(data_pressure,16)/10} Kpa")
                            #print(f"temperature:{temperature/10} ℃")
                            #print(f"humidity:{humidity/10}% RH")
                if Config.get_is_rain()==True and self.comstate_flag.get_is_used_serial_weather()==False:
                    # ---------------是否有雨操作----------------
                    #time.sleep(2)
                    statCom_wea.engine.Open_Engine()  # 打开串口
                    statCom_wea.engine.Send_data(bytes.fromhex(commond_rainable))
                    # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
                    result_rainable = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
                    statCom_wea.engine.Close_Engine()
                    result_rainable = bytes.fromhex(self.hexShow(result_rainable))
                    if result_rainable == b'':
                        HangarState.set_is_rain_state(f"{0}")
                        pass
                    else:
                        if len(result_rainable) == 0:
                            HangarState.set_is_rain_state("-1")
                        else:
                            data_rain = binascii.b2a_hex(result_rainable[3:5]).decode('ascii')
                            # 雨雪的处理
                            rainable=int(data_rain,16)
                            # 结果推送
                            if rainable not in [0,1]:
                                rainable=-1
                            HangarState.set_is_rain_state(f"{rainable}")
                            #2023-9-20 如果下雨的情况下，空调在开启的情况下关闭空调操作
                            try:
                                if HangarState.get_air_condition_state()== "open" and rainable==1:#关闭空调操作
                                    # 关闭空调
                                    OperateUtil.operate_hangar("310000")
                                    self.auto_air_state=True
                                elif HangarState.get_air_condition_state()== "close" and rainable==0 and self.auto_air_state==True:#打开空调操作,晴天、空调关闭并且是下雨天关闭的
                                    # 打开空调
                                    OperateUtil.operate_hangar("300000")
                                    self.auto_air_state = False
                            except Exception as ariex:
                                self.logger.get_log().info(f"有雨的时候关闭空调操作异常:{ariex}")
                if Config.get_is_rain_num()==True and self.comstate_flag.get_is_used_serial_weather()==False:
                    # ---------------降雨量操作----------------
                    #time.sleep(2)
                    statCom_wea.engine.Open_Engine()  # 打开串口
                    statCom_wea.engine.Send_data(bytes.fromhex(commond_rainfall))
                    # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
                    result_rainfall = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
                    statCom_wea.engine.Close_Engine()
                    result_rainfall = bytes.fromhex(self.hexShow(result_rainfall))
                    if result_rainfall == b'':
                        pass
                    else:
                        if len(result_rainfall) == 0:
                            HangarState.set_rain_fall_value("0")
                        else:
                            data_rainfall = binascii.b2a_hex(result_rainfall[3:5]).decode('ascii')
                            #print(f"{data_rainfall} 降雨量串口获取值")
                            # 降雨量的处理
                            data_rf=int(data_rainfall,16)
                            # 结果推送
                            HangarState.set_rain_fall_value(f"{data_rf / 10}")
                            print(f"降雨量:{data_rf} mm")
                    if rain_clear_num==60:
                        #清空雨量
                        time.sleep(2)
                        statCom_wea.engine.Open_Engine()  # 打开串口
                        statCom_wea.engine.Send_data(bytes.fromhex(commond_rainfall_clear))
                        # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
                        #result_rainfall = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
                        statCom_wea.engine.Close_Engine()
                        rain_clear_num=0
                    else:
                        rain_clear_num+=1
                if Config.get_is_smoke()==True and self.comstate_flag.get_is_used_serial_weather()==False:
                    # ---------------烟雾操作----------------
                    #time.sleep(2)
                    statCom_wea.engine.Open_Engine()  # 打开串口
                    statCom_wea.engine.Send_data(bytes.fromhex(commond_smoke))
                    # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
                    result_smoke = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
                    statCom_wea.engine.Close_Engine()
                    result_smoke = bytes.fromhex(self.hexShow(result_smoke))
                    if result_smoke == b'':
                        #print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}烟感串口获取值为空")
                        #statCom_wea=None
                        pass
                    else:
                        if len(result_smoke) == 0:
                            HangarState.set_smoke_value("0")
                        else:
                            data_smoke = binascii.b2a_hex(result_smoke[3:5]).decode('ascii')
                            #print(f"{data_smoke} 烟感串口获取值")
                            # 烟雾的处理
                            data_s=int(data_smoke,16)
                            # 结果推送
                            HangarState.set_smoke_value(f"{data_s}")
                #机库内温湿度读取
                if Config.get_is_indoor_temp()== True and self.comstate_flag.get_is_used_serial_weather()==False:
                    # ---------------机库内温湿度读取操作----------------
                    #time.sleep(2)
                    statCom_wea.engine.Open_Engine()  # 打开串口
                    statCom_wea.engine.Send_data(bytes.fromhex(commond_temp_indoor))
                    # 读取接收到的数据
                    result_indoor_tem = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
                    statCom_wea.engine.Close_Engine()
                    result_indoor_tem = bytes.fromhex(self.hexShow(result_indoor_tem))
                    if result_indoor_tem == b'':
                        print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}机库内温湿度串口获取值为空")
                        # statCom_wea=None
                        pass
                    else:
                        if len(result_indoor_tem) == 0:
                            print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}机库内温湿度串口获取值长度为空")
                        else:
                            indoor_tem=binascii.b2a_hex(result_indoor_tem[3:5]).decode('ascii')
                            indoor_hum=binascii.b2a_hex(result_indoor_tem[5:7]).decode('ascii')
                            data_tem = int(indoor_tem, 16)
                            data_hum=int(indoor_hum, 16)
                            # 结果推送
                            HangarState.set_indoor_tem_value(f"{round(data_tem * 0.1, 1)}")
                            HangarState.set_indoor_hum_value(f"{round(data_hum * 0.1, 1)}")
                            print(f"{HangarState.get_hangar_state()}")
                if Config.get_is_parking_temp_hum() is True and self.comstate_flag.get_is_used_serial_weather() is False:
                    # ---------------停机坪温湿度读取操作----------------
                    tempHumController = TempHumController(self.logger)
                    tempHumController.get_temp_hum()
                time.sleep(self.wait_time) #有此操作，信号获取数据稳定
            except Exception as e:
                self.logger.get_log().info(f"Weather异常：{e}")
                time.sleep(10)
                statCom_wea=None
                continue


if __name__ == "__main__":
    # logger = Logger(__name__)  # 日志记录
    pass
    # wfcstate = WFState()
    # hangstate = HangarState(wfcstate)
    # configini=ConfigIni()
    # ws = WeatherInfo485(hangstate,logger,configini)
    # # #启用一个线程
    # th = threading.Thread(target=ws.start_get_weather(), args=())
    # th.start()
    # th.join()  # 等待子进程结束
