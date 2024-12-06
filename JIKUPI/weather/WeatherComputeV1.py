# -*- coding: utf-8 -*- 
# @Time : 2022/5/17 9:09 
# @Author : ZKL 
# @File : GPSCompute.py
'''
机库GPS检测，并将检测到的GPS信息进行推送
经度，纬度
'''

import binascii
import threading
import time
import struct

from BASEUtile.HangerState import HangerState
from BASEUtile.logger import Logger
from ConfigIni import ConfigIni
from SATA.SATACom import JKSATACOM
from USBDevice.USBDeviceConfig import USBDeviceConfig
from WFCharge.WFState import WFState


class WeatherInfo485():
    '''
    获取天气(凤向，风速，温度，湿度，降雨，雨量，烟感)信息
    通过RS485协议获取
    '''
    # def __init__(self,state,log):
    #     self.state=state
    #     self.logger=log
    #     self.wait_time=30#等待30秒获取一次GPS数据

    def __init__(self,state,log,configini):
        self.state = state
        self.logger = log
        self.wait_time = 10  # 等待3秒获取一次气象信息，并推送给到web平台
        self.configini=configini
        self.comconfig=USBDeviceConfig(self.configini)

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

    def start_get_weather(self):
        #启动获取GPS信息的线程
        statCom_wea = None
        statCom_wea = JKSATACOM(self.state, self.comconfig.get_device_info_weather(), self.comconfig.get_bps_weather(), self.comconfig.get_timeout_weather(),
                                self.logger,None)
        winddir="北" #推送风向
        windspeed=0 #推送的风速
        temperature=0.0 #温度
        humidity=0.0 #湿度
        rainable=0 #无雨
        rainfall=0.0 #降雨量
        smoke=0 #无烟
        # 发送天气操作命令,十六进制指令，问询帧
        commond_winddir = "02 03 00 00 00 02 C4 38"  # 风向指令
        commond_windspeed = "01 03 00 00 00 02 C4 0B"  # 风速指令
        commond_temperature = "04 03 00 00 00 02 C4 5E"  # 湿度、温度指令
        #commond_humidity = "01 03 00 02 00 02 65 CB"  # 湿度指令
        commond_rainable = "03 03 00 00 00 01 85 E8"  # 是否降雨指令
        commond_rainfall = "05 03 00 00 00 02 C5 8F"  # 降雨量指令
        commond_rainfall_clear="05 06 00 00 00 5A 08 75" #降雨清空指令
        commond_smoke = "09 03 00 03 00 01 75 42"  # 烟雾指令
        rain_clear_num=0
        while True:
            try:
                #if statCom_wea==None:
                statCom_wea = JKSATACOM(self.state, self.comconfig.get_device_info_weather(), self.comconfig.get_bps_weather(), self.comconfig.get_timeout_weather(),
                                self.logger,None)
                if self.configini.get_wind_dir()==True:
                    #----------------风向操作----------------
                    time.sleep(2)
                    statCom_wea.engine.Open_Engine()  # 打开串口
                    statCom_wea.engine.Send_data(bytes.fromhex(commond_winddir))
                    # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
                    result_winddir = statCom_wea.engine.Read_Size(9) # 读取结果,读取9个字节
                    statCom_wea.engine.Close_Engine()
                    if result_winddir==b'':
                        #print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}风向串口获取值为空")
                        # statCom_wea=None
                        # continue
                        pass
                    else:
                        if len(result_winddir) == 0:
                           self.state.set_winddirection("北风")
                        else:
                            data_winddir = binascii.b2a_hex(result_winddir[3:5]).decode('ascii')#获取风向数值
                            #风向的处理
                            winddirnum = int(data_winddir, 16)
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
                            self.state.set_winddirection(f"{winddir}")
                            #print(f"风向:{winddir}")
                if self.configini.get_wind()==True:
                    # ----------------风速操作----------------
                    time.sleep(2)
                    statCom_wea.engine.Open_Engine()  # 打开串口
                    statCom_wea.engine.Send_data(bytes.fromhex(commond_windspeed))
                    # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
                    result_windspeed = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
                    statCom_wea.engine.Close_Engine()
                    if result_windspeed == b'':
                        #print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}风速串口获取值为空")
                        #statCom_wea=None
                        #continue
                        pass
                    else:
                        if len(result_windspeed) == 0:
                            self.state.set_windspeed("0")
                        else:
                            data_windspeed = binascii.b2a_hex(result_windspeed[3:5]).decode('ascii')
                            #print(f"{data_windspeed} 风速串口获取值")
                            # 风的处理
                            windspeed=(int(data_windspeed,16))/10
                            # 结果推送
                            if windspeed>=20:
                                windspeed=1
                            self.state.set_windspeed(f"{windspeed}")
                            #print(f"风speed:{windspeed}")
                if self.configini.get_tem_hum()==True:
                    # ----------------温度、湿度操作----------------
                    time.sleep(2)
                    statCom_wea.engine.Open_Engine()  # 打开串口
                    statCom_wea.engine.Send_data(bytes.fromhex(commond_temperature))
                    # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
                    result_temper_humidity= statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
                    statCom_wea.engine.Close_Engine()
                    if result_temper_humidity == b'':
                        #print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}温湿度串口获取值为空")
                        #statCom_wea=None
                        pass
                    else:
                        if len(result_temper_humidity) == 0:
                            self.state.set_temperature("0.0")
                            self.state.set_humidity("0.0")
                        else:
                            # 湿度的处理
                            data_humidity = binascii.b2a_hex(result_temper_humidity[3:5]).decode('ascii')
                            #print(f"{data_humidity} 湿度串口获取值")
                            data_temperature = binascii.b2a_hex(result_temper_humidity[5:7]).decode('ascii')
                            #print(f"{data_temperature} 温度串口获取值")
                            humidity=int(data_humidity,16)
                            temperature=self.get_num_f_h(data_temperature)
                            #print(f"{temperature} 温度转换后获取值")
                            # 结果推送
                            self.state.set_humidity(f"{humidity/10}")
                            self.state.set_temperature(f"{temperature/10}")
                            #print(f"temperature:{temperature/10} ℃")
                            #print(f"humidity:{humidity/10}% RH")
                if self.configini.get_rain()==True:
                    # ---------------是否有雨操作----------------
                    time.sleep(2)
                    statCom_wea.engine.Open_Engine()  # 打开串口
                    statCom_wea.engine.Send_data(bytes.fromhex(commond_rainable))
                    # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
                    result_rainable = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
                    statCom_wea.engine.Close_Engine()
                    if result_rainable == b'':
                        #print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}雨雪串口获取值为空")
                        #statCom_wea=None
                        pass
                    else:
                        if len(result_rainable) == 0:
                            self.state.set_rain("0")
                        else:
                            data_rain = binascii.b2a_hex(result_rainable[3:5]).decode('ascii')
                            #print(f"{data_rain} 降雨串口获取值")
                            # 雨雪的处理
                            rainable=int(data_rain,16)
                            # 结果推送
                            if rainable not in [0,1]:
                                rainable=0
                            self.state.set_rain(f"{rainable}")
                            #print(f"rainable:{rainable}")
                if self.configini.get_rain_num()==True:
                    # ---------------降雨量操作----------------
                    time.sleep(2)
                    statCom_wea.engine.Open_Engine()  # 打开串口
                    statCom_wea.engine.Send_data(bytes.fromhex(commond_rainfall))
                    # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
                    result_rainfall = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
                    statCom_wea.engine.Close_Engine()
                    if result_rainfall == b'':
                        #print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}雨量串口获取值为空")
                        #statCom_wea=None
                        pass
                    else:
                        if len(result_rainfall) == 0:
                            self.state.set_rainfall("0")
                        else:
                            data_rainfall = binascii.b2a_hex(result_rainfall[3:5]).decode('ascii')
                            #print(f"{data_rainfall} 降雨量串口获取值")
                            # 降雨量的处理
                            data_rf=int(data_rainfall,16)
                            # 结果推送
                            self.state.set_rainfall(f"{data_rf/10}")
                            #print(f"rainfall:{data_rf}")
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
                if self.configini.get_smoke()==True:
                    # ---------------烟雾操作----------------
                    time.sleep(2)
                    statCom_wea.engine.Open_Engine()  # 打开串口
                    statCom_wea.engine.Send_data(bytes.fromhex(commond_smoke))
                    # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
                    result_smoke = statCom_wea.engine.Read_Size(9)  # 读取结果,读取9个字节
                    statCom_wea.engine.Close_Engine()
                    if result_smoke == b'':
                        #print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}烟感串口获取值为空")
                        #statCom_wea=None
                        pass
                    else:
                        if len(result_smoke) == 0:
                            self.state.set_smoke("0")
                        else:
                            data_smoke = binascii.b2a_hex(result_smoke[3:5]).decode('ascii')
                            #print(f"{data_smoke} 烟感串口获取值")
                            # 烟雾的处理
                            data_s=int(data_smoke,16)
                            # 结果推送
                            self.state.set_smoke(f"{data_s}")
                time.sleep(self.wait_time) #有此操作，信号获取数据稳定
            except Exception as e:
                self.logger.get_log.info(f"Weather异常{e}")
                time.sleep(60)
                statCom_wea=None
                continue


if __name__ == "__main__":
    logger = Logger(__name__)  # 日志记录
    wfcstate = WFState()
    hangstate = HangerState(wfcstate)
    configini=ConfigIni()
    ws = WeatherInfo485(hangstate,logger,configini)
    # #启用一个线程
    th = threading.Thread(target=ws.start_get_weather(), args=())
    th.start()
    th.join()  # 等待子进程结束
