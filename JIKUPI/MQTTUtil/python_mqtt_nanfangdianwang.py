import json
import time
import uuid
import os
import datetime
import base64
import requests
from dateutil import parser
from threading import Thread

from paho.mqtt import client as mqtt_client

import BASEUtile.InitFileTool
import BASEUtile.OperateUtil as OperateUtil
import BASEUtile.HangarState as HangarState
from BASEUtile.logger import Logger
from ServerManager.websockets import WebSocketUtil

# logger = Logger(__name__)  # 日志记录

'''
南方电网专有接口部分
'''
ini_serialNumber = BASEUtile.InitFileTool.get_str_value("mqtt_info", "serial_number")

# 操控系统下发命令主题(通配表达式#会多捕获自己的应答，所以采用元组方式)
topic_subscribe_list = [
    # (f"/{ini_serialNumber}/callback", 2),  # 回调，这里测试时自己捕获用于调试 TODO 正式版本注释
    # (f"/{ini_serialNumber}/status/base", 2),  # 主动发布 5.3.1 机库基础状态常量 TODO 正式版本注释
    # (f"/{ini_serialNumber}/status/upgrade", 2),  # 主动发布 5.3.9 机库基础状态常量 TODO 正式版本注释 看起来是升级的信息，所以应该拿掉
    (f"/{ini_serialNumber}/sys/motor", 2),  # 订阅 8.2.2 舱门控制 8.2.3 归中装置控制
    (f"/{ini_serialNumber}/sys/power", 2),  # 订阅 8.3.5 无人机开关机 8.3.6 无人机充电
    (f"/{ini_serialNumber}/sys/general", 2)
    # 订阅8.4.4 查询机库固件版本号 8.4.5 下发更新机库固件命令(暂不支持) 8.4.6 机巣上传日志至平台服务器 8.4.7 机巣取消上传日志至平台服务器(暂不支持)

]
# topic_publish = ""  # 终端系统反馈执行结果主题(应答主题改为每个接口不同了)
client_id = 'jiku-001'  # 客户端id 后续读取配置文件覆盖

client_publish = None  # 用于推送消息的客户端
webclient: WebSocketUtil = None  # websocket推送线程
# hangstate = None  # 机库状态信息
logger = None  # 日志对象

'''
关于qos设置，考虑我们场景，应该统一为2
qos=0:最多发送一次，到达不到达发布者不管，发布者（客户端，服务端做为发送端的时候）只发送一次，不管接收端是否收到数据；
qos=1:至少到达一次，发布者需要到达后有确认，发布者（客户端，服务端做为发送端的时候）发布消息后等待接收者（客户端，服务端做为接收端的时候）的确认信息报文；如果发布都没有收到确认报文，发布者会一直发送消息；
qos=2:只有一次到达，发布者需要到达后确认，接收者需要发布者再次确

'''

# MQTT 应答码常量
rc_status = ["连接成功", "协议版本错误", "无效的客户端标识", "服务器无法使用", "用户名或密码错误", "无授权"]


def connect_mqtt() -> mqtt_client:
    # 连接MQTT服务器
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logger.get_log().info("[MQTT]链接 MQTT Broker 连接成功!")
            global client_publish
            client_publish = client  # 设置全局链接，用于下发消息
            subscribe(client)  # 注册订阅消息

        else:
            logger.get_log().info(f"[MQTT]链接 MQTT 失败！, 错误码: {rc}  错误信息: {rc_status[rc]}")

    def on_connect_fail(client, userdata):
        logger.get_log().error("[MQTT] 链接已断开，重连失败!")

    # 循环重新链接，直到连接上为止
    is_run = False
    while not is_run:
        try:
            # 从ini中读取运行配置信息
            host_str = BASEUtile.InitFileTool.get_str_value("mqtt_info", "host_str")
            port_int = BASEUtile.InitFileTool.get_int_value("mqtt_info", "port_int")
            username = BASEUtile.InitFileTool.get_str_value("mqtt_info", "username_str")
            password = BASEUtile.InitFileTool.get_str_value("mqtt_info", "password_str")

            global client_id
            client_id = BASEUtile.InitFileTool.get_str_value("mqtt_info", "client_id")

            logger.get_log().info(
                f"[MQTT]启动创建MQTT链接，登录MTQQ服务器客户端ID:[{client_id}] 服务IP:[{host_str}] 服务POST:[{port_int}] 登录账户名:[{username}] 登录密码:[{password}] 订阅主题:[{topic_subscribe_list}]  ")
            client = mqtt_client.Client(client_id)
            client.on_connect = on_connect
            client.on_connect_fail = on_connect_fail
            client.reconnect_delay_set(min_delay=10, max_delay=120)
            # client.username_pw_set("admin", "password")
            client.username_pw_set(username, password)  # 账户密码
            # broker = 'broker.emqx.io'
            # port = 1883
            # client.connect(broker, port)
            # client.connect(host='127.0.0.1', port=1883)
            client.connect(host=host_str, port=port_int)  # IP和端口
            is_run = True
        except Exception as e:
            logger.get_log().error(f"[MQTT] 创建链接失败!异常:{e}")
            time.sleep(10)  # 休眠10秒之后重新创建链接
    return client


'''
订阅消息
'''


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        # TODO 接到消息处理
        try:
            message = msg.payload.decode()
            logger.get_log().info(f"[MQTT] 收到来自订阅[{msg.topic}]的消息为:{message}")
            msg_topic = msg.topic

            my_callback = f"/{ini_serialNumber}/callback"  # 回调，这里测试时自己捕获用于调试
            my_status_base = f"/{ini_serialNumber}/status/base"  # 5.3.1 机库基础状态常量
            my_status_upgrade = f"/{ini_serialNumber}/status/upgrade"  # 5.3.9 机库基础状态常量
            my_sys_motor = f"/{ini_serialNumber}/sys/motor"  # 8.2.2 舱门控制 8.2.3 归中装置控制
            my_sys_power = f"/{ini_serialNumber}/sys/power"  # 8.3.5 无人机开关机 8.3.6 无人机充电
            my_sys_general = f"/{ini_serialNumber}/sys/general"  # 8.4.4 查询机库固件版本号 8.4.5 下发更新机库固件命令（暂不支持） 8.4.6 机巣上传日志至平台服务器 8.4.7 机巣取消上传日志至平台服务器

            if msg_topic == my_sys_motor:
                thread_do_sys_motor = Thread(target=do_sys_motor, args=([msg_topic, message]), daemon=True)
                thread_do_sys_motor.start()
            elif msg_topic == my_sys_power:
                thread_do_sys_power = Thread(target=do_sys_power, args=([msg_topic, message]), daemon=True)
                thread_do_sys_power.start()
            elif msg_topic == my_sys_general:
                thread_do_sys_general = Thread(target=do_sys_general, args=([msg_topic, message]), daemon=True)
                thread_do_sys_general.start()
            else:
                logger.get_log().info(f"[MQTT] 订阅[{msg.topic}]不在处理业务范围内")
        except Exception as e:
            logger.get_log().error(f"[MQTT] 处理消息发生异常!异常:{e}")

    client.subscribe(topic_subscribe_list, qos=2)  # 订阅具体topic的消息
    client.on_message = on_message


'''
下发消息
'''


def publish(topic_publish, message):
    # logger.get_log().info(f"[MQTT][publish]准备下发消息内容为:{message}")
    global client_publish
    if client_publish is not None:
        # time.sleep(10)  # 正常走不到这个流程里，正常会有链接对象，等待10秒怎么也链接上了
        logger.get_log().info(f"[MQTT][publish]执行下发消息,主题：{topic_publish},消息:{message}")
        result = client_publish.publish(topic_publish, message, qos=0)
        status = result[0]
        logger.get_log().info(f"[MQTT][publish]执行下发消息后收到应答码:{status}  含义:{rc_status[status]}")


def publish_debug_log(topic_publish, message):
    logger.get_log().debug(f"[MQTT][publish]准备下发消息内容为:{message}")
    global client_publish
    if client_publish is None:
        time.sleep(10)  # 正常走不到这个流程里，正常会有链接对象，等待10秒怎么也链接上了
    logger.get_log().debug(f"[MQTT][publish]执行下发消息:{message}")
    result = client_publish.publish(topic_publish, message, qos=0)
    status = result[0]
    logger.get_log().debug(f"[MQTT][publish]执行下发消息后收到应答码:{status}  含义:{rc_status[status]}")


def run():
    # 本地测试方法
    client = connect_mqtt()
    # subscribe(client)
    client.loop_forever()


'''
线程启动MQTT[南方电力定制]
'''


def run_status_base():
    time.sleep(10)  # 晚10秒启动推送，给MQTT链接创造时间
    while True:
        try:
            do_status_base()
            time.sleep(BASEUtile.InitFileTool.get_int_value("nanfangdianwang_info", "do_status_base_time"))  # 休眠X秒就推送
        except Exception as e:
            logger.get_log().error(f"[MQTT] do_status_base 发生异常{e}")
            time.sleep(10)  # 异常后晚10秒启动推送，给MQTT链接创造时间


def start_mqtt_thread_nanfangdianwang(web_client, logger_in):
    global logger
    logger = logger_in
    global webclient
    webclient = web_client
    # global hangstate
    # hangstate = hang_state
    logger.get_log().info("[MQTT] 启动 MQTT 任务线程 [开始]")
    # print(f"hangstate.getHangerState={hangstate.getHangerState()}")
    # print(f"hangstate.get_state_dict()={hangstate.get_state_dict()}")
    thread = Thread(target=run, args=([]), daemon=True)
    thread.start()
    logger.get_log().info("[MQTT] 启动 MQTT 主接收发送任务线程 [完成]")

    # thread_status_base = Thread(target=run_status_base, args=([]), daemon=True)
    # thread_status_base.start()
    # logger.get_log().info("[MQTT] 启动 [/status/base]定时推送机库注册信息线程 [完成]")

    logger.get_log().info("[MQTT] 启动 MQTT 任务线程 [结束]")

    '''
    下发消息构建
    '''


def make_result_message(msgType, msgCode, msgExplain, respCode, respMsg):
    result_message = {
        "msgType": msgType,
        "msgCode": msgCode,
        "msgExplain": msgExplain,
        "data": {
            "respCode": respCode,
            "respMsg": respMsg
        }
    }
    return json.dumps(result_message, ensure_ascii=False)


'''
各个指令接口的处理
'''


def do_status_base():
    topic_publish = f"/{ini_serialNumber}/status/base"  # 5.3.1 机库基础状态常量
    result_message = {
        "aircraftStateConstant": "UNKNOWN",  # 无人机状态
        "isConnected": True,  # 是否连接 TODO 什么是否链接
        "isAircraftConnected": False,  # 无人机是否连接 TODO 不清楚
        "nestStateConstant": "STANDBY",  # 机库状态  TODO 大量状态不是机库自己能掌握的
        "isRemoteControllerConnected": False,  # 遥控器是否连接 TODO 不清楚
        "isRemotePowerOn": False,  # 遥控器是否开机 TODO 不清楚
        "isAntPowerOn": True,  # 天线是否打开 TODO 不涉及
        "nestBatteryAvailable": 0  # 机库内电池数量 TODO 我们没有
    }
    result_json = json.dumps(result_message, ensure_ascii=False)
    # publish(topic_publish, result_json)  # TODO 正式版本注释 正式时候切换debug日志
    publish_debug_log(topic_publish, result_json)


def do_status_upgrade():
    topic_publish = f"/{ini_serialNumber}/status/upgrade"  # 5.3.9 机库基础状态常量
    result_message = {
        "version": "V2.0.6",
        "state": "unknown",
        "progress": 95.5,
        "remark": None,
        "date": 15581616472
    }


def do_sys_motor(msg_topic, message):
    topic_subscribe = f"/{ini_serialNumber}/sys/motor"  # 8.2.2 舱门控制 8.2.3 归中装置控制
    topic_publish = f"/{ini_serialNumber}/callback"
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT][do_sys_motor]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    '''
    code
    1001 请求成功
    4000 未知错误
    4001 飞机错误
    4002 Json 错误
    4003 数据库错误
    4004 设备未连接错误
    4005 端口错误
    4006 参数错误
    9001 机库不空闲/不可用
    9002 任务不存在
    9003 任务启动取消
    '''
    result_message = {
        "code": 1001,
        "pCode": "15001",
        "msg": "success",
        "date": 0
    }
    params = json.loads(message)
    if "code" in params:
        code = params["code"]
        result_message["pCode"] = code  # pCode为之前传入的code
        logger.get_log().info(f"[MQTT]执行[/sys/motor_{code}][开始]")
        if code == "15001":  # 15001: 舱门控制-打开
            result = OperateUtil.operate_hangar("140000")
            # result = "9140"  # TODO 正式版本注释 放开正式操作
            logger.get_log().info(f"[MQTT]执行[/sys/motor_{code}][打开舱门][结束]底层下位机接口应答结果[{result}]")
            if not result.endswith("0"):
                result_message["code"] = 4000
                result_message["msg"] = result
        elif code == "15002":  # 15002: 舱门控制-关门
            result = OperateUtil.operate_hangar("150000")
            # result = "9150"  # TODO 正式版本注释 放开正式操作
            logger.get_log().info(f"[MQTT]执行[/sys/motor_{code}][关闭舱门][结束]底层下位机接口应答结果[{result}]")
            if not result.endswith("0"):
                result_message["code"] = 4000
                result_message["msg"] = result
        elif code == "15011":  # 15011: 归中机构控制-夹紧
            result = OperateUtil.operate_hangar("2e10002000")
            # result = "92e0"  # TODO 正式版本注释 放开正式操作
            logger.get_log().info(f"[MQTT]执行[/sys/motor_{code}][夹紧推杆][结束]底层下位机接口应答结果[{result}]")
            if not result.endswith("0"):
                result_message["code"] = 4000
                result_message["msg"] = result
        elif code == "15012":  # 15012: 归中机构控制-松开
            result = OperateUtil.operate_hangar("500000")
            # result = "9500"  # TODO 正式版本注释 放开正式操作
            logger.get_log().info(f"[MQTT]执行[/sys/motor_{code}][松开推杆][结束]底层下位机接口应答结果[{result}]")
            if not result.endswith("0"):
                result_message["code"] = 4000
                result_message["msg"] = result
        else:
            logger.get_log().info(f"[MQTT]执行[/sys/motor_{code}][不支持的指令][结束]")
            result_message["code"] = 4000
            result_message["msg"] = "不支持的指令"
        result_message["date"] = int(time.time())
        result_json = json.dumps(result_message, ensure_ascii=False)
        publish(topic_publish, result_json)
    else:
        logger.get_log().info(f"[MQTT]非法结构，不处理")


def do_sys_power(msg_topic, message):
    topic_subscribe = f"/{ini_serialNumber}/sys/power"
    topic_publish = f"/{ini_serialNumber}/callback"
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT][do_sys_power][{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    '''
    code
    1001 请求成功
    4000 未知错误
    4001 飞机错误
    4002 Json 错误
    4003 数据库错误
    4004 设备未连接错误
    4005 端口错误
    4006 参数错误
    9001 机库不空闲/不可用
    9002 任务不存在
    9003 任务启动取消
    '''
    result_message = {
        "code": 1001,
        "pCode": "",
        "msg": "success",
        "date": 0
    }
    params = json.loads(message)
    if "code" in params:
        code = params["code"]
        result_message["pCode"] = code  # pCode为之前传入的code
        logger.get_log().info(f"[MQTT]执行[/sys/power_{code}][开始]")
        if code == "17012":  # 17012: 无人机-开机
            result = OperateUtil.operate_hangar("dt0000")
            # result = "9dt0"  # TODO 正式版本注释 放开正式操作
            logger.get_log().info(f"[MQTT]执行[/sys/power_{code}][无人机开机][结束]底层下位机接口应答结果[{result}]")
            if not result.endswith("0"):
                result_message["code"] = 4000
                result_message["msg"] = result
        elif code == "17013":  # 17013: 无人机-关机
            result = OperateUtil.operate_hangar("dd0000")
            # result = "9dd0"  # TODO 正式版本注释 放开正式操作
            logger.get_log().info(f"[MQTT]执行[/sys/power_{code}][无人机关机][结束]底层下位机接口应答结果[{result}]")
            if not result.endswith("0"):
                result_message["code"] = 4000
                result_message["msg"] = result
        elif code == "17007":  # 17007: 无人机-充电
            result = OperateUtil.operate_hangar("cp0000")
            # result = "9cp0"  # TODO 正式版本注释 放开正式操作
            logger.get_log().info(f"[MQTT]执行[/sys/power_{code}][无人机充电][结束]底层下位机接口应答结果[{result}]")
            if not result.endswith("0"):
                result_message["code"] = 4000
                result_message["msg"] = result
        elif code == "17008":  # 17008: 无人机-待机(停止充电)
            result = OperateUtil.operate_hangar("sb0000")
            # result = "9sb0"  # TODO 正式版本注释 放开正式操作
            logger.get_log().info(f"[MQTT]执行[/sys/power_{code}][无人机待机][结束]底层下位机接口应答结果[{result}]")
            if not result.endswith("0"):
                result_message["code"] = 4000
                result_message["msg"] = result
        else:
            logger.get_log().info(f"[MQTT]执行[/sys/power_{code}][不支持的指令][结束]")
            result_message["code"] = 4000
            result_message["msg"] = "不支持的指令"
        result_message["date"] = int(time.time())
        result_json = json.dumps(result_message, ensure_ascii=False)
        publish(topic_publish, result_json)
    else:
        logger.get_log().info(f"[MQTT]非法结构，不处理")


def do_sys_general(msg_topic, message):
    topic_subscribe = f"/{ini_serialNumber}/sys/general"
    topic_publish = f"/{ini_serialNumber}/callback"
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT][do_sys_general][{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    '''
        code
        1001 请求成功
        4000 未知错误
        4001 飞机错误
        4002 Json 错误
        4003 数据库错误
        4004 设备未连接错误
        4005 端口错误
        4006 参数错误
        9001 机库不空闲/不可用
        9002 任务不存在
        9003 任务启动取消
        '''
    result_message = {
        "code": 1001,
        "pCode": "",
        "msg": "success",
        "date": 0
    }
    params = json.loads(message)
    if "code" in params and "param" in params:
        code = params["code"]
        param = params["param"]
        result_message["pCode"] = code  # pCode为之前传入的code
        if code == "314002":  # 314002: 查看固件版本
            if "firmwareType" not in param:
                logger.get_log().info(f"[MQTT][do_sys_general][缺失firmwareType参数]")
                result_message["code"] = 4006
                result_message["msg"] = "参数错误"
            else:
                param_firmwareType = param["firmwareType"]
                if param_firmwareType == 0:  # TODO 不知道param_firmwareType 值那个是机库的，先按照0默认算
                    result_message["param"] = {}
                    result_message["param"]["version"] = BASEUtile.InitFileTool.get_str_value("nanfangdianwang_info",
                                                                                              "version")
                    result_message["param"]["firmwareType"] = param_firmwareType
                else:
                    return  # 不是发给机库的，不做应答
        elif code == "314003":  # 314003: 机巣上传日志至平台服务器
            required_fields = ["userId", "startDateTime", "endDateTime", "uploadUrl", "firmwareType"]
            if check_fields(data=param, fields=required_fields):
                param_userId = param["userId"]
                param_startDateTime = param["startDateTime"]
                param_endDateTime = param["endDateTime"]
                param_uploadUrl = param["uploadUrl"]
                param_firmwareType = param["firmwareType"]

                if param_firmwareType == 3:  # TODO 不知道param_firmwareType 值那个是机库的，先按照3这个机库SDK算
                    # 日期只取前19位 YYYY-MM-DD
                    param_startDateTime = str(param_startDateTime)[0:10]
                    param_endDateTime = str(param_endDateTime)[0:10]
                    logger.get_log().info(
                        f"[MQTT][do_sys_general][解析后参数][{param_userId}][{param_startDateTime}][{param_endDateTime}][{param_uploadUrl}][{param_firmwareType}]")
                    try:
                        filelist = logger.getLogFiles(starttime=param_startDateTime, endtime=param_endDateTime)
                        # 异步上传文件，结束处理
                        thread_do_log_http_post = Thread(target=do_log_http_post, args=(
                            [filelist, param_userId, param_uploadUrl, param_firmwareType]), daemon=True)
                        thread_do_log_http_post.start()

                    except Exception as e:
                        logger.get_log().info(f"[MQTT][do_sys_general][查找日志文件错误]")
                        result_message["code"] = 4006
                        result_message["msg"] = "参数错误"
                else:
                    return  # 不是发给机库的，不做应答

            else:
                logger.get_log().info(f"[MQTT][do_sys_general][缺失参数]")
                result_message["code"] = 4006
                result_message["msg"] = "参数错误"
        else:
            return  # 不是发给机库的，不做应答
        # 统一返回应答
        result_message["date"] = int(time.time())
        result_json = json.dumps(result_message, ensure_ascii=False)
        publish(topic_publish, result_json)
    else:
        logger.get_log().info(f"[MQTT]非法结构，不处理")


def do_log_http_post(filelist, param_userId, param_uploadUrl, param_firmwareType):
    for file_path in filelist:
        try:
            logger.get_log().info(f"[MQTT][do_log_http_post]上传文件[{file_path}]开始")
            request_obj = {
                "airportID": "airportID",
                "userID": f"{param_userId}",
                "firmwareType": param_firmwareType
            }
            with open(rf"{file_path}", 'rb') as file:  # 二进制方式打开
                up_files = {'file': file}
                r = requests.post(param_uploadUrl, data=request_obj, files=up_files)
                logger.get_log().info(f"[MQTT][do_log_http_post]上传文件[{file_path}]返回应答：{r.text}")
        except Exception as e:
            logger.get_log().error(f"[MQTT][do_log_http_post]处理机巢日志[{file_path}]发生异常：{e}")


def check_fields(data, fields):
    for field in fields:
        if not data.get(field):
            return False
    return True


if __name__ == '__main__':
    # run()
    logger.get_log().info("====1")
    start_mqtt_thread_nanfangdianwang(None, None)
    logger.get_log().info("====2")
    time.sleep(1)
    # test_message = {
    #     "code": "15001"
    # }
    #
    # test_message["code"] = "15001"
    # publish(f"/{ini_serialNumber}/sys/motor", json.dumps(test_message))
    # time.sleep(5)
    #
    # test_message["code"] = "15002"
    # publish(f"/{ini_serialNumber}/sys/motor", json.dumps(test_message))
    # time.sleep(5)
    #
    # test_message["code"] = "15011"
    # publish(f"/{ini_serialNumber}/sys/motor", json.dumps(test_message))
    # time.sleep(5)
    #
    # test_message["code"] = "15012"
    # publish(f"/{ini_serialNumber}/sys/motor", json.dumps(test_message))
    # time.sleep(5)
    #
    # test_message["code"] = "17012"
    # publish(f"/{ini_serialNumber}/sys/power", json.dumps(test_message))
    # time.sleep(5)
    #
    # test_message["code"] = "17013"
    # publish(f"/{ini_serialNumber}/sys/power", json.dumps(test_message))
    # time.sleep(5)
    #
    # test_message["code"] = "17007"
    # publish(f"/{ini_serialNumber}/sys/power", json.dumps(test_message))
    # time.sleep(5)
    #
    # test_message["code"] = "17008"
    # publish(f"/{ini_serialNumber}/sys/power", json.dumps(test_message))
    # time.sleep(5)
    #
    # test_message["code"] = "314002"
    # test_message["param"] = {}
    # test_message["param"]["firmwareType"] = 0
    #
    # publish(f"/{ini_serialNumber}/sys/general", json.dumps(test_message))
    # time.sleep(5)
    #
    # test_message["code"] = "314003"
    # test_message["param"] = {
    #     "userId": 1234567890,
    #     "startDateTime": "2024-03-15 11:00:00",
    #     "endDateTime": "2024-03-16 11:00:00",
    #     "uploadUrl": r"http://127.0.0.1:4523/m1/1148311-0-default/uplogNanWangDianLi",
    #     "firmwareType": 3
    # }
    # publish(f"/{ini_serialNumber}/sys/general", json.dumps(test_message))
    # time.sleep(5)

    time.sleep(600)
