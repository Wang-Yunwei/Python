import BASEUtile.BusinessConstant as BusinessConstant
import BASEUtile.HangarState as HangarState
import SerialUsedStateFlag
import time
import BASEUtile.Config as Config
from WFCharge.WFCServer import WFCServer
from WFCharge.WFCServerV2 import WFCServerV2
from WFCharge.WFCServerV2Sender import WFCServerV2Sender
from WFCharge.JCCServerM300 import JCCServerM300
from WFCharge.JCCServerV2M300Single import JCCServerV2M300Single
from WFCharge.JCCServerM300Sender import JCCServerM300Sender
from WFCharge.JCCServerV3M300 import JCCServerV3M300
from WFCharge.JCCServerV4M350 import JCCServerV4M350
from WFCharge.JCCServerV5 import JCCServerV5
from WFCharge.JCCServerV6M350 import JCCServerV6M350
from Lift.TurnLift import TurnLift
from JKController.JKDoorServer import JKDoorServer
from JKController.LightController import LightController
from JKController.JKBarServer import JKBarServer
from AirCondition.AirConditionComputerCommon import AirConditionComputerCommon
from ShutterDoor.RollingShutterDoor import RollingShutterDoor
from ShutterDoor.ShadeWindow import ShadeWindow
from weather.UAVController import UAVController
from weather.OutLiftController import OutLiftController
import WFCharge.WFState as WFState
import threading
import weather.AlarmLightController as AlarmLightController
from Lift.UpdownLiftCommon import UpdownLiftCommon
from weather.AlarmController import AlarmController
import requests
import os

"""
机库单步操作==================================================start
"""


@AlarmLightController.AlarmLight
def step_scene_up_lift_700000():
    """
    升降台上升
    """
    def_success_result = "9700"  # 成功
    def_error_result = "9701"  # 默认异常
    def_overtime_result = "970c"  # 超时
    state_error_result = "9706"  # 状态异常
    used_error_result = "970d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_up_lift_700000]升降台上升-开始")
    # 门打开，可以上升
    if HangarState.get_hangar_door_state() != BusinessConstant.OPEN_STATE:
        BusinessConstant.LOGGER.get_log().info(
            f"[OperateUtil.step_scene_up_lift_700000]升降台上升-结束,异常信息为:门状态为:{HangarState.get_hangar_door_state()},不能上升")
        return state_error_result
    # elif HangarState.get_hangar_bar_state() != BusinessConstant.CLOSE_STATE:
    #     BusinessConstant.LOGGER.get_log().info(
    #         f"[OperateUtil.step_scene_up_lift_700000]升降台上升-异常,夹杆状态为{HangarState.get_hangar_bar_state()},不能上升")
    #     return state_error_result
    # 上升操作
    if SerialUsedStateFlag.get_is_used_serial_updown_lift() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_up_lift_700000]升降台上升,端口被占用")
        result = used_error_result
    else:
        init_lift_state = HangarState.get_updown_lift_state()
        try:
            HangarState.set_updown_lift_state(BusinessConstant.UPING_STATE)
            SerialUsedStateFlag.set_used_serial_updown_lift()
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            updownLift = UpdownLiftCommon(BusinessConstant.LOGGER)
            result = updownLift.up_lift()
            if result is None or result == "" or result == BusinessConstant.ERROR:
                result = def_error_result
            elif result == BusinessConstant.SUCCESS or result == def_success_result:  # 底层返回success，设置操作成功
                result = def_success_result
            elif result == BusinessConstant.OVERTIME:
                result = def_error_result
            # 状态设置
            if result == def_success_result:
                HangarState.set_updown_lift_state(BusinessConstant.UP_STATE)
            else:
                HangarState.set_updown_lift_state(init_lift_state)
        except Exception as ex:
            HangarState.set_updown_lift_state(init_lift_state)
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_up_lift_700000]升降台上升-异常,异常信息为:{ex}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_updown_lift()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_up_lift_700000]升降台下降-结束,返回结果为:{result}")
    return result


@AlarmLightController.AlarmLight
def step_scene_down_lift_710000():
    """
    升降台下降
    """
    def_success_result = "9710"  # 成功
    def_error_result = "9711"  # 默认异常
    def_overtime_result = "971c"  # 超时
    state_error_result = "9716"  # 状态异常
    used_error_result = "971d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_down_lift_710000]升降台下降-开始")
    # # 夹杆夹紧，可以下降
    # if HangarState.get_hangar_bar_state() != BusinessConstant.CLOSE_STATE:
    #     BusinessConstant.LOGGER.get_log().info(
    #         f"[OperateUtil.step_scene_down_lift_710000]升降台下降-异常,夹杆状态为{HangarState.get_hangar_bar_state()},不能下降")
    #     return state_error_result
    # 下降
    if SerialUsedStateFlag.get_is_used_serial_updown_lift() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_down_lift_710000]升降台下降,端口被占用")
        result = used_error_result
    else:
        init_lift_state = HangarState.get_updown_lift_state()
        try:
            HangarState.set_updown_lift_state(BusinessConstant.DOWNING_STATE)
            SerialUsedStateFlag.set_used_serial_updown_lift()
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            updownLift = UpdownLiftCommon(BusinessConstant.LOGGER)
            result = updownLift.down_lift()
            if result is None or result == "" or result == BusinessConstant.ERROR:
                result = def_error_result
            elif result == BusinessConstant.SUCCESS or result == def_success_result:  # 底层返回success，设置操作成功
                result = def_success_result
            elif result == BusinessConstant.OVERTIME:
                result = def_error_result
            # 状态设置
            if result == def_success_result:
                HangarState.set_updown_lift_state(BusinessConstant.DOWN_STATE)
            else:
                HangarState.set_updown_lift_state(init_lift_state)
        except Exception as ex:
            HangarState.set_updown_lift_state(init_lift_state)
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_down_lift_710000]升降台下降-异常,异常信息为:{ex}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_updown_lift()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_down_lift_710000]升降台下降-结束,返回结果为:{result}")
    return result


def step_scene_state_updown_lift_730000():
    """
    旋转台状态获取
    """
    def_success_result = "9730"  # 成功
    def_error_result = "9731"  # 默认异常
    state_up_result = "9734"  # 上升状态
    state_down_result = "9735"  # 下降状态
    used_error_result = "973d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_state_updown_lift_730000]升降台状态获取-开始")
    # 业务逻辑
    if SerialUsedStateFlag.get_is_used_serial_updown_lift() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_state_updown_lift_730000]升降台状态获取,端口被占用")
        result = used_error_result
    else:
        try:
            SerialUsedStateFlag.set_used_serial_updown_lift()
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            updownLift = UpdownLiftCommon(BusinessConstant.LOGGER)
            result = updownLift.get_lift_state()
            if result == state_up_result:
                HangarState.set_updown_lift_state(BusinessConstant.UP_STATE)
                result = def_success_result
            elif result == state_down_result:
                HangarState.set_updown_lift_state(BusinessConstant.DOWN_STATE)
                result = def_success_result
            elif result == BusinessConstant.SUCCESS or result == def_success_result:
                result = def_success_result
            else:
                result = def_error_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(
                f"[OperateUtil.step_scene_state_updown_lift_730000]升降台状态获取-异常,异常信息为:{str(ex)}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_updown_lift()
    BusinessConstant.LOGGER.get_log().info(
        f"[OperateUtil.step_scene_state_updown_lift_730000]升降台状态获取-结束,返回结果为:{result}")
    return result


@AlarmLightController.AlarmLight
def step_scene_reset_lift_720000():
    """
    升降台复位
    """
    def_success_result = "9720"  # 成功
    def_error_result = "9721"  # 默认异常
    def_overtime_result = "972c"  # 超时
    state_error_result = "9726"  # 状态异常
    used_error_result = "972d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_reset_lift_720000]升降台复位-开始")
    if SerialUsedStateFlag.get_is_used_serial_updown_lift() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_reset_lift_720000]升降台复位,端口被占用")
        result = used_error_result
    else:
        init_lift_state = HangarState.get_updown_lift_state()
        try:
            HangarState.set_updown_lift_state(BusinessConstant.DOWNING_STATE)
            SerialUsedStateFlag.set_used_serial_updown_lift()
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            updownLift = UpdownLiftCommon(BusinessConstant.LOGGER)
            result = updownLift.reset_lift()
            if result is None or result == "" or result == BusinessConstant.ERROR:
                result = def_error_result
            elif result == BusinessConstant.SUCCESS:  # 底层返回success，设置操作成功
                result = def_success_result
            elif result == BusinessConstant.OVERTIME:
                result = def_error_result
            # 状态设置
            if result == def_success_result:
                HangarState.set_updown_lift_state(BusinessConstant.DOWN_STATE)
            else:
                HangarState.set_updown_lift_state(init_lift_state)
        except Exception as ex:
            HangarState.set_updown_lift_state(init_lift_state)
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_reset_lift_720000]升降台复位-异常,异常信息为:{ex}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_updown_lift()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_reset_lift_720000]升降台复位-结束,返回结果为:{result}")
    return result


def step_scene_out_up_lift_740000():
    """
    外挂升降台上升
    """
    def_success_result = "9740"  # 成功
    def_error_result = "9741"  # 默认异常
    used_error_result = "974d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_out_up_lift_740000]升降台上升-开始")
    # 上升操作
    if SerialUsedStateFlag.get_is_used_serial_updown_lift() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_out_up_lift_740000]升降台上升,端口被占用")
        result = used_error_result
    else:
        try:
            SerialUsedStateFlag.set_used_serial_updown_lift()
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            updownLift = OutLiftController(BusinessConstant.LOGGER)
            result = updownLift.lift_up()
            if result is None or result == "" or result == BusinessConstant.ERROR:
                result = def_error_result
            elif result == BusinessConstant.SUCCESS or result == def_success_result:  # 底层返回success，设置操作成功
                HangarState.set_out_lift_state(BusinessConstant.UP_STATE)
                result = def_success_result
            elif result == BusinessConstant.OVERTIME:
                result = def_error_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_out_up_lift_740000]升降台上升-异常,异常信息为:{ex}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_updown_lift()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_out_up_lift_740000]升降台下降-结束,返回结果为:{result}")
    return result


def step_scene_out_down_lift_750000():
    """
    外挂升降台下降
    """
    def_success_result = "9740"  # 成功
    def_error_result = "9741"  # 默认异常
    used_error_result = "974d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_out_down_lift_750000]升降台下降-开始")
    # 上升操作
    if SerialUsedStateFlag.get_is_used_serial_updown_lift() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_out_down_lift_750000]升降台下降,端口被占用")
        result = used_error_result
    else:
        try:
            SerialUsedStateFlag.set_used_serial_updown_lift()
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            updownLift = OutLiftController(BusinessConstant.LOGGER)
            result = updownLift.lift_down()
            if result is None or result == "" or result == BusinessConstant.ERROR:
                result = def_error_result
            elif result == BusinessConstant.SUCCESS or result == def_success_result:  # 底层返回success，设置操作成功
                HangarState.set_out_lift_state(BusinessConstant.DOWN_STATE)
                result = def_success_result
            elif result == BusinessConstant.OVERTIME:
                result = def_error_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_out_down_lift_750000]升降台下降-异常,异常信息为:{ex}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_updown_lift()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_out_down_lift_750000]升降台下降-结束,返回结果为:{result}")
    return result


@AlarmLightController.AlarmLight
def step_scene_turn_lift_800000():
    """
    旋转台旋转
    """
    result = step_scene_turn_lift_800000_base()
    return result


def step_scene_turn_lift_800000_base():
    """
    旋转台旋转
    """
    def_success_result = "9800"  # 成功
    def_error_result = "9801"  # 默认异常
    state_error_result = "9806"  # 状态异常
    used_error_result = "980d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_turn_lift_800000_base]旋转台旋转-开始")
    # 升降台在下面并且夹杆松开，不可以旋转
    if HangarState.get_updown_lift_state() == BusinessConstant.DOWN_STATE and HangarState.get_hangar_bar_state() == BusinessConstant.OPEN_STATE:
        BusinessConstant.LOGGER.get_log().info(
            f"[OperateUtil.step_scene_turn_lift_800000_base]旋转台旋转-结束,异常信息为:夹杆状态为:{HangarState.get_hangar_bar_state()},升降台状态:{HangarState.get_updown_lift_state()},不能旋转")
        return state_error_result
    # elif HangarState.get_updown_lift_state() != BusinessConstant.DOWN_STATE:
    #     BusinessConstant.LOGGER.get_log().info(
    #         f"[OperateUtil.step_scene_turn_lift_800000]旋转台旋转-异常,升降台为{HangarState.get_updown_lift_state()},不能旋转")
    #     return state_error_result
    # 旋转操作
    if SerialUsedStateFlag.get_is_used_serial_turn_lift() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_turn_lift_800000_base]旋转台旋转,端口被占用")
        result = used_error_result
    else:
        init_lift_state = HangarState.get_turn_lift_state()
        try:
            HangarState.set_turn_lift_state(BusinessConstant.TURNING_STATE)
            SerialUsedStateFlag.set_used_serial_turn_lift()
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            turnLift = TurnLift(BusinessConstant.LOGGER)
            result = turnLift.turn_lift()
            if result == BusinessConstant.SUCCESS or result == def_success_result:
                result = def_success_result
            elif result == BusinessConstant.BUSY:
                result = used_error_result
            elif result == BusinessConstant.ERROR:
                result = def_error_result
            # 状态设置
            if result == def_success_result:
                HangarState.set_turn_lift_state(BusinessConstant.TURN_STATE)
            else:
                HangarState.set_turn_lift_state(init_lift_state)
        except Exception as ex:
            HangarState.set_turn_lift_state(init_lift_state)
            BusinessConstant.LOGGER.get_log().info(
                f"[OperateUtil.step_scene_turn_lift_800000_base]旋转台旋转-异常,异常信息为:{str(ex)}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_turn_lift()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_turn_lift_800000_base]旋转台旋转-结束,返回结果为:{result}")
    return result


@AlarmLightController.AlarmLight
def step_scene_back_lift_810000():
    """
    旋转台回位
    """
    result = step_scene_back_lift_810000_base()
    return result


def step_scene_back_lift_810000_base():
    """
    旋转台回位
    """
    def_success_result = "9810"  # 成功
    def_error_result = "9811"  # 默认异常
    state_error_result = "9816"  # 默认异常
    command_error_result = "981a"  # 不支持方法异常
    used_error_result = "981d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_back_lift_810000_base]旋转台回位-开始")
    # 升降台在下面并且夹杆松开，不可以旋转
    if HangarState.get_updown_lift_state() == BusinessConstant.DOWN_STATE and HangarState.get_hangar_bar_state() == BusinessConstant.OPEN_STATE:
        BusinessConstant.LOGGER.get_log().info(
            f"[OperateUtil.step_scene_back_lift_810000_base]旋转台回位-结束,异常信息为:夹杆状态为:{HangarState.get_hangar_bar_state()},升降台状态:{HangarState.get_updown_lift_state()},不能旋转")
        return state_error_result
    # elif HangarState.get_updown_lift_state() != BusinessConstant.DOWN_STATE:
    #     BusinessConstant.LOGGER.get_log().info(
    #         f"[OperateUtil.step_scene_back_lift_810000]旋转台回位-异常,升降台为{HangarState.get_updown_lift_state()},不能旋转")
    #     return state_error_result
    # 旋转操作
    if SerialUsedStateFlag.get_is_used_serial_turn_lift() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_back_lift_810000_base]旋转台回位,端口被占用")
        result = used_error_result
    else:
        init_lift_state = HangarState.get_turn_lift_state()
        try:
            HangarState.set_turn_lift_state(BusinessConstant.BACKING_STATE)
            SerialUsedStateFlag.set_used_serial_turn_lift()
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            turnLift = TurnLift(BusinessConstant.LOGGER)
            result = turnLift.back_lift()
            if result == BusinessConstant.SUCCESS or result == def_success_result:
                result = def_success_result
            elif result == BusinessConstant.BUSY:
                result = used_error_result
            elif result == BusinessConstant.ERROR:
                result = def_error_result
            # 状态设置
            if result == def_success_result:
                HangarState.set_turn_lift_state(BusinessConstant.BACK_STATE)
            else:
                HangarState.set_turn_lift_state(init_lift_state)
        except Exception as ex:
            HangarState.set_turn_lift_state(init_lift_state)
            BusinessConstant.LOGGER.get_log().info(
                f"[OperateUtil.step_scene_back_lift_810000_base]旋转台回位-异常,异常信息为:{str(ex)}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_turn_lift()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_back_lift_810000_base]旋转台回位-结束,返回结果为:{result}")
    return result


def step_scene_state_turn_lift_830000():
    """
    旋转台状态获取
    """
    def_success_result = "9830"  # 成功
    def_error_result = "9831"  # 默认异常
    state_turn_result = "9834"  # 旋转状态
    state_back_result = "9835"  # 回位状态
    used_error_result = "983d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_get_lift_830000]旋转台状态获取-开始")
    # 业务逻辑
    if SerialUsedStateFlag.get_is_used_serial_turn_lift() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_get_lift_830000]旋转台状态获取,端口被占用")
        result = used_error_result
    else:
        try:
            SerialUsedStateFlag.set_used_serial_turn_lift()
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            turnLift = TurnLift(BusinessConstant.LOGGER)
            result = turnLift.get_lift_state()
            if result == state_turn_result:
                HangarState.set_turn_lift_state(BusinessConstant.TURN_STATE)
                result = def_success_result
            elif result == state_back_result:
                HangarState.set_turn_lift_state(BusinessConstant.BACK_STATE)
                result = def_success_result
            elif result == BusinessConstant.SUCCESS or result == def_success_result:
                result = def_success_result
            else:
                result = def_error_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(
                f"[OperateUtil.step_scene_get_lift_830000]旋转台状态获取-异常,异常信息为:{str(ex)}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_turn_lift()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_get_lift_830000]旋转台状态获取-结束,返回结果为:{result}")
    return result


@AlarmLightController.AlarmLight
def step_scene_door_open_140000():
    """
    机库开门
    """
    #  常量/参数部分
    recv_text = "140000"  # 下发指令
    def_success_result = "9140"
    def_error_result = "9141"  # 默认异常
    command_error_result = "914a"  # 不支持方法异常
    used_error_result = "914d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_door_open_140000]机库门打开-开始")
    #  业务逻辑部分
    if SerialUsedStateFlag.get_is_used_serial_door() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_door_open_140000]机库门打开,端口被占用")
        result = used_error_result
    else:
        # 门初始状态
        init_door_state = HangarState.get_hangar_door_state()
        try:
            # 开门中状态设置
            HangarState.set_hangar_door_state(BusinessConstant.OPENING_STATE)
            SerialUsedStateFlag.set_used_serial_door()  # 串口设置使用中
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            jkDoorServer = JKDoorServer(BusinessConstant.LOGGER)  # 控制对象
            result = jkDoorServer.open_door()
            if result is None or result == "" or result == BusinessConstant.ERROR:
                result = def_error_result
            elif result == def_success_result or result == BusinessConstant.SUCCESS:
                result = def_success_result
            elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
                result = def_error_result
            elif result.endswith("a") and result.startswith("9"):
                result = command_error_result
            # 状态设置
            if result == def_success_result:
                HangarState.set_hangar_door_state(BusinessConstant.OPEN_STATE)
            else:
                HangarState.set_hangar_door_state(init_door_state)
            # # 开启夜灯线程
            # threading.Thread(target=step_scene_night_light_open_400000, args=()).start()
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_door_open_140000]机库门打开-异常,异常信息为:{ex}")
            HangarState.set_hangar_door_state(init_door_state)
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_door()
            # 开启夜灯
            step_scene_night_light_open_400000()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_door_open_140000]机库门打开-结束,返回结果为:{result}")
    return result


@AlarmLightController.AlarmLight
def step_scene_door_close_150000():
    """
    机库关门
    """
    #  常量/参数部分
    recv_text = "150000"  # 下发指令
    def_success_result = "9150"
    def_error_result = "9151"  # 默认异常
    state_error_result = "9156"  # 状态异常
    command_error_result = "915a"  # 不支持方法异常
    used_error_result = "915d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_door_close_150000]机库门关闭-开始")
    # M350小机库,带旋转台和升降台
    if Config.get_hangar_version() == "wk_nest_02":
        # 升降台在下面，才可以关门
        if HangarState.get_updown_lift_state() != BusinessConstant.DOWN_STATE:
            BusinessConstant.LOGGER.get_log().info(
                f"[OperateUtil.step_scene_door_close_150000]机库门关闭-结束,异常信息为:升降台状态为:{HangarState.get_updown_lift_state()},不能关门")
            return state_error_result
        # else:
        # # 关门时调用一次旋转或回位动作，防止忘记收桨
        # if HangarState.get_turn_lift_state() == BusinessConstant.BACK_STATE:
        #     result = step_scene_turn_lift_800000_base()
        # else:
        #     result = step_scene_back_lift_810000_base()
        # if result == "9800" or result == "9810":
        #     BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_door_close_150000]机库门关闭-旋转台旋转完成,返回结果为:{result}")
        # else:
        #     BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_door_close_150000]机库门关闭-结束,旋转台旋转异常,旋转返回结果为:{def_error_result}")
        #     return def_error_result
    #  业务逻辑部分
    if SerialUsedStateFlag.get_is_used_serial_door() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_door_close_150000]机库门关闭,端口被占用")
        result = used_error_result
    else:
        # 门初始状态
        init_door_state = HangarState.get_hangar_door_state()
        try:
            # 关门中状态
            HangarState.set_hangar_door_state(BusinessConstant.CLOSING_STATE)
            SerialUsedStateFlag.set_used_serial_door()  # 串口设置使用中
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            jkDoorServer = JKDoorServer(BusinessConstant.LOGGER)  # 控制对象
            result = jkDoorServer.close_door()
            if result is None or result == "" or result == BusinessConstant.ERROR:
                result = def_error_result
            elif result == def_success_result or result == BusinessConstant.SUCCESS:
                result = def_success_result
            elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
                result = def_error_result
            elif result.endswith("a") and result.startswith("9"):
                result = command_error_result
            else:
                result = def_error_result
            # 状态设置
            if result == def_success_result:
                HangarState.set_hangar_door_state(BusinessConstant.CLOSE_STATE)
            else:
                HangarState.set_hangar_door_state(init_door_state)
            # # 关闭夜灯线程
            # threading.Thread(target=step_scene_night_light_close_410000, args=()).start()
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_door_close_150000]机库门关闭-异常,异常信息为:{ex}")
            HangarState.set_hangar_door_state(init_door_state)
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_door()
            # 关闭夜灯
            step_scene_night_light_close_410000()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_door_close_150000]机库门关闭-结束,返回结果为:{result}")
    return result


def step_scene_door_state_170000():
    """
    机库门状态
    """
    #  常量/参数部分
    recv_text = "170000"  # 下发指令
    def_success_result = "9170"
    def_error_result = "9171"  # 默认异常
    state_open_result = "9174"
    state_close_result = "9175"
    used_error_result = "917d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_door_state_170000]机库门状态获取-开始")
    #  业务逻辑部分
    if SerialUsedStateFlag.get_is_used_serial_door() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_door_state_170000]机库门状态获取,端口被占用")
        result = used_error_result
    else:
        try:
            SerialUsedStateFlag.set_used_serial_door()  # 串口设置使用中
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            jkDoorServer = JKDoorServer(BusinessConstant.LOGGER)  # 控制对象
            result = jkDoorServer.get_door_state()
            if result == state_open_result:
                HangarState.set_hangar_door_state(BusinessConstant.OPEN_STATE)
                result = def_success_result
            elif result == state_close_result:
                HangarState.set_hangar_door_state(BusinessConstant.CLOSE_STATE)
                result = def_success_result
            elif result is None or result == "" or result == BusinessConstant.ERROR:
                result = def_error_result
            elif result == def_success_result or result == BusinessConstant.SUCCESS:
                result = def_success_result
            else:
                result = def_error_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_door_state_170000]机库门状态获取-异常,异常信息为:{ex}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_door()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_door_state_170000]机库门状态获取-结束,返回结果为:{result}")
    return result


@AlarmLightController.AlarmLight
def step_scene_bar_close_2e10002000():
    """
    推杆夹紧
    """
    #  常量/参数部分
    recv_text = "2e10002000"  # 下发指令
    def_success_result = "92e0"
    def_error_result = "92e1"  # 默认异常
    command_error_result = "92ea"  # 不支持方法异常
    used_error_result = "92ed"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_bar_close_2e10002000]推杆夹紧-开始")
    #  业务逻辑部分
    if SerialUsedStateFlag.get_is_used_serial_bar() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_bar_close_2e10002000]推杆夹紧,端口被占用")
        result = used_error_result
    else:
        # 夹杆初始状态
        init_bar_state = HangarState.get_hangar_bar_state()
        try:
            HangarState.set_hangar_bar_state(BusinessConstant.CLOSING_STATE)
            SerialUsedStateFlag.set_used_serial_bar()  # 串口设置使用中
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            jkBarServer = JKBarServer(BusinessConstant.LOGGER)  # 控制对象
            result = jkBarServer.close_bar()
            if result is None or result == "" or result == BusinessConstant.ERROR:
                result = def_error_result
            elif result == def_success_result or result == BusinessConstant.SUCCESS:
                result = def_success_result
            elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
                result = def_error_result
            elif result.endswith("a") and result.startswith("9"):
                result = command_error_result
            # 状态设置
            if result == def_success_result:
                # 此处只设置总推杆状态为close
                HangarState.set_hangar_td_bar_state(BusinessConstant.CLOSE_STATE)
                HangarState.set_hangar_lr_bar_state(BusinessConstant.CLOSE_STATE)
                HangarState.set_hangar_bar_state(BusinessConstant.CLOSE_STATE)
                # 配置项td_bar：推杆夹紧后，前后推杆打开
                if Config.get_is_td_bar() is True:
                    HangarState.set_hangar_td_bar_state(BusinessConstant.OPEN_STATE)
            else:
                HangarState.set_hangar_bar_state(init_bar_state)
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_bar_close_2e10002000]推杆夹紧-异常,异常信息为:{ex}")
            HangarState.set_hangar_bar_state(init_bar_state)
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_bar()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_bar_close_2e10002000]推杆夹紧-结束,返回结果为:{result}")
    return result


@AlarmLightController.AlarmLight
def step_scene_bar_open_2f10002000():
    """
    推杆打开
    """
    #  常量/参数部分
    recv_text = "2f10002000"  # 下发指令
    def_success_result = "92f0"
    def_error_result = "92f1"  # 默认异常
    command_error_result = "92fa"  # 不支持方法异常
    used_error_result = "92fd"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_bar_open_2f10002000]推杆打开-开始")
    if SerialUsedStateFlag.get_is_used_serial_bar() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_bar_open_2f10002000]推杆打开,端口被占用")
        result = used_error_result
    else:
        # 夹杆初始状态
        init_bar_state = HangarState.get_hangar_bar_state()
        try:
            HangarState.set_hangar_bar_state(BusinessConstant.OPENING_STATE)
            SerialUsedStateFlag.set_used_serial_bar()  # 串口设置使用中
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            jkBarServer = JKBarServer(BusinessConstant.LOGGER)  # 控制对象
            result = jkBarServer.open_bar()
            if result is None or result == "" or result == BusinessConstant.ERROR:
                result = def_error_result
            elif result == def_success_result or result == BusinessConstant.SUCCESS or result == "9500":
                result = def_success_result
            elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
                result = def_error_result
            elif result.endswith("a") and result.startswith("9"):
                result = command_error_result
            else:
                result = def_error_result
            # 状态设置
            if result == def_success_result:
                HangarState.set_hangar_lr_bar_state(BusinessConstant.OPEN_STATE)
                HangarState.set_hangar_td_bar_state(BusinessConstant.OPEN_STATE)
                HangarState.set_hangar_bar_state(BusinessConstant.OPEN_STATE)
            else:
                HangarState.set_hangar_bar_state(init_bar_state)
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_bar_open_2f10002000]推杆打开-异常,异常信息为:{ex}")
            HangarState.set_hangar_bar_state(init_bar_state)
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_bar()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_bar_open_2f10002000]推杆打开-结束,返回结果为:{result}")
    return result


@AlarmLightController.AlarmLight
def step_scene_td_bar_open_2f2000():
    """
    前后推杆打开
    """
    #  常量/参数部分
    recv_text = "2f2000"  # 下发指令
    def_success_result = "92f0"
    def_error_result = "92f1"  # 默认异常
    command_error_result = "92fa"  # 不支持方法异常
    used_error_result = "92fd"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_bar_open_2f2000]前后推杆打开-开始")
    if SerialUsedStateFlag.get_is_used_serial_bar() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_bar_open_2f2000]前后推杆打开,端口被占用")
        result = used_error_result
    else:
        # 夹杆初始状态
        init_td_bar_state = HangarState.get_hangar_td_bar_state()
        try:
            HangarState.set_hangar_td_bar_state(BusinessConstant.OPENING_STATE)
            SerialUsedStateFlag.set_used_serial_bar()  # 串口设置使用中
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            jkBarServer = JKBarServer(BusinessConstant.LOGGER)  # 控制对象
            result = jkBarServer.open_td_bar()
            if result is None or result == "" or result == BusinessConstant.ERROR:
                result = def_error_result
            elif result == def_success_result or result == BusinessConstant.SUCCESS:
                result = def_success_result
            elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
                result = def_error_result
            elif result.endswith("a") and result.startswith("9"):
                result = command_error_result
            else:
                result = def_error_result
            # 状态设置
            if result == def_success_result:
                HangarState.set_hangar_td_bar_state(BusinessConstant.OPEN_STATE)
            else:
                HangarState.set_hangar_td_bar_state(init_td_bar_state)
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_bar_open_2f2000]前后推杆打开-异常,异常信息为:{ex}")
            HangarState.set_hangar_td_bar_state(init_td_bar_state)
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_bar()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_bar_open_2f2000]前后推杆打开-结束,返回结果为:{result}")
    return result


@AlarmLightController.AlarmLight
def step_scene_bar_reset_500000():
    """
    推杆复位(打开)
    """
    #  常量/参数部分
    recv_text = "500000"  # 下发指令
    def_success_result = "9500"
    def_error_result = "9501"  # 默认异常
    command_error_result = "950a"  # 不支持方法异常
    used_error_result = "950d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_bar_reset_500000]推杆复位-开始")
    if SerialUsedStateFlag.get_is_used_serial_bar() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_bar_reset_500000]推杆复位,端口被占用")
        result = used_error_result
    else:
        # 夹杆初始状态
        init_bar_state = HangarState.get_hangar_bar_state()
        try:
            HangarState.set_hangar_bar_state(BusinessConstant.OPENING_STATE)
            SerialUsedStateFlag.set_used_serial_bar()  # 串口设置使用中
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            jkBarServer = JKBarServer(BusinessConstant.LOGGER)  # 控制对象
            result = jkBarServer.reset_bar()
            if result is None or result == "" or result == BusinessConstant.ERROR:
                result = def_error_result
            elif result == def_success_result or result == BusinessConstant.SUCCESS:
                result = def_success_result
            elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
                result = def_error_result
            elif result.endswith("a") and result.startswith("9"):
                result = command_error_result
            else:
                result = def_error_result
            # 状态设置
            if result == def_success_result:
                HangarState.set_hangar_td_bar_state(BusinessConstant.OPEN_STATE)
                HangarState.set_hangar_lr_bar_state(BusinessConstant.OPEN_STATE)
                HangarState.set_hangar_bar_state(BusinessConstant.OPEN_STATE)
            else:
                HangarState.set_hangar_bar_state(init_bar_state)
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_bar_reset_500000]推杆复位-异常,异常信息为:{ex}")
            HangarState.set_hangar_bar_state(init_bar_state)
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_bar()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_bar_reset_500000]推杆复位-结束,返回结果为:{result}")
    return result


def step_scene_bar_state_2g0000():
    """
    推杆状态获取
    """
    #  常量/参数部分
    recv_text = "2g0000"  # 下发指令
    def_success_result = "92g0"
    def_error_result = "92g1"  # 默认异常
    state_open_result = "92g4"
    state_close_result = "92g5"
    used_error_result = "92gd"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_bar_state_2g0000]推杆状态获取-开始")
    if SerialUsedStateFlag.get_is_used_serial_bar() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_bar_state_2g0000]推杆状态获取,端口被占用")
        result = used_error_result
    else:
        try:
            SerialUsedStateFlag.set_used_serial_bar()  # 串口设置使用中
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            jkBarServer = JKBarServer(BusinessConstant.LOGGER)  # 控制对象
            result = jkBarServer.get_bar_state()
            if result == state_open_result:
                HangarState.set_hangar_bar_state(BusinessConstant.OPEN_STATE)
                HangarState.set_hangar_td_bar_state(BusinessConstant.OPEN_STATE)
                HangarState.set_hangar_lr_bar_state(BusinessConstant.OPEN_STATE)
                result = def_success_result
            elif result == state_close_result:
                HangarState.set_hangar_bar_state(BusinessConstant.CLOSE_STATE)
                HangarState.set_hangar_td_bar_state(BusinessConstant.CLOSE_STATE)
                HangarState.set_hangar_lr_bar_state(BusinessConstant.CLOSE_STATE)
                result = def_success_result
            elif result is None or result == "" or result == BusinessConstant.ERROR:
                result = def_error_result
            elif result == def_success_result or result == BusinessConstant.SUCCESS:
                result = def_success_result
            else:
                result = def_error_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_bar_state_2g0000]推杆状态获取-异常,异常信息为:{ex}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_bar()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_bar_state_2g0000]推杆状态获取-结束,返回结果为:{result}")
    return result


@AlarmLightController.AlarmLight
def step_scene_air_open_300000():
    """
    打开空调
    """
    #  常量/参数部分
    recv_text = "300000"  # 下发指令
    def_success_result = "9300"
    def_error_result = "9301"  # 默认异常
    command_error_result = "930a"  # 不支持方法异常
    used_error_result = "930d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_air_open_300000]空调打开-开始")
    if SerialUsedStateFlag.get_is_used_serial_weather() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_air_open_300000]空调打开,端口被占用")
        result = used_error_result
    else:
        try:
            SerialUsedStateFlag.set_used_serial_weather()  # 串口设置使用中
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            airConditionComputer = AirConditionComputerCommon(BusinessConstant.LOGGER)  # 控制对象
            result = airConditionComputer.openAircondition()
            if result is None or result == "" or result == BusinessConstant.ERROR:
                result = def_error_result
            elif result == def_success_result or result == BusinessConstant.SUCCESS:
                HangarState.set_air_condition_state(BusinessConstant.OPEN_STATE)
                result = def_success_result
            elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
                result = def_error_result
            elif result.endswith("a") and result.startswith("9"):
                result = command_error_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_air_open_300000]空调打开-异常,异常信息为:{ex}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_weather()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_air_open_300000]空调打开-结束,返回结果为:{result}")
    return result


@AlarmLightController.AlarmLight
def step_scene_air_close_310000():
    """
    关闭空调
    """
    #  常量/参数部分
    recv_text = "310000"  # 下发指令
    def_success_result = "9310"
    def_error_result = "9311"  # 默认异常
    command_error_result = "931a"  # 不支持方法异常
    used_error_result = "931d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_air_close_310000]空调关闭-开始")
    if SerialUsedStateFlag.get_is_used_serial_weather() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_air_close_310000]空调关闭,端口被占用")
        result = used_error_result
    else:
        try:
            SerialUsedStateFlag.set_used_serial_weather()  # 串口设置使用中
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            airConditionComputer = AirConditionComputerCommon(BusinessConstant.LOGGER)  # 控制对象
            result = airConditionComputer.closeAircondition()
            if result is None or result == "" or result == BusinessConstant.ERROR:
                result = def_error_result
            elif result == def_success_result or result == BusinessConstant.SUCCESS:
                HangarState.set_air_condition_state(BusinessConstant.CLOSE_STATE)
                result = def_success_result
            elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
                result = def_error_result
            elif result.endswith("a") and result.startswith("9"):
                result = command_error_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_air_close_310000]空调关闭-异常,异常信息为:{ex}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_weather()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_air_close_310000]空调关闭-结束,返回结果为:{result}")
    return result


def step_scene_night_light_open_400000():
    """
    机库夜灯打开
    """
    #  常量/参数部分
    recv_text = "400000"  # 下发指令
    def_success_result = "9400"
    def_error_result = "9401"  # 默认异常
    command_error_result = "940a"  # 不支持方法异常
    used_error_result = "940d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_night_light_open_400000]机库夜灯打开-开始")
    #  业务逻辑部分
    # time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)  # 等待时间原因：在打开机库门时，同时需要开灯线程，等待时间，防止端口被锁，无法处理
    if SerialUsedStateFlag.get_is_used_serial_door() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_night_light_open_400000]机库夜灯打开,端口被占用")
        result = used_error_result
    else:
        try:
            SerialUsedStateFlag.set_used_serial_door()  # 串口设置使用中
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            lightController = LightController(BusinessConstant.LOGGER)  # 控制对象
            result = lightController.open_light()
            if result is None or result == "" or result == BusinessConstant.ERROR:
                result = def_error_result
            elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
                result = def_error_result
            elif result.endswith("a") and result.startswith("9"):
                result = command_error_result
            elif result == def_success_result or result == BusinessConstant.SUCCESS:
                HangarState.set_night_light_state(BusinessConstant.OPEN_STATE)
                result = def_success_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(
                f"[OperateUtil.step_scene_night_light_open_400000]机库夜灯打开-异常,异常信息为:{ex}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_door()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_night_light_open_400000]机库夜灯打开-结束,返回结果为:{result}")
    return result


def step_scene_night_light_close_410000():
    """
    机库夜灯关闭
    """
    #  常量/参数部分
    recv_text = "410000"  # 下发指令
    def_success_result = "9410"
    def_error_result = "9411"  # 默认异常
    command_error_result = "941a"  # 不支持方法异常
    used_error_result = "941d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_night_light_close_410000]机库夜灯关闭-开始")
    #  业务逻辑部分
    time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)  # 等待时间原因：在关闭机库门时，同时需要关灯线程，等待时间，防止端口被锁，无法处理
    if SerialUsedStateFlag.get_is_used_serial_door() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_night_light_close_410000]机库夜灯关闭,端口被占用")
        result = used_error_result
    else:
        try:
            SerialUsedStateFlag.set_used_serial_door()  # 串口设置使用中
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            lightController = LightController(BusinessConstant.LOGGER)  # 控制对象
            result = lightController.close_light()
            if result is None or result == "" or result == BusinessConstant.ERROR:
                result = def_error_result
            elif not result.startswith("9"):  # 过滤底层返回error等非标的情况
                result = def_error_result
            elif result.endswith("a") and result.startswith("9"):
                result = command_error_result
            elif result == def_success_result or result == BusinessConstant.SUCCESS:
                HangarState.set_night_light_state(BusinessConstant.CLOSE_STATE)
                result = def_success_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(
                f"[OperateUtil.step_scene_night_light_close_410000]机库夜灯关闭-异常,异常信息为:{ex}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_door()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_night_light_close_410000]机库夜灯关闭-结束,返回结果为:{result}")
    return result


def step_scene_alarm_light_close_420000():
    """
    警示灯关闭
    """
    #  常量/参数部分
    recv_text = "420000"  # 下发指令
    def_success_result = "9420"
    def_error_result = "9421"  # 默认异常
    used_error_result = "942d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_alarm_light_close_420000]警示灯关闭-开始")
    #  业务逻辑部分
    if SerialUsedStateFlag.get_is_used_serial_gps() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_alarm_light_close_420000]警示灯关闭,端口被占用")
        result = used_error_result
    else:
        try:
            SerialUsedStateFlag.set_used_serial_gps()  # 串口设置使用中
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            result = AlarmLightController.open_green_light()  # 控制对象
            if result is None or result == "" or result == BusinessConstant.ERROR:
                result = def_error_result
            elif result == def_success_result or result == BusinessConstant.SUCCESS:
                result = def_success_result
            else:
                result = def_error_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(
                f"[OperateUtil.step_scene_alarm_light_close_420000]警示灯关闭-异常,异常信息为:{ex}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_gps()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_alarm_light_close_420000]警示灯关闭-结束,返回结果为:{result}")
    return result


def step_scene_alarm_green_light_open_430000():
    """
    警示灯绿灯开启
    """
    #  常量/参数部分
    recv_text = "430000"  # 下发指令
    def_success_result = "9430"
    def_error_result = "9431"  # 默认异常
    used_error_result = "943d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_alarm_green_light_open_430000]警示绿灯打开-开始")
    #  业务逻辑部分
    if SerialUsedStateFlag.get_is_used_serial_gps() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_alarm_green_light_open_430000]警示绿灯打开,端口被占用")
        result = used_error_result
    else:
        try:
            SerialUsedStateFlag.set_used_serial_gps()  # 串口设置使用中
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            result = AlarmLightController.open_green_light()  # 控制对象
            if result is None or result == "" or result == BusinessConstant.ERROR:
                result = def_error_result
            elif result == def_success_result or result == BusinessConstant.SUCCESS:
                result = def_success_result
            else:
                result = def_error_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(
                f"[OperateUtil.step_scene_alarm_green_light_open_430000]警示绿灯打开-异常,异常信息为:{ex}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_gps()
    BusinessConstant.LOGGER.get_log().info(
        f"[OperateUtil.step_scene_alarm_green_light_open_430000]警示绿灯打开-结束,返回结果为:{result}")
    return result


def step_scene_alarm_controller_open_460000():
    """
    警示灯打开
    """
    #  常量/参数部分
    recv_text = "460000"  # 下发指令
    def_success_result = "9460"
    def_error_result = "9461"  # 默认异常
    command_error_result = "946a"  # 不支持方法异常
    used_error_result = "946d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_alarm_controller_open_460000]警示灯打开-开始")
    #  业务逻辑部分
    # time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)  # 等待时间原因：在打开机库门时，同时需要开灯线程，等待时间，防止端口被锁，无法处理
    if SerialUsedStateFlag.get_is_used_serial_alarm_controller() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_alarm_controller_open_460000]警示灯打开,端口被占用")
        result = used_error_result
    else:
        try:
            SerialUsedStateFlag.set_used_serial_alarm_controller()  # 串口设置使用中
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            alarmController = AlarmController(BusinessConstant.LOGGER)  # 控制对象
            result = alarmController.start_alarm()
            if result is None or result == "" or result == BusinessConstant.ERROR:
                result = def_error_result
            elif result == def_success_result or result == BusinessConstant.SUCCESS:
                HangarState.set_alarm_state(BusinessConstant.OPEN_STATE)
                result = def_success_result
            else:
                result = def_error_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(
                f"[OperateUtil.step_scene_alarm_controller_open_460000]警示灯打开-异常,异常信息为:{ex}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_alarm_controller()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_alarm_controller_open_460000]警示灯打开-结束,返回结果为:{result}")
    return result


def step_scene_alarm_controller_close_470000():
    """
    警示灯关闭
    """
    #  常量/参数部分
    recv_text = "470000"  # 下发指令
    def_success_result = "9470"
    def_error_result = "9471"  # 默认异常
    command_error_result = "947a"  # 不支持方法异常
    used_error_result = "947d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_alarm_controller_close_470000]警示灯关闭-开始")
    #  业务逻辑部分
    # time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)  # 等待时间原因：在打开机库门时，同时需要开灯线程，等待时间，防止端口被锁，无法处理
    if SerialUsedStateFlag.get_is_used_serial_alarm_controller() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_alarm_controller_close_470000]警示灯关闭,端口被占用")
        result = used_error_result
    else:
        try:
            SerialUsedStateFlag.set_used_serial_alarm_controller()  # 串口设置使用中
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            alarmController = AlarmController(BusinessConstant.LOGGER)  # 控制对象
            result = alarmController.stop_alarm()
            if result is None or result == "" or result == BusinessConstant.ERROR:
                result = def_error_result
            elif result == def_success_result or result == BusinessConstant.SUCCESS:
                HangarState.set_alarm_state(BusinessConstant.CLOSE_STATE)
                result = def_success_result
            else:
                result = def_error_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(
                f"[OperateUtil.step_scene_alarm_controller_close_470000]警示灯关闭-异常,异常信息为:{ex}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_alarm_controller()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_alarm_controller_close_470000]警示灯关闭-结束,返回结果为:{result}")
    return result


def step_scene_shutter_open_920000():
    """
    天窗打开
    """
    #  常量/参数部分
    recv_text = "920000"  # 下发指令
    def_success_result = "9920"  # 成功
    def_error_result = "9921"  # 默认异常
    def_overtime_result = "992c"  # 超时
    command_error_result = "992a"  # 不支持方法异常
    used_error_result = "992d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_shutter_open_920000]天窗打开-开始")
    if SerialUsedStateFlag.get_is_used_serial_weather() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_shutter_open_920000]天窗打开,端口被占用")
        result = used_error_result
    else:
        try:
            SerialUsedStateFlag.set_used_serial_weather()
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            rollingShutterDoor = RollingShutterDoor(BusinessConstant.LOGGER)
            result = rollingShutterDoor.open()
            if result is None or result == "" or result == BusinessConstant.ERROR:
                result = def_error_result
            elif result == BusinessConstant.SUCCESS:  # 底层返回success，设置操作成功
                HangarState.set_hangar_door_state(BusinessConstant.OPEN_STATE)
                result = def_success_result
            elif result == BusinessConstant.BUSY:  # 底层返回busy，设置底层端口或串口被占用异常
                result = used_error_result
            elif result == BusinessConstant.OVERTIME:
                result = def_overtime_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_shutter_open_920000]天窗打开-异常,异常信息为:{ex}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_weather()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_shutter_open_920000]天窗打开-结束,返回结果为:{result}")
    return result


def step_scene_shutter_close_930000():
    """
    天窗关闭
    """
    #  常量/参数部分
    recv_text = "930000"  # 下发指令
    def_success_result = "9930"  # 成功
    def_error_result = "9931"  # 默认异常
    def_overtime_result = "933c"  # 超时
    state_error_result = "9936"  # 状态异常
    used_error_result = "993d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_shutter_close_930000]天窗关闭-开始")
    if HangarState.get_updown_lift_state() != BusinessConstant.DOWN_STATE:
        BusinessConstant.LOGGER.get_log().info(
            f"[websockets.step_scene_shutter_close_930000]天窗关闭-异常,升降台状态为{HangarState.get_updown_lift_state()},不能关闭")
        return state_error_result
    # 业务逻辑处理
    if SerialUsedStateFlag.get_is_used_serial_weather() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_shutter_close_930000]天窗关闭,端口被占用")
        result = used_error_result
    else:
        try:
            SerialUsedStateFlag.set_used_serial_weather()
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            rollingShutterDoor = RollingShutterDoor(BusinessConstant.LOGGER)
            result = rollingShutterDoor.close()
            if result is None or result == "" or result == BusinessConstant.ERROR:
                result = def_error_result
            elif result == BusinessConstant.SUCCESS:  # 底层返回success，设置操作成功
                HangarState.set_hangar_door_state(BusinessConstant.CLOSE_STATE)
                result = def_success_result
            elif result == BusinessConstant.BUSY:  # 底层返回busy，设置底层端口或串口被占用异常
                result = used_error_result
            elif result == BusinessConstant.OVERTIME:
                result = def_overtime_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_shutter_close_930000]天窗关闭-异常,异常信息为:{ex}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_weather()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_shutter_close_930000]天窗关闭-结束,返回结果为:{result}")
    return result


def step_scene_window_open_940000():
    """
    百叶窗打开
    """
    #  常量/参数部分
    recv_text = "940000"  # 下发指令
    def_success_result = "9940"  # 成功
    def_error_result = "9941"  # 默认异常
    command_error_result = "994a"  # 不支持方法异常
    def_overtime_result = "994c"
    used_error_result = "994d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_window_open_940000]百叶窗打开-开始")
    if SerialUsedStateFlag.get_is_used_serial_weather() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_window_open_940000]百叶窗打开,端口被占用")
        result = used_error_result
    else:
        try:
            SerialUsedStateFlag.set_used_serial_weather()
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            shadeWindow = ShadeWindow(BusinessConstant.LOGGER)
            result = shadeWindow.open()
            if result is None or result == "" or result == BusinessConstant.ERROR:
                result = def_error_result
            elif result == BusinessConstant.SUCCESS:  # 底层返回success，设置操作成功
                HangarState.set_shade_window_state(BusinessConstant.OPEN_STATE)
                result = def_success_result
            elif result == BusinessConstant.BUSY:  # 底层返回busy，设置底层端口或串口被占用异常
                result = used_error_result
            elif result == BusinessConstant.OVERTIME:
                result = def_overtime_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_window_open_940000]百叶窗打开-异常,异常信息为:{ex}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_weather()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_window_open_940000]百叶窗打开-结束,返回结果为:{result}")
    return result


def step_scene_window_close_950000():
    """
    百叶窗关闭
    """
    #  常量/参数部分
    recv_text = "950000"  # 下发指令
    def_success_result = "9950"  # 成功
    def_error_result = "9951"  # 默认异常
    def_overtime_result = "995c"
    command_error_result = "995a"  # 不支持方法异常
    used_error_result = "995d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_window_close_950000]百叶窗关闭-开始")
    if SerialUsedStateFlag.get_is_used_serial_weather() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_window_close_950000]百叶窗关闭,端口被占用")
        result = used_error_result
    else:
        try:
            SerialUsedStateFlag.set_used_serial_weather()
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            shadeWindow = ShadeWindow(BusinessConstant.LOGGER)
            result = shadeWindow.close()
            if result is None or result == "" or result == BusinessConstant.ERROR:
                result = def_error_result
            elif result == BusinessConstant.SUCCESS:  # 底层返回success，设置操作成功
                HangarState.set_shade_window_state(BusinessConstant.CLOSE_STATE)
                result = def_success_result
            elif result == BusinessConstant.BUSY:  # 底层返回busy，设置底层端口或串口被占用异常
                result = used_error_result
            elif result == BusinessConstant.OVERTIME:
                result = def_overtime_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_window_close_950000]百叶窗关闭-异常,异常信息为:{ex}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_weather()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_window_close_950000]百叶窗关闭-结束,返回结果为:{result}")
    return result


@AlarmLightController.AlarmLight
def step_scene_handle_open_h00000():
    """
    手柄开启
    """
    recv_text = "h00000"  # 下发指令
    def_success_result = "9h00"  # 成功
    def_error_result = "9h01"  # 默认异常
    command_error_result = "9h0a"  # 不支持方法异常
    used_error_result = "9h0d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_handle_open_h00000]手柄开启-开始")
    if SerialUsedStateFlag.get_is_used_serial_weather() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_handle_open_h00000]手柄开启,端口被占用")
        result = used_error_result
    else:
        try:
            SerialUsedStateFlag.set_used_serial_weather()
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            uavController = UAVController(BusinessConstant.LOGGER)
            result = uavController.open_controller()
            if result is None or result == "":
                result = def_error_result
            elif result == BusinessConstant.SUCCESS:  # 底层返回success，设置操作成功
                HangarState.set_uav_controller_state(BusinessConstant.OPEN_STATE)
                result = def_success_result
            elif not result.startswith("9") or result == BusinessConstant.ERROR:  # 过滤底层返回error等非标的情况
                result = def_error_result
            elif result.endswith("a") and result.startswith("9"):
                result = command_error_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_handle_open_h00000]手柄开启-异常,异常信息为:{ex}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_weather()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_handle_open_h00000]手柄开启-结束,返回结果为:{result}")
    return result


@AlarmLightController.AlarmLight
def step_scene_handle_close_h10000():
    """
    手柄关闭
    """
    recv_text = "h10000"  # 下发指令
    def_success_result = "9h10"  # 成功
    def_error_result = "9h11"  # 默认异常
    command_error_result = "9h1a"  # 不支持方法异常
    used_error_result = "9h1d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_handle_close_h10000]手柄关闭-开始")
    if SerialUsedStateFlag.get_is_used_serial_weather() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_handle_close_h10000]手柄关闭,端口被占用")
        result = used_error_result
    else:
        try:
            SerialUsedStateFlag.set_used_serial_weather()
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            uavController = UAVController(BusinessConstant.LOGGER)
            result = uavController.close_controller()
            if result is None or result == "":
                result = def_error_result
            elif result == BusinessConstant.SUCCESS:  # 底层返回success，设置操作成功
                HangarState.set_uav_controller_state(BusinessConstant.CLOSE_STATE)
                result = def_success_result
            elif not result.startswith("9") or result == BusinessConstant.ERROR:  # 过滤底层返回error等非标的情况
                result = def_error_result
            elif result.endswith("a") and result.startswith("9"):
                result = command_error_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_handle_close_h10000]手柄关闭-异常,异常信息为:{ex}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_weather()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_handle_close_h10000]手柄关闭-结束,返回结果为:{result}")
    return result


@AlarmLightController.AlarmLight
def step_scene_handle_return_h20000():
    """
    手柄一键返航
    """
    recv_text = "h20000"  # 下发指令
    def_success_result = "9h20"  # 成功
    def_error_result = "9h21"  # 默认异常
    command_error_result = "9h2a"  # 不支持方法异常
    used_error_result = "9h2d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_handle_return_h20000]手柄一键返航-开始")
    if SerialUsedStateFlag.get_is_used_serial_weather() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_handle_return_h20000]手柄一键返航,端口被占用")
        result = used_error_result
    else:
        try:
            SerialUsedStateFlag.set_used_serial_weather()
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            uavController = UAVController(BusinessConstant.LOGGER)
            result = uavController.return_controller()
            if result is None or result == "":
                result = def_error_result
            elif result == BusinessConstant.SUCCESS:  # 底层返回success，设置操作成功
                result = def_success_result
            elif not result.startswith("9") or result == BusinessConstant.ERROR:  # 过滤底层返回error等非标的情况
                result = def_error_result
            elif result.endswith("a") and result.startswith("9"):
                result = command_error_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_handle_return_h20000]手柄一键返航-异常,异常信息为:{ex}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_weather()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_handle_return_h20000]手柄一键返航-结束,返回结果为:{result}")
    return result


def step_scene_open_together_600000():
    """
    同时打开机库门和推杆，命令为600000
    (1)判断是否是1.0板子，如果是则继续，否则返回错误代码9601
    (2)进行开门操作
    (3)进行开推杆操作
    """
    def_success_result = "9600"
    def_error_result = "9601"
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_open_together_600000]机库门和推杆同时打开-开始")
    recv_text = "600000"
    if Config.get_down_version() != "V1.0":
        BusinessConstant.LOGGER.get_log().info(
            f"[OperateUtil.step_scene_open_together_600000]机库门和推杆同时打开-结束,返回结果为:{def_error_result},"
            f"下位机版本为:{Config.get_down_version()},只有V1.0版本才可以同时操作")
        def_error_result
    # 待机操作
    step_scene_drone_standby_sb0000()
    # 开始做开门操作，打开一个开门的线程
    thread_open_door = threading.Thread(target=step_scene_door_open_140000, args=())
    thread_open_door.setDaemon(True)
    thread_open_door.start()
    # 开始做开推杆操作，打开一个打开推杆线程
    thread_open_bar = threading.Thread(target=step_scene_bar_reset_500000, args=())
    thread_open_bar.setDaemon(True)
    thread_open_bar.start()
    # 根据返回值，判断操作结果是否完成，完成则返回成功(根据hanger中机库状态判断执行是否成功)，失败则返回9601
    # 等待55秒
    for i in range(50):
        if HangarState.get_hangar_door_state() == "open" and HangarState.get_hangar_bar_state() == "open":
            BusinessConstant.LOGGER.get_log().info(
                f"[OperateUtil.step_scene_open_together_600000]机库门和推杆同时打开-结束,返回结果为:{def_success_result}")
            return def_success_result
        time.sleep(1)
    BusinessConstant.LOGGER.get_log().info(
        f"[OperateUtil.step_scene_open_together_600000]机库门和推杆同时打开-结束,返回结果为:{def_error_result}")


@AlarmLightController.AlarmLight
def step_scene_drone_standby_sb0000():
    """
    无人机待机
    """
    recv_text = "Standby"  # 下发指令
    def_success_result = "9sb0"  # 成功
    def_error_result = "9sb1"  # 默认异常
    command_error_result = "9sba"  # 不支持方法异常
    used_error_result = "9sbd"  # 底层端口或串口被占用异常
    state_error_result = "9sb6"
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_drone_standby_sb0000]无人机待机-开始")
    if SerialUsedStateFlag.get_is_used_serial_charge() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_drone_standby_sb0000]无人机待机,端口被占用")
        result = used_error_result
    elif HangarState.get_hangar_bar_state() != BusinessConstant.CLOSE_STATE:
        BusinessConstant.LOGGER.get_log().info(
            f"[OperateUtil.step_scene_drone_standby_sb0000]无人机待机,夹杆状态为:{HangarState.get_hangar_bar_state()},不能待机")
        result = state_error_result
    else:
        try:
            SerialUsedStateFlag.set_used_serial_charge()
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            result = exe_charge_command(recv_text)
            if result is None or result == "":
                result = def_error_result
            elif result == BusinessConstant.SUCCESS:  # 底层返回success，设置操作成功
                HangarState.close_auto_charge()  # 结束自动充电
                result = def_success_result
            else:
                result = def_error_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(
                f"[OperateUtil.step_scene_drone_standby_sb0000]无人机待机-异常,异常信息为:{str(ex)}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_charge()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_drone_standby_sb0000]无人机待机-结束,返回结果为:{result}")
    return result


@AlarmLightController.AlarmLight
def step_scene_drone_takeoff_dt0000():
    """
    无人机开机
    """
    recv_text = "TakeOff"  # 下发指令
    def_success_result = "9dt0"  # 成功
    def_error_result = "9dt1"  # 默认异常
    command_error_result = "9dta"  # 不支持方法异常
    used_error_result = "9dtd"  # 底层端口或串口被占用异常
    state_error_result = "9dt6"  # 状态异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_drone_takeoff_dt0000]无人机开机-开始")
    if SerialUsedStateFlag.get_is_used_serial_charge() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_drone_takeoff_dt0000]无人机开机,端口被占用")
        result = used_error_result
    elif HangarState.get_hangar_bar_state() != BusinessConstant.CLOSE_STATE:
        BusinessConstant.LOGGER.get_log().info(
            f"[OperateUtil.step_scene_drone_takeoff_dt0000]无人机开机,夹杆状态为:{HangarState.get_hangar_bar_state()},不能开机")
        result = state_error_result
    else:
        try:
            SerialUsedStateFlag.set_used_serial_charge()
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            result = exe_charge_command(recv_text)
            if result is None or result == "":
                result = def_error_result
            elif result == BusinessConstant.SUCCESS:  # 底层返回success，设置操作成功
                HangarState.close_auto_charge()  # 结束自动充电
                result = def_success_result
            else:
                result = def_error_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(
                f"[OperateUtil.step_scene_drone_takeoff_dt0000]无人机开机-异常,异常信息为:{str(ex)}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_charge()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_drone_takeoff_dt0000]无人机开机-结束,返回结果为:{result}")
    return result


@AlarmLightController.AlarmLight
def step_scene_drone_off_dd0000():
    """
    无人机关机
    """
    #  常量/参数部分
    recv_text = "DroneOff"  # 下发指令
    def_success_result = "9dd0"  # 成功
    def_error_result = "9dd1"  # 默认异常
    command_error_result = "9dda"  # 不支持方法异常
    used_error_result = "9ddd"  # 底层端口或串口被占用异常
    state_error_result = "9dd6"
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_drone_off_dd0000]无人机关机-开始")
    if SerialUsedStateFlag.get_is_used_serial_charge() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_drone_off_dd0000]无人机关机,端口被占用")
        result = used_error_result
    elif HangarState.get_hangar_bar_state() != BusinessConstant.CLOSE_STATE:
        BusinessConstant.LOGGER.get_log().info(
            f"[OperateUtil.step_scene_drone_off_dd0000]无人机关机,夹杆状态为:{HangarState.get_hangar_bar_state()},不能关机")
        result = state_error_result
    else:
        try:
            SerialUsedStateFlag.set_used_serial_charge()
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            result = exe_charge_command(recv_text)
            if result is None or result == "":
                result = def_error_result
            elif result == BusinessConstant.SUCCESS:  # 底层返回success，设置操作成功
                HangarState.open_auto_charge()  # 启动自动充电
                result = def_success_result
            else:
                result = def_error_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_drone_off_dd0000]无人机关机-异常,异常信息为:{str(ex)}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_charge()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_drone_off_dd0000]无人机关机-结束,返回结果为:{result}")
    return result


@AlarmLightController.AlarmLight
def step_scene_drone_charge_cp0000():
    """
    无人机充电
    """
    recv_text = "Charge"  # 下发指令
    def_success_result = "9cp0"  # 成功
    def_error_result = "9cp1"  # 默认异常
    command_error_result = "9cpa"  # 不支持方法异常
    used_error_result = "9cpd"  # 底层端口或串口被占用异常
    state_error_result = "9cp6"
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_drone_charge_cp0000]无人机充电-开始")
    if SerialUsedStateFlag.get_is_used_serial_charge() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_drone_charge_cp0000]无人机充电,端口被占用")
        result = used_error_result
    elif HangarState.get_hangar_bar_state() != BusinessConstant.CLOSE_STATE:
        BusinessConstant.LOGGER.get_log().info(
            f"[OperateUtil.step_scene_drone_charge_cp0000]无人机充电,夹杆状态为:{HangarState.get_hangar_bar_state()},不能充电")
        result = state_error_result
    else:
        try:
            SerialUsedStateFlag.set_used_serial_charge()
            time.sleep(BusinessConstant.SERIAL_WAIT_TIMEOUT)
            HangarState.open_auto_charge()  # 启动自动充电
            result = exe_charge_command(recv_text)
            if result is None or result == "":
                result = def_error_result
            elif result == BusinessConstant.SUCCESS:  # 底层返回success，设置操作成功
                result = def_success_result
            else:
                result = def_error_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(
                f"[OperateUtil.step_scene_drone_charge_cp0000]无人机充电-异常,异常信息为:{str(ex)}")
            result = def_error_result
        finally:
            SerialUsedStateFlag.set_used_serial_free_charge()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_drone_charge_cp0000]无人机充电-结束,返回结果为:{result}")
    return result


def step_scene_drone_check_ck0000():
    """
    无人机状态检查,端口不被占用
    """
    recv_text = "Check"  # 下发指令
    def_success_result = "9ck0"  # 成功
    def_error_result = "9ck1"  # 默认异常
    command_error_result = "9cka"  # 不支持方法异常
    used_error_result = "9ckd"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_drone_check_ck0000]无人机状态检查-开始")
    if SerialUsedStateFlag.get_is_used_serial_charge() is True:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_drone_check_ck0000]无人机状态检查,端口被占用")
        result = used_error_result
    else:
        try:
            result = exe_charge_command(recv_text)
            if result is None or result == "":
                result = def_error_result
            elif result == BusinessConstant.SUCCESS:  # 底层返回success，设置操作成功
                result = def_success_result
            else:
                result = def_error_result
        except Exception as ex:
            BusinessConstant.LOGGER.get_log().info(
                f"[OperateUtil.step_scene_drone_check_ck0000]无人机状态检查-异常,异常信息为:{str(ex)}")
            result = def_error_result
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_drone_check_ck0000]无人机状态检查-结束,返回结果为:{result}")
    return result


def step_scene_auto_charge_on_c00000():
    """
    启动自动化充电,不进行充电操作
    """
    recv_text = "c00000"  # 下发指令
    def_success_result = "9c00"  # 成功
    def_error_result = "9c01"  # 默认异常
    unsupported_error_result = "9c04"  # 不支持自动化充电功能
    command_error_result = "9c0a"  # 不支持方法异常
    used_error_result = "9c0d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_auto_charge_on_c00000]无人机开启自动充电-开始")
    if not Config.get_is_need_auto_charge():
        result = unsupported_error_result
    else:
        HangarState.open_auto_charge()
        result = def_success_result
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_auto_charge_on_c00000]无人机开启自动充电-结束,返回结果为:{result}")
    return result


def step_scene_auto_charge_off_c10000():
    """
    关闭自动化充电,不进行充电操作
    """
    recv_text = "c10000"  # 下发指令
    def_success_result = "9c10"  # 成功
    def_error_result = "9c11"  # 默认异常
    unsupported_error_result = "9c14"  # 不支持自动化充电功能
    command_error_result = "9c1a"  # 不支持方法异常
    used_error_result = "9c1d"  # 底层端口或串口被占用异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_auto_charge_off_c10000]无人机关闭自动充电-开始")
    if not Config.get_is_need_auto_charge():
        result = unsupported_error_result
    else:
        HangarState.close_auto_charge()
        result = def_success_result
    BusinessConstant.LOGGER.get_log().info(
        f"[OperateUtil.step_scene_auto_charge_off_c10000]无人机关闭自动充电-结束,返回结果为:{result}")
    return result


def step_scene_upload_log_lg0000(site_id, upload_log_datetime):
    """
    调用接口上传日志
    """
    def_success_result = "9lg0"
    def_error_result = "9lg1"
    command_error_result = "9lga"  # 文件不存在异常
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_upload_log_lg0000]机库日志上传-开始")
    try:
        url = Config.get_upload_log_url()
        file_name = "/home/wkzn/JIKUPI/log/log_" + upload_log_datetime + ".txt"
        # file_name = "E:/zyhk/shangweiji/jikuapi/common/luxd/log_"+upload_log_datetime+".txt"
        result = def_error_result
        if os.path.exists(file_name) is True:
            with open(file_name, 'rb') as file:
                files = {'file': file}
                response = requests.post(url=url, data={"siteId": site_id, "fromEquipment": "swj", "type": "1"},
                                         files=files)
                # print(f"[OperateUtil.step_scene_upload_log_lg0000]机库日志上传-返回结果,code:{response.status_code},text:{response.text}")
                BusinessConstant.LOGGER.get_log().info(
                    f"[OperateUtil.step_scene_upload_log_lg0000]机库日志上传-返回结果,code:{response.status_code},text:{response.text}")
                if response.status_code == 200:
                    result = def_success_result
        else:
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_upload_log_lg0000]机库日志上传-未找到日志文件")
            result = command_error_result
    except Exception as ex:
        result = def_error_result
        # print(f"[OperateUtil.step_scene_upload_log_lg0000]机库日志上传-异常,异常信息为:{str(ex)}")
        BusinessConstant.LOGGER.get_log().info(
            f"[OperateUtil.step_scene_upload_log_lg0000]机库日志上传-异常,异常信息为:{str(ex)}")
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.step_scene_upload_log_lg0000]机库日志上传-结束,返回结果为:{result}")
    return result


def exe_charge_command(command):
    """
    执行电池相关命令
    """
    try:
        BusinessConstant.LOGGER.get_log().info(
            f"[OperateUtil.exe_charge_command]执行电池命令-开始,命令为:{command},版本为:{Config.get_wlc_version()}")
        if Config.get_charge_version() == "wfc":  # 无线充电
            if Config.get_wfc_version() == 'V1.0':  # V1.0版本
                WFC = WFCServer(BusinessConstant.LOGGER)
            elif Config.get_wfc_version() == 'V2.0':  # V2.0版本
                if Config.get_is_wfc_double_connect() is False:
                    WFC = WFCServerV2(BusinessConstant.LOGGER)
                else:
                    WFC = WFCServerV2Sender(BusinessConstant.LOGGER)
        else:  # 触点充电
            if Config.get_wlc_version() == "V1.0":
                if Config.get_is_wlc_double_connect() is True:  # 全双工通信
                    WFC = JCCServerM300Sender(BusinessConstant.LOGGER)
                else:
                    WFC = JCCServerM300(BusinessConstant.LOGGER)
            elif Config.get_wlc_version() == "V2.0":  # V2.0
                WFC = JCCServerV2M300Single(BusinessConstant.LOGGER)
            elif Config.get_wlc_version() == "V3.0":  # V3.0
                WFC = JCCServerV3M300(BusinessConstant.LOGGER)
                result = WFC.operator_charge(command)
            elif Config.get_wlc_version() == "V4.0":  # V4.0
                WFC = JCCServerV4M350(BusinessConstant.LOGGER)
            elif Config.get_wlc_version() == "V5.0":  # V5.0
                WFC = JCCServerV5(BusinessConstant.LOGGER)
            elif Config.get_wlc_version() == "V6.0":  # V6.0
                WFC = JCCServerV6M350(BusinessConstant.LOGGER)
        result = WFC.operator_charge(command)
        BusinessConstant.LOGGER.get_log().info(
            f"[OperateUtil.exe_charge_command]执行电池命令-结束,命令为:{command},返回结果为:{result}")
        return result
    except Exception as ex:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.exe_charge_command]执行电池命令-异常,命令为:{command},异常信息为:{ex}")
        return BusinessConstant.ERROR


"""
机库单步操作==================================================end
"""

"""
机库复合操作(单步操作组合)==================================================start
"""

open_door_result_code = ""


def open_door_thread():
    """
    开门线程
    """
    global open_door_result_code
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.open_door_thread]机库门打开线程-开始")
    open_door_result_code = step_scene_door_open_140000()
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.open_door_thread]机库门打开线程-结束,返回值为:{open_door_result_code}")


def big_scene_A000():
    """
    大场景-一键起飞准备，开门、开机（如果充电有待机）、松推杆
    """
    recv_text = "A000"  # 大场景命令全码
    def_success_result = "A0009000"  # 成功
    def_error_result = "A0009001"  # 默认异常
    begin_time = time.time()  # 开始时间
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A000]大场景-开始,执行命令{recv_text}")
    try:
        if Config.get_is_meanopen() is True:  # 同时开启机库门和开机
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A000]大场景-机库门开门线程")
            threading.Thread(target=open_door_thread, args=()).start()
        else:
            # 进入机库门打开step
            result = step_scene_door_open_140000()
            if not result.endswith("0"):
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A000]大场景-开门失败,进行复位操作")
                big_scene_C000()
                BusinessConstant.LOGGER.get_log().info(
                    f"[OperateUtil.big_scene_A000]大场景-结束,执行命令{recv_text}，返回结果为:{result}")
                return result
        HangarState.close_auto_charge()
        # ---------------进入待机step，需要判断当前是否为充电状态，如果是充电状态需要加待机，非充电状态不需要加待机
        if WFState.get_battery_state() == "charging" or WFState.get_battery_state() == "waiting":
            result = step_scene_drone_standby_sb0000()
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A000]大场景-执行待机步骤,返回结果为:{result}")
            if not result.endswith("0"):
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A000]大场景-待机失败,进行复位操作")
                big_scene_C000()
                BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A000]大场景-执行待机异常,返回结果为:{result}")
                return result
            time.sleep(3)
        # -----------实测中发现，经过跟下位机沟通，确定待机执行返回较快，但是底层有响应时间，休眠10秒后续执行
        # time.sleep(3)
        # 进入无人机开机step
        result = step_scene_drone_takeoff_dt0000()
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A000]大场景-执行开机步骤,返回结果为:{result}")
        if not result.endswith("0"):
            # 末尾不为0，返回拼装8位错误码
            result = recv_text + result
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A000]大场景-开机失败,进行复位操作")
            big_scene_C000()
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A000]大场景-执行开机异常,返回结果为:{result}")
            return result
        if Config.get_is_meanopen() is True:  # 同时开启机库门和开机
            # 松推杆之前检查门的状态是否为关闭状态，如果关闭则判定失败 2023-2-15
            # 2023-5-26 加门的打开等待时间,门的执行太慢，开机太快导致失败
            time.sleep(7)
            if not open_door_result_code.endswith(
                    "0") or HangarState.get_hangar_door_state() == "close":  # 开门失败或者门是关闭的
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A000]大场景-开门失败,进行复位操作")
                big_scene_C000()
                BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A000]大场景-开门失败,返回结果为:{result}")
                return open_door_result_code

        # 进入XY推杆打开step
        result = step_scene_bar_reset_500000()
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A000]大场景-XY推杆松开操作,返回结果为:{result}")
        if not result.endswith("0"):
            # 末尾不为0，返回拼装8位错误码
            result = recv_text + result
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A000]大场景-XY推杆松开操作失败,进行复位操作")
            big_scene_C000()
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A000]大场景-XY推杆松开操作失败,返回结果为:{result}")
            return result
        # 最后应答
        end_time = time.time()
        run_time = end_time - begin_time
        BusinessConstant.LOGGER.get_log().info(
            f"[OperateUtil.big_scene_A000]大场景-结束,执行命令{recv_text},返回结果为:{def_success_result},整体运行时间为:{run_time}")
        return def_success_result
    except Exception as e:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A000]大场景-异常,进行复位操作")
        big_scene_C000()
        BusinessConstant.LOGGER.get_log().info(
            f"[OperateUtil.big_scene_A000]大场景-异常,执行命令{recv_text},返回结果为:{def_error_result},异常信息为:{e}")
        return def_error_result


def big_scene_C000():
    """
    大场景-一键复位(内部根据充电方式切换不同复位操作)
    """
    recv_text = "C000"  # 大场景命令全码
    def_success_result = "C0009000"  # 成功
    def_error_result = "C0009001"  # 默认异常
    charge_type_error_result = "C0009002"  # 充电方式不是触点式
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_C000]大场景一键复位-开始,充电方式:{Config.get_charge_version()}")
    try:
        if Config.get_charge_version() == "wlc":
            result = big_scene_C100()
        else:
            result = charge_type_error_result
    except Exception as e:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_C000]大场景一键复位-异常,异常信息为:{e}")
        result = def_error_result
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_C000]大场景一键复位-结束,返回结果为:{result}")
    return result


def big_scene_C100():
    """
    大场景-一键复位(触点式复位)
    """
    recv_text = "C100"  # 大场景命令全码
    def_success_result = "C1009000"  # 成功
    def_error_result = "C1009001"  # 默认异常
    charge_type_error_result = "C1009002"  # 充电方式不是触点式
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_C100]大场景一键触点复位-开始")
    if Config.get_charge_version() == "wlc":
        try:
            # 进入XY推杆夹住step
            result = step_scene_bar_close_2e10002000()
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_C100]大场景一键触点复位-XY推杆夹紧,返回结果为:{result}")
            if not result.endswith("0"):
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_C100]大场景一键触点复位-结束,返回结果为:{result}")
                return result
            # 进入无人机关机step
            result = step_scene_drone_off_dd0000()
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_C100]大场景一键触点复位-无人机关机,返回结果为:{result}")
            if not result.endswith("0"):
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_C100]大场景一键触点复位-结束,返回结果为:{result}")
                return result
            # 进入机库门关闭step
            result = step_scene_door_close_150000()
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_C100]大场景一键触点复位-机库门关闭,返回结果为:{result}")
            if not result.endswith("0"):
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_C100]大场景一键触点复位-结束,返回结果为:{result}")
                return result
            # 进入空调开机step
            result = step_scene_air_open_300000()
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_C100]大场景一键触点复位-空调打开,返回结果为:{result}")
            if not result.endswith("0"):
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_C100]大场景一键触点复位-结束,返回结果为:{result}")
                return result
            BusinessConstant.LOGGER.get_log().info(
                f"[OperateUtil.big_scene_C100]大场景一键触点复位-结束,返回结果为:{def_success_result}")
            return def_success_result
        except Exception as e:
            BusinessConstant.LOGGER.get_log().info(
                f"[OperateUtil.big_scene_C100]大场景一键触点复位-异常,返回结果为:{def_error_result},异常信息为:{e}")
            return def_error_result
    else:
        BusinessConstant.LOGGER.get_log().info(
            f"[OperateUtil.big_scene_C100]大场景一键触点复位-结束,返回结果为:{charge_type_error_result}")
        return charge_type_error_result


def big_scene_A010():
    """
    开机状态下的一键起飞
    """
    recv_text = "A010"  # 大场景命令全码
    def_success_result = "A0109000"  # 成功
    def_error_result = "A0109001"  # 默认异常
    begin_time = time.time()  # 开始时间
    try:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A010]大场景开机状态下一键起飞-开始")
        # 进入机库门打开step
        result = step_scene_door_open_140000()
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A010]大场景开机状态下一键起飞-机库门打开,返回结果为:{result}")
        if not result.endswith("0"):
            # 末尾不为0，返回拼装8位错误码
            result = recv_text + result
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A010]大场景开机状态下一键起飞-机库门打开失败,进行复位操作")
            big_scene_C000()
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A010]大场景开机状态下一键起飞-机库门打开失败,返回结果为:{result}")
            return result
        HangarState.close_auto_charge()
        # 进入XY推杆打开step
        result = step_scene_bar_reset_500000()
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A010]大场景开机状态下一键起飞-XY推杆打开,步骤返回为:{result}")
        if not result.endswith("0"):
            # 末尾不为0，返回拼装8位错误码
            result = recv_text + result
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A010]大场景开机状态下一键起飞-XY推杆打开失败,进行复位操作")
            big_scene_C000()
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A010]大场景开机状态下一键起飞-XY推杆打开失败,返回结果为:{result}")
            return result
        end_time = time.time()
        run_time = end_time - begin_time
        BusinessConstant.LOGGER.get_log().info(
            f"[OperateUtil.big_scene_A010]大场景开机状态下一键起飞-结束,执行命令{recv_text},返回结果为:{def_success_result},整体运行时间为:{run_time}")
        return def_success_result
    except Exception as e:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A010]大场景开机状态下一键起飞-异常,进行复位操作")
        big_scene_C000()
        BusinessConstant.LOGGER.get_log().info(
            f"[OperateUtil.big_scene_A010]大场景开机状态下一键起飞-异常,执行命令{recv_text},返回结果为:{def_error_result},异常信息为:{e}")
        return def_error_result


def big_scene_A100():
    """
    大场景-一键起飞后续(自检成功),关闭机库门
    """
    recv_text = "A100"  # 大场景命令全码
    def_success_result = "A1009000"  # 成功
    def_error_result = "A1009001"  # 默认异常
    try:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A100]大场景关闭机库门-开始")
        HangarState.close_auto_charge()
        # 进入机库门关闭step
        result = step_scene_door_close_150000()

        if not result.endswith("0"):
            # 末尾不为0，返回拼装8位错误码
            result = recv_text + result
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A100]大场景关闭机库门-结束,关闭失败,返回结果为:{result}")
            return result
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A100]大场景关闭机库门-结束,返回结果为:{def_success_result}")
        return def_success_result
    except Exception as e:
        BusinessConstant.LOGGER.get_log().info(
            f"[OperateUtil.big_scene_A100]大场景关闭机库门-异常,返回结果为:{def_error_result},异常信息为:{e}")
        return def_error_result


def big_scene_A200():
    """
    大场景-一键起飞后续(自检失败)
    """
    recv_text = "A200"  # 大场景命令全码
    def_success_result = "A2009000"  # 成功
    def_error_result = "A2009001"  # 默认异常
    try:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A200]大场景一键起飞后续(自检失败)-开始")
        HangarState.close_auto_charge()
        # 进入XY推杆夹住step
        result = step_scene_bar_close_2e10002000()
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A200]大场景一键起飞后续(自检失败)-XY推杆夹住,返回结果为:{result}")
        if not result.endswith("0"):
            # 末尾不为0，返回拼装8位错误码
            result = recv_text + result
            BusinessConstant.LOGGER.get_log().info(
                f"[OperateUtil.big_scene_A200]大场景一键起飞后续(自检失败)-XY推杆夹住失败,返回结果为:{result}")
            return result
        # 进入机库门关闭step
        result = step_scene_door_close_150000()
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A200]大场景一键起飞后续(自检失败)-机库门关闭,返回结果为:{result}")
        if not result.endswith("0"):
            # 末尾不为0，返回拼装8位错误码
            result = recv_text + result
            BusinessConstant.LOGGER.get_log().info(
                f"[OperateUtil.big_scene_A200]大场景一键起飞后续(自检失败)-机库门关闭失败,返回结果为:{result}")
            return result
        # 进入空调开机step
        result = step_scene_air_open_300000()
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A200]大场景一键起飞后续(自检失败)-空调开机,返回结果为:{result}")
        if not result.endswith("0"):
            # 末尾不为0，返回拼装8位错误码
            result = recv_text + result
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A200]大场景一键起飞后续(自检失败)-空调开机失败,返回结果为:{result}")
            return result
        # 进入无人机关机step
        result = step_scene_drone_off_dd0000()
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_A200]大场景一键起飞后续(自检失败)-无人机关机,返回结果为:{result}")
        if not result.endswith("0"):
            # 末尾不为0，返回拼装8位错误码
            result = recv_text + result
            BusinessConstant.LOGGER.get_log().info(
                f"[OperateUtil.big_scene_A200]大场景一键起飞后续(自检失败)-无人机关机失败,返回结果为:{result}")
            return result
        HangarState.open_auto_charge()
        BusinessConstant.LOGGER.get_log().info(
            f"[OperateUtil.big_scene_A200]大场景一键起飞后续(自检失败)-结束,返回结果为:{def_success_result}")
        return def_success_result
    except Exception as e:
        HangarState.close_auto_charge()
        BusinessConstant.LOGGER.get_log().info(
            f"[OperateUtil.big_scene_A200]大场景一键起飞后续(自检失败)-异常,返回结果为:{def_error_result},异常信息为:{e}")
        return def_error_result


def big_scene_B000():
    """
    大场景-一键降落准备,开门
    """
    recv_text = "B000"  # 大场景命令全码
    def_success_result = "B0009000"  # 成功
    def_error_result = "B0009001"  # 默认异常
    try:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_B000]大场景一键降落准备,开门-开始")
        HangarState.close_auto_charge()
        # 进入机库门打开step
        result = step_scene_door_open_140000()
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_B000]大场景一键降落准备,开门-机库门打开,返回结果为:{result}")
        if not result.endswith("0"):
            # 末尾不为0，返回拼装8位错误码
            result = recv_text + result
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_B000]大场景一键降落准备,开门-机库门打开失败,返回结果为:{result}")
            return result
        BusinessConstant.LOGGER.get_log().info(
            f"[OperateUtil.big_scene_B000]大场景一键降落准备,开门-结束,返回结果为:{def_success_result}")
        return def_success_result
    except Exception as e:
        BusinessConstant.LOGGER.get_log().info(
            f"[OperateUtil.big_scene_B000]大场景一键降落准备,开门-异常,返回结果为:{def_error_result},异常信息为:{e}")
        return def_error_result


def big_scene_B100():
    """
    大场景-一键降落后续，收推杆，关机，关门
    """
    recv_text = "B100"  # 大场景命令全码
    def_success_result = "B1009000"  # 成功
    def_error_result = "B1009001"  # 默认异常
    try:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_B100]大场景收推杆、关机、关门-开始")
        HangarState.close_auto_charge()
        # 进入XY推杆夹住step
        result = step_scene_bar_close_2e10002000()
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_B100]大场景收推杆、关机、关门-XY推杆夹住,返回结果为:{result}")
        if not result.endswith("0"):
            # 末尾不为0，返回拼装8位错误码
            result = recv_text + result
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_B100]大场景收推杆、关机、关门-XY推杆夹住失败,返回结果为:{result}")
            return result
        # 进入机库门关闭step
        result = step_scene_door_close_150000()
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_B100]大场景收推杆、关机、关门-机库门关闭,返回结果为:{result}")
        if not result.endswith("0"):
            # 末尾不为0，返回拼装8位错误码
            result = recv_text + result
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_B100]大场景收推杆、关机、关门-机库门关闭失败,返回结果为:{result}")
            return result
        # 进入待机step
        result = step_scene_drone_standby_sb0000()
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_B100]大场景收推杆、关机、关门-无人机待机,返回结果为:{result}")
        if not result.endswith("0"):
            # 末尾不为0，返回拼装8位错误码
            result = recv_text + result
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_B100]大场景收推杆、关机、关门-无人机待机失败,返回结果为:{result}")
        # 实测中发现，经过跟下位机沟通，确定待机执行返回较快，但是底层有响应时间，休眠10秒后续执行
        time.sleep(2)
        # 进入无人机关机step
        result = step_scene_drone_off_dd0000()
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_B100]大场景收推杆、关机、关门-无人机关机,返回结果为:{result}")
        if not result.endswith("0"):
            # 末尾不为0，返回拼装8位错误码
            result = recv_text + result
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_B100]大场景收推杆、关机、关门-无人机关机失败,返回结果为:{result}")
            return result
        # 进入空调开机step
        result = step_scene_air_open_300000()
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_B100]大场景收推杆、关机、关门-空调开机,返回结果为:{result}")
        if not result.endswith("0"):
            # 末尾不为0，返回拼装8位错误码
            result = recv_text + result
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_B100]大场景收推杆、关机、关门-空调开机失败,返回结果为:{result}")
            return result
        HangarState.open_auto_charge()
        BusinessConstant.LOGGER.get_log().info(
            f"[OperateUtil.big_scene_B100]大场景收推杆、关机、关门-结束,返回结果为:{def_success_result}")
        return def_success_result
    except Exception as e:
        BusinessConstant.LOGGER.get_log().info(
            f"[OperateUtil.big_scene_B100]大场景收推杆、关机、关门-异常,返回结果为:{def_error_result},异常信息为:{e}")
        return def_error_result


def big_scene_B200():
    """
    大场景-一键降落取消
    """
    recv_text = "B200"  # 大场景命令全码
    def_success_result = "B2009000"  # 成功
    def_error_result = "B2009001"  # 默认异常
    try:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_B200]大场景一键降落取消-开始")
        HangarState.close_auto_charge()
        # 进入机库门关闭step
        result = step_scene_door_close_150000()
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_B200]大场景一键降落取消-机库门关闭,返回结果为:{result}")
        if not result.endswith("0"):
            # 末尾不为0，返回拼装8位错误码
            result = recv_text + result
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_B200]大场景一键降落取消-机库门关闭失败,返回结果为:{result}")
            return result
        #  夜灯流程进入判断
        night_light = Config.get_is_night_light()  # 是否启动夜灯功能
        if night_light:
            time.sleep(2)
            # 进入关闭夜灯step
            result = step_scene_night_light_close_410000()
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_B200]大场景一键降落取消-夜灯关闭,返回结果为:{result}")
            if not result.endswith("0"):
                # 末尾不为0，返回拼装8位错误码
                result = recv_text + result
                BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_B200]大场景一键降落取消-夜灯关闭失败,返回结果为:{result}")
                return result
        else:
            BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_B200]大场景一键降落取消-夜灯关闭不进行,未配置夜灯开启项")
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.big_scene_B200]大场景一键降落取消-结束,返回结果为:{def_success_result}")
        return def_success_result
    except Exception as e:
        BusinessConstant.LOGGER.get_log().info(
            f"[OperateUtil.big_scene_B200]大场景一键降落取消-异常,返回结果为:{def_error_result},异常信息为:{e}")
        return def_error_result


"""
机库复合操作(单步操作组合)==================================================end
"""


def operate_hangar(command: str):
    """
    所有操作机库指令
    """
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.operate_hangar]机库操作-开始,操作命令为:{command}")
    result = "error_command"
    if command == "A000":
        result = big_scene_A000()
        step_scene_night_light_open_400000()
    elif command == "A010":
        result = big_scene_A010()
        step_scene_night_light_close_410000()
    elif command == "A100":
        result = big_scene_A100()
        step_scene_night_light_close_410000()
    elif command == "A200":
        result = big_scene_A200()
        step_scene_night_light_close_410000()
    elif command == "B000":
        result = big_scene_B000()
        step_scene_night_light_open_400000()
    elif command == "B100":
        result = big_scene_B100()
        step_scene_night_light_close_410000()
    elif command == "B200":
        result = big_scene_B200()
    elif command == "C000":
        result = big_scene_C000()
    elif command == "C100":
        result = big_scene_C100()
    elif command == "140000" or command.startswith("14"):
        result = step_scene_door_open_140000()
    elif command == "150000" or command.startswith("15"):
        result = step_scene_door_close_150000()
    elif command == "170000":
        result = step_scene_door_state_170000()
    elif command == "2e10002000" or command.startswith("2e"):
        result = step_scene_bar_close_2e10002000()
    elif command == "2f10002000" or command.startswith("2f"):
        if command == "2f2000":
            result = step_scene_td_bar_open_2f2000()  # 前后推杆打开
        else:
            result = step_scene_bar_open_2f10002000()  # 所有推杆打开
    elif command == "500000":
        result = step_scene_bar_reset_500000()
    elif command == "2g0000":
        result = step_scene_bar_state_2g0000()  # 推杆状态获取
    elif command == "300000":
        result = step_scene_air_open_300000()
    elif command == "310000":
        result = step_scene_air_close_310000()
    elif command == "400000": # 夜灯打开
        result = step_scene_night_light_open_400000()
    elif command == "410000": # 夜灯关闭
        result = step_scene_night_light_close_410000()
    elif command == "420000": # 操作过程灯带关闭
        result = step_scene_alarm_light_close_420000()
    elif command == "430000": # 操作过程灯带打开
        result = step_scene_alarm_green_light_open_430000()
    elif command == "460000": # 报警灯打开
        result = step_scene_alarm_controller_open_460000()
    elif command == "470000": # 报警灯关闭
        result = step_scene_alarm_controller_close_470000()
    elif command == "h00000" or command == "opencontroller":
        result = step_scene_handle_open_h00000()  # 遥控器开启
    elif command == "h10000" or command == "closecontroller":
        result = step_scene_handle_close_h10000()  # 遥控器关闭
    elif command == "h20000":
        result = step_scene_handle_return_h20000()  # 手柄一键返航
    elif command == "dt0000" or command == "TakeOff":  # 开机
        result = step_scene_drone_takeoff_dt0000()
    elif command == "dd0000" or command == "DroneOff":  # 关机
        result = step_scene_drone_off_dd0000()
    elif command == "cp0000" or command == "Charge":  # 充电
        result = step_scene_drone_charge_cp0000()
    elif command == "ck0000" or command == "Check":
        result = step_scene_drone_check_ck0000()
    elif command == "sb0000" or command == "Standby":  # 待机
        result = step_scene_drone_standby_sb0000()
    elif command == "c00000":
        result = step_scene_auto_charge_on_c00000()  # 开启自动充电标识,不会立即充电
    elif command == "c10000":
        result = step_scene_auto_charge_off_c10000()  # 关闭自动充电标识,不会立即结束充电
    elif command == "800000":
        result = step_scene_turn_lift_800000()  # 旋转台旋转
    elif command == "810000":
        result = step_scene_back_lift_810000()  # 旋转台回位
    elif command == "830000":
        result = step_scene_state_turn_lift_830000()  # 旋转台状态获取
    elif command == "700000":
        result = step_scene_up_lift_700000()  # 升降台上升
    elif command == "710000":
        result = step_scene_down_lift_710000()  # 升降台下降
    elif command == "730000":
        result = step_scene_state_updown_lift_730000()  # 升降台状态获取
    elif command == "740000" or command == "outliftup":
        result = step_scene_out_up_lift_740000()  # 外挂升降台上升
    elif command == "750000" or command == "outliftdown":
        result = step_scene_out_down_lift_750000()  # 外挂升降台下降
    elif command == "920000":
        result = step_scene_shutter_open_920000()  # 卷帘门打开
    elif command == "930000":
        result = step_scene_shutter_close_930000()  # 卷帘门关闭
    elif command == "940000":
        result = step_scene_window_open_940000()  # 百叶窗打开
    elif command == "950000":
        result = step_scene_window_close_950000()  # 百叶窗关闭
    elif command == "600000":
        result = step_scene_open_together_600000()  # 机库门和推杆同时打开
    elif command in ["DisplayOn", "DisplayOff", "Connect"]:
        result = exe_charge_command(command)  # 待测试
    else:
        BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.operate_hangar]机库操作-异常,暂不支持命令:{command}")
        result = BusinessConstant.ERROR
    BusinessConstant.LOGGER.get_log().info(f"[OperateUtil.operate_hangar]机库操作-结束,操作命令为:{command},返回结果为:{result}")
    return result


if __name__ == '__main__':
    result = step_scene_upload_log_lg0000("123", "2024-12-04")
    print(result)
