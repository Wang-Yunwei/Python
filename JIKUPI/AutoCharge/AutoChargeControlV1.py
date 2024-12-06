import uuid
import time

from USBDevice.USBDeviceConfig import USBDeviceConfig
from WFCharge.JCCServer import M300JCCServer
from WFCharge.JCCServerSend import M300JCCServerSender
from WFCharge.JCCServerV2 import M300JCCServerV2
from WFCharge.JCCServerV3 import M300JCCServerV3
from WFCharge.WFCServer import WFCServer
from WFCharge.WFCServerV2 import WFCServerV2
from WFCharge.WFCServerV2Sender import WFCServerV2Sender


class AutoChargeControlV1(object):
    def __init__(self, logger, wf_state, comstate_flag, configini, hangstate):
        # 外部传入
        self.logger = logger  # 日志对象
        self.wf_state = wf_state  # 充电状态 WFState()
        self.comstate_flag = comstate_flag  # 串口使用标记
        self.configini = configini  # 全局配置
        self.hangstate = hangstate  # 追加状态参数
        self.comconfig = USBDeviceConfig(self.configini)
        #  内部参数
        self.run_auto_charge = 0  # 是否启动自动化充电流程 0:否 1:是 (默认0:否)
        self.fly_back = -1  # 是否飞机飞回 -1:未知 0:否 1:是 (默认-1:未知)
        self.uuid_str = str(uuid.uuid4())  # 充电编号
        self.charge_num = 0  # 充电次数
        self.charge_max_num = 5  # 充电次数异常阀值，大于等于该阀值报异常
        self.def_sleep_time = 60  # 自动充电检查执行间隔 默认60秒
        self.only_takeoff=True #就是要执行任务或做开机测试用，不进行充电

        self.wait_charge_time = 300  # 执行充电间隔时间 默认900秒 15分钟 TODO 考虑外部配置传入

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
        self.wf_state.set_battery_value(0)

    def one_time_charge_error(self):
        self.charge_num = self.charge_num + 1
        return self.charge_num

    def get_only_takeoff(self):
        return self.only_takeoff

    def set_only_takeoff(self,value):
        self.only_takeoff=value

    def start_auto_charge(self):
        # for pang.hy test
        # self.run_auto_charge = 1  # 是否启动自动化充电流程 0:否 1:是 (默认0:否)
        # self.fly_back = 1  # 是否飞机飞回 -1:未知 0:否 1:是 (默认-1:未知)
        # self.wait_charge_time = 15  # 执行充电间隔时间 默认900秒 15分钟
        while True:
            try:
                if self.configini.need_auto_charge:
                    self.logger.get_log().info(f"[AutoChargeControl]===启用自动化充电功能===")
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
                f"自动化充电流程执行 run_auto_charge = {self.run_auto_charge} fly_back = {self.fly_back} uuid_str = {self.uuid_str}  state = {self.wf_state.get_state()} battery_value = {self.wf_state.get_battery_value()} charge_num = {self.charge_num}")
            if self.run_auto_charge == 1:#启动充电
                if self.fly_back == 1:#飞机返回
                    self.logger.get_log().debug(f"[AutoChargeControl][是否飞机飞回状态]状态 是 -继续")
                    is_need_charge = self.isNeedCharge()  # 充电状态是否需要充电
                    # 判断是否需要执行充电
                    if is_need_charge:
                        self.logger.get_log().info(f"[AutoChargeControl]自动化充电流程-需要充电-流程开始-进行休眠")
                        keep_uuid = self.uuid_str  # 缓存并记录[充电编号]
                        time.sleep(self.wait_charge_time)  # 休眠，无人机降温中？？？？？？？？？？
                        self.logger.get_log().debug(f"[AutoChargeControl]自动化充电流程-需要充电-休眠唤醒")
                        # 如下判断考虑手动停止开启操作时，可能自动化正处在休眠之中的情况，故咋充电之前要进行二次判断
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
                                # if this_time_charge_num >= self.charge_max_num:  # 充电次数大于等于阀值
                                #     self.run_auto_charge = 0  # 设置 是否启动自动化充电流程 0:否
                                #     self.fly_back = -1  # 设置 是否飞机飞回 -1:未知
                                self.logger.get_log().info(
                                        f"[AutoChargeControl][告警]:warning:连续{self.charge_max_num}次充电发生异常")
                        else:
                            self.logger.get_log().debug(f"[AutoChargeControl]充电编号不一致 -结束")
                        self.logger.get_log().debug(f"[AutoChargeControl]自动化充电流程-需要充电-流程结束")
                    else:
                        self.logger.get_log().debug(f"[AutoChargeControl]自动化充电流程-无需start充电 -结束")
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
        state = self.wf_state.get_state()  # 当前充电状态，close/charging/standby/takeoff/outage/cool
        battery_value = self.wf_state.get_battery_value()  # 电池电量, 0/1/2/3/4/100 满电情况下为100
        if state == "close":
            if battery_value == "100":#满电飞走，又飞回来关机，后启动自动充电？？？？？？？？？？？？？？？无人机飞回后，一定把电池值设置为0
                # self.run_auto_charge = 0  # 设置 是否启动自动化充电流程 0:否
                # self.fly_back = -1  # 设置 是否飞机飞回 -1:未知
                self.reset_charge_num()  # 充电成功 充电次数计数器重置0
                self.logger.get_log().info(f"[AutoChargeControl][充满电]情况")
            elif battery_value == "0":
                is_charge = True
                self.logger.get_log().info(f"[AutoChargeControl][电量未知]情况")
            else:
                is_charge = True
                self.logger.get_log().info(f"[AutoChargeControl][未充电]情况")
        elif state == "takeoff":#如果手动开机了如何操作？
            if battery_value == "100" or self.only_takeoff==True:
                # self.run_auto_charge = 0  # 设置 是否启动自动化充电流程 0:否
                # self.fly_back = -1  # 设置 是否飞机飞回 -1:未知
                # self.reset_charge_num()  # 充电成功 充电次数计数器重置0
                self.logger.get_log().debug(f"[AutoChargeControl][充满电]情况")
            elif battery_value == "0":
                is_charge = True
                self.logger.get_log().debug(f"[AutoChargeControl][电量未知]情况")
            else:
                is_charge = True
                self.logger.get_log().debug(f"[AutoChargeControl][未充电]情况")
        elif state == "charging":
            self.logger.get_log().debug(f"[AutoChargeControl][充电中]情况")
        elif state == "standby":#下位机所有状态都会返回standby ok，standby 状态非常多
            is_charge = True
            self.logger.get_log().debug(f"[AutoChargeControl][待机启动充电]情况")
        elif state == "outage":
            self.logger.get_log().debug(f"[AutoChargeControl][充电箱断电]情况")
        elif state == "cool":
            self.logger.get_log().debug(f"[AutoChargeControl][电池冷却中]情况")
        else:
            is_charge = True
            self.logger.get_log().debug(f"[AutoChargeControl]无法识别的，启动充电[当前充电状态]:{state}")
        return is_charge

    '''
    执行充电指令
    '''

    def doCharge(self):  # TODO 执行充电指令(保留无线充电，但实际暂无此场景)
        # 常量
        recv_text = "Charge"  # 充电固定指令
        result = "chargeerror"  # 充电返回状态
        if not self.comstate_flag.get_charge_isused():
            self.comstate_flag.set_charge_used()
            try:
                if self.configini.get_charge_version() == "wfc":  # 无线充电
                    if self.configini.get_wfc_version() == 'V1.0':  # V1.0版本
                        WFC = WFCServer(self.wf_state, self.logger, self.configini)
                        result = WFC.operator_charge(recv_text)
                    elif self.configini.get_wfc_version() == 'V2.0':  # V2.0版本
                        if self.configini.wfc_double_connect == False:
                            WFC = WFCServerV2(self.wf_state, self.logger, self.configini)
                        else:
                            WFC = WFCServerV2Sender(self.wf_state, self.logger, self.comconfig)
                        result = WFC.operator_charge(recv_text)
                else:  # 触点充电
                    if self.configini.get_wlc_version() == "V1.0":
                        if self.configini.wlc_double_connect == True:  # 全双工通信
                            WFC = M300JCCServerSender(self.hangstate, self.wf_state, self.logger, self.comconfig)
                        else:
                            WFC = M300JCCServer(self.wf_state, self.logger, self.configini)
                        result = WFC.operator_charge(recv_text)
                    elif self.configini.get_wlc_version() == "V2.0":  # V2.0
                        WFC = M300JCCServerV2(self.hangstate, self.wf_state, self.logger, self.configini)
                        result = WFC.operator_charge(recv_text)
                    elif self.configini.get_wlc_version() == "V3.0":  # V3.0
                        WFC = M300JCCServerV3(self.hangstate, self.wf_state, self.logger, self.configini)
                        result = WFC.operator_charge(recv_text)
                self.comstate_flag.set_charge_free()
            except Exception as charex:
                self.comstate_flag.set_charge_free()
                result = "chargeerror"
        else:
            result = "busy"
            self.logger.get_log().info("自动充电，充电端口被占用，busy")
            result="chargeerror"
        return result
