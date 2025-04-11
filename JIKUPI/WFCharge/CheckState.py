# -*- coding: utf-8 -*- 
# @Time : 2022/6/13 1:25 
# @Author : ZKL 
# @File : CheckState.py
import time
import BASEUtile.OperateUtil as OperateUtil
import SerialUsedStateFlag as SerialUsedStateFlag


class CheckState:
    '''
    做触点充电状态线程
    每隔1分钟更新一次状态信息
    '''

    def __init__(self, logger):
        # self.hangstate = hangstate
        self.logger = logger
        # self.wfstate = wfstate
        self.comstate_flag = SerialUsedStateFlag
        # if Config.get_is_wlc_double_connect() == True and Config.get_wlc_version() == "V1.0":
        #     self.WFC = WFCServerV2Sender(self.logger)
        # elif Config.get_wlc_version() == "V2.0":
        #     self.WFC = JCCServerV2M300Single(self.logger)
        # elif Config.get_wlc_version() == "V3.0":  # 触点充电3.0
        #     self.WFC = JCCServerV3M300(self.logger)
        # elif Config.get_wlc_version() == "V4.0":  # 触点充电4.0
        #     self.WFC = JCCServerV4M350(self.logger)
        # elif Config.get_wlc_version() == "V5.0":  # 触点充电5.0
        #     self.WFC = JCCServerV5(self.logger)
        # else:
        #     self.WFC = JCCServerM300(self.logger)
        self.sleeptime = 60  # 1分钟检查一次状态

    def checkinfo(self):
        if self.comstate_flag.get_is_used_serial_charge() is True:
            return
        else:
            # if Config.get_is_wlc_double_connect() == True and Config.get_wlc_version() == "V1.0":
            #     WFC = WFCServerV2Sender(self.logger)
            # elif Config.get_wlc_version() == "V2.0":
            #     WFC = JCCServerV2M300Single(self.logger)
            # elif Config.get_wlc_version() == "V3.0":  # 触点充电3.0
            #     WFC = JCCServerV3M300(self.logger)
            # elif Config.get_wlc_version() == "V4.0":  # 触点充电4.0
            #     WFC = JCCServerV4M350(self.logger)
            # elif Config.get_wlc_version() == "V5.0":  # 触点充电5.0
            #     WFC = JCCServerV5(self.logger)
            # else:
            #     WFC = JCCServerM300(self.logger)
            # result = self.WFC.operator_charge("Check")
            result = OperateUtil.operate_hangar("Check")

    def start_check(self):
        while True:
            try:
                self.checkinfo()
                time.sleep(self.sleeptime)
            except Exception as ex:
                self.logger.get_log().info(f"[CheckState]获取电池状态线程异常,异常信息为:{ex}")
