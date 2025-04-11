import time
import WFCharge.WFState as WFState
import BASEUtile.Config as Config
import BASEUtile.HangarState as HangarState
import BASEUtile.BusinessConstant as BusinessConstant
import BASEUtile.OperateUtil as OperateUtil


class AutoChargeControl:
    """
    自动化充电线程,配置文件中开启充电
    """
    def __init__(self, logger):
        self._logger = logger  # 日志对象
        self._charge_max_num = 5  # 充电次数异常阀值，大于等于该阀值报异常
        self._def_sleep_time = 60  # 自动充电检查执行间隔 默认60秒
        self._wait_charge_time = 900  # 执行充电间隔时间 默认900秒 15分钟 TODO 考虑外部配置传入

    def start_auto_charge(self):

        while True:
            try:
                if Config.get_is_need_auto_charge():
                    self._logger.get_log().debug(f"[AutoChargeControl.start_auto_charge]===启用自动化充电功能===")
                    self.doAutoCharge()
                else:
                    self._logger.get_log().debug(f"[AutoChargeControl.start_auto_charge]===禁用自动化充电功能===")
                #  休眠
                time.sleep(self._def_sleep_time)
            except Exception as ex:
                self._logger.get_log().error(f"[AutoChargeControl.start_auto_charge]===自动化充电功能发生异常{ex}")
                continue

    def doAutoCharge(self):
        try:
            run_auto_charge = HangarState.get_run_auto_charge()
            self._logger.get_log().info(
                f"[AutoChargeControl.doAutoCharge]自动化充电流程-开始,run_auto_charge:{run_auto_charge},uuid_str:{HangarState.get_charge_uuid()},state:{WFState.get_battery_state()},battery_value:{WFState.get_battery_value()},charge_num:{HangarState.get_charge_num()}")
            if run_auto_charge == 1:
                is_need_charge = self.isNeedCharge()  # 充电状态是否需要充电
                # 判断是否需要执行充电
                if is_need_charge:
                    self._logger.get_log().info(
                        f"[AutoChargeControl.doAutoCharge]自动化充电流程-需要充电,进行休眠,休眠时间为:{self._wait_charge_time}秒")
                    keep_uuid = HangarState.get_charge_uuid()  # 缓存并记录[充电编号]
                    time.sleep(self._wait_charge_time)  # 休眠，无人机降温中
                    self._logger.get_log().debug(f"[AutoChargeControl.doAutoCharge]自动化充电流程-需要充电,休眠唤醒")
                    # 如下判断考虑手动停止开启操作时，可能自动化线程正处在休眠之中的情况，故充电之前要进行二次判断
                    run_auto_charge = HangarState.get_run_auto_charge()
                    if run_auto_charge == 0:
                        self._logger.get_log().debug(
                            f"[AutoChargeControl.doAutoCharge]自动化充电流程-结束,休眠唤醒后,二次判断不需要自动化充电,run_auto_charge:{run_auto_charge}")
                        return
                    if keep_uuid == HangarState.get_charge_uuid():
                        #  这里追加判断 二次判断充电状态是否需要充电
                        is_need_charge_again = self.isNeedCharge()  # 充电状态是否需要充电
                        if not is_need_charge_again:
                            self._logger.get_log().debug(
                                f"[AutoChargeControl.doAutoCharge]自动化充电流程-结束,休眠唤醒后,二次判断不需要自动化充电,is_need_charge_again:{is_need_charge_again}")
                            return
                        self._logger.get_log().info(f"[AutoChargeControl.doAutoCharge]自动化充电流程-执行充电指令")
                        charge_result = OperateUtil.operate_hangar("cp0000")
                        if charge_result == BusinessConstant.SUCCESS:
                            self._logger.get_log().info(f"[AutoChargeControl.doAutoCharge]自动化充电流程-执行充电指令成功")
                            HangarState.set_charge_num(0)  # 充电成功 充电次数计数器重置0
                        else:
                            self._logger.get_log().info(
                                f"[AutoChargeControl.doAutoCharge]自动化充电流程-执行充电指令失败,失败原因为:{charge_result}")
                            HangarState.add_charge_num_error()  # 充电次数计数器+1
                            charge_num = HangarState.get_charge_num()  # 充电次数
                            if charge_num >= self._charge_max_num:  # 充电次数大于等于阀值
                                HangarState.set_run_auto_charge(0)
                                self._logger.get_log().info(
                                    f"[AutoChargeControl.doAutoCharge]自动化充电流程-告警,连续{self._charge_max_num}次充电发生异常")
                    else:
                        self._logger.get_log().info(f"[AutoChargeControl.doAutoCharge]自动化充电流程-结束,充电编号不一致")
                else:
                    self._logger.get_log().info(
                        f"[AutoChargeControl.doAutoCharge]自动化充电流程-结束,无需充电,is_need_charge:{is_need_charge}")
            elif run_auto_charge == 0:
                self._logger.get_log().debug(
                    f"[AutoChargeControl.doAutoCharge]自动化充电流程-结束,未启动自动化充电,run_auto_charge:{run_auto_charge}")
            else:
                self._logger.get_log().debug(
                    f"[AutoChargeControl.doAutoCharge]自动化充电流程-结束,无法识别自动化充电状态,run_auto_charge:{run_auto_charge}")
        except Exception as e:
            self._logger.get_log().info(f"[AutoChargeControl.doAutoCharge]自动化充电流程-异常,异常信息为:{e}")

    def isNeedCharge(self):
        """
        是否需要充电
        """
        is_charge = False  # 是否需要充电
        state = WFState.get_battery_state()  # 当前充电状态，close/charging/standby/takeoff/outage
        battery_value = WFState.get_battery_value()  # 电池电量, 0/1/2/3/4/100 满电情况下为100
        if state == "close":  # 关机
            if battery_value == "100":
                HangarState.close_auto_charge()
                self._logger.get_log().debug(f"[AutoChargeControl.isNeedCharge]是否需要充电-满电情况,不需充电")
            # 如果是御3或者V1.0版本，开机充电，这个时候不能再启动充电？如果是降温的情况如何处理？如果是新版M300充电，如何处理
            else:  # 需要充电
                is_charge = True
                self._logger.get_log().debug(f"[AutoChargeControl.isNeedCharge]是否需要充电-需要充电,电量为:{battery_value}")
        elif state == "takeoff":  # 开机
            if battery_value == "100":
                HangarState.close_auto_charge()
                self._logger.get_log().debug(f"[AutoChargeControl.isNeedCharge]是否需要充电-满电情况,不需充电")
            else:
                is_charge = True
                self._logger.get_log().debug(f"[AutoChargeControl.isNeedCharge]是否需要充电-需要充电,电量为:{battery_value}")
        elif state == "charging":
            self._logger.get_log().debug(f"[AutoChargeControl.isNeedCharge]是否需要充电-充电中,不需再开启")
        elif state == "standby":
            self._logger.get_log().debug(f"[AutoChargeControl.isNeedCharge]是否需要充电-待机中,不开启充电")
        elif state == "outage":
            self._logger.get_log().debug(f"[AutoChargeControl.isNeedCharge]是否需要充电-充电箱断电，不开启充电")
        elif state == "cool":
            self._logger.get_log().debug(f"[AutoChargeControl.isNeedCharge]是否需要充电-电池冷却中,不开启充电")
        else:
            self._logger.get_log().debug(f"[AutoChargeControl.isNeedCharge]是否需要充电-无法识别的当前状态,当前状态为:{state}")
        return is_charge
