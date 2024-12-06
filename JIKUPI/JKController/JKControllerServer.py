# -*- coding: utf-8 -*- 
# @Time : 2021/12/15 14:45 
# @Author : ZKL 
# @File : JKControllerServer.py
#机库控制端server
import time

from BASEUtile.Config import Config
from BASEUtile.HangerState import HangerState
from BASEUtile.logger import Logger
from SATA.SATACom import JKSATACOM
from WFCharge.WFState import WFState


class JKControllerServer1():
    def __init__(self,statcom_door,statcom_bar,hangerstate,logger):
        '''
        :param statcom_l: 左串口对象
        :param statcom_r: 右串口对象
        :param hangerstate: 机库状态
        '''
        self.server_service=True
        self.logger=logger
        self.statcom_door=statcom_door#机库门串口、状态串口
        self.statcom_bar=statcom_bar#机库门推拉杆、状态串口,aricondition
        self.hangerstate=hangerstate
        self.config=Config()#命令配置文件


    def get_hanger_state(self):  # 获取机库当前状态
        return self.hangerstate.getHangerState()

    def get_connet_state(self):#获取机库连接状态
        '''
        获取机库状态
        :return:
        '''
        #发送机库连接命令，然后根据返回值返回机库的状态信息
        result1=self.statcom_door.operator_hanger("000000\r\n")
        result2=self.statcom_bar.operator_hanger("010000\r\n")
        self.logger.get_log().info(f"连接状态---：{result1},{result2}")
        if result1=="9000" and result2=="9010":
            return "9000"
        else:
            return "9001"#机库通信连接异常
        #return "9000"

    def oper_door(self,commond):
        '''
        机库门的操作，包括左右门同时开启和关闭
        :return:
        '''
        try:
            # 直接调用串口发送命令
            self.logger.get_log().info(f"接收到发送过来的命令{commond}")
            if len(commond) != 6 and len(commond) != 8:
                self.logger.get_log().error(f"接收到端命令{commond}，长度不为6或8")
                return 'error'
            #机库门操作特殊处理
            if commond.startswith("14") or commond.startswith("15"):#门的开启操作
                #机库门的操作，左右机库门的操作，同时开启
                #先开机库左门，然后再开机库右门（需要确认）
                if commond.startswith("14"):
                    #开门操作
                    commond=self.config.getcommond()[0][1]
                else:
                    #关门操作
                    commond = self.config.getcommond()[0][2]
                result=self.statcom_door.operator_hanger(commond+"\r\n")
                #判断返回的结果
                self.logger.get_log().info(f"机库门--,下位机返回结果：{result}")
                if result == "90119021":
                    if commond.startswith("14"):
                        result="9141"
                    else:
                        result="9151"
                return result
        except Exception as e:
            self.logger.get_log().info(f"机库门--，机库门操作异常，{e}")
            return "error"

    def oper_bar(self, commond):
        '''
        推拉杠的操作，包括推拉杠同时开启和关闭
        :return:
        '''
        try:
            # 直接调用串口发送命令
            self.logger.get_log().info(f"推拉杆--接收到发送过来的命令{commond}")
            if len(commond) != 6 and len(commond) != 10 and len(commond) != 8 and len(commond) != 12:
                self.logger.get_log().error(f"接收到外部端命令{commond}，长度不为6 、 10、8、12")
                return 'error'
            # 机库门操作特殊处理
            if commond.startswith("2a") or commond.startswith("2b") or commond.startswith("2c") or commond.startswith("2d") or commond.startswith("2e") or commond.startswith("2f"):  # 左右推杆打开
                if commond.startswith("2e"):
                    #打开推杆
                    commond=self.config.getcommond()[0][4]
                elif commond.startswith("2f"):
                    #关门操作
                    commond = self.config.getcommond()[0][3]
                result = self.statcom_bar.operator_hanger(commond + "\r\n")
                    # 判断返回的结果
                self.logger.get_log().info(f"推拉杆--下位机返回结果：{result}")
                if result == "90119021":
                    if commond.startswith("2f"):
                        result="92f1"
                    elif commond.startswith("2e"):
                        result="92e1"
                    elif commond.startswith("2a"):
                        result="92a1"
                    elif commond.startswith("2b"):
                        result="92b1"
                    elif commond.startswith("2c"):
                        result="92c1"
                    elif commond.startswith("2d"):
                        result="92d1"
                return result
        except Exception as e:
            self.logger.get_log().info(f"推拉杆--机库操作异常，{e}")
            return "error"


    def oper_aircondition(self,commond):#操作空调
        '''
        操作空调
        :return:
        '''
        #发送空调操作命令
        result=self.statcom_bar.operator_hanger(commond+"\r\n")
        self.logger.get_log().info(f"空调---返回值为：{result}")
        if result == "90119021":
            if commond.startswith("30"):
                result = "9301"
            else:
                result = "9311"
        return result

    def oper_controller(self,commond):#操作遥控器
        '''
        操作无人机遥控器
        :return:
        '''
        #发送空调操作命令
        result=self.statcom_door.operator_hanger(commond+"\r\n")
        self.logger.get_log().info(f"遥控器---返回值为：{result}")
        if result == "90119021":
            if commond.startswith("40"):
                result = "9401"
            else:
                result = "9411"
        return result

    def oper_reset_bar(self, commond):  # 推杆复位
        '''
        推杆复位打开
        :return:
        '''
        # 发送空调操作命令
        result = self.statcom_bar.operator_hanger(commond + "\r\n")
        self.logger.get_log().info(f"遥控器---返回值为：{result}")
        if result == "90119021":
            if commond.startswith("50"):
                result = "9501"
            else:
                result = "9511"

        return result

    def operator_hanger(self,commond):
        '''
        操作机库
        :param commond: 操作命令
        :return:
        '''
        try:
            # 直接调用串口发送命令
            if len(commond) != 6 and len(commond) != 10 and len(commond) != 8 and len(commond) != 12:
                self.logger.get_log().error(f"接收到外部端命令{commond}，长度不为6、10、8、12")
                return 'error'
            #机库门操作特殊处理
            if commond.startswith("0"):#连接状态的操作
                return self.get_hanger_state()
            elif commond.startswith("1"):#门的操作
                return self.oper_door(commond)
            elif commond.startswith("2"):#推杆操作:
                return self.oper_bar(commond)
            elif commond.startswith("3"):#空调操作:
                return self.oper_aircondition(commond)
            elif commond.startswith("4"):#遥控操作:
                return self.oper_controller(commond)
            elif commond.startswith("5"):#推杆:
                return self.oper_reset_bar(commond)
        except Exception as e:
            self.logger.get_log().info(f"机库操作异常，{e}")
            return "error"

if __name__=="__main__":
    logger=Logger(__name__)#日志记录
    wfcstate=WFState()
    hangstate = HangerState(wfcstate)
    device_info_bar = "/dev/ttyUSBBar" #机库门串口、状态串口
    bps_l = 57600
    timeout_l = 22
    device_info_door = "/dev/ttyUSBDoor" #推拉杠、状态串口,空调
    bps_r = 57600
    timeout_r = 22

    statCom_l = JKSATACOM(hangstate, device_info_door, bps_l, timeout_l,logger,0)
    statCom_r = JKSATACOM(hangstate, device_info_bar, bps_r, timeout_r,logger,0)
    #jkcontroller = JKControllerServer(statCom_l, statCom_r, hangstate,logger)
    #result=jkcontroller.operator_hanger("2e12912230")#commond 加紧
    #result = jkcontroller.operator_hanger("2f10002000")  # commond 打开
    #result = jkcontroller.operator_hanger("140123")  # open door
    #result = jkcontroller.operator_hanger("150000")  # close door
    #result = jkcontroller.operator_hanger("300000")  # open aircondition
    #result = jkcontroller.operator_hanger("310000")  # close aircondition
    #result = jkcontroller.operator_hanger("400000")  # open/close uav controller
    #result = jkcontroller.operator_hanger("500000")  # 推杆复位
    #result_close = jkcontroller.operator_hanger("150000")  # close door
    #print(f"{result}")
    # for i in range(1):
    #     time.sleep(3)
    #     result_open = jkcontroller.operator_hanger("140120")  # open door
    #     if result_open !='9140':
    #         break
    #     time.sleep(3)
    #     result_close = jkcontroller.operator_hanger("150120")  # close door
    #     if result_close !='9150':
    #         break
    #     print(f"times is {i+1}")

    # result = jkcontroller.operator_hanger("000000")  # commond
    # print(f"{result}")



