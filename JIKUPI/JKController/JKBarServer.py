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


class JKBarServer():
    def __init__(self,statcom_bar,hangerstate,logger,configini):
        '''
        :param statcom_l: 左串口对象
        :param statcom_r: 右串口对象
        :param hangerstate: 机库状态
        '''
        self.server_service=True
        self.logger=logger
        self.statcom_bar=statcom_bar#机库门推拉杆、状态串口,aricondition
        self.hangerstate=hangerstate
        self.config=Config()#命令配置文件
        self.configini=configini


    def get_hanger_state(self):  # 获取机库当前状态
        return self.hangerstate.getHangerState()

    def get_connet_state(self):#获取机库连接状态
        '''
        获取机库状态
        :return:
        '''
        #发送机库连接命令，然后根据返回值返回机库的状态信息
        #result1=self.statcom_door.operator_hanger("000000\r\n")
        result2=self.statcom_bar.operator_hanger("010000\r\n")
        self.logger.get_log().info(f"连接状态---：{result2}")
        if  result2=="9010":
            return "9000"
        else:
            return "9001"#机库通信连接异常
        #return "9000"

    def oper_bar(self, commond):
        '''
        推拉杠的操作，包括推拉杠同时开启和关闭
        :return:
        '''
        try:
            # 直接调用串口发送命令
            self.logger.get_log().info(f"推拉杆--接收到发送过来的命令{commond}")
            if len(commond) != 6 and len(commond) != 10 and len(commond) != 8 and len(commond) != 12:
                self.logger.get_log().error(f"接收到外部端命令{commond}，长度不为6 or 10")
                return 'error'
            # 机库门操作特殊处理
            result=""
            if commond.startswith("2a") or commond.startswith("2b") or commond.startswith("2c") or commond.startswith("2d") or commond.startswith("2e") or commond.startswith("2f"):  # 左右推杆打开
                if commond.startswith("2e"):
                    #close
                    commond=self.config.getcommond()[0][4]
                    # 关闭推杆操作
                    # if self.configini.get_bar_diff_move() == True:  # 先推前后，再推左右
                    #     #夹紧前后之前，先做一下短距离的左右夹紧
                    #     commond_td = commond[:3] + "0002" + commond[7:]
                    #     result_td = self.statcom_bar.operator_hanger(commond_td + "\r\n")
                    #     self.logger.get_log().info(f"前后推杆的返回值{result_td}")
                    #     time.sleep(2)
                    #     if self.configini.get_down_version() == "V2.0":
                    #         commond_lr = commond[:7] + "000"
                    #     else:
                    #         commond_lr = commond
                    #     result_lr = self.statcom_bar.operator_hanger(commond_lr + "\r\n")  # 左右推杆动
                    #     self.logger.get_log().info(f"左右推杆的返回值{result_td}")
                    #     if result_lr=="92e0" and result_td=="92e0":
                    #         result="92e0"
                    #     else:
                    #         result="92e1"
                    #         # time.sleep(20)
                    #         # result = "92e0"
                    if self.configini.get_bar_move_style() == 'TDF':  # 先推前后，再推左右
                        # 夹紧前后之前，先做一下短距离的左右夹紧
                        commond_td = commond[:3] + "0002" + commond[7:]
                        result_td = self.statcom_bar.operator_hanger(commond_td + "\r\n")
                        self.logger.get_log().info(f"前后推杆的返回值{result_td}")
                        time.sleep(2)
                        if result_td!="92e0":
                            return "92e1"
                        if self.configini.get_down_version() == "V2.0":
                            commond_lr = commond[:7] + "000"
                        else:
                            commond_lr = commond
                        result_lr = self.statcom_bar.operator_hanger(commond_lr + "\r\n")  # 左右推杆动
                        self.logger.get_log().info(f"左右推杆的返回值{result_lr}")
                        if result_lr == "92e0" and result_td == "92e0":
                            result = "92e0"
                        else:
                            result = "92e1"
                            # time.sleep(20)
                            # result = "92e0"
                    elif self.configini.get_bar_move_style() == 'LRF':  # 先推左右再前后
                        commond_lr = commond[:7] + "000"
                        result_lr = self.statcom_bar.operator_hanger(commond_lr + "\r\n")  # 左右推杆动
                        self.logger.get_log().info(f"左右推杆的返回值{result_lr}")
                        time.sleep(2)
                        if result_lr!="92e0":
                            return "92e1"
                        if self.configini.get_down_version() == "V2.0":
                            commond_td = commond[:3] + "0002" + commond[7:]
                        else:
                            commond_td = commond
                        result_td = self.statcom_bar.operator_hanger(commond_td + "\r\n")  #前后推杆动作
                        self.logger.get_log().info(f"前后推杆的返回值{result_td}")
                        if result_lr == "92e0" and result_td == "92e0":
                            result = "92e0"
                        else:
                            result = "92e1"
                            # time.sleep(20)
                            # result = "92e0"
                    else:#同时夹紧
                        result = self.statcom_bar.operator_hanger(commond+ "\r\n")
                    # 2023-9-13 如果有夹紧后打开前后推杆配置
                    if self.configini.get_td_bar()==True:
                        #如果配置了前后打开操作
                        commond = self.config.getcommond()[0][3]#2f10002000
                        if self.configini.get_down_version()=="V2.0":
                            commond="2f10002"+commond[7:]
                            result1 = self.statcom_bar.operator_hanger(commond + "\r\n")
                            self.logger.get_log().info(f"前后推杆打开的返回值{result1}")
                            self.hangerstate.set_hanger_bar("close")
                            self.hangerstate.set_hanger_td_bar("open")
                        elif self.configini.get_down_version()=="V3.0":
                            commond_close=self.config.getcommond()[0][4]
                            commond="2f1"+commond_close[3:6]+"2000"
                            result1=self.statcom_bar.operator_hanger(commond+ "\r\n")
                            self.logger.get_log().info(f"前后推杆打开的返回值{result1}")
                            self.hangerstate.set_hanger_bar("close")
                            self.hangerstate.set_hanger_td_bar("open")
                elif commond.startswith("2f"):
                    #open
                    commond = self.config.getcommond()[0][3]
                    result = self.statcom_bar.operator_hanger(commond + "\r\n")
                    # 判断返回的结果
                self.logger.get_log().info(f"推拉杆--下位机返回结果：{result}")
                if not result.startswith("92"):
                    self.logger.get_log().info(f"推杆操作---返回值错误，为：{result}")
                    if commond.startswith("2f"):
                        return "92f1"
                    if commond.startswith("2e"):
                        return "92e1"
                if result == "90119021":
                    if commond.startswith("2f"):
                        if self.hangerstate.get_hanger_bar() == "open":#2023-04-24加状态判断，如果下位机返回空，但是当前机库推杆为打开则返回正确值
                            result='92f0'
                        else:
                            result="92f1"
                        # result = "92f0"
                        # self.hangerstate.set_hanger_bar("open")
                    elif commond.startswith("2e"):
                        result="92e1"
                        # result = "92e0"
                        # self.hangerstate.set_hanger_bar("close")
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


    def oper_reset_bar(self, commond):  # 推杆复位
        '''
        推杆复位打开
        :return:
        '''
        # 发送空调操作命令
        result = self.statcom_bar.operator_hanger(commond + "\r\n")
        time.sleep(1)#偶尔出现上下推杆不一致的情况，需要做一下等待
        self.logger.get_log().info(f"推杆复位---返回值为：{result}")
        if not result.startswith("95"):
            self.logger.get_log().info(f"推杆复位---返回值错误，为：{result}")
            return "9501"
        if result == "90119021":
            if commond.startswith("50"):
                if self.hangerstate.get_hanger_bar()=="open":#2023-04-24加状态判断，如果下位机返回空，但是当前机库推杆为打开则返回正确值
                    result="9500"
                    self.logger.get_log().info(f"推杆复位：下位机返回空null,但是推杆是打开的，则修改返回结果为9500")
                else:
                    result = "9501"
                # time.sleep(20)
                # result = "9500"
                # self.hangerstate.set_hanger_bar("open")
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
                self.logger.get_log().error(f"接收到外部端命令{commond}，长度不为6 or 10")
                return 'error'
            #机库门操作特殊处理
            if commond.startswith("0"):#连接状态的操作
                return self.get_hanger_state()
            elif commond.startswith("2"):#推杆操作:
                return self.oper_bar(commond)
            elif commond.startswith("3"):#空调操作:
                return self.oper_aircondition(commond)
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


