'''
WebSocket的基本操作
'''

import threading
import time

from websocket import create_connection
import client
from BASEUtile import MINIO
from BASEUtile.Config import Config
from JKController.JKBarServer import JKBarServer
from JKController.JKDoorServer import JKDoorServer
from SATA.SATACom import JKSATACOM
#from WFCharge.JCCServer import M300JCCServer
from WFCharge.JCCServer import M300JCCServer
from WFCharge.JCCServerSend import M300JCCServerSender
from WFCharge.WFCServer import WFCServer
from WFCharge.WFCServerV2 import WFCServerV2
from WFCharge.WFCServerV2Sender import WFCServerV2Sender


class WebSocketUtilV1():
    def __init__(self,server_addr,hangerstate,wf_state,logger,comstate_flag,configini,comconfig):
        '''
        :param server_addr: Websocket server address
        :param statcomm: 串口对象；
        '''
        self.ip="127.0.0.1"
        self.socket='8000'
        self.station_id='123456789'
        self.server_addr = server_addr
        self.server_service=True
        self.logger=logger
        self.hangerstate=hangerstate
        self.jkdoor=None
        self.jkbar=None
        self.wfc_server=None
        self.wf_state=wf_state
        self.comstate_flag=comstate_flag#串口使用标记
        self.configini=configini
        self.comconfig=comconfig
        self.init_server_addr()#初始化服务器参数

    def init_server_addr(self):
        '''
        初始化服务器地址
        :return:
        '''
        config = Config()
        configinfo_list = config.getconfiginfo()  # 列表元组的形式
        if configinfo_list is None:
            # create table
            config.createTable()
        if configinfo_list is not None and len(configinfo_list) == 1:
            self.ip = configinfo_list[0][1]
            self.socket = configinfo_list[0][2]
            self.station_id = configinfo_list[0][3]
            self.server_addr = f"ws://{self.ip}:{self.socket}/uav/hangarServer/{self.station_id}"
            #print(f"{self.server_addr}")

    def start_service(self):
        '''
        启动一个线程
        :return:
        '''
        threading.Thread(target=self.get_msg, args=()).start()

    def close_socket(self):
        '''
        关闭内容
        '''
        self.server_service=False

    def bar_use_check(self,commond):
        result = ""
        # 如果使用485读取天气，则不作waiting处理
        if self.configini.weather_485==True:
            if self.comstate_flag.get_bar_isused() == False:
                self.logger.get_log().info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} websocket推杆调用，收到命令{commond}")
                self.comstate_flag.set_bar_used()
                try:
                    statCom_bar = JKSATACOM(self.hangerstate, self.comconfig.get_device_info_bar(), self.comconfig.get_bps_bar(),
                                            self.comconfig.get_timeout_bar(), self.logger, 0)
                    jkbar = JKBarServer(statCom_bar, self.hangerstate, self.logger, self.configini)
                    result = jkbar.operator_hanger(commond)
                    self.comstate_flag.set_bar_free()
                    self.logger.get_log().info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} websocket推杆调用，返回{result}")
                except Exception as barex:
                    self.comstate_flag.set_bar_free()
            else:
                self.logger.get_log().info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} websocket推杆调用，推杆端口被占用，返回busy")
                result = "busy"
        else:  # 使用推杆串口读取天气信息
            # 否则做waiting处理
            self.logger.get_log().info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} websocket推杆调用，使用推杆串口读取天气信息，收到命令{commond}")
            if self.comstate_flag.get_bar_isused() == False or self.comstate_flag.get_bar_waiting() == False:  # 串口没被占用或者天气在占用（天气占用的时候，waiting是False）
                # 第一步先判断是否是天气串口在使用，waiting=false,used=true,这个时候等待5秒，再做检测
                # 如果是waiting=false,used=false 可以直接使用
                # 如果是waiting=true,used=False 有另外高级命令在执行，直接失败
                if self.comstate_flag.get_bar_isused() == False and self.comstate_flag.get_bar_waiting() == True:
                    self.logger.get_log().info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} websocket推杆调用，上个推杆命令在执行等待,本次命令不执行，收到的命令是{commond}")
                    time.sleep(10)
                    result = "error"
                elif self.comstate_flag.get_bar_isused() == False and self.comstate_flag.get_bar_waiting() == False:
                    if not commond.startswith("70"):  # 调用推拉杆
                        self.logger.get_log().info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} websocket推杆调用，有天气共用串口，可以执行本次命令，执行命令{commond}")
                    self.comstate_flag.set_bar_waiting()
                    self.comstate_flag.set_bar_used()
                    try:
                        statCom_bar = JKSATACOM(self.hangerstate, self.comconfig.get_device_info_bar(), self.comconfig.get_bps_bar(),
                                                self.comconfig.get_timeout_bar(), self.logger, 0)
                        jkbar = JKBarServer(statCom_bar, self.hangerstate, self.logger, self.configini)
                        result = jkbar.operator_hanger(commond)
                        self.comstate_flag.set_bar_waiting_free()
                        self.comstate_flag.set_bar_free()
                    except Exception as barex:
                        self.comstate_flag.set_bar_waiting_free()
                        self.comstate_flag.set_bar_free()
                    self.comstate_flag.set_bar_waiting_free()
                else:  # 天气在使用，先锁定等待，然后5秒后再检测是否被占用，如果占用则失败
                    # 如果此时bar_is_used==True,如何处理？
                    self.logger.get_log().info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} websocket推杆调用，天气占用串口，等待4秒后继续执行，执行命令{commond}")
                    self.comstate_flag.set_bar_waiting()
                    time.sleep(4)
                    if self.comstate_flag.get_bar_isused() == False:
                        self.comstate_flag.set_bar_waiting()
                        self.comstate_flag.set_bar_used()
                        try:
                            statCom_bar = JKSATACOM(self.hangerstate, self.comconfig.get_device_info_bar(),
                                                    self.comconfig.get_bps_bar(),
                                                    self.comconfig.get_timeout_bar(), self.logger, 0)
                            jkbar = JKBarServer(statCom_bar, self.hangerstate, self.logger, self.configini)
                            result = jkbar.operator_hanger(commond)
                            self.comstate_flag.set_bar_waiting_free()
                            self.comstate_flag.set_bar_free()
                            self.logger.get_log().info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} websocket推杆调用，天气占用串口，等待4秒后，执行命令{commond}，执行结果为{result}")
                        except Exception as barex:
                            self.comstate_flag.set_bar_waiting_free()
                            self.comstate_flag.set_bar_free()
                    else:  # 失败
                        self.logger.get_log().info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} websocket推杆调用，天气占用串口，等待4秒后，执行命令{commond},端口仍然被占用,失败，busy")
                        time.sleep(5)
                        result = "busy"
                    self.comstate_flag.set_bar_waiting_free()
            else:
                self.logger.get_log().info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} websocket推杆调用，执行命令{commond},端口被占用,失败，busy")
                time.sleep(5)
                result = "busy"
        return result

    def dealMessage(self,ws,recv_text):
        """
         thread, deal the receive message
        :param ws:
        :param recv_text:
        :return:
        """
        result=""
        # ---------------1、充电操作-------
        if recv_text in ["Charge", "TakeOff", "Standby", "DroneOff","Check","DisplayOn","DisplayOff"]:
            if not self.comstate_flag.get_charge_isused():
                self.comstate_flag.set_charge_used()
                try:
                    if self.configini.get_charge_version() == "wfc":  # 充电
                        if self.configini.get_wfc_version() == 'V1.0':  # V1.0版本
                            WFC = WFCServer(self.wf_state, self.logger,self.configini)
                            result = WFC.operator_charge(recv_text)
                        elif self.configini.get_wfc_version() == 'V2.0':  # V2.0版本
                            #WFC = WFCServerV2(self.wf_state, self.logger)
                            WFC = None
                            if self.configini.double_connect == False:
                                WFC = WFCServerV2(self.wf_state, self.logger,self.configini)
                            else:
                                WFC = WFCServerV2Sender(self.wf_state, self.logger,self.comconfig)
                            result = WFC.operator_charge(recv_text)
                    else:  # 触点充电
                        if self.configini.wlc_double_connect == True:  # 全双工通信
                            WFC = M300JCCServerSender(self.wf_state, self.logger, self.comconfig)
                        else:
                            WFC = M300JCCServer(self.wf_state, self.logger, self.configini)
                        result = WFC.operator_charge(recv_text)
                    self.comstate_flag.set_charge_free()
                except Exception as charex:
                    self.comstate_flag.set_charge_free()
            else:
                result = "busy"
            self.logger.get_log().error(f"充电返回结果为{result}")
            if result=="busy":
                result="chargeerror"
        else:
            # -------------2.机库操作--------------
            if len(recv_text) != 6 and len(recv_text) != 10:
                result = "commond_error"
                self.logger.get_log().error(f"接收到server端命令{recv_text}，长度不为6或10")
                ws.send(self.hangerstate.getHangerState())  # json对象
                return
            # device_info_door = "/dev/ttyUSBDoor"
            # bps_door = 57600
            # timeout_door = 22
            # device_info_bar = "/dev/ttyUSBBar"
            # bps_bar = 57600
            # timeout_bar = 22
            result = ''
            if recv_text.startswith("1") or recv_text.startswith("4"):  # 门的操作
                if self.comstate_flag.get_door_isused() == False:  # 串口没有在使用
                    self.comstate_flag.set_door_used()
                    try:
                        statCom_door = JKSATACOM(self.hangerstate, self.comconfig.get_device_info_door(), self.comconfig.get_bps_door(), self.comconfig.get_timeout_door(), self.logger, 0)
                        self.jkdoor = JKDoorServer(statCom_door, self.hangerstate, self.logger)
                        result = self.jkdoor.operator_hanger(recv_text)
                        self.comstate_flag.set_door_free()
                    except Exception as doorex:
                        self.comstate_flag.set_door_free()
                else:
                    time.sleep(5)
                    self.logger.get_log().error(f"接收到server端命令{recv_text}，门端口被占用")
                    result="error"
            else:
                result=self.bar_use_check(recv_text)
        ws.send(result)

    def reset_hanger(self,ws):
        '''
        一键复位机库，（1）复位推杆 （2）关闭机库门  （3）复位充电
        :return:
        '''
        result_charge=""
        if not self.comstate_flag.get_charge_isused():
            self.comstate_flag.set_charge_used()
            try:
                if self.configini.get_charge_version() == "wfc":  # 充电
                    if self.configini.get_wfc_version() == 'V1.0':  # V1.0版本
                        WFC = WFCServer(self.wf_state, self.logger,self.configini)
                        result = WFC.operator_charge("Standby")
                        result = WFC.operator_charge("DroneOff")  # 关闭无人机
                    elif self.configini.get_wfc_version() == 'V2.0':  # V2.0版本
                        WFC = None
                        if self.configini.double_connect == False:
                            WFC = WFCServerV2(self.wf_state, self.logger,self.configini)
                        else:
                            WFC = WFCServerV2Sender(self.wf_state, self.logger, self.comconfig)
                        result = WFC.operator_charge("Standby")
                        result = WFC.operator_charge("DroneOff")  # 关闭无人机
                else:  # 触点充电
                    if self.configini.wlc_double_connect == True:  # 全双工通信
                        WFC = M300JCCServerSender(self.wf_state, self.logger, self.comconfig)
                    else:
                        WFC = M300JCCServer(self.wf_state, self.logger, self.configini)
                    result = WFC.operator_charge("Standby")#关闭充电箱
                    result = WFC.operator_charge("DroneOff")#关闭无人机
                self.comstate_flag.set_charge_free()
            except Exception as charex:
                self.comstate_flag.set_charge_free()
        else:
            result_charge = "busy"
        self.logger.get_log().error(f"充电返回结果为{result_charge}")
        if result_charge == "busy":
            result_charge = "chargeerror"
        self.logger.get_log().error(f"充电返回结果为{result_charge}")

        result_bar = ''
        result_door=""
        if self.comstate_flag.get_door_isused() == False:  # 串口没有在使用
            self.comstate_flag.set_door_used()
            try:
                statCom_door = JKSATACOM(self.hangerstate, self.comconfig.get_device_info_door(), self.comconfig.get_bps_door(), self.comconfig.get_timeout_door(), self.logger, 0)
                self.jkdoor = JKDoorServer(statCom_door, self.hangerstate, self.logger)
                result_door = self.jkdoor.operator_hanger("150000")
                self.comstate_flag.set_door_free()
            except Exception as doorex:
                self.comstate_flag.set_door_free()
        else:
            time.sleep(5)
            self.logger.get_log().error(f"一键复位，门端口被占用")
            result_door = "error"

        result_bar = self.bar_use_check("500000")


        self.logger.get_log().error(f"一键复位，推杆复位结果为{result_bar}")
        self.logger.get_log().error(f"一键复位，机库门复位结果为{result_door}")
        ws.send(f"推杆复位：{result_bar},门关闭：{result_door},充电复位：{result_charge}")

    def get_msg(self):#启用一个线程调用
        '''
        获取消息,服务端交互
        '''
        #创建
        ws=None
        try:
            #print(f"开始启动websocket服务")
            self.init_server_addr()
            ws=create_connection(self.server_addr,timeout=30)

        except Exception as e:
            print(f"第一次启动，无法连接websocket服务器，{e}")
        while self.server_service:
            try:
                #一直接收消息
                if ws==None:
                    self.init_server_addr()
                    ws = create_connection(self.server_addr,timeout=30)#如果30秒没有收到消息则结束等待
                recv_text = ws.recv()#远程主机强迫关闭了一个现有的连接,需要做连接重连,如果无命令则一直等待
                if recv_text!="":
                    # 获取机库状态的指令
                    #print(f"{recv_text}")
                    if recv_text == 'state' or 'jklog' in recv_text or 'update' in recv_text or "settime" in recv_text or "reset" in recv_text:
                        if recv_text == 'state':

                            ws.send(self.hangerstate.getHangerState())  # json对象
                            continue
                        elif 'jklog' in recv_text:
                            # ws.send(self.hangerstate.getHangerState()) #json对象
                            # 触发本地日志上传
                            self.logger.get_log().info(f"接收到jklog命令")
                            # buck_name = "uav-test"
                            # # 获取站点ID编号
                            # config = Config()
                            # configinfo_list = config.getconfiginfo()
                            # station_id = configinfo_list[0][3]
                            utilminio = MINIO.MiniUtils(self.logger)
                            utilminio.start_uploadlog()
                            #utilminio.start_uploadfile(buck_name, f"{station_id}.log")
                            continue
                        elif 'update' in recv_text:#更新日志信息
                            client.updatesoftware()
                            continue
                        elif 'settime' in recv_text:#更新系统时间
                            #linux系统
                            import os
                            print(f"receive  txt is {recv_text}")
                            pwd="wkzn123"
                            time_value=recv_text.split(',')[1]
                            #os.system(f"date -s '{time_value}'")
                            os.system(f"echo {pwd} | sudo -S date -s '{time_value}'")
                            continue
                        elif 'reset' in recv_text:  #一键复位
                            thread_reset = threading.Thread(target=self.reset_hanger, args=(ws,))
                            thread_reset.setDaemon(True)
                            thread_reset.start()
                            continue
                        continue
                    else:
                        #直接调用串口发送命令
                        self.logger.get_log().info(f"接收到命令{recv_text}")
                        thread_read = threading.Thread(target=self.dealMessage, args=(ws,recv_text))
                        thread_read.setDaemon(True)
                        thread_read.start()
                else:
                    #没有接收到消息，重连
                    #print("socket server is off")
                    ws = None
                    self.hangerstate.set_STAT_connet_state('error')
                    # self.logger.get_log().error(f"web socket error is e {e}")
                    continue
            except Exception as e:
                #self.logger.get_log().info(f"websocket接收发送消息--异常，{e}")
                #print(f"exception {e}")
                ws=None
                self.hangerstate.set_STAT_connet_state('error')
                #self.logger.get_log().error(f"web socket error is e {e}")
                time.sleep(10)
                continue

if __name__=="__main__":
    # ws=WebSocketUtil('')
    # # #启用一个线程
    # th=threading.Thread(target=ws.get_msg,args=())
    # th.start()
    # th.join()#等待子进程结束
    pass

