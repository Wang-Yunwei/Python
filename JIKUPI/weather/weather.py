# -*- coding: utf-8 -*- 
# @Time : 2022/2/11 17:20 
# @Author : ZKL 
# @File : weather.py
# 获取天气信息
import binascii
import threading
import time

import BASEUtile.HangarState as HangarState
from BASEUtile.logger import Logger
from SATA.SATACom import JKSATACOM
import SerialUsedStateFlag as SerialUsedStateFlag
import USBDevice.USBDeviceConfig as USBDeviceConfig
import BASEUtile.Config as Config


# from WFCharge.WFState import WFState


class WeatherInfo:
    '''
    获取天气信息
    '''

    def __init__(self, log):
        # self.state=state
        self.logger = log
        self.wait_time = 10  # 等待3秒获取一次天气数据
        self.comstate_flag = SerialUsedStateFlag  # 串口标识
        # USBDeviceConfig = USBDeviceConfig()

    def hexShow(self, argv):
        hLen = len(argv)
        out_s = ''
        for i in range(hLen):
            out_s = out_s + '{:02X}'.format(argv[i]) + ' '
        return out_s

    def startgetinfo(self):
        # 启动获取天气的线程
        statCom_bar = None
        statCom_bar = JKSATACOM(USBDeviceConfig.get_serial_usb_bar(), USBDeviceConfig.get_serial_bps_bar(), 2,
                                # USBDeviceConfig.get_timeout_bar(),
                                self.logger, 0)
        windspeed_push = 0  # 推送的风速
        currentwindspeed = 0  # 当前瞬时风速
        wind_list = []
        times = 1  # 3秒读取一次，15秒推送最大值
        while True:
            try:
                if statCom_bar == None:
                    statCom_bar = JKSATACOM(USBDeviceConfig.get_serial_usb_bar(), USBDeviceConfig.get_serial_bps_bar(), 2,
                                            # USBDeviceConfig.get_timeout_bar(),
                                            self.logger, 0)
                # 发送天气操作命令
                commond = "700000\r\n"
                if self.comstate_flag.get_is_used_serial_bar() == True or self.comstate_flag.get_bar_waiting() == True:  # 被占用或者有高级命令等待
                    time.sleep(10)  # 等待8秒再做操作
                    continue
                else:
                    self.comstate_flag.set_used_serial_bar()
                    statCom_bar.engine.Open_Engine()  # 打开串口
                    statCom_bar.engine.Send_data(commond.encode('ascii'))
                    result_org = statCom_bar.engine.Read_Size(6)  # 读取结果,读取6个字节
                    # result_org = statCom_bar.engine.read_all_data()  # 读取结果
                    statCom_bar.engine.Close_Engine()
                    self.comstate_flag.set_used_serial_free_bar()
                    result_org = bytes.fromhex(self.hexShow(result_org))
                    # print(f"天气---返回值为：{result_org[:2]}")#结果为b'/x00/x01/x00/x07/x00/x00'
                    if result_org == b'':
                        time.sleep(30)
                        statCom_bar = None
                        continue
                    windspeed = binascii.b2a_hex(result_org[0:2]).decode('ascii')
                    winddir = binascii.b2a_hex(result_org[2:4]).decode('ascii')
                    rainnum = binascii.b2a_hex(result_org[4:6]).decode('ascii')
                    # print(f"wind is {windspeed},{winddir},{rainnum}")
                    if len(result_org) == 0:
                        HangarState.set_wind_speed_value("error")
                        HangarState.set_wind_direction_value("error")
                        HangarState.set_is_rain_state("error")
                    else:
                        # 十六进制转10进制
                        # 风速、风向、雨雪
                        # self.state.set_windspeed(str(int(result_windsp.upper(), 16)))#16进制转10进制
                        # 判断风向
                        winddirnum = int(winddir, 16)
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
                            winddir = "北"

                        currentwindspeed = int(windspeed, 16) / 10
                        wind_list.append(currentwindspeed)
                        if times == 5:
                            times = 1
                            windspeed_push = max(wind_list)
                            wind_list.clear()  # 清除列表内容
                        else:
                            times = times + 1
                        if Config.get_is_wind() == True:
                            if windspeed_push > 50:
                                windspeed_push = 0
                            HangarState.set_wind_speed_value(windspeed_push)
                        if Config.get_is_wind_dir() == True:
                            HangarState.set_wind_direction_value(winddir)
                        if Config.get_is_rain() == True:
                            HangarState.set_is_rain_state(int(rainnum, 16))
                    # print(int(windspeed,16)/10,winddir,int(rainnum,16))
                time.sleep(self.wait_time)  # 有此操作，信号获取数据稳定
            except Exception as e:
                # print(f"天气异常{e}")
                self.comstate_flag.set_used_serial_free_bar()
                time.sleep(self.wait_time)
                statCom_bar = None
                continue


if __name__ == "__main__":
    pass
    # logger = Logger(__name__)  # 日志记录
    # wfcstate = WFState()
    # hangstate = HangarState(wfcstate)
    # configini = ConfigIni()
    # comstate = StateFlag()
    # ws = WeatherInfo(hangstate, logger, comstate, configini)
    # # #启用一个线程
    # th = threading.Thread(target=ws.startgetinfo, args=())
    # th.start()
    # th.join()  # 等待子进程结束
