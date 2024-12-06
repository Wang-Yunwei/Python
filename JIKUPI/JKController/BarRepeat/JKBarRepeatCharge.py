# -*- coding: utf-8 -*- 
# @Time : 2022/12/6 12:08 
# @Author : ZKL 
# @File : JKBarRepeatCharge.py
'''
如果充电时候，充电失败，并且启用了该配置
推杆左右推杆打开回退10cm;
然后左右推杆再多夹紧10cm+2mm;
再进行充电操作；
无论充电是否成功，保存推杆打开和关闭参数；
'''
import BASEUtile.logger
from BASEUtile.Config import Config
from BASEUtile.HangerState import HangerState
from SATA.SATACom import JKSATACOM
from WFCharge.WFState import WFState


class JKBarRepeatCharge:
    def __init__(self,state,logger,comconfig):
        self.bar_distance=2 #左右推杆移动的距离
        self.back_distance=100 #推杆回退的距离,要区分出来下位机的配置是2.0还是3.0版本，2.0是走动的距离，3.0要考虑距离终点的距离
        self.config=Config() #参数设置和读取配置工具
        self.config_repeat=True #配置了充电失败推杆重复操作，如果是true则做推杆重复操作
        self.state=state #当前机库的状态
        self.statcom_bar = JKSATACOM(self.state, comconfig.get_device_info_bar(), comconfig.get_bps_bar(),
                                        comconfig.get_timeout_bar(), logger, 0)  # 机库门推拉杆、状态串口,aricondition

    def repeat_bar(self):
        '''
        推杆先打开指定的距离，然后再夹紧指定的距离
        '''
        print(f"最打开推杆，重复夹紧操作")
        old_openbar_para=self.config.getcommond()[0][3]
        old_closebar_para=self.config.getcommond()[0][4]
        move_para=0
        back_openbar_para =""
        closebar_para=""
        if self.config.get_down_version()=="V1.0" and self.state.hanger_bar=="close":
            if int(old_closebar_para[3:6])>self.back_distance:
                move_para=self.back_distance
                back_openbar_para = old_openbar_para[:3] + str(move_para) + "2000"
            else:
                return False
        elif self.config.get_down_version()=="V2.0" and self.state.hanger_bar=="close":
            if int(old_closebar_para[3:6])>self.back_distance:
                move_para=int(old_closebar_para[3:6])-self.back_distance
                back_openbar_para = old_openbar_para[:3] + str(move_para) + old_closebar_para[6:]
            else:
                return False
        elif self.state.hanger_bar=="open":
            return False
        #做机库的打开操作
        result = self.statcom_bar.operator_hanger(back_openbar_para + "\r\n")
        if result!="92f0":
            return False
        #做机库的夹紧操作
        closebar_para="2e1"+str(int(old_closebar_para[3:6])+self.bar_distance)+old_closebar_para[6:]
        result = self.statcom_bar.operator_hanger(closebar_para + "\r\n")
        if result!="92e0":
            return False
        print(f"{self.config.getdetail_config()},{old_openbar_para},{old_closebar_para},{back_openbar_para},{closebar_para}")
        #做机库推拉杆的参数保存
        new_openbar_para =""
        new_closebar_para =""
        if self.config.get_down_version()=="V1.0":
            new_openbar_para ="2f1"+closebar_para[3:6]+old_openbar_para[6:]
            new_closebar_para=closebar_para
        elif self.config.get_down_version()=="V2.0":
            new_openbar_para =old_openbar_para
            new_closebar_para = closebar_para
        self.config.setcommon_sign(open_bar=new_openbar_para,close_bar=new_closebar_para)
        return True

if __name__=="__main__":
    # ---------------无线充电操作
    wf_state = WFState()  # 创建对象
    # ---------机库状态---包括当前无线充电的状态
    hangstate = HangerState(wf_state)
    logger=BASEUtile.logger.Logger(__name__)  # 日志记录)
    jkbar=JKBarRepeatCharge(hangstate,logger)
    jkbar.repeat_bar()
