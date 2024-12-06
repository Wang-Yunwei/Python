# -*- coding: utf-8 -*- 
# @Time : 2022/6/13 1:25 
# @Author : ZKL 
# @File : CheckState.py
import time

from WFCharge.WFCServerV2 import WFCServerV2
from WFCharge.WFCServerV2Sender import WFCServerV2Sender


class CheckStateWFCV2():
    '''
    做触点充电状态线程
    每隔1分钟更新一次状态信息
    '''
    def __init__(self,logger,wfstate,comstate_flag,configini,comconfig):
        self.logger=logger
        self.wfstate=wfstate
        self.comstate_flag=comstate_flag
        if configini.wfc_double_connect==True:
            self.WFC= WFCServerV2Sender(self.wfstate, self.logger,comconfig)
        else:
            self.WFC=WFCServerV2(self.wfstate, self.logger,configini)
        self.sleeptime=60

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
