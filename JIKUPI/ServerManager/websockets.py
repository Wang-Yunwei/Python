'''
WebSocket的基本操作
'''
import datetime
import threading
import time

from websocket import create_connection
import client
from Activate.ActivateUtils import ActivateUtils
from AirCondition.AirConditionComputer import AirConditionOper
from AutoCharge.AutoChargeControl import AutoChargeControl
from AutoCharge.AutoChargeControlV1 import AutoChargeControlV1
from BASEUtile import MINIO
from BASEUtile.Config import Config
from JKController.JKBarServer import JKBarServer
from JKController.JKDoorServer import JKDoorServer
from JKController.LightController import LightController
from SATA.SATACom import JKSATACOM
from WFCharge.JCCServer import M300JCCServer
from WFCharge.JCCServerSend import M300JCCServerSender
#from WFCharge.JCCServerV2 import M300JCCServerV2
from WFCharge.JCCServerV2_Single import M300JCCServerV2
from WFCharge.JCCServerV3 import M300JCCServerV3
from WFCharge.JCCServerV4M350 import M300JCCServerV4
from WFCharge.WFCServer import WFCServer
from WFCharge.WFCServerV2 import WFCServerV2
from WFCharge.WFCServerV2Sender import WFCServerV2Sender
from weather.AlarmController import AlarmController
from weather.OutLiftController import OutLiftController
from weather.UAVController import UAVController


class WebSocketUtil():
    def __init__(self, server_addr, hangerstate, wf_state, logger, comstate_flag, configini, auto_charge, comconfig):
        '''
        :param server_addr: Websocket server address
        :param statcomm: 串口对象；
        '''
        self.ip = "127.0.0.1"
        self.socket = '8000'
        self.station_id = '123456789'
        self.server_addr = server_addr
        self.server_service = True
        self.logger = logger
        self.hangerstate = hangerstate
        self.jkdoor = None
        self.jkbar = None
        self.wfc_server = None
        self.wf_state = wf_state
        self.comstate_flag = comstate_flag  # 串口使用标记
        self.configini = configini
        # pang.hy:新存放链接对象的 由于原来get_msg中ws对象外部无法获取，故这里使用方法共享self对象存放
        self.web_socket = None
        # pang.hy:心跳间隔
        self.alive_second = 5
        # pang.hy:自动化充电对象 可能为None
        self.auto_charge = auto_charge
        # 串口信息
        self.comconfig = comconfig
        # 执行初始化
        self.init_server_addr()  # 初始化服务器参数
        # 是否在执行websocket指令
        self.is_run_command = False

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
            if len(configinfo_list[0]) == 5:
                web_socket_url = configinfo_list[0][4]  # 如果url不为空，则直接读取url
            else:
                web_socket_url = ''
            if web_socket_url == "" or web_socket_url is None:
                self.server_addr = f"ws://{self.ip}:{self.socket}/uav/hangarServer/{self.station_id}"
                if (not isinstance(self.auto_charge, AutoChargeControlV1)):
                    print(f"{self.auto_charge.__class__}")
                    self.auto_charge = AutoChargeControlV1(self.logger, self.wf_state, self.comstate_flag,
                                                           self.configini,hangstate=self.hangerstate)
            else:
                self.server_addr = web_socket_url
                # 天宇的自动充电
                if (not isinstance(self.auto_charge, AutoChargeControl)):
                    print(f"{self.auto_charge.__class__}")
                    self.auto_charge = AutoChargeControl(self.logger, self.wf_state, self.comstate_flag, self.configini,hangstate=self.hangerstate)
            # for pang.hy test
            # self.server_addr = f"ws://172.16.20.152:8080/intelligent_algorithm/uav/hangarServer/{self.station_id}"
            # self.server_addr = f"ws://120.26.167.5:15005/95091e705eceda57"
            # self.server_addr = f"ws://api.wogrid.com:15005/95091e705eceda57"

            # print(f"{self.server_addr}")

    def start_service(self):
        '''
        启动一个线程
        :return:
        '''
        # 创建
        self.web_socket = None
        self.logger.get_log().info(f"开始启动websocket服务")
        try:
            # 初始化最新配置
            self.init_server_addr()
            web_socket_temp = create_connection(self.server_addr, timeout=30)
            if web_socket_temp is None:
                self.logger.get_log().info(f"第一次启动，创建web_socket为空")
            else:
                self.web_socket = web_socket_temp
        except Exception as e:
            self.logger.get_log().info(f"第一次启动，无法连接websocket服务器，{e}")

        threading.Thread(target=self.get_msg, args=()).start()
        if self.configini.need_heartbeat_check:
            self.logger.get_log().info(f"需要启动心跳检测，休眠后启动")
            # 休眠一下再启动心跳
            time.sleep(5)
            # pang.hy: 追加启动一个心跳线程，循环发送状态信息
            threading.Thread(target=self.send_alive_msg, args=()).start()
        else:
            self.logger.get_log().info(f"不需要启动心跳检测，心跳线程不运行")

    def close_socket(self):
        '''
        关闭内容
        '''
        self.server_service = False

    def bar_use_check(self, commond):
        result = ""
        if self.configini.get_aircon485() == True and commond.startswith('3'):
            airManager = AirConditionOper(self.hangerstate.get_airstate(), self.hangerstate, self.comconfig, self.logger)
            if commond.startswith('30'):  # 开空调
                airManager.openAircondition()
                self.hangerstate.set_air_condition('open')
                result = '9300'
            else:
                airManager.closeAircondition()
                self.hangerstate.set_air_condition('close')
                result = '9310'
        else:
            if (commond.startswith("2f") or commond.startswith("50")) and (self.hangerstate.wfcstate.get_state()=="charging" or self.hangerstate.wfcstate.get_state()=="waiting"):  # 推杆打开操作或者复位操作
               self.exe_charge_commond("standby")

            # 如果使用485读取天气，则不作waiting处理
            if self.configini.weather_485 == True:
                if self.comstate_flag.get_bar_isused() == False:
                    self.logger.get_log().info(
                        f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} websocket推杆调用，收到命令{commond}")
                    self.comstate_flag.set_bar_used()
                    try:
                        statCom_bar = JKSATACOM(self.hangerstate, self.comconfig.get_device_info_bar(),
                                                self.comconfig.get_bps_bar(),
                                                self.comconfig.get_timeout_bar(), self.logger, 0)
                        jkbar = JKBarServer(statCom_bar, self.hangerstate, self.logger, self.configini)
                        result = jkbar.operator_hanger(commond)
                        self.comstate_flag.set_bar_free()
                        self.logger.get_log().info(
                            f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} websocket推杆调用，返回{result}")
                    except Exception as barex:
                        self.comstate_flag.set_bar_free()
                else:
                    self.logger.get_log().info(
                        f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} websocket推杆调用，推杆端口被占用，返回busy")
                    result = "busy"
            else:  # 使用推杆串口读取天气信息
                # 否则做waiting处理
                self.logger.get_log().info(
                    f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} websocket推杆调用，使用推杆串口读取天气信息，收到命令{commond}")
                if self.comstate_flag.get_bar_isused() == False or self.comstate_flag.get_bar_waiting() == False:  # 串口没被占用或者天气在占用（天气占用的时候，waiting是False）
                    # 第一步先判断是否是天气串口在使用，waiting=false,used=true,这个时候等待5秒，再做检测
                    # 如果是waiting=false,used=false 可以直接使用
                    # 如果是waiting=true,used=False 有另外高级命令在执行，直接失败
                    if self.comstate_flag.get_bar_isused() == False and self.comstate_flag.get_bar_waiting() == True:
                        self.logger.get_log().info(
                            f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} websocket推杆调用，上个推杆命令在执行等待,本次命令不执行，收到的命令是{commond}")
                        time.sleep(10)
                        result = "error"
                    elif self.comstate_flag.get_bar_isused() == False and self.comstate_flag.get_bar_waiting() == False:
                        if not commond.startswith("70"):  # 调用推拉杆
                            self.logger.get_log().info(
                                f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} websocket推杆调用，有天气共用串口，可以执行本次命令，执行命令{commond}")
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
                        except Exception as barex:
                            self.comstate_flag.set_bar_waiting_free()
                            self.comstate_flag.set_bar_free()
                        self.comstate_flag.set_bar_waiting_free()
                    else:  # 天气在使用，先锁定等待，然后5秒后再检测是否被占用，如果占用则失败
                        # 如果此时bar_is_used==True,如何处理？
                        self.logger.get_log().info(
                            f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} websocket推杆调用，天气占用串口，等待4秒后继续执行，执行命令{commond}")
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
                                self.logger.get_log().info(
                                    f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} websocket推杆调用，天气占用串口，等待4秒后，执行命令{commond}，执行结果为{result}")
                            except Exception as barex:
                                self.comstate_flag.set_bar_waiting_free()
                                self.comstate_flag.set_bar_free()
                        else:  # 失败
                            self.logger.get_log().info(
                                f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} websocket推杆调用，天气占用串口，等待4秒后，执行命令{commond},端口仍然被占用,失败，busy")
                            time.sleep(5)
                            result = "busy"
                        self.comstate_flag.set_bar_waiting_free()
                else:
                    self.logger.get_log().info(
                        f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} websocket推杆调用，执行命令{commond},端口被占用,失败，busy")
                    time.sleep(5)
                    result = "busy"
        return result

    # 充电处理
    def exe_charge_commond(self, commond):
        '''
        执行充电相关命令
        :param commond:
        :return:
        '''
        global WFC
        try:
            result = ""
            if self.comstate_flag.get_charge_isused() == False:
                self.comstate_flag.set_charge_used()
                try:
                    if self.configini.get_charge_version() == "wfc":  # 无线充电
                        if self.configini.get_wfc_version() == 'V1.0':  # V1.0版本
                            WFC = WFCServer(self.wf_state, self.logger, self.configini)
                            result = WFC.operator_charge(commond)
                        elif self.configini.get_wfc_version() == 'V2.0':  # V2.0版本
                            if self.configini.wfc_double_connect == False:
                                WFC = WFCServerV2(self.wf_state, self.logger, self.configini)
                            else:
                                WFC = WFCServerV2Sender(self.wf_state, self.logger, self.comconfig)
                            result = WFC.operator_charge(commond)
                    else:  # 触点充电
                        if self.configini.get_wlc_version() == "V1.0":
                            if self.configini.wlc_double_connect == True:  # 全双工通信
                                WFC = M300JCCServerSender(self.hangerstate,self.wf_state, self.logger, self.comconfig)
                            else:
                                WFC = M300JCCServer(self.wf_state, self.logger, self.configini)
                        elif self.configini.get_wlc_version() == "V2.0":  # V2.0
                            WFC = M300JCCServerV2(self.hangerstate,self.wf_state, self.logger, self.configini)
                        elif self.configini.get_wlc_version() == "V3.0":  # V3.0
                            WFC = M300JCCServerV3(self.hangerstate, self.wf_state, self.logger, self.configini)
                        elif self.configini.get_wlc_version() == "V4.0":  # V3.0
                            WFC = M300JCCServerV4(self.hangerstate, self.wf_state, self.logger, self.configini)
                        result = WFC.operator_charge(commond)
                    self.comstate_flag.set_charge_free()
                except Exception as charex:
                    self.comstate_flag.set_charge_free()
            else:
                self.logger.get_log().info(f"websocket 充电指令{commond}无法执行，因为充电串口被占用")
                result = "chargeerror"
            return result
        except Exception as ex:
            self.logger.get_log().info(f"websocket 充电指令{commond}执行异常")
            return "chargeerror"

    def open_autocharge(self):
        '''
        调用自动充电
        设置自动充电(auto_charge,fly_back)+电量为0+充电
        :return:
        '''
        # 充电操作
        self.wf_state.set_battery_value("0")  # 电池状态未知
        result = "chargeerror"
        result = self.exe_charge_commond("Charge")
        self.auto_charge.set_run_auto_charge(1)
        self.auto_charge.set_fly_back(1)

        return result

    def close_autocharge(self):
        '''
        结束自动充电
        设置自动充电关闭+standby
        :return:
        '''

        self.auto_charge.set_run_auto_charge(0)#不启用自动充电
        self.auto_charge.set_fly_back(-1)#飞机非飞回状态
        # 复位操作
        result = "chargeerror"
        if self.hangerstate.wfcstate.get_state()=="charging" or self.hangerstate.wfcstate.get_state()=="waiting":
            result = self.exe_charge_commond("Standby")
        else:
            result='success'
        return result

    def takeoff(self):
        '''
        设置开机
        close_autocharge()
        takeoff命令
        :return:
        '''
        self.close_autocharge()
        result = "chargeerror"
        result = self.exe_charge_commond("TakeOff")
        return result

    def droneoff(self):
        '''
        设置关机
        关机+自动充电
        :return:
        '''
        result = "chargeerror"
        self.close_autocharge()
        # self.exe_charge_commond("Standby")
        result = self.exe_charge_commond("DroneOff")
        # self.wf_state.set_battery_value("0")  # 电池状态未知
        # self.auto_charge.set_run_auto_charge(1)
        # self.auto_charge.set_fly_back(1)
        return result

    def standby(self):
        '''
        设置复位操作
        结束自动充电+复位
        :return:
        '''
        result = self.close_autocharge()
        return result

    def dealMessage(self, ws, recv_text):
        """
         thread, deal the receive message
        :param ws:
        :param recv_text:
        :return:
        """
        # if self.is_run_command:
        #     # 被占用直接报错
        #     ws.send("error")
        # else:
        try:
            # 进入就被占用执行
            self.is_run_command = True
            result = ""
            # ---------------1、充电操作-------
            if recv_text in ["Charge", "TakeOff", "Standby", "DroneOff", "Check", "DisplayOn", "DisplayOff"]:
                if self.configini.need_auto_charge:  # 启动自动充电
                    if recv_text == "Charge":  # 充电操作
                        result = self.open_autocharge()
                    elif recv_text == "TakeOff":
                        result = self.takeoff()
                    elif recv_text == "DroneOff":
                        result = self.droneoff()
                    elif recv_text == "Standby":
                        result = self.standby()
                    else:
                        result = self.exe_charge_commond(recv_text)
                else:  # 非自动充电
                    result = self.exe_charge_commond(recv_text)
            # pang.hy : 新的大流程命令入口
            elif recv_text == "dt0000":#无人机开机
                result = self.step_scene_drone_takeoff_dt0000()
            elif recv_text == "dd0000":#无人机关机
                result = self.step_scene_drone_off_dd0000()
            elif recv_text == "cp0000":#无人机充电
                result = self.step_scene_drone_charge_cp0000()
            elif recv_text == "ck0000":
                result = self.step_scene_drone_check_ck0000()
            elif recv_text == "sb0000":#无人机待机
                result = self.step_scene_drone_standby_sb0000()
            elif recv_text == "A000":#一键起飞,#开门，开启无人机，松推杆
                result = self.big_scene_A000()
                #开灯
                # 如果是关门操作，则做关灯操作
                lightcontroller = LightController(comstate_flag=self.comstate_flag, logger=self.logger,
                                                  hangerstate=self.hangerstate,
                                                  comconfig=self.comconfig)
                lightcontroller.open_light()
            elif recv_text == "A010":#一键起飞,#开门，松推杆
                result = self.big_scene_A010()
                #开灯
                lightcontroller = LightController(comstate_flag=self.comstate_flag, logger=self.logger,
                                                  hangerstate=self.hangerstate,
                                                  comconfig=self.comconfig)
                lightcontroller.open_light()
            elif recv_text == "A100":#起飞后操作，关门操作
                result = self.big_scene_A100()
                lightcontroller = LightController(comstate_flag=self.comstate_flag, logger=self.logger,
                                                  hangerstate=self.hangerstate,
                                                  comconfig=self.comconfig)
                lightcontroller.close_light()
            elif recv_text == "A200":#自检失败后续操作，收推杆，关机，关门，关灯
                result = self.big_scene_A200()
                lightcontroller = LightController(comstate_flag=self.comstate_flag, logger=self.logger,
                                                  hangerstate=self.hangerstate,
                                                  comconfig=self.comconfig)
                lightcontroller.close_light()
            elif recv_text == "B000":#一键降落准备，开门
                result = self.big_scene_B000()
                lightcontroller = LightController(comstate_flag=self.comstate_flag, logger=self.logger,
                                                  hangerstate=self.hangerstate,
                                                  comconfig=self.comconfig)
                lightcontroller.open_light()
            elif recv_text == "B100":#正常降落完成后的后续操作
                result = self.big_scene_B100()
                lightcontroller = LightController(comstate_flag=self.comstate_flag, logger=self.logger,
                                                  hangerstate=self.hangerstate,
                                                  comconfig=self.comconfig)
                lightcontroller.close_light()
            elif recv_text == "B200":
                result = self.big_scene_B200()
            #  新的命令
            elif recv_text == "c00000":
                result = self.step_scene_auto_charge_on_c00000()
            elif recv_text == "c10000":
                result = self.step_scene_auto_charge_off_c10000()
            elif recv_text == "outliftup":#2023-06-05 机库外置升降台控制
                outlift= OutLiftController(self.hangerstate,self.logger,self.configini,self.comstate_flag)
                outlift.lift_up()
            elif recv_text == "outliftdown":#2023-06-05 机库外置升降台控制
                outlift = OutLiftController(self.hangerstate, self.logger, self.configini,self.comstate_flag)
                outlift.lift_down()
            elif recv_text == "opencontroller":#2023-08-14 机库遥控器远程开启
                startcontroller= UAVController(self.hangerstate,self.logger,self.configini,self.comstate_flag)
                result=startcontroller.start_close_controller("open")
            elif recv_text == "closecontroller":#2023-08-14 机库遥控器远程关闭
                startcontroller = UAVController(self.hangerstate, self.logger, self.configini, self.comstate_flag)
                result=startcontroller.start_close_controller("close")
            else:
                # -------------2.机库操作--------------
                if len(recv_text) != 6 and len(recv_text) != 10 and len(recv_text) != 8 and len(recv_text) != 12:
                    result = "commond_error"
                    self.logger.get_log().error(f"接收到server端命令{recv_text}，长度不为6、10、8、12")
                    # ws.send(self.hangerstate.getHangerState())  # json对象
                    # ws.send("900a")  # 改为统一无法识别命令错误码
                    return

                result = ''
                #衢州版本，可以同时打开机库门
                if recv_text == "600000":  # 同时打开操作
                    self.logger.get_log().error(f"接收到server端命令{recv_text}，同时打开机库门和推拉杆")
                    self.exe_charge_commond("standby")
                    result = self.opendoor_bar_together()
                    print(f"{result}")
                    ws.send(result)
                    return result
                if recv_text.startswith("1") or recv_text.startswith("4"):  # 门的操作,灯光的操作
                    if self.comstate_flag.get_door_isused() == False:  # 串口没有在使用
                        self.comstate_flag.set_door_used()
                        try:
                            statCom_door = JKSATACOM(self.hangerstate, self.comconfig.get_device_info_door(),
                                                     self.comconfig.get_bps_door(),
                                                     self.comconfig.get_timeout_door(),
                                                     self.logger, 0)
                            self.jkdoor = JKDoorServer(statCom_door, self.hangerstate, self.logger)
                            result = self.jkdoor.operator_hanger(recv_text)
                            self.comstate_flag.set_door_free()
                            # 新增夜灯配置，2023-04-24
                            if recv_text.startswith("14") or recv_text.startswith("15"):
                                thead_auto = threading.Thread(target=self.open_close_light, args=(recv_text,))
                                thead_auto.start()
                            # if recv_text.startswith("14"):
                            #     #如果是开门操作，则做开灯操作
                            #     lightcontroller=LightController(comstate_flag=self.comstate_flag,logger=self.logger,hangerstate=self.hangerstate,comconfig=self.comconfig)
                            #     lightcontroller.open_light()
                            # elif recv_text.startswith("15"):
                            #     #如果是关门操作，则做关灯操作
                            #     lightcontroller = LightController(comstate_flag=self.comstate_flag, logger=self.logger,
                            #                                       hangerstate=self.hangerstate,
                            #                                       comconfig=self.comconfig)
                            #     lightcontroller.close_light()

                        except Exception as doorex:
                            self.comstate_flag.set_door_free()
                    else:
                        time.sleep(5)
                        self.logger.get_log().error(f"接收到server端命令{recv_text}，门端口被占用")
                        result = "error"
                else:#推杆操作
                    result = self.bar_use_check(recv_text)
            self.logger.get_log().info(f"接收到server端命令{recv_text}，websocket返回值为：{result}")
            ws.send(result)
        except Exception as comex:
            self.logger.get_log().error(f"执行指令发生异常:{comex}")
        finally:
            self.is_run_command = False

    def open_close_light(self,recv_text):
        '''
        打开或关闭灯光线程
        '''
        # 打开或关闭灯光线程
        if recv_text.startswith("14"):
            # 如果是开门操作，则做开灯操作
            lightcontroller = LightController(comstate_flag=self.comstate_flag, logger=self.logger,
                                              hangerstate=self.hangerstate, comconfig=self.comconfig)
            lightcontroller.open_light()
        elif recv_text.startswith("15"):
            # 如果是关门操作，则做关灯操作
            lightcontroller = LightController(comstate_flag=self.comstate_flag, logger=self.logger,
                                              hangerstate=self.hangerstate,
                                              comconfig=self.comconfig)
            lightcontroller.close_light()

    #-------------------衢州操作-----------------------begin
    def opendoor_thread(self):
        '''
        开门操作
        '''
        recv_text="140120"
        if self.comstate_flag.get_door_isused() == False:  # 串口没有在使用
            self.comstate_flag.set_door_used()
            try:
                statCom_door = JKSATACOM(self.hangerstate, self.comconfig.get_device_info_door(),
                                         self.comconfig.get_bps_door(), self.comconfig.get_timeout_door(),
                                         self.logger, 0)
                self.jkdoor = JKDoorServer(statCom_door, self.hangerstate, self.logger)
                result = self.jkdoor.operator_hanger(recv_text)
                self.comstate_flag.set_door_free()
            except Exception as doorex:
                self.comstate_flag.set_door_free()
        else:
            time.sleep(5)
            self.logger.get_log().error(f"接收到server端命令{recv_text}，门端口被占用")
            result = "error"

    def openbar_thread(self):
        '''
        打开推杆线程
        '''
        recv_text="500000" #复位操作
        self.bar_use_check(recv_text)

    def opendoor_bar_together(self):
        '''
        同时打开机库门和推杆，命令为600000
        (1)判断是否是1.0板子，如果是则继续，否则返回错误代码9601
        (2)进行开门操作
        (3)进行开推杆操作
        '''
        recv_text="600000"
        if self.configini.get_down_version() != "V1.0":
            return "9601"
        #开始做开门操作，打开一个开门的线程
        thread_opendoor = threading.Thread(target=self.opendoor_thread, args=())
        thread_opendoor.setDaemon(True)
        thread_opendoor.start()
        #开始做开推杆操作，打开一个打开推杆线程
        thread_openbar = threading.Thread(target=self.openbar_thread, args=())
        thread_openbar.setDaemon(True)
        thread_openbar.start()
        #根据返回值，判断操作结果是否完成，完成则返回成功(根据hanger中机库状态判断执行是否成功)，失败则返回9601
        #等待55秒
        for i in range(50):
            if self.hangerstate.get_hanger_door()=="open" and self.hangerstate.get_hanger_bar()=="open":
                return "9600"
            time.sleep(1)
        return "9601"
    # -------------------衢州操作-----------------------end

    def reset_hanger(self, ws):
        '''
        一键复位机库，（1）复位推杆 （2）关闭机库门  （3）复位充电
        :return:
        '''
        global WFC
        result_charge = ""
        if not self.comstate_flag.get_charge_isused():
            self.comstate_flag.set_charge_used()
            try:
                if self.configini.get_charge_version() == "wfc":  # 充电
                    if self.configini.get_wfc_version() == 'V1.0':  # V1.0版本
                        WFC = WFCServer(self.wf_state, self.logger, self.configini)
                        result = WFC.operator_charge("Standby")
                        result = WFC.operator_charge("DroneOff")  # 关闭无人机
                    elif self.configini.get_wfc_version() == 'V2.0':  # V2.0版本
                        if self.configini.wfc_double_connect == False:
                            WFC = WFCServerV2(self.wf_state, self.logger, self.configini)
                        else:
                            WFC = WFCServerV2Sender(self.wf_state, self.logger, self.comconfig)
                        result = WFC.operator_charge("Standby")
                        result = WFC.operator_charge("DroneOff")  # 关闭无人机
                else:  # 触点充电
                    if self.configini.get_wlc_version() == "V1.0":
                        if self.configini.wlc_double_connect == True:  # 全双工通信
                            WFC = M300JCCServerSender(self.hangerstate,self.wf_state, self.logger, self.comconfig)
                        else:
                            WFC = M300JCCServer(self.wf_state, self.logger, self.configini)
                    elif self.configini.get_wlc_version() == "V2.0":  # V2.0机库
                        WFC = M300JCCServerV2(self.hangerstate,self.wf_state, self.logger, self.configini)
                    elif self.configini.get_wlc_version() == "V3.0":  # V2.0机库
                        WFC = M300JCCServerV3(self.hangerstate,self.wf_state, self.logger, self.configini)
                    elif self.configini.get_wlc_version() == "V4.0":  # V2.0机库
                        WFC = M300JCCServerV4(self.hangerstate, self.wf_state, self.logger, self.configini)
                    result = WFC.operator_charge("Standby")  # 关闭充电箱
                    result = WFC.operator_charge("DroneOff")  # 关闭无人机
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
        result_door = ""
        if self.comstate_flag.get_door_isused() == False:  # 串口没有在使用
            self.comstate_flag.set_door_used()
            try:
                statCom_door = JKSATACOM(self.hangerstate, self.comconfig.get_device_info_door(),
                                         self.comconfig.get_bps_door(), self.comconfig.get_timeout_door(),
                                         self.logger, 0)
                self.jkdoor = JKDoorServer(statCom_door, self.hangerstate, self.logger)
                result_door = self.jkdoor.operator_hanger("150000")
                self.comstate_flag.set_door_free()
            except Exception as doorex:
                self.comstate_flag.set_door_free()
        else:
            time.sleep(5)
            self.logger.get_log().error(f"一键复位，门端口被占用")
            result_door = "error"
        commond = "500000"
        result_bar = self.bar_use_check(commond)

        self.logger.get_log().error(f"一键复位，推杆复位结果为{result_bar}")
        self.logger.get_log().error(f"一键复位，机库门复位结果为{result_door}")
        ws.send(f"推杆复位：{result_bar},门关闭：{result_door},充电复位：{result_charge}")

    """
    pang.hy 
    心跳检测方法，循环发送心跳信息
    """

    def send_alive_msg(self):  # 启用一个线程调用
        while self.server_service:
            try:
                if self.web_socket is None:
                    try:
                        self.logger.get_log().info(f"心跳websocket未连接")
                        # 初始化最新配置
                        # self.init_server_addr()
                        # web_socket_temp = create_connection(self.server_addr, timeout=30)  # 如果30秒没有收到消息则结束等待
                        # if web_socket_temp is None:
                        #     self.logger.get_log().error(f"心跳-web_socket创建失败，创建web_socket为空")
                        # else:
                        #     self.web_socket = web_socket_temp
                    except Exception as e:
                        self.logger.get_log().error(f"心跳-web_socket创建失败，无法连接websocket服务器，{e}")
                    time.sleep(10)
                    continue
                else:
                    self.web_socket.send(self.hangerstate.getHangerState())  # json对象
                    self.logger.get_log().debug(f"websocket 心跳检测--正常")
                    time.sleep(self.alive_second)  # 休眠若干秒后继续推送
                    continue
            except Exception as e:
                self.logger.get_log().info(f"websocket 心跳检测--异常，{e}")
                # pang.hy : 看了下代码 重新创建链接在get_msg 方法中，为确保无多线程冲突，由get_msg 识别异常并重建链接。未来是不是改成心跳重新创建待议
                # self.web_socket = None
                # self.hangerstate.set_STAT_connet_state('error')
                time.sleep(10)
                continue
        self.logger.get_log().debug(f"websocket 心跳检测--退出执行")

    """
    pang.hy 
    包装方法
    小场景(步骤)-机库门打开
    """

    def step_scene_door_open_140000(self):
        #  常量/参数部分
        recv_text = "140000"  # 下发指令
        def_error_result = "9141"  # 默认异常
        command_error_result = "914a"  # 不支持方法异常
        used_error_result = "914d"  # 底层端口或串口被占用异常
        #  业务逻辑部分
        if self.comstate_flag.get_door_isused() is False:  # 串口没有在使用
            self.comstate_flag.set_door_used()  # 串口设置使用中
            try:
                #  对下位机进行操作
                statCom_bar = JKSATACOM(self.hangerstate, self.comconfig.get_device_info_door(),
                                        self.comconfig.get_bps_door(), self.comconfig.get_timeout_door(),
                                        self.logger,
                                        0)  # 操作的实例
                self.jkdoor = JKDoorServer(statCom_bar, self.hangerstate, self.logger)  # 控制对象
                result = self.jkdoor.operator_hanger(recv_text)  # 执行命令
                self.comstate_flag.set_door_free()  # 串口设置没有在使用
                # 如果是关门操作，则做关灯操作
                # lightcontroller = LightController(comstate_flag=self.comstate_flag, logger=self.logger,
                #                                   hangerstate=self.hangerstate,
                #                                   comconfig=self.comconfig)
                # lightcontroller.open_light()
            except Exception as e:
                self.comstate_flag.set_door_free()  # 串口设置没有在使用
                self.logger.get_log().info(f"执行命令{recv_text}发生异常，{e}")
                result = def_error_result
        else:
            self.logger.get_log().error(f"执行命令{recv_text}，门端口被占用")
            result = used_error_result
        if result is None:
            result = def_error_result
        elif result == "":
            result = def_error_result
        elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
            result = def_error_result
        elif result.endswith("a") and result.startswith("9"):
            result = command_error_result
        self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
        return result

    """
    pang.hy 
    包装方法
    小场景(步骤)-机库门关闭
    """

    def step_scene_door_close_150000(self):
        #  常量/参数部分
        recv_text = "150000"  # 下发指令
        def_error_result = "9151"  # 默认异常
        command_error_result = "915a"  # 不支持方法异常
        used_error_result = "915d"  # 底层端口或串口被占用异常
        #  业务逻辑部分
        if self.comstate_flag.get_door_isused() is False:  # 串口没有在使用
            self.comstate_flag.set_door_used()  # 串口设置使用中
            try:
                #  对下位机进行操作
                statCom_door = JKSATACOM(self.hangerstate, self.comconfig.get_device_info_door(),
                                         self.comconfig.get_bps_door(), self.comconfig.get_timeout_door(),
                                         self.logger,
                                         0)  # 操作的实例
                self.jkdoor = JKDoorServer(statCom_door, self.hangerstate, self.logger)  # 控制对象
                result = self.jkdoor.operator_hanger(recv_text)  # 执行命令
                self.comstate_flag.set_door_free()  # 串口设置没有在使用
                # 如果是关门操作，则做关灯操作
                # lightcontroller = LightController(comstate_flag=self.comstate_flag, logger=self.logger,
                #                                   hangerstate=self.hangerstate,
                #                                   comconfig=self.comconfig)
                # lightcontroller.close_light()
            except Exception as e:
                self.comstate_flag.set_door_free()  # 串口设置没有在使用
                self.logger.get_log().info(f"执行命令{recv_text}发生异常，{e}")
                result = def_error_result
        else:
            self.logger.get_log().error(f"执行命令{recv_text}，门端口被占用")
            result = used_error_result
        if result is None:
            result = def_error_result
        elif result == "":
            result = def_error_result
        elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
            result = def_error_result
        elif result.endswith("a") and result.startswith("9"):
            result = command_error_result
        self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
        return result

    """
    pang.hy 
    包装方法
    小场景(步骤)-夜灯开
    """

    def step_scene_night_light_open_400000(self):
        #  常量/参数部分
        recv_text = "400000"  # 下发指令
        def_error_result = "9401"  # 默认异常
        command_error_result = "940a"  # 不支持方法异常
        used_error_result = "940d"  # 底层端口或串口被占用异常
        #  业务逻辑部分
        if self.comstate_flag.get_door_isused() is False:  # 串口没有在使用
            self.comstate_flag.set_door_used()  # 串口设置使用中
            try:
                #  对下位机进行操作
                statCom_door = JKSATACOM(self.hangerstate, self.comconfig.get_device_info_door(),
                                         self.comconfig.get_bps_door(), self.comconfig.get_timeout_door(),
                                         self.logger,
                                         0)  # 操作的实例
                self.jkdoor = JKDoorServer(statCom_door, self.hangerstate, self.logger)  # 控制对象
                result = self.jkdoor.operator_hanger(recv_text)  # 执行命令
                self.comstate_flag.set_door_free()  # 串口设置没有在使用
            except Exception as e:
                self.comstate_flag.set_door_free()  # 串口设置没有在使用
                self.logger.get_log().info(f"执行命令{recv_text}发生异常，{e}")
                result = def_error_result
        else:
            self.logger.get_log().error(f"执行命令{recv_text}，门端口被占用")
            result = used_error_result
        if result is None:
            result = def_error_result
        elif result == "":
            result = def_error_result
        elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
            result = def_error_result
        elif result.endswith("a") and result.startswith("9"):
            result = command_error_result
        self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
        return result

    """
    pang.hy
    包装方法
    开灯-新版本非底层串口的开灯开关 2024年开始之后使用
    """
    def step_scene_open_light(self):
        # 开灯
        lightcontroller = LightController(comstate_flag=self.comstate_flag, logger=self.logger,
                                          hangerstate=self.hangerstate,
                                          comconfig=self.comconfig)
        return lightcontroller.open_light()


    """
    pang.hy 
    包装方法
    小场景(步骤)-夜灯关
    """

    def step_scene_night_light_close_410000(self):
        #  常量/参数部分
        recv_text = "410000"  # 下发指令
        def_error_result = "9411"  # 默认异常
        command_error_result = "941a"  # 不支持方法异常
        used_error_result = "941d"  # 底层端口或串口被占用异常
        #  业务逻辑部分
        if self.comstate_flag.get_door_isused() is False:  # 串口没有在使用
            self.comstate_flag.set_door_used()  # 串口设置使用中
            try:
                #  对下位机进行操作
                statCom_door = JKSATACOM(self.hangerstate, self.comconfig.get_device_info_door(),
                                         self.comconfig.get_bps_door(), self.comconfig.get_timeout_door(),
                                         self.logger,
                                         0)  # 操作的实例
                self.jkdoor = JKDoorServer(statCom_door, self.hangerstate, self.logger)  # 控制对象
                result = self.jkdoor.operator_hanger(recv_text)  # 执行命令
                self.comstate_flag.set_door_free()  # 串口设置没有在使用
            except Exception as e:
                self.comstate_flag.set_door_free()  # 串口设置没有在使用
                self.logger.get_log().info(f"执行命令{recv_text}发生异常，{e}")
                result = def_error_result
        else:
            self.logger.get_log().error(f"执行命令{recv_text}，门端口被占用")
            result = used_error_result
        if result is None:
            result = def_error_result
        elif result == "":
            result = def_error_result
        elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
            result = def_error_result
        elif result.endswith("a") and result.startswith("9"):
            result = command_error_result
        self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
        return result

    """
    pang.hy
    包装方法
    关灯-新版本非底层串口的开灯开关 2024年开始之后使用
    """

    def step_scene_close_light(self):
        # 开灯
        lightcontroller = LightController(comstate_flag=self.comstate_flag, logger=self.logger,
                                          hangerstate=self.hangerstate,
                                          comconfig=self.comconfig)
        return lightcontroller.close_light()

    """
    pang.hy 
    包装方法
    小场景(步骤)-XY推杆夹住
    """

    def step_scene_bar_close_2e10002000(self):
        #  常量/参数部分
        recv_text = "2e10002000"  # 下发指令
        def_error_result = "92e1"  # 默认异常
        command_error_result = "92ea"  # 不支持方法异常
        used_error_result = "92ed"  # 底层端口或串口被占用异常

        #  业务逻辑部分
        commond = recv_text
        result = self.bar_use_check(commond)
        if result == "busy":
            self.logger.get_log().error(f"执行命令{recv_text}，推杆端口被占用")
            result = used_error_result
        if result is None:
            result = def_error_result
        elif result == "":
            result = def_error_result
        elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
            result = def_error_result
        elif result.endswith("a") and result.startswith("9"):
            result = command_error_result
        self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
        return result

    """
    pang.hy 
    包装方法
    小场景(步骤)-XY推杆打开
    """

    def step_scene_bar_open_2f10002000(self):
        #  常量/参数部分
        recv_text = "2f10002000"  # 下发指令
        def_error_result = "92f1"  # 默认异常
        command_error_result = "92fa"  # 不支持方法异常
        used_error_result = "92fd"  # 底层端口或串口被占用异常
        #  业务逻辑部分
        commond = recv_text
        result = self.bar_use_check(commond)
        if result == "busy":
            self.logger.get_log().error(f"执行命令{recv_text}，推杆端口被占用")
            result = used_error_result

        if result is None:
            result = def_error_result
        elif result == "":
            result = def_error_result
        elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
            result = def_error_result
        elif result.endswith("a") and result.startswith("9"):
            result = command_error_result
        self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
        return result

    """
    pang.hy 
    包装方法
    小场景(步骤)-XY推杆复位
    """

    def step_scene_bar_reset_500000(self):
        #  常量/参数部分
        recv_text = "500000"  # 下发指令
        def_error_result = "9501"  # 默认异常
        command_error_result = "950a"  # 不支持方法异常
        used_error_result = "950d"  # 底层端口或串口被占用异常
        #  业务逻辑部分
        commond = recv_text
        result = self.bar_use_check(commond)
        if result == "busy":
            self.logger.get_log().error(f"执行命令{recv_text}，推杆端口被占用")
            result = used_error_result

        if result is None:
            result = def_error_result
        elif result == "":
            result = def_error_result
        elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
            result = def_error_result
        elif result.endswith("a") and result.startswith("9"):
            result = command_error_result
        self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
        return result

    """
    pang.hy 
    包装方法
    小场景(步骤)-空调开机
    """

    def step_scene_air_open_300000(self):
        #  常量/参数部分
        recv_text = "300000"  # 下发指令
        def_error_result = "9301"  # 默认异常
        command_error_result = "930a"  # 不支持方法异常
        used_error_result = "930d"  # 底层端口或串口被占用异常
        #  业务逻辑部分
        commond = recv_text
        result = self.bar_use_check(commond)
        if result == "busy":
            self.logger.get_log().error(f"执行命令{recv_text}，推杆端口被占用")
            result = used_error_result

        if result is None:
            result = def_error_result
        elif result == "":
            result = def_error_result
        elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
            result = def_error_result
        elif result.endswith("a") and result.startswith("9"):
            result = command_error_result
        self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
        return result

    """
    pang.hy 
    包装方法
    小场景(步骤)-空调关机
    """

    def step_scene_air_close_310000(self):
        #  常量/参数部分
        recv_text = "310000"  # 下发指令
        def_error_result = "9311"  # 默认异常
        command_error_result = "931a"  # 不支持方法异常
        used_error_result = "931d"  # 底层端口或串口被占用异常
        #  业务逻辑部分
        commond = recv_text
        result = self.bar_use_check(commond)
        if result == "busy":
            self.logger.get_log().error(f"执行命令{recv_text}，推杆端口被占用")
            result = used_error_result

        if result is None:
            result = def_error_result
        elif result == "":
            result = def_error_result
        elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
            result = def_error_result
        elif result.endswith("a") and result.startswith("9"):
            result = command_error_result
        self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
        return result

    """
    pang.hy 
    包装方法 对无人机下发指令
    """

    def send_command_to_drone(self, command):
        global WFC
        result = None
        #  业务逻辑部分
        if not self.comstate_flag.get_charge_isused():  # 串口没有在使用
            self.comstate_flag.set_charge_used()  # 串口设置使用中
            try:
                if self.configini.get_charge_version() == "wfc":  # 充电
                    if self.configini.get_wfc_version() == 'V1.0':  # V1.0版本
                        WFC = WFCServer(self.wf_state, self.logger, self.configini)
                        result = WFC.operator_charge(command)
                    elif self.configini.get_wfc_version() == 'V2.0':  # V2.0版本
                        if self.configini.wfc_double_connect == False:
                            WFC = WFCServerV2(self.wf_state, self.logger, self.configini)
                        else:
                            WFC = WFCServerV2Sender(self.wf_state, self.logger, self.comconfig)
                        result = WFC.operator_charge(command)
                else:  # 触点充电
                    if self.configini.get_wlc_version() == "V1.0":
                        if self.configini.wlc_double_connect == True:  # 全双工通信
                            WFC = M300JCCServerSender(self.hangerstate,self.wf_state, self.logger, self.comconfig)
                        else:
                            WFC = M300JCCServer(self.wf_state, self.logger, self.configini)
                    elif self.configini.get_wlc_version() == "V2.0":
                        WFC = M300JCCServerV2(self.hangerstate,self.wf_state, self.logger, self.configini)
                    elif self.configini.get_wlc_version() == "V3.0":
                        WFC = M300JCCServerV3(self.hangerstate,self.wf_state, self.logger, self.configini)
                    elif self.configini.get_wlc_version() == "V4.0":
                        WFC = M300JCCServerV4(self.hangerstate,self.wf_state, self.logger, self.configini)
                    result = WFC.operator_charge(command)
                self.comstate_flag.set_charge_free()
            except Exception as e:
                self.comstate_flag.set_charge_free()
                self.logger.get_log().info(f"执行命令{command}发生异常，{e}")
                result = "error"
        else:
            result = "busy"
        return result

    """
    pang.hy 
    包装方法
    小场景(步骤)-进入待机
    """

    def step_scene_drone_standby_sb0000(self):
        #  常量/参数部分
        recv_text = "Standby"  # 下发指令
        def_success_result = "9sb0"  # 成功
        def_error_result = "9sb1"  # 默认异常
        command_error_result = "9sba"  # 不支持方法异常
        used_error_result = "9sbd"  # 底层端口或串口被占用异常
        #  改为调用包装方法
        self.logger.get_log().info(f"[step_scene][Standby]开始执行")
        result = ""
        if self.configini.need_auto_charge:  # 如果启动了自动充电
            result = self.standby()
        else:
            result = self.send_command_to_drone(recv_text)
        self.logger.get_log().info(f"[step_scene][Standby]返回结果为{result}")
        if result is None:
            result = def_error_result
        elif result == "":
            result = def_error_result
        elif result == "success":  # 底层返回success，设置操作成功
            result = def_success_result
        elif result == "busy":  # 底层返回busy，设置底层端口或串口被占用异常
            result = used_error_result
        elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
            result = def_error_result
        elif result.endswith("a") and result.startswith("9"):
            result = command_error_result
        self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
        return result

    """
    pang.hy 
    包装方法
    小场景(步骤)-无人机开机
    """

    def step_scene_drone_takeoff_dt0000(self):
        #  常量/参数部分
        recv_text = "TakeOff"  # 下发指令
        def_success_result = "9dt0"  # 成功
        def_error_result = "9dt1"  # 默认异常
        command_error_result = "9dta"  # 不支持方法异常
        used_error_result = "9dtd"  # 底层端口或串口被占用异常
        #  改为调用包装方法
        self.logger.get_log().info(f"[step_scene][TakeOff]开始执行")
        result=""
        if self.configini.need_auto_charge:#如果启动了自动充电
            result=self.takeoff()
        else:
            result = self.send_command_to_drone(recv_text)
        self.logger.get_log().info(f"[step_scene][TakeOff]返回结果为{result}")
        if result is None:
            result = def_error_result
        elif result == "":
            result = def_error_result
        elif result == "success":  # 底层返回success，设置操作成功
            result = def_success_result
        elif result == "busy":  # 底层返回busy，设置底层端口或串口被占用异常
            result = used_error_result
        elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
            result = def_error_result
        elif result.endswith("a") and result.startswith("9"):
            result = command_error_result
        self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
        return result

    """
    pang.hy 
    包装方法
    小场景(步骤)-无人机关机
    """

    def step_scene_drone_off_dd0000(self):
        #  常量/参数部分
        recv_text = "DroneOff"  # 下发指令
        def_success_result = "9dd0"  # 成功
        def_error_result = "9dd1"  # 默认异常
        command_error_result = "9dda"  # 不支持方法异常
        used_error_result = "9ddd"  # 底层端口或串口被占用异常
        #  改为调用包装方法
        self.logger.get_log().info(f"[step_scene][DroneOff]开始执行")
        result=""
        if self.configini.need_auto_charge:  # 如果启动了自动充电
            result = self.droneoff()
        else:
            result = self.send_command_to_drone(recv_text)
        self.logger.get_log().info(f"[step_scene][DroneOff]返回结果为{result}")
        if result is None:
            result = def_error_result
        elif result == "":
            result = def_error_result
        elif result == "success":  # 底层返回success，设置操作成功
            result = def_success_result
        elif result == "busy":  # 底层返回busy，设置底层端口或串口被占用异常
            result = used_error_result
        elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
            result = def_error_result
        elif result.endswith("a") and result.startswith("9"):
            result = command_error_result
        self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
        return result

    """
    pang.hy 
    包装方法
    小场景(步骤)-无人机充电
    """

    def step_scene_drone_charge_cp0000(self):
        #  常量/参数部分
        recv_text = "Charge"  # 下发指令
        def_success_result = "9cp0"  # 成功
        def_error_result = "9cp1"  # 默认异常
        command_error_result = "9cpa"  # 不支持方法异常
        used_error_result = "9cpd"  # 底层端口或串口被占用异常
        #  改为调用包装方法
        self.logger.get_log().info(f"[step_scene][Charge]开始执行")
        result = ""
        if self.configini.need_auto_charge:  # 如果启动了自动充电
            result = self.open_autocharge()
        else:
            result = self.send_command_to_drone(recv_text)
        self.logger.get_log().info(f"[step_scene][Charge]返回结果为{result}")
        if result is None:
            result = def_error_result
        elif result == "":
            result = def_error_result
        elif result == "success":  # 底层返回success，设置操作成功
            result = def_success_result
        elif result == "busy":  # 底层返回busy，设置底层端口或串口被占用异常
            result = used_error_result
        elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
            result = def_error_result
        elif result.endswith("a") and result.startswith("9"):
            result = command_error_result
        self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
        return result

    """
    pang.hy 
    包装方法
    小场景(步骤)-无人机检测(执行一次)
    """

    def step_scene_drone_check_ck0000(self):
        #  常量/参数部分
        recv_text = "Check"  # 下发指令
        def_success_result = "9ck0"  # 成功
        def_error_result = "9ck1"  # 默认异常
        command_error_result = "9cka"  # 不支持方法异常
        used_error_result = "9ckd"  # 底层端口或串口被占用异常
        #  改为调用包装方法
        self.logger.get_log().info(f"[step_scene][Check]开始执行")
        result = self.send_command_to_drone(recv_text)
        self.logger.get_log().info(f"[step_scene][Check]返回结果为{result}")
        if result is None:
            result = def_error_result
        elif result == "":
            result = def_error_result
        elif result == "success":  # 底层返回success，设置操作成功
            result = def_success_result
        elif result == "busy":  # 底层返回busy，设置底层端口或串口被占用异常
            result = used_error_result
        elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
            result = def_error_result
        elif result.endswith("a") and result.startswith("9"):
            result = command_error_result
        self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
        return result

    """
    pang.hy 
    包装方法
    小场景(步骤)-手动启动自动化充电
    """

    def step_scene_auto_charge_on_c00000(self):
        #  常量/参数部分
        recv_text = "c00000"  # 下发指令
        def_success_result = "9c00"  # 成功
        def_error_result = "9c01"  # 默认异常
        unsupported_error_result = "9c04"  # 不支持自动化充电功能
        command_error_result = "9c0a"  # 不支持方法异常
        used_error_result = "9c0d"  # 底层端口或串口被占用异常
        try:
            # 不支持自动化充电功能
            if not self.configini.need_auto_charge:
                return unsupported_error_result
            self.auto_charge_init()  # 重置自动充电参数
            self.auto_charge_set_status(1, 1)  # 是 是
            result = def_success_result
        except Exception as e:
            self.logger.get_log().info(f"执行命令{recv_text}发生异常，{e}")
            result = def_error_result
        self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
        return result

    """
    pang.hy 
    包装方法
    小场景(步骤)-手动关闭自动化充电
    """

    def step_scene_auto_charge_off_c10000(self):
        #  常量/参数部分
        recv_text = "c10000"  # 下发指令
        def_success_result = "9c10"  # 成功
        def_error_result = "9c11"  # 默认异常
        unsupported_error_result = "9c14"  # 不支持自动化充电功能
        command_error_result = "9c1a"  # 不支持方法异常
        used_error_result = "9c1d"  # 底层端口或串口被占用异常
        try:
            # 不支持自动化充电功能
            if not self.configini.need_auto_charge:
                return unsupported_error_result
            self.auto_charge_init()  # 重置自动充电参数
            self.auto_charge_set_status(0, -1)  # 否 未知
            result = def_success_result
        except Exception as e:
            self.logger.get_log().info(f"执行命令{recv_text}发生异常，{e}")
            result = def_error_result
        self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
        return result

    """
    pang.hy 
    包装方法
    自动化充电参数设置公共方法
    """

    def auto_charge_init(self):
        if self.auto_charge is not None:
            self.auto_charge.new_uuid_str()  # 重新生成UUID
            self.auto_charge.reset_charge_num()  # 重置充电编号为0

    def auto_charge_reset_battery_value(self):
        if self.auto_charge is not None:
            self.auto_charge.reset_battery_value()  # 重置电量为0 未知

    def auto_charge_set_status(self, run_auto_charge, fly_back):
        if self.auto_charge is not None:
            self.auto_charge.set_run_auto_charge(run_auto_charge)  # 是否启动自动化充电流程 0:否 1:是 (默认0:否)
            self.auto_charge.set_fly_back(fly_back)  # 是否飞机飞回 -1:未知 0:否 1:是 (默认-1:未知)

    """
    pang.hy 
    大场景-一键起飞准备，开门、开机（如果充电有待机）、松推杆
    """
    opendoor_result_code=""
    def opendoor_thread(self):
        global opendoor_result_code
        self.logger.get_log().info(f"同步执行----执行命令opendoor")
        opendoor_result_code = self.step_scene_door_open_140000()
        self.logger.get_log().info(f"同步执行----执行命令opendoor，执行完毕[机库门打开]步骤，步骤返回{opendoor_result_code}")
    def big_scene_A000(self):
        #  常量/参数部分
        global opendoor_result_code
        opendoor_result_code=""
        recv_text = "A000"  # 大场景命令全码
        def_success_result = "A0009000"  # 成功
        def_error_result = "A0009001"  # 默认异常
        begin_time=time.time()#开始时间
        try:
            if self.configini.get_meanopen()==True:#同时开启机库门和开机
                # 添加线程开门操作2023-2-15
                self.logger.get_log().info(f"同步执行----执行命令{recv_text}")
                thread_opendoor = threading.Thread(target=self.opendoor_thread, args=())
                thread_opendoor.start()
            else:
                # 进入机库门打开step
                result = self.step_scene_door_open_140000()
                self.logger.get_log().info(f"单步执行----执行命令{recv_text}，执行完毕[机库门打开]步骤，步骤返回{result}")
                if not result.endswith("0"):
                    # 末尾不为0，返回拼装8位错误码
                    result = recv_text + result
                    self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                    self.logger.get_log().info(f"尝试复位...")
                    self.big_scene_C000()
                    return result
                #休眠一下
                #time.sleep(3)

            self.auto_charge_init()  # 重置自动充电参数
            self.auto_charge_set_status(0, -1)  # 否 未知
            self.auto_charge_reset_battery_value()  # standby状态时，设置battery_value等于0  因为第一步就是standby，所以初始化马上执行
            # ---------------进入待机step，需要判断当前是否为充电状态，如果是充电状态需要加待机，非充电状态不需要加待机
            if self.hangerstate.wfcstate.get_state()=="charging" or self.hangerstate.wfcstate.get_state()=="waiting":
                result = self.step_scene_drone_standby_sb0000()
                self.logger.get_log().info(f"执行命令{recv_text}，执行完毕[待机]步骤，步骤返回{result}")
                if not result.endswith("0"):
                    # 末尾不为0，返回拼装8位错误码
                    result = recv_text + result
                    self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                    self.logger.get_log().info(f"尝试复位...")
                    self.big_scene_C000()
                    return result
                time.sleep(3)
            # -----------实测中发现，经过跟下位机沟通，确定待机执行返回较快，但是底层有响应时间，休眠10秒后续执行
            #time.sleep(3)
            # 进入无人机开机step
            result = self.step_scene_drone_takeoff_dt0000()
            self.logger.get_log().info(f"执行命令{recv_text}，执行完毕[无人机开机]步骤，步骤返回{result}")
            if not result.endswith("0"):
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                self.logger.get_log().info(f"尝试复位...")
                self.big_scene_C000()
                return result
            # 休眠一下
            # time.sleep(2)
            # self.logger.get_log().info(f"流程中，门的操作")
            # #等待15秒，如果一直失败，则返回失败
            # open_door_fail=False
            if self.configini.get_meanopen()==True:#同时开启机库门和开机
                #松推杆之前检查门的状态是否为关闭状态，如果关闭则判定失败 2023-2-15
                #2023-5-26 加门的打开等待时间,门的执行太慢，开机太快导致失败
                time.sleep(7)
                if not opendoor_result_code.endswith("0") or self.hangerstate.get_hanger_door()=="close":#开门失败或者门是关闭的
                    # 末尾不为0，返回拼装8位错误码
                    result = recv_text + result
                    self.logger.get_log().info(f"执行开门操作命令失败")
                    self.logger.get_log().info(f"尝试复位...")
                    self.big_scene_C000()
                    return opendoor_result_code

            # 进入XY推杆打开step
            result = self.step_scene_bar_reset_500000()
            self.logger.get_log().info(f"执行命令{recv_text}，执行完毕[XY推杆打开]步骤，步骤返回{result}")
            if not result.endswith("0"):
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                self.logger.get_log().info(f"尝试复位...")
                self.big_scene_C000()
                return result

            #  夜灯流程进入判断
            # config = Config()
            # night_light = config.get_night_light()  # 是否启动夜灯功能
            # hour = int(time.strftime("%H", time.localtime()))   #当前系统时间小时数
            # night_light_time_begin = int(config.get_night_light_time_begin())
            # night_light_time_end = int(config.get_night_light_time_end())
            # #  运行夜灯功能，且当前小时在业务配置的时间段内
            # if night_light and (night_light_time_begin <= hour or night_light_time_end > hour):
            #     # 休眠一下
            #     time.sleep(2)
            #     # 打开夜灯判断
            #     result = self.step_scene_night_light_open_400000()
            #     self.logger.get_log().info(f"执行命令{recv_text}，执行完毕[打开夜灯]步骤，步骤返回{result}")
            #     if not result.endswith("0"):
            #         # 末尾不为0，返回拼装8位错误码
            #         result = recv_text + result
            #         self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
            #         self.logger.get_log().info(f"尝试复位...")
            #         self.big_scene_C000()
            #         return result
            # else:
            #     self.logger.get_log().info(f"执行命令{recv_text}，无需执行[打开夜灯]步骤")
            # 最后应答
            endtime=time.time()
            run_time = endtime - begin_time
            self.logger.get_log().info(f"----------------------执行命令{recv_text},返回结果{def_success_result},整体运行时间为{run_time}-------------------------")
            return def_success_result
        except Exception as e:
            self.logger.get_log().info(f"执行命令{recv_text}发生异常，{e}")
            self.logger.get_log().info(f"执行命令{recv_text}，返回结果{def_error_result}")
            self.logger.get_log().info(f"尝试复位...")
            self.big_scene_C000()
            return def_error_result

    '''
    ZKL
    开机状态下的一键起飞
    '''
    def big_scene_A010(self):
        #  常量/参数部分
        global opendoor_result_code
        opendoor_result_code = ""
        recv_text = "A010"  # 大场景命令全码
        def_success_result = "A0109000"  # 成功
        def_error_result = "A0109001"  # 默认异常
        begin_time = time.time()  # 开始时间
        try:
            # 进入机库门打开step
            result = self.step_scene_door_open_140000()
            self.logger.get_log().info(f"单步执行----执行命令{recv_text}，执行完毕[机库门打开]步骤，步骤返回{result}")
            if not result.endswith("0"):
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                self.logger.get_log().info(f"尝试复位...")
                self.big_scene_C000()
                return result
            # 休眠一下
            # time.sleep(3)
            self.auto_charge_init()  # 重置自动充电参数
            self.auto_charge_set_status(0, -1)  # 否 未知
            self.auto_charge_reset_battery_value()  # standby状态时，设置battery_value等于0  因为第一步就是standby，所以初始化马上执行

            # 进入XY推杆打开step
            result = self.step_scene_bar_reset_500000()
            self.logger.get_log().info(f"执行命令{recv_text}，执行完毕[XY推杆打开]步骤，步骤返回{result}")
            if not result.endswith("0"):
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                self.logger.get_log().info(f"尝试复位...")
                self.big_scene_C000()
                return result
            endtime = time.time()
            run_time = endtime - begin_time
            self.logger.get_log().info(
                f"----------------------执行命令{recv_text},返回结果{def_success_result},整体运行时间为{run_time}-------------------------")
            return def_success_result
        except Exception as e:
            self.logger.get_log().info(f"执行命令{recv_text}发生异常，{e}")
            self.logger.get_log().info(f"执行命令{recv_text}，返回结果{def_error_result}")
            self.logger.get_log().info(f"尝试复位...")
            self.big_scene_C000()
            return def_error_result

    """
    pang.hy 
    大场景-一键起飞后续(自检成功),关闭机库门
    """

    def big_scene_A100(self):
        #  常量/参数部分
        recv_text = "A100"  # 大场景命令全码
        def_success_result = "A1009000"  # 成功
        def_error_result = "A1009001"  # 默认异常
        try:
            self.auto_charge_init()  # 重置自动充电参数
            self.auto_charge_set_status(0, 0)  # 否 否
            # 进入机库门关闭step
            result = self.step_scene_door_close_150000()
            self.logger.get_log().info(f"执行命令{recv_text}，执行完毕[机库门关闭]步骤，步骤返回{result}")
            if not result.endswith("0"):
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                return result
            self.logger.get_log().info(f"执行命令{recv_text}，返回结果{def_success_result}")
            return def_success_result
        except Exception as e:
            self.logger.get_log().info(f"执行命令{recv_text}发生异常，{e}")
            self.logger.get_log().info(f"执行命令{recv_text}，返回结果{def_error_result}")
            return def_error_result

    """
        pang.hy 
        大场景-一键起飞后续(自检失败)
        """

    def big_scene_A200(self):
        #  常量/参数部分
        recv_text = "A200"  # 大场景命令全码
        def_success_result = "A2009000"  # 成功
        def_error_result = "A2009001"  # 默认异常
        try:
            self.auto_charge_init()  # 重置自动充电参数
            # 进入XY推杆夹住step
            result = self.step_scene_bar_close_2e10002000()
            self.logger.get_log().info(f"执行命令{recv_text}，执行完毕[XY推杆夹住]步骤，步骤返回{result}")
            if not result.endswith("0"):
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                self.auto_charge_set_status(0, -1)  # 否 未知
                self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                return result
            # 进入机库门关闭step
            result = self.step_scene_door_close_150000()
            self.logger.get_log().info(f"执行命令{recv_text}，执行完毕[机库门关闭]步骤，步骤返回{result}")
            if not result.endswith("0"):
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                self.auto_charge_set_status(0, -1)  # 否 未知
                self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                return result
            # 进入空调开机step
            result = self.step_scene_air_open_300000()
            self.logger.get_log().info(f"执行命令{recv_text}，执行完毕[空调开机]步骤，步骤返回{result}")
            if not result.endswith("0"):
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                self.auto_charge_set_status(0, -1)  # 否 未知
                self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                return result
            # 进入无人机关机step
            result = self.step_scene_drone_off_dd0000()
            self.logger.get_log().info(f"执行命令{recv_text}，执行完毕[无人机关机]步骤，步骤返回{result}")
            if not result.endswith("0"):
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                self.auto_charge_set_status(0, -1)  # 否 未知
                self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                return result
            self.auto_charge_set_status(1, 1)  # 是 是
            self.logger.get_log().info(f"执行命令{recv_text}，返回结果{def_success_result}")
            return def_success_result
        except Exception as e:
            self.auto_charge_set_status(0, -1)  # 否 未知
            self.logger.get_log().info(f"执行命令{recv_text}发生异常，{e}")
            self.logger.get_log().info(f"执行命令{recv_text}，返回结果{def_error_result}")
            return def_error_result

    """
    pang.hy 
    大场景-一键降落准备,开门
    """

    def big_scene_B000(self):
        #  常量/参数部分
        recv_text = "B000"  # 大场景命令全码
        def_success_result = "B0009000"  # 成功
        def_error_result = "B0009001"  # 默认异常
        try:
            self.auto_charge_init()  # 重置自动充电参数
            self.auto_charge_set_status(0, -1)  # 否 未知
            # 进入机库门打开step
            result = self.step_scene_door_open_140000()
            self.logger.get_log().info(f"执行命令{recv_text}，执行完毕[机库门打开]步骤，步骤返回{result}")
            if not result.endswith("0"):
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                return result
            self.logger.get_log().info(f"执行命令{recv_text}，返回结果{def_success_result}")
            return def_success_result
        except Exception as e:
            self.logger.get_log().info(f"执行命令{recv_text}发生异常，{e}")
            self.logger.get_log().info(f"执行命令{recv_text}，返回结果{def_error_result}")
            return def_error_result

    """
    pang.hy 
    大场景-一键降落后续，收推杆，关机，关门
    """

    def big_scene_B100(self):
        #  常量/参数部分
        recv_text = "B100"  # 大场景命令全码
        def_success_result = "B1009000"  # 成功
        def_error_result = "B1009001"  # 默认异常
        try:
            self.auto_charge_init()  # 重置自动充电参数
            # 进入XY推杆夹住step
            result = self.step_scene_bar_close_2e10002000()
            self.logger.get_log().info(f"执行命令{recv_text}，执行完毕[XY推杆夹住]步骤，步骤返回{result}")
            if not result.endswith("0"):
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                self.auto_charge_set_status(0, -1)  # 否 未知
                self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                return result
            # 进入机库门关闭step
            result = self.step_scene_door_close_150000()
            self.logger.get_log().info(f"执行命令{recv_text}，执行完毕[机库门关闭]步骤，步骤返回{result}")
            if not result.endswith("0"):
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                self.auto_charge_set_status(0, -1)  # 否 未知
                self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                return result
            # 进入待机step
            result = self.step_scene_drone_standby_sb0000()
            self.logger.get_log().info(f"执行命令{recv_text}，执行完毕[待机]步骤，步骤返回{result}")
            if not result.endswith("0"):
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
            # 实测中发现，经过跟下位机沟通，确定待机执行返回较快，但是底层有响应时间，休眠10秒后续执行
            time.sleep(2)
            # 进入无人机关机step
            result = self.step_scene_drone_off_dd0000()
            self.logger.get_log().info(f"执行命令{recv_text}，执行完毕[无人机关机]步骤，步骤返回{result}")
            if not result.endswith("0"):
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                self.auto_charge_set_status(0, -1)  # 否 未知
                self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                return result
            self.auto_charge_set_status(1, 1)  # 是 是
            self.logger.get_log().info(f"执行命令{recv_text}，返回结果{def_success_result}")
            # 进入空调开机step
            result = self.step_scene_air_open_300000()
            self.logger.get_log().info(f"执行命令{recv_text}，执行完毕[空调开机]步骤，步骤返回{result}")
            if not result.endswith("0"):
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                self.auto_charge_set_status(0, -1)  # 否 未知
                self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                return result
            #  夜灯流程进入判断
            # config = Config()
            # night_light = config.get_night_light()  # 是否启动夜灯功能
            # if night_light:
            #     time.sleep(2)
            #     # 进入关闭夜灯step
            #     result = self.step_scene_night_light_close_410000()
            #     self.logger.get_log().info(f"执行命令{recv_text}，执行完毕[关闭夜灯]步骤，步骤返回{result}")
            #     if not result.endswith("0"):
            #         # 末尾不为0，返回拼装8位错误码
            #         result = recv_text + result
            #         self.auto_charge_set_status(0, -1)  # 否 未知
            #         self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
            #         return result
            # else:
            #     self.logger.get_log().info(f"执行命令{recv_text}，无需执行[关闭夜灯]步骤")
            return def_success_result
        except Exception as e:
            self.auto_charge_set_status(0, -1)  # 否 未知
            self.logger.get_log().info(f"执行命令{recv_text}发生异常，{e}")
            self.logger.get_log().info(f"执行命令{recv_text}，返回结果{def_error_result}")
            return def_error_result

    """
    pang.hy 
    大场景-一键降落取消
    """

    def big_scene_B200(self):
        #  常量/参数部分
        recv_text = "B200"  # 大场景命令全码
        def_success_result = "B2009000"  # 成功
        def_error_result = "B2009001"  # 默认异常
        try:
            self.auto_charge_init()  # 重置自动充电参数
            self.auto_charge_set_status(0, 0)  # 否 否
            # 进入机库门关闭step
            result = self.step_scene_door_close_150000()
            self.logger.get_log().info(f"执行命令{recv_text}，执行完毕[机库门关闭]步骤，步骤返回{result}")
            if not result.endswith("0"):
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                return result

            #  夜灯流程进入判断
            config = Config()
            night_light = config.get_night_light()  # 是否启动夜灯功能
            if night_light:
                time.sleep(2)
                # 进入关闭夜灯step
                result = self.step_scene_night_light_close_410000()
                self.logger.get_log().info(f"执行命令{recv_text}，执行完毕[关闭夜灯]步骤，步骤返回{result}")
                if not result.endswith("0"):
                    # 末尾不为0，返回拼装8位错误码
                    result = recv_text + result
                    self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                    return result
            else:
                self.logger.get_log().info(f"执行命令{recv_text}，无需执行[关闭夜灯]步骤")

            self.logger.get_log().info(f"执行命令{recv_text}，返回结果{def_success_result}")
            return def_success_result
        except Exception as e:
            self.logger.get_log().info(f"执行命令{recv_text}发生异常，{e}")
            self.logger.get_log().info(f"执行命令{recv_text}，返回结果{def_error_result}")
            return def_error_result

    """
    pang.hy 
    大场景-一键复位(内部根据充电方式切换不同复位操作)
    """

    def big_scene_C000(self):
        #  常量/参数部分
        recv_text = "C000"  # 大场景命令全码
        def_success_result = "C0009000"  # 成功
        def_error_result = "C0009001"  # 默认异常
        charge_type_error_result = "C0009002"  # 充电方式不是触点式
        try:
            if self.configini.get_charge_version() == "wlc":
                return self.big_scene_C100()
            else:
                return charge_type_error_result
        except Exception as e:
            self.logger.get_log().info(f"执行命令{recv_text}发生异常，{e}")
            self.logger.get_log().info(f"执行命令{recv_text}，返回结果{def_error_result}")
            return def_error_result

    """
    pang.hy 
    大场景-一键复位(触点式复位)
    """
    def big_scene_C100(self):
        #  常量/参数部分
        recv_text = "C100"  # 大场景命令全码
        def_success_result = "C1009000"  # 成功
        def_error_result = "C1009001"  # 默认异常
        charge_type_error_result = "C1009002"  # 充电方式不是触点式
        if self.configini.get_charge_version() == "wlc":
            try:
                # 进入XY推杆夹住step
                result = self.step_scene_bar_close_2e10002000()
                self.logger.get_log().info(f"执行命令{recv_text}，执行完毕[XY推杆夹住]步骤，步骤返回{result}")
                if not result.endswith("0"):
                    # 末尾不为0，返回拼装8位错误码
                    result = recv_text + result
                    self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                    return result
                # 进入无人机关机step
                result = self.step_scene_drone_off_dd0000()
                self.logger.get_log().info(f"执行命令{recv_text}，执行完毕[无人机关机]步骤，步骤返回{result}")
                if not result.endswith("0"):
                    # 末尾不为0，返回拼装8位错误码
                    result = recv_text + result
                    self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                    return result
                # 进入机库门关闭step
                result = self.step_scene_door_close_150000()
                self.logger.get_log().info(f"执行命令{recv_text}，执行完毕[机库门关闭]步骤，步骤返回{result}")
                if not result.endswith("0"):
                    # 末尾不为0，返回拼装8位错误码
                    result = recv_text + result
                    self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                    return result
                # 进入空调开机step
                result = self.step_scene_air_open_300000()
                self.logger.get_log().info(f"执行命令{recv_text}，执行完毕[空调开机]步骤，步骤返回{result}")
                if not result.endswith("0"):
                    # 末尾不为0，返回拼装8位错误码
                    result = recv_text + result
                    self.logger.get_log().info(f"执行命令{recv_text}，返回结果{result}")
                    return result
                self.logger.get_log().info(f"执行命令{recv_text}，返回结果{def_success_result}")
                return def_success_result
            except Exception as e:
                self.logger.get_log().info(f"执行命令{recv_text}发生异常，{e}")
                self.logger.get_log().info(f"执行命令{recv_text}，返回结果{def_error_result}")
                return def_error_result
        else:
            return charge_type_error_result



    def get_msg(self):  # 启用一个线程调用
        '''
        获取消息,服务端交互
        '''
        #config = Config()
        activate = ActivateUtils(self.configini,self.logger)
        while self.server_service:
            try:
                # 一直接收消息
                if self.web_socket is None:
                    try:
                        self.logger.get_log().info(f"--------------开始启动websocket服务-----------------")
                        # 初始化最新配置
                        self.init_server_addr()
                        web_socket_temp = create_connection(self.server_addr, timeout=3000)  # 如果30秒没有收到消息则结束等待
                        if web_socket_temp is None:
                            self.logger.get_log().error(f"接收-web_socket创建失败，创建web_socket为空")
                            self.web_socket = None
                            time.sleep(20)  # 10秒后重连
                            continue
                        else:
                            self.web_socket = web_socket_temp
                    except Exception as e:
                        self.logger.get_log().error(f"接收-web_socket创建失败，无法连接websocket服务器，{e}")
                        # 由于目标计算机积极拒绝 已经建立连接的情况下，远程服务器关掉连接

                        self.web_socket = None
                        time.sleep(20)  # 10秒后重连
                        continue
                recv_text = self.web_socket.recv()  # 远程主机强迫关闭了一个现有的连接,需要做连接重连,如果无命令则一直等待
                if recv_text != "":
                    # 2023-08-25 验证获取的liecense
                    try:
                        if 'jklog' in recv_text:
                            # 触发本地日志上传
                            self.logger.get_log().info(f"接收到jklog命令")
                            utilminio = MINIO.MiniUtils(self.logger)
                            utilminio.start_uploadlog()
                            continue
                        if recv_text == 'state':
                            #self.logger.get_log().info(f"receive data is {recv_text}")
                            self.web_socket.send(self.hangerstate.getHangerState())  # json对象
                            continue
                        #2023-12-15新增远程更新上位机license码
                        if "GetLicense" in recv_text or "getLicense" in recv_text or "getlicense" in recv_text:
                            self.logger.get_log().info(f"接收到GetLicense命令")
                            mac_id=activate.get_unique_identifier()
                            activate_code=self.configini.get_license_code()
                            left_days="1900-01-01 00:00:00"
                            try:
                                left_days=activate.get_pass_date()
                            except Exception as e:
                                left_days="1900-01-01 00:00:00"
                            res=f"\"mac_id\":\"{mac_id}\",\"active_code\":\"{activate_code}\",\"left_days\":\"{left_days}\""
                            res="{"+res+"}"
                            self.logger.get_log().info(f"服务端获取lincense：{res}")
                            self.web_socket.send(f"{res}")  # json对象
                            continue
                        if "SetLicense" in recv_text or "setLicense" in recv_text or "setlicense" in recv_text:
                            self.logger.get_log().info(f"接收到SetLicense命令")
                            try:
                                code=recv_text.split(r":")
                                if len(code)==2:
                                    self.logger.get_log().info(f"设置lincense：{code[1]}")
                                    #判断此激活码是否有效
                                    res = activate.checkInputLicense(code[1])
                                    if len(res) != 0 and res['status'] == False:
                                        self.logger.get_log().info(f"设置lincense,输入licensecod无效：{code[1]}")
                                        self.web_socket.send(f"setlicense:fail")
                                    else:
                                        self.logger.get_log().info(f"设置lincense,输入licensecod有效：{code[1]}")
                                        self.configini.set_license_code(code[1])
                                        self.web_socket.send(f"setlicense:success")
                                    continue
                                else:
                                    self.logger.get_log().info(f"设置lincense错误，传递的license是：{code[1]}")
                                    self.web_socket.send(f"setlicense:fail")
                                    continue
                            except Exception as setex:
                                self.logger.get_log().info(f"设置lincense异常：{setex}")
                                self.web_socket.send(f"setlicense:fail")
                                continue
                        res = activate.checkLicens()
                        if len(res) != 0 and res['status'] == False:
                            self.web_socket.send("激活码无效或过期，请联系机库厂商")
                            self.logger.get_log().info(f"license 验证结果 {res}")
                            continue
                    except Exception as ee:
                        print(f"异常，{ee}")
                        continue

                    if recv_text == "heartbeat":
                        self.logger.get_log().debug(f"接收到心跳应答heartbeat")
                        continue
                    # 获取机库状态的指令
                    if 'state' in recv_text or 'jklog' in recv_text or 'update' in recv_text or "settime" in recv_text or "reset" in recv_text or "deletelog" in recv_text or "startalarm" in recv_text  or "stopalarm" in recv_text:
                        if recv_text == 'state':
                            #self.logger.get_log().info(f"receive data is {recv_text}")
                            self.web_socket.send(self.hangerstate.getHangerState())  # json对象
                            continue
                        elif 'jklog' in recv_text:
                            # 触发本地日志上传
                            self.logger.get_log().info(f"接收到jklog命令")
                            utilminio = MINIO.MiniUtils(self.logger)
                            utilminio.start_uploadlog()
                            continue
                        elif 'update' in recv_text:  # 更新日志信息
                            client.updatesoftware()
                            continue
                        elif 'settime' in recv_text:  # 更新系统时间
                            # linux系统
                            import os
                            # print(f"receive  txt is {recv_text}")
                            pwd = "wkzn123"
                            time_value = recv_text.split(',')[1]
                            # os.system(f"date -s '{time_value}'")
                            os.system(f"echo {pwd} | sudo -S date -s '{time_value}'")
                            continue
                        elif 'reset' in recv_text:  # 一键复位
                            thread_reset = threading.Thread(target=self.reset_hanger, args=(self.web_socket,))
                            # thread_reset.setDaemon(True)
                            thread_reset.start()
                            continue
                        elif 'deletelog' in recv_text:  # 删除日志
                            self.logger.delete_log()
                            continue
                        elif 'startalarm' in recv_text:  # 开启警报
                            alarmcontroller=AlarmController(self.hangerstate,self.logger,self.configini)
                            alarmcontroller.start_alarm()
                            continue
                        elif 'stopalarm' in recv_text:  # 关闭警报
                            alarmcontroller = AlarmController(self.hangerstate, self.logger, self.configini)
                            alarmcontroller.stop_alarm()
                            continue
                    else:
                        # 直接调用串口发送命令
                        self.logger.get_log().info(f"socket接收到命令:{recv_text}")
                        # 2023-4-17 如果上一个线程还没处理结束，又启动了一个新线程需要优化处理
                        thread_read = threading.Thread(target=self.dealMessage, args=(self.web_socket, recv_text))
                        thread_read.start()
                        # 2023-4-17 如果上一个线程还没处理结束，又启动了一个新线程优化处理，做一下测试
                        # threading.Thread(target=self.dealMessage, args=(self.web_socket, recv_text)).start()
                else:
                    # 没有接收到消息，重连
                    self.logger.get_log().info(f"接收到消息，为空")
                    # try:
                    #     self.web_socket.close()
                    # except Exception as e:
                    #     self.logger.get_log().info(f"websocket没有接收到消息，关闭链接--异常，{e}")
                    # self.web_socket = None
                    #self.hangerstate.set_STAT_connet_state('error')
                    continue
            except Exception as ex:
                #self.logger.get_log().info(f"websocket接收发送消息--异常，{ex}")
                try:
                    self.logger.get_log().info(f"websocket接收发送消息--异常，{ex.__str__()}")
                    # if "远程主机强迫关闭了一个现有的连接" in f"{ex}": #已经建立了套接字，本地网络问题导致无法连接
                    if "timed out" not in f"{ex}":  # 已经建立了套接字，但是网络问题导致无法连接
                        print("---非timed out导致无法连接,重启-----")
                    self.web_socket.close()
                    self.web_socket = None
                except Exception as e:
                    self.logger.get_log().info(f"websocket循环处理业务因异常退出,尝试关闭链接--异常，{e}")
                    self.web_socket = None
                self.hangerstate.set_STAT_connet_state('error')
                time.sleep(5)
                continue

    def do_test_step(self):
        print(f"模拟在websockets中被调用某方法，实际不链接机库，测试被知道用步骤")
        return "9xx0"


if __name__ == "__main__":
    pass
    print("abc")
