'''
WebSocket的基本操作
'''
import datetime
import threading
import time

from websocket import create_connection
import client
from Activate.ActivateUtils import ActivateUtils
from AirCondition.AirConditionComputer import AirConditionComputer
from AutoCharge.AutoChargeControl import AutoChargeControl
from AutoCharge.AutoChargeControlV1 import AutoChargeControlV1
from BASEUtile import MINIO
import BASEUtile.Config as Config
from JKController.JKBarServer import JKBarServer
from JKController.JKDoorServer import JKDoorServer
from JKController.LightController import LightController
from SATA.SATACom import JKSATACOM
from WFCharge.JCCServerM300 import JCCServerM300
from WFCharge.JCCServerM300Sender import JCCServerM300Sender
# from WFCharge.JCCServerV2 import M300JCCServerV2
from WFCharge.JCCServerV2M300Single import JCCServerV2M300Single
from WFCharge.JCCServerV3M300 import JCCServerV3M300
from WFCharge.JCCServerV4M350 import JCCServerV4M350
from WFCharge.WFCServer import WFCServer
from WFCharge.WFCServerV2 import WFCServerV2
from WFCharge.WFCServerV2Sender import WFCServerV2Sender
from weather.AlarmController import AlarmController
from weather.OutLiftController import OutLiftController
from weather.UAVController import UAVController
from ShutterDoor.RollingShutterDoor import RollingShutterDoor
from ShutterDoor.ShadeWindow import ShadeWindow
import BASEUtile.BusinessConstant as BusinessConstant
from Lift.UpdownLift import UpdownLift
import SerialUsedStateFlag as SerialUsedStateFlag
from WFCharge.JCCServerV5 import JCCServerV5
import BASEUtile.HangarState as HangarState
import WFCharge.WFState as WFState
import USBDevice.USBDeviceConfig as USBDeviceConfig
import BASEUtile.OperateUtil as OperateUtil


class WebSocketUtil():
    def __init__(self, server_addr, logger, auto_charge):
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
        # self.hangerstate = hangerstate
        self.jkdoor = None
        self.jkbar = None
        self.wfc_server = None
        # self.wf_state = wf_state
        # self.configini = Config
        # pang.hy:新存放链接对象的 由于原来get_msg中ws对象外部无法获取，故这里使用方法共享self对象存放
        self.web_socket = None
        # pang.hy:心跳间隔
        self.alive_second = Config.get_web_socket_heart()
        # pang.hy:自动化充电对象 可能为None
        self.auto_charge = auto_charge
        # 串口信息
        # self.comconfig = comconfig
        # 执行初始化
        self.init_server_addr()  # 初始化服务器参数
        # 是否在执行websocket指令
        self.is_run_command = False

    def init_server_addr(self):
        '''
        初始化服务器地址
        :return:
        '''
        # config = Config()
        configinfo_list = Config.get_websocket_config_info()  # 列表元组的形式
        self.server_addr = configinfo_list[0][2]
        # if configinfo_list is None:
        #     # create table
        #     Config.createTable()
        # if configinfo_list is not None and len(configinfo_list) == 1:
        #     self.ip = configinfo_list[0][1]
        #     self.socket = configinfo_list[0][2]
        #     self.station_id = configinfo_list[0][3]
        #     if len(configinfo_list[0]) == 5:
        #         web_socket_url = configinfo_list[0][4]  # 如果url不为空，则直接读取url
        #     else:
        #         web_socket_url = ''
        #     if web_socket_url == "" or web_socket_url is None:
        #         self.server_addr = f"ws://{self.ip}:{self.socket}/uav/hangarServer/{self.station_id}"
        #         if (not isinstance(self.auto_charge, AutoChargeControlV1)):
        #             print(f"{self.auto_charge.__class__}")
        #             self.auto_charge = AutoChargeControlV1(self.logger)
        #     else:
        #         self.server_addr = web_socket_url
        #         # 天宇的自动充电
        #         if (not isinstance(self.auto_charge, AutoChargeControl)):
        #             print(f"{self.auto_charge.__class__}")
        #             self.auto_charge = AutoChargeControl(self.logger)
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
        if Config.get_is_need_heartbeat_check():
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

    def dealMessage(self, ws, recv_text: str):
        """
         thread, deal the receive message
        :param ws:
        :param recv_text:
        :return:
        """
        try:
            self.logger.get_log().info(f"[websockets.dealMessage]接收到websocket端命令-开始,操作指令为:{recv_text}")
            # 进入就被占用执行
            self.is_run_command = True
            result = OperateUtil.operate_hangar(recv_text)
            self.logger.get_log().info(
                f"[websockets.dealMessage]接收到websocket端命令-结束,操作指令为:{recv_text},返回结果为:{result}")
            ws.send(result)
        except Exception as comex:
            self.logger.get_log().error(f"[websockets.dealMessage]接收到websocket端命令-异常,异常信息为:{comex}")
        finally:
            self.is_run_command = False

    # -------------------衢州操作-----------------------end

    def reset_hanger(self, ws):
        '''
        一键复位机库，（1）复位推杆 （2）关闭机库门  （3）复位充电
        :return:
        '''
        result_charge = OperateUtil.operate_hangar("sb0000")
        result_charge = OperateUtil.operate_hangar("dd0000")
        result_door = OperateUtil.operate_hangar("150000")
        commond = "500000"
        result_bar = OperateUtil.operate_hangar(commond)

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
                    self.web_socket.send(HangarState.get_hangar_state())  # json对象
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

    def get_msg(self):  # 启用一个线程调用
        '''
        获取消息,服务端交互
        '''
        # config = Config()
        activate = ActivateUtils(self.logger)
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
                print(f"[websocket.get_msg]收到websocket命令-{recv_text}")
                if recv_text != "":
                    # 2023-08-25 验证获取的liecense
                    try:
                        if 'jklog' in recv_text:
                            # 触发本地日志上传
                            self.logger.get_log().info(f"[websocket.get_msg]接收到jklog命令:{recv_text}")
                            utilminio = MINIO.MiniUtils(self.logger)
                            utilminio.start_uploadlog()
                            continue
                        elif 'upload_log' in recv_text:
                            self.logger.get_log().info(f"[websocket.get_msg]接收到上传日志命令-开始,接收到信息为:{recv_text}")
                            upload_log_datetime = recv_text.split(",")[1]
                            siteId = recv_text.split(",")[2]
                            result = OperateUtil.step_scene_upload_log_lg0000(siteId,upload_log_datetime)
                            self.web_socket.send(result)
                            self.logger.get_log().info(f"[websocket.get_msg]接收到上传日志命令-结束,接收到信息为:{recv_text},返回结果为:{result}")
                            continue
                        if recv_text == 'state':
                            # self.logger.get_log().info(f"receive data is {recv_text}")
                            self.web_socket.send(HangarState.get_hangar_state())  # json对象
                            continue
                        # 2023-12-15新增远程更新上位机license码
                        if "GetLicense" in recv_text or "getLicense" in recv_text or "getlicense" in recv_text:
                            self.logger.get_log().info(f"接收到GetLicense命令")
                            mac_id = activate.get_unique_identifier()
                            activate_code = Config.get_license_code()
                            left_days = "1900-01-01 00:00:00"
                            try:
                                left_days = activate.get_pass_date()
                            except Exception as e:
                                left_days = "1900-01-01 00:00:00"
                            res = f"\"mac_id\":\"{mac_id}\",\"active_code\":\"{activate_code}\",\"left_days\":\"{left_days}\""
                            res = "{" + res + "}"
                            self.logger.get_log().info(f"服务端获取lincense：{res}")
                            self.web_socket.send(f"{res}")  # json对象
                            continue
                        if "SetLicense" in recv_text or "setLicense" in recv_text or "setlicense" in recv_text:
                            self.logger.get_log().info(f"接收到SetLicense命令")
                            try:
                                code = recv_text.split(r":")
                                if len(code) == 2:
                                    self.logger.get_log().info(f"设置lincense：{code[1]}")
                                    # 判断此激活码是否有效
                                    res = activate.checkInputLicense(code[1])
                                    if len(res) != 0 and res['status'] == False:
                                        self.logger.get_log().info(f"设置lincense,输入licensecod无效：{code[1]}")
                                        self.web_socket.send(f"setlicense:fail")
                                    else:
                                        self.logger.get_log().info(f"设置lincense,输入licensecod有效：{code[1]}")
                                        Config.set_license_code(code[1])
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
                    if 'state' in recv_text or 'jklog' in recv_text or 'update' in recv_text or "settime" in recv_text or "reset" in recv_text or "deletelog" in recv_text or "startalarm" in recv_text or "stopalarm" in recv_text:
                        if recv_text == 'state':
                            # self.logger.get_log().info(f"receive data is {recv_text}")
                            self.web_socket.send(HangarState.get_hangar_state())  # json对象
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
                            alarmcontroller = AlarmController(self.logger)
                            alarmcontroller.start_alarm()
                            continue
                        elif 'stopalarm' in recv_text:  # 关闭警报
                            alarmcontroller = AlarmController(self.logger)
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
                    # self.hangerstate.set_STAT_connet_state('error')
                    continue
            except Exception as ex:
                # self.logger.get_log().info(f"websocket接收发送消息--异常，{ex}")
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
                HangarState.set_stat_connect_state('error')
                time.sleep(5)
                continue

    def do_test_step(self):
        print(f"模拟在websockets中被调用某方法，实际不链接机库，测试被知道用步骤")
        return "9xx0"


if __name__ == "__main__":
    w = WebSocketUtil(None,None,None)
    w.dealMessage(None,"B100")
