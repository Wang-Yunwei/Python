import uuid
import time

from WFCharge.JCCServerM300 import JCCServerM300
from WFCharge.JCCServerM300Sender import JCCServerM300Sender
from WFCharge.JCCServerV2M300Single import JCCServerV2M300Single
from WFCharge.JCCServerV3M300 import JCCServerV3M300
from WFCharge.JCCServerV4M350 import JCCServerV4M350
from WFCharge.WFCServer import WFCServer
from WFCharge.WFCServerV2 import WFCServerV2
from WFCharge.WFCServerV2Sender import WFCServerV2Sender
import SerialUsedStateFlag as SerialUsedStateFlag
from WFCharge.JCCServerV5 import JCCServerV5
import WFCharge.WFState as WFState
import BASEUtile.Config as Config


class AutoChargeControl_bk(object):
    def __init__(self, logger):
        # 外部传入
        self.logger = logger  # 日志对象
        # self.wf_state = wf_state  # 充电状态 WFState()
        self.comstate_flag = SerialUsedStateFlag  # 串口使用标记
        # self.configini = Config  # 全局配置
        # self.hangstate = hangstate  # 追加状态参数
        # self.comconfig = USBDeviceConfig()
        #  内部参数
        self.run_auto_charge = 0  # 是否启动自动化充电流程 0:否 1:是 (默认0:否)
        self.fly_back = -1  # 是否飞机飞回 -1:未知 0:否 1:是 (默认-1:未知)
        self.uuid_str = str(uuid.uuid4())  # 充电编号
        self.charge_num = 0  # 充电次数
        self.charge_max_num = 5  # 充电次数异常阀值，大于等于该阀值报异常
        self.def_sleep_time = 60  # 自动充电检查执行间隔 默认60秒

        self.wait_charge_time = 900  # 执行充电间隔时间 默认900秒 15分钟 TODO 考虑外部配置传入

    def get_run_auto_charge(self):
        return self.run_auto_charge

    def set_run_auto_charge(self, value):
        self.run_auto_charge = value

    def get_fly_back(self):
        return self.fly_back

    def set_fly_back(self, value):
        self.fly_back = value

    def new_uuid_str(self):
        self.uuid_str = str(uuid.uuid4())

    def get_charge_num(self):
        return self.charge_num

    def reset_charge_num(self):
        self.charge_num = 0

    def reset_battery_value(self):
        WFState.set_battery_value(0)

    def one_time_charge_error(self):
        self.charge_num = self.charge_num + 1
        return self.charge_num

    def start_auto_charge(self):
        # for pang.hy test
        # self.run_auto_charge = 1  # 是否启动自动化充电流程 0:否 1:是 (默认0:否)
        # self.fly_back = 1  # 是否飞机飞回 -1:未知 0:否 1:是 (默认-1:未知)
        # self.wait_charge_time = 15  # 执行充电间隔时间 默认900秒 15分钟

        while True:
            try:
                if Config.get_is_need_auto_charge():
                    self.logger.get_log().debug(f"[AutoChargeControl]===启用自动化充电功能===")
                    self.doAutoCharge()
                else:
                    self.logger.get_log().debug(f"[AutoChargeControl]===禁用自动化充电功能===")
                #  休眠
                time.sleep(self.def_sleep_time)
            except Exception as ex:
                self.logger.get_log().error(f"[AutoChargeControl]===自动化充电功能发生异常{ex}")
                continue

    def doAutoCharge(self):
        try:
            self.logger.get_log().debug(
                f"自动化充电流程执行 run_auto_charge = {self.run_auto_charge} fly_back = {self.fly_back} uuid_str = {self.uuid_str}  state = {WFState.get_battery_state()} battery_value = {WFState.get_battery_value()} charge_num = {self.charge_num}")
            if self.run_auto_charge == 1:
                if self.fly_back == 1:
                    self.logger.get_log().debug(f"[AutoChargeControl][是否飞机飞回状态]状态 是 -继续")
                    is_need_charge = self.isNeedCharge()  # 充电状态是否需要充电
                    # 判断是否需要执行充电
                    if is_need_charge:
                        self.logger.get_log().info(f"[AutoChargeControl]自动化充电流程-需要充电-流程开始-进行休眠[{self.wait_charge_time}]")
                        keep_uuid = self.uuid_str  # 缓存并记录[充电编号]
                        time.sleep(self.wait_charge_time)  # 休眠，无人机降温中
                        self.logger.get_log().debug(f"[AutoChargeControl]自动化充电流程-需要充电-休眠唤醒")
                        # 如下判断考虑手动停止开启操作时，可能自动化线程正处在休眠之中的情况，故充电之前要进行二次判断
                        if not self.run_auto_charge == 1:
                            self.logger.get_log().debug(f"[AutoChargeControl]休眠唤醒判断-未启动自动化充电状态-结束")
                            return
                        if not self.fly_back == 1:
                            self.logger.get_log().debug(f"[AutoChargeControl][是否飞机飞回状态]状态 否 -结束")
                            return
                        if keep_uuid == self.uuid_str:
                            #  这里追加判断 二次判断充电状态是否需要充电
                            is_need_charge_again = self.isNeedCharge()  # 充电状态是否需要充电
                            if not is_need_charge_again:
                                self.logger.get_log().debug(f"[AutoChargeControl]自动化充电流程-需要充电-二次判断充电状态为无需充电-结束")
                                return
                            self.logger.get_log().info(f"[AutoChargeControl]自动化充电流程-执行充电指令")
                            charge_result = self.doCharge()
                            if charge_result == "success":
                                self.logger.get_log().info(f"[AutoChargeControl]自动化充电流程-需要充电-充电成功")
                                self.reset_charge_num()  # 充电成功 充电次数计数器重置0
                            else:
                                self.logger.get_log().info(f"[AutoChargeControl]自动化充电流程-需要充电-失败-{charge_result}")
                                this_time_charge_num = self.one_time_charge_error()  # 充电次数计数器+1
                                if this_time_charge_num >= self.charge_max_num:  # 充电次数大于等于阀值
                                    self.run_auto_charge = 0  # 设置 是否启动自动化充电流程 0:否
                                    self.fly_back = -1  # 设置 是否飞机飞回 -1:未知
                                    self.logger.get_log().info(
                                        f"[AutoChargeControl][告警]:warning:连续{self.charge_max_num}次充电发生异常")
                        else:
                            self.logger.get_log().debug(f"[AutoChargeControl]充电编号不一致 -结束")
                        self.logger.get_log().debug(f"[AutoChargeControl]自动化充电流程-需要充电-流程结束")
                    else:
                        self.logger.get_log().debug(f"[AutoChargeControl]自动化充电流程-无需充电 -结束")
                elif self.fly_back == 0:
                    self.logger.get_log().debug(f"[AutoChargeControl][是否飞机飞回状态]状态 否 -结束")
                elif self.fly_back == -1:
                    self.logger.get_log().debug(f"[AutoChargeControl][是否飞机飞回状态]状态 未知 - 结束")
                    return
                else:
                    self.logger.get_log().debug(f"[AutoChargeControl]无法识别的[是否飞机飞回状态]:{self.fly_back}")
            elif self.run_auto_charge == 0:
                self.logger.get_log().debug(f"[AutoChargeControl]未启动自动化充电状态")
            else:
                self.logger.get_log().debug(f"[AutoChargeControl]无法识别的[是否启动自动化充电流程状态]:{self.run_auto_charge}")
        except Exception as e:
            self.logger.get_log().debug(f"[AutoChargeControl]AutoChargeControl-doAutoCharge发生不可知异常,{e}")

    def isNeedCharge(self):
        is_charge = False  # 是否需要充电
        state = WFState.get_battery_state()  # 当前充电状态，close/charging/standby/takeoff/outage
        battery_value = WFState.get_battery_value()  # 电池电量, 0/1/2/3/4/100 满电情况下为100
        if state == "close":
            if battery_value == "100":
                self.run_auto_charge = 0  # 设置 是否启动自动化充电流程 0:否
                self.fly_back = -1  # 设置 是否飞机飞回 -1:未知
                self.reset_charge_num()  # 充电成功 充电次数计数器重置0
                self.logger.get_log().debug(f"[AutoChargeControl][充满电]情况")
            #如果是御3或者V1.0版本，开机充电，这个时候不能再启动充电？如果是降温的情况如何处理？如果是新版M300充电，如何处理
            elif battery_value == "0":#需要充电
                is_charge = True
                self.logger.get_log().debug(f"[AutoChargeControl][电量未知]情况")
            else:
                is_charge = True
                self.logger.get_log().debug(f"[AutoChargeControl][未充电]情况")
        elif state == "takeoff":
            if battery_value == "100":
                self.run_auto_charge = 0  # 设置 是否启动自动化充电流程 0:否
                self.fly_back = -1  # 设置 是否飞机飞回 -1:未知
                self.reset_charge_num()  # 充电成功 充电次数计数器重置0
                self.logger.get_log().debug(f"[AutoChargeControl][充满电]情况")
            elif battery_value == "0":
                is_charge = True
                self.logger.get_log().debug(f"[AutoChargeControl][电量未知]情况")
            else:
                is_charge = True
                self.logger.get_log().debug(f"[AutoChargeControl][未充电]情况")
        elif state == "charging":
            self.logger.get_log().debug(f"[AutoChargeControl][充电中]情况")
        elif state == "standby":
            self.logger.get_log().debug(f"[AutoChargeControl][待机无法充电]情况")
        elif state == "outage":
            self.logger.get_log().debug(f"[AutoChargeControl][充电箱断电]情况")
        elif state == "cool":
            self.logger.get_log().debug(f"[AutoChargeControl][电池冷却中]情况")
        else:
            self.logger.get_log().debug(f"[AutoChargeControl]无法识别的[当前充电状态]:{state}")
        return is_charge

    '''
    执行充电指令
    '''

    def doCharge(self):  # TODO 执行充电指令(保留无线充电，但实际暂无此场景)
        # 常量
        #首先确定是否要继续执行自动充电，如果前面自动充电已经断开，等待一定时间后，要做重新检测
        if self.run_auto_charge!=1:#2023-3-9
            return "error"
        recv_text = "Charge"  # 充电固定指令
        result = "error"  # 充电返回状态
        if not self.comstate_flag.get_is_used_serial_charge():
            self.comstate_flag.set_used_serial_charge()
            try:
                if Config.get_charge_version() == "wfc":  # 无线充电
                    if Config.get_wfc_version() == 'V1.0':  # V1.0版本
                        WFC = WFCServer(self.logger)
                        result = WFC.operator_charge(recv_text)
                    elif Config.get_wfc_version() == 'V2.0':  # V2.0版本
                        if Config.get_is_wfc_double_connect() == False:
                            WFC = WFCServerV2(self.logger)
                        else:
                            WFC = WFCServerV2Sender(self.logger)
                        result = WFC.operator_charge(recv_text)
                else:  # 触点充电
                    if Config.get_wlc_version() == "V1.0":
                        if Config.get_is_wlc_double_connect() == True:  # 全双工通信
                            WFC = JCCServerM300Sender(self.logger)
                        else:
                            WFC = JCCServerM300(self.logger)
                        result = WFC.operator_charge(recv_text)
                    elif Config.get_wlc_version() == "V2.0":  # V2.0
                        WFC = JCCServerV2M300Single(self.logger)
                        result = WFC.operator_charge(recv_text)
                    elif Config.get_wlc_version() == "V3.0":  # V3.0
                        WFC = JCCServerV3M300(self.logger)
                        result = WFC.operator_charge(recv_text)
                    elif Config.get_wlc_version() == "V4.0":  # V4.0
                        WFC = JCCServerV4M350(self.logger)
                        result = WFC.operator_charge(recv_text)
                    elif Config.get_wlc_version() == "V5.0":  # V5.0
                        WFC = JCCServerV5(self.logger)
                        result = WFC.operator_charge(recv_text)
                self.comstate_flag.set_used_serial_free_charge()
            except Exception as charex:
                self.comstate_flag.set_used_serial_free_charge()
                result = "chargeerror"
        else:
            result = "busy"
        return result
