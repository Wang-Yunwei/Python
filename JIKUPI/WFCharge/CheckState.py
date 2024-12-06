# -*- coding: utf-8 -*- 
# @Time : 2022/6/13 1:25 
# @Author : ZKL 
# @File : CheckState.py
import time

from WFCharge.JCCServer import M300JCCServer
#from WFCharge.JCCServerV2 import M300JCCServerV2
from WFCharge.JCCServerV2_Single import M300JCCServerV2
from WFCharge.JCCServerV3 import M300JCCServerV3
from WFCharge.JCCServerV4M350 import M300JCCServerV4
from WFCharge.WFCServerV2Sender import WFCServerV2Sender


class CheckState():
    '''
    做触点充电状态线程
    每隔1分钟更新一次状态信息
    '''

    def __init__(self,hangstate, logger, wfstate, comstate_flag,configini,comconfig):
        self.hangstate=hangstate
        self.logger = logger
        self.wfstate = wfstate
        self.comstate_flag = comstate_flag
        if configini.wlc_double_connect==True and configini.get_wlc_version()=="V1.0":
            self.WFC = WFCServerV2Sender(self.wfstate, self.logger, comconfig)
        elif configini.get_wlc_version()=="V2.0":
            self.WFC=M300JCCServerV2(self.hangstate,self.wfstate, self.logger,configini)
        elif configini.get_wlc_version()=="V3.0":#触点充电3.0
            self.WFC=M300JCCServerV3(self.hangstate,self.wfstate, self.logger,configini)
        elif configini.get_wlc_version()=="V4.0":#触点充电4.0
            self.WFC=M300JCCServerV4(self.hangstate,self.wfstate, self.logger,configini)
        else:
            self.WFC = M300JCCServer(self.wfstate, self.logger,configini)
        self.sleeptime = 60  #1分钟检查一次状态

    def checkinfo(self):
        if self.comstate_flag.get_charge_isused() == True:
            return
        else:
            result = self.WFC.operator_charge("Check")

    def start_check(self):
        while True:
            try:
                self.checkinfo()
                time.sleep(self.sleeptime)
            except Exception as ex:
                continue
