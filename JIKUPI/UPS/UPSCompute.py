# -*- coding: utf-8 -*- 
# @Time : 2022/5/17 9:09 
# @Author : ZKL 
# @File : UPSCompute.py
'''
机库UPS检测，并将检测到的UPS信息进行推送
经度，纬度
'''

import binascii
import threading
import time
import struct

import BASEUtile.HangarState as HangarState
from BASEUtile.logger import Logger
from SATA.SATACom import JKSATACOM
# from WFCharge.WFState import WFState


class UPSInfo():
    '''
    获取UPS信息
    '''
    def __init__(self,log):
        # self.state = state
        self.logger = log
        self.wait_time = 5  # 等待30秒获取一次UPS数据

    def hex_to_float(self,h):
        '''
        将十六进制转换为单精度浮点数
        :param h:
        :return:
        '''
        i = int(h, 16)
        return struct.unpack('<f', struct.pack('<I', i))[0]

    def ups_reset(self):
        '''
        ups重启  S<n>R<m><cr>
        :return:
        '''
        device_info_bar = "/dev/ttyUSBUPS"
        # device_info_bar = "COM7"
        bps_bar = 2400
        timeout_bar = 0
        statCom_ups = JKSATACOM(device_info_bar, bps_bar, timeout_bar,
                                self.logger, None)
        commond_ups = "S0.1R0.2\r\n"  # 获取状态指令
        # 发送操作命令
        statCom_ups.engine.Open_Engine()  # 打开串口
        statCom_ups.engine.Send_data(bytes.fromhex(commond_ups))
        # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
        result_state = statCom_ups.engine.Read_Size(10)  # 读取结果,读取10个字节
        statCom_ups.engine.Close_Engine()
        print(result_state.decode('ascii'))

    def start_get_ups(self):
        #启动获取UPS信息的线程
        device_info_bar = "/dev/ttyUSBUPS"
        #device_info_bar = "COM7"
        bps_bar = 2400
        timeout_bar = 0
        statCom_ups = JKSATACOM(device_info_bar, bps_bar, timeout_bar,
                                self.logger,None)
        commond_ups = "Q1\r\n"  # 获取状态指令
        while True:
            try:
                if statCom_ups==None:
                    statCom_ups = JKSATACOM(device_info_bar, bps_bar, timeout_bar,
                                            self.logger,None)
                # 发送操作命令
                statCom_ups.engine.Open_Engine()  # 打开串口
                statCom_ups.engine.Send_data(bytes.fromhex(commond_ups))
                # 读取接收到的数据，如果超时无返回数据则返回error,同时更新机库的当前状态
                result_state = statCom_ups.engine.Read_Size(100) # 读取结果,读取9个字节
                statCom_ups.engine.Close_Engine()

                if result_state==b'' :
                    time.sleep(5)
                    statCom_ups=None
                    print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}ups串口获取值为空")
                    continue
                if len(result_state) == 0:
                   HangarState.set_is_ups_state(f"0")
                else:
                    data_state = result_state.decode('ascii').split(' ')[7][0]
                    if data_state=='0':
                        HangarState.set_is_ups_state(f"0")
                    else:
                        HangarState.set_is_ups_state(f"1")#市电异常
                time.sleep(self.wait_time) #有此操作，信号获取数据稳定
            except Exception as e:
                print(f"ups异常{e}")
                time.sleep(self.wait_time)
                statCom_ups=None
                continue


if __name__ == "__main__":
    pass
    # logger = Logger(__name__)  # 日志记录
    # wfcstate = WFState()
    # hangstate = HangarState(wfcstate)
    # ws = UPSInfo(hangstate,logger)
    # # #启用一个线程
    # th = threading.Thread(target=ws.start_get_ups(), args=())
    # th.start()
    # th.join()  # 等待子进程结束
