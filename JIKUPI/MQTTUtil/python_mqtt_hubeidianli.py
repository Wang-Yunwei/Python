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
from BASEUtile import HangerState
from BASEUtile.logger import Logger

logger = Logger(__name__)  # 日志记录

ini_serialNumber = BASEUtile.InitFileTool.get_str_value("hubeidianli_info", "serialNumber")

# 操控系统下发命令主题(通配表达式#会多捕获自己的应答，所以采用元组方式)
topic_subscribe_list = [
    # (f"/api/machine/nest/information_{ini_serialNumber}", 2),  # 1.2.1 机巢基础信息 # 上报无需订阅
    # (f"/api/machine/nest/info_{ini_serialNumber}", 2),  # 1.2.2 机巢状态信息
    # (f"/api/machine/nest/env/info_{ini_serialNumber}", 2),  # 1.2.3 机巢环境信息
    # (f"/api/machine/nest/alarm_{ini_serialNumber}", 2),  # 1.2.4 机巢告警信息
    (f"/api/machine/nest/control_{ini_serialNumber}", 2),  # 1.2.5 机巢控制指令
    (f"/api/machine/nest/time_{ini_serialNumber}", 2),  # 1.2.6 机巢对时指令
    (f"/api/machine/nest/logControl_{ini_serialNumber}", 2)  # 1.2.7 机巢远程日志控制
]
# topic_publish = ""  # 终端系统反馈执行结果主题(应答主题改为每个接口不同了)
client_id = 'jiku-001'  # 客户端id

client_publish = None  # 用于推送消息的客户端
webclient = None  # websocket推送线程
hangstate = None  # 机库状态信息

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
            do_code_information()  # 注册成功时自动发送机库信息

        else:
            logger.get_log().info(f"[MQTT]链接 MQTT 失败！, 错误码: {rc}  错误信息: {rc_status[rc]}")

    def on_connect_fail(client, userdata):
        logger.get_log().error("[MQTT] 链接已断开，重连失败!")

    # 循环重新链接，直到连接上为止
    is_run = False
    while not is_run:
        try:
            # 从ini中读取运行配置信息
            host_str = BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "mqttHost")
            port_int = BASEUtile.InitFileTool.get_int_value("mqtt_edit_info", "mqttPort")
            username = BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "mqttUserName")
            password = BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "mqttPassWord")

            global client_id
            client_id = BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "serialNumber")

            logger.get_log().info(
                f"[MQTT]启动创建MQTT链接，登录MTQQ服务器客户端ID:[{client_id}] 服务IP:[{host_str}] 服务POST:[{port_int}] 登录账户名:[{username}] 登录密码:[{password}] 订阅主题:[{topic_subscribe_list}]  ")
            client = mqtt_client.Client(client_id)
            client.on_connect = on_connect
            client.on_connect_fail = on_connect_fail
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
            my_control_topic = f"/api/machine/nest/control_{ini_serialNumber}"
            my_time_topic = f"/api/machine/nest/time_{ini_serialNumber}"
            my_logControl_topic = f"/api/machine/nest/logControl_{ini_serialNumber}"

            if msg_topic == my_control_topic:
                do_code_control(msg_topic, message)
            elif msg_topic == my_time_topic:
                do_code_time(msg_topic, message)
            elif msg_topic == my_logControl_topic:
                do_code_log(msg_topic, message)
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
    logger.get_log().info(f"[MQTT][publish]准备下发消息内容为:{message}")
    global client_publish
    if client_publish is None:
        time.sleep(10)  # 正常走不到这个流程里，正常会有链接对象，等待10秒怎么也链接上了
    logger.get_log().info(f"[MQTT][publish]执行下发消息:{message}")
    result = client_publish.publish(topic_publish, message, qos=2)
    status = result[0]
    logger.get_log().info(f"[MQTT][publish]执行下发消息后收到应答码:{status}  含义:{rc_status[status]}")


def publish_debug_log(topic_publish, message):
    logger.get_log().debug(f"[MQTT][publish]准备下发消息内容为:{message}")
    global client_publish
    if client_publish is None:
        time.sleep(10)  # 正常走不到这个流程里，正常会有链接对象，等待10秒怎么也链接上了
    logger.get_log().debug(f"[MQTT][publish]执行下发消息:{message}")
    result = client_publish.publish(topic_publish, message, qos=2)
    status = result[0]
    logger.get_log().debug(f"[MQTT][publish]执行下发消息后收到应答码:{status}  含义:{rc_status[status]}")


def run():
    # 本地测试方法
    client = connect_mqtt()
    # subscribe(client)
    client.loop_forever()


'''
线程启动MQTT[电信定制]
'''


def run_information():
    time.sleep(10)  # 晚10秒启动推送，给MQTT链接创造时间
    while True:
        try:
            do_code_information()
            time.sleep(BASEUtile.InitFileTool.get_int_value("hubeidianli_info", "do_code_information_time"))  # 休眠X秒就推送
        except Exception as e:
            logger.get_log().error(f"[MQTT] do_code_information_time发生异常{e}")
            time.sleep(10)  # 异常后晚10秒启动推送，给MQTT链接创造时间


def run_info():
    time.sleep(10)  # 晚10秒启动推送，给MQTT链接创造时间
    while True:
        try:
            do_code_info()
            time.sleep(BASEUtile.InitFileTool.get_int_value("hubeidianli_info", "do_code_info_time"))  # 休眠X秒就推送
        except Exception as e:
            logger.get_log().error(f"[MQTT] do_code_info发生异常{e}")
            time.sleep(10)  # 异常后晚10秒启动推送，给MQTT链接创造时间


def run_env_info():
    time.sleep(10)  # 晚10秒启动推送，给MQTT链接创造时间
    while True:
        try:
            do_code_env_info()
            time.sleep(BASEUtile.InitFileTool.get_int_value("hubeidianli_info", "do_code_env_info_time"))  # 休眠X秒就推送
        except Exception as e:
            logger.get_log().error(f"[MQTT] do_code_env_info发生异常{e}")
            time.sleep(10)  # 异常后晚10秒启动推送，给MQTT链接创造时间


def run_alarm():
    time.sleep(10)  # 晚10秒启动推送，给MQTT链接创造时间
    while True:
        try:
            do_code_alarm()
            time.sleep(BASEUtile.InitFileTool.get_int_value("hubeidianli_info", "do_code_alarm_time"))  # 休眠X秒就推送
        except Exception as e:
            logger.get_log().error(f"[MQTT] do_code_alarm发生异常{e}")
            time.sleep(10)  # 异常后晚10秒启动推送，给MQTT链接创造时间


def start_mqtt_thread_hubeidianli(web_client, hang_state):
    logger.get_log().info("[MQTT] 启动 MQTT 任务线程 [开始]")
    global webclient
    webclient = web_client
    global hangstate
    hangstate = hang_state
    # print(f"hangstate.getHangerState={hangstate.getHangerState()}")
    # print(f"hangstate.get_state_dict()={hangstate.get_state_dict()}")
    thread = Thread(target=run, args=([]), daemon=True)
    thread.start()
    logger.get_log().info("[MQTT] 启动 MQTT 主接收发送任务线程 [完成]")

    thread_information = Thread(target=run_information, args=([]), daemon=True)
    thread_information.start()
    logger.get_log().info("[MQTT] 启动 information定时推送机库注册信息线程 [完成]")

    thread_info = Thread(target=run_info, args=([]), daemon=True)
    thread_info.start()
    logger.get_log().info("[MQTT] 启动 info定时推送机库状态线程 [完成]")

    thread_env_info = Thread(target=run_env_info, args=([]), daemon=True)
    thread_env_info.start()
    logger.get_log().info("[MQTT] 启动 env_info定时推送机库环境信息线程 [完成]")

    # thread_alarm = Thread(target=run_alarm, args=([]), daemon=True)
    # thread_alarm.start()
    # logger.get_log().info("[MQTT] 启动 alarm定时推送告警线程 [完成]")

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


def do_code_information():
    topic_publish = f"/api/machine/nest/information_{ini_serialNumber}"  # 1.2.1 机巢基础信息
    tid = uuid.uuid4()
    result_message = {
        "key": f"{ini_serialNumber}",
        "tid": f"{tid}",
        "softwareVersion": BASEUtile.InitFileTool.get_str_value("hubeidianli_info", "softwareVersion"),
        "hardwareVersion": BASEUtile.InitFileTool.get_str_value("hubeidianli_info", "hardwareVersion"),
        "produceDate": BASEUtile.InitFileTool.get_str_value("hubeidianli_info", "produceDate"),
        "nestType": BASEUtile.InitFileTool.get_str_value("hubeidianli_info", "nestType"),
        "nestManufacture": BASEUtile.InitFileTool.get_str_value("hubeidianli_info", "nestManufacture"),
        "nestSnCode": BASEUtile.InitFileTool.get_str_value("hubeidianli_info", "nestSnCode")
    }
    result_json = json.dumps(result_message, ensure_ascii=False)
    publish(topic_publish, result_json)


def do_code_info():
    topic_publish = f"/api/machine/nest/info_{ini_serialNumber}"  # 1.2.2 机巢状态信息
    tid = uuid.uuid4()

    cabinDoorStatus_result = hangstate.get_hanger_door()
    cabinDoorStatus = 2  # 2: 舱门关闭
    if cabinDoorStatus_result == "open":
        cabinDoorStatus = 1  # 1: 舱门开启

    clampStatus_result = hangstate.get_hanger_bar()
    clampStatus = 1  # 1: 夹紧器夹紧
    if clampStatus_result == "open":
        clampStatus = 2  # 2: 夹紧器打开

    airconditionStatus_result = hangstate.get_air_condition()
    airconditionStatus = 2  # 2: 空调关闭
    if airconditionStatus_result == "open":
        airconditionStatus = 1  # 1: 空调打开

    chargerStatus_result = hangstate.get_wfcstate()
    chargerStatus = 2  # 2: 无人机充电关闭
    if chargerStatus_result == "charging":
        chargerStatus = 1  # 1: 无人机充电打开

    if clampStatus_result == "open":  # 推杆打开了，就是未知
        UAVStatus = 0  # 0: 未知
    elif chargerStatus_result == "charging":  # 充电呢 只考虑御3
        UAVStatus = 1  # 1: 无人机开机
    elif chargerStatus_result == "takeoff":  # 开机执行中 只考虑御3
        UAVStatus = 1  # 1: 无人机开机
    elif chargerStatus_result == "close":  # 关机情况 只考虑御3
        UAVStatus = 2  # 2: 无人机关闭
    else:
        UAVStatus = 0  # 0: 未知

    uavLightStatus_result = hangstate.get_night_light_state()
    uavLightStatus = 0  # 0: 开启
    if uavLightStatus_result == "close":
        uavLightStatus = 1  # 1: 关闭

    result_message = {
        "key": f"{ini_serialNumber}",
        "tid": f"{tid}",
        "joyStickStatus": 1,  # 手柄 固定为1 在线
        "UAVStatus": UAVStatus,  # 无人机状态
        "cabinDoorStatus": cabinDoorStatus,  # 机库门状态
        "clampStatus": clampStatus,  # 归中机构(推杆)状态
        "liftStatus": 0,  # 升降台 固定为0 未知
        "airconditionStatus": airconditionStatus,  # 空调状态
        "chargerStatus": chargerStatus,  # 无人机充电状态
        "uavNestStatus": 0,  # 机巢 固定为0 待命
        "uavLightStatus": uavLightStatus,  # 照明状态
        "chargerCurrent": 0.0  # 充电电流 未知故暂时上报0
    }
    result_json = json.dumps(result_message, ensure_ascii=False)
    publish(topic_publish, result_json)


def do_code_env_info():
    topic_publish = f"/api/machine/nest/env/info_{ini_serialNumber}"  # 1.2.3 机巢环境信息
    tid = uuid.uuid4()

    externalWindPower_str = hangstate.get_windspeed()
    externalWindPower = 0.0
    if externalWindPower_str is not None:
        externalWindPower = float(externalWindPower_str)
        externalWindPower = externalWindPower + 1.1  # TODO 检测值 追加1.1

    externalWindDirection_result = hangstate.get_winddirection()
    if externalWindDirection_result == "北风":
        externalWindDirection = 1
    elif externalWindDirection_result == "东北风":
        externalWindDirection = 2
    elif externalWindDirection_result == "东风":
        externalWindDirection = 3
    elif externalWindDirection_result == "东南风":
        externalWindDirection = 4
    elif externalWindDirection_result == "南风":
        externalWindDirection = 5
    elif externalWindDirection_result == "西南风":
        externalWindDirection = 6
    elif externalWindDirection_result == "西风":
        externalWindDirection = 7
    elif externalWindDirection_result == "西北风":
        externalWindDirection = 8
    elif externalWindDirection_result == "北":  # 旧版本一个特性代指[兼容]
        externalWindDirection = 1
    else:
        externalWindDirection = 1  # 默认北风

    interiorHumidity = hangstate.get_indoor_hum()  # 机库内湿度
    interiorAirTemperature = hangstate.get_indoor_tem()  # 机库内温度

    result_message = {
        "key": f"{ini_serialNumber}",
        "tid": f"{tid}",
        "externalRainfall": 0.1,  # 外部雨量 单位: mm/d  没有 TODO 检测值
        "uv": 0.0,  # 紫外线强度 可选项，单位: uW/cm2  没有
        "interiorHumidity": interiorHumidity,  # 内部湿度 单位: %
        "interiorAirTemperature": interiorAirTemperature,  # 内部温度 单位: ℃
        "light": 0.0,  # 光照强度 可选项，单位: LUX  没有
        "externalWindPower": externalWindPower,  # 外部风速 单位: m/s TODO 检测值
        "externalAirTemperature": -4.2,  # 外部温度 单位: ℃  没有  TODO 检测值
        "externalHumidity": 39.0,  # 外部湿度 单位: %  没有  TODO 检测值
        "externalAirPressure": 1.0,  # 外部气压 单位: Pa  没有  TODO 检测值
        "externalWindDirection": externalWindDirection,
        # 外部风向 0: WINDLESS 1: NORTH 2: NORTH_EAST 3: EAST 4: SOUTH_EAST
        # 5: SOUTH 6: SOUTH_WEST 7: WEST 8: NORTH_WEST -1: UNKNOWN
        "others": ""  # 其他传感器
    }
    result_json = json.dumps(result_message, ensure_ascii=False)
    publish(topic_publish, result_json)


def do_code_alarm():
    topic_publish = f"/api/machine/nest/alarm_{ini_serialNumber}"  # 1.2.4 机巢告警信息
    tid = uuid.uuid4()
    result_message = {
        "key": f"{ini_serialNumber}",
        "tid": f"{tid}",
        "time": "",
        "content": "",
        "type": "",
        "code": ""
    }
    result_json = json.dumps(result_message, ensure_ascii=False)
    publish(topic_publish, result_json)


def do_code_control(msg_topic, message):
    topic_subscribe = f"/api/machine/nest/control_{ini_serialNumber}"
    topic_publish = f"/api/machine/requestResult_{ini_serialNumber}"
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]control的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    result_message = {
        "key": f"{ini_serialNumber}",
        "tid": "",
        "api": f"/api/machine/nest/control_{ini_serialNumber}",
        "message": "ok",
        "result": True
    }
    params = json.loads(message)
    if "key" in params and "tid" in params and "type" in params and "parameter" in params:
        key = params["key"]
        tid = params["tid"]
        type = params["type"]
        parameter = params["parameter"]
        result_message["tid"] = tid  # 初始化应答tid
        if key != ini_serialNumber:
            logger.get_log().info(f"[MQTT]control接入的设备ID[{key}]与本地设备ID[{ini_serialNumber}]不一致，不处理")
            return
        logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][开始]")
        if type == 1:  # 1: 舱门控制
            if parameter == 0:  # 无操作
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            elif parameter == 1:  # 打开
                result = webclient.step_scene_door_open_140000()
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][结束]底层下位机接口应答结果[{result}]")
                if not result.endswith("0"):
                    result_message["message"] = "打开舱门失败"
                    result_message["result"] = False
            elif parameter == 2:  # 关闭
                result = webclient.step_scene_door_close_150000()
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][结束]底层下位机接口应答结果[{result}]")
                if not result.endswith("0"):
                    result_message["message"] = "关闭舱门失败"
                    result_message["result"] = False
            elif parameter == 3:  # 复位
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            elif parameter == 4:  # 停止
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            else:
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][不存在，无需操作]")
                return
        elif type == 2:  # 2: 升降台控制
            if parameter == 0:  # 无操作
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            elif parameter == 1:  # 下降
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            elif parameter == 2:  # 上升
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            elif parameter == 3:  # 复位
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            elif parameter == 4:  # 停止
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            else:
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][不存在，无需操作]")
                return
        elif type == 3:  # 3: 归中机构控制
            if parameter == 0:  # 无操作
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            elif parameter == 1:  # 展开
                result = webclient.step_scene_bar_reset_500000()
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][结束]底层下位机接口应答结果[{result}]")
                if not result.endswith("0"):
                    result_message["message"] = "归中机构展开失败"
                    result_message["result"] = False
            elif parameter == 2:  # 归中
                result = webclient.step_scene_bar_close_2e10002000()
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][结束]底层下位机接口应答结果[{result}]")
                if not result.endswith("0"):
                    result_message["message"] = "归中机构归中失败"
                    result_message["result"] = False
            elif parameter == 3:  # 复位
                result = webclient.step_scene_bar_reset_500000()
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][结束]底层下位机接口应答结果[{result}]")
                if not result.endswith("0"):
                    result_message["message"] = "归中机构复位失败"
                    result_message["result"] = False
            elif parameter == 4:  # 停止
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            else:
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][不存在，无需操作]")
                return
        elif type == 4:  # 4: 无人机开关控制
            if parameter == 0:  # 无操作
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            elif parameter == 1:  # 开启
                result = webclient.step_scene_drone_takeoff_dt0000()
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][结束]底层下位机接口应答结果[{result}]")
                if not result.endswith("0"):
                    result_message["message"] = "无人机开机失败"
                    result_message["result"] = False
            elif parameter == 2:  # 关闭
                result = webclient.step_scene_drone_off_dd0000()
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][结束]底层下位机接口应答结果[{result}]")
                if not result.endswith("0"):
                    result_message["message"] = "无人机关机失败"
                    result_message["result"] = False
            elif parameter == 3:  # 重置
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            else:
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][不存在，无需操作]")
                return
        elif type == 5:  # 5: 遥控器开关控制
            if parameter == 0:  # 无操作
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            elif parameter == 1:  # 开启
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            elif parameter == 2:  # 关闭
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            elif parameter == 3:  # 重置
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            else:
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][不存在，无需操作]")
                return
        elif type == 6:  # 6: 无人机充电控制
            if parameter == 0:  # 无操作
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            elif parameter == 1:  # 开启
                result = webclient.step_scene_drone_charge_cp0000()
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][结束]底层下位机接口应答结果[{result}]")
                if not result.endswith("0"):
                    result_message["message"] = "无人机开启充电失败"
                    result_message["result"] = False
            elif parameter == 2:  # 关闭
                result = webclient.step_scene_drone_standby_sb0000()
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][结束]底层下位机接口应答结果[{result}]")
                if not result.endswith("0"):
                    result_message["message"] = "无人机关闭充电失败"
                    result_message["result"] = False
            elif parameter == 3:  # 重置
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            else:
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][不存在，无需操作]")
                return
        elif type == 7:  # 7: 空调控制
            if parameter == 0:  # 无操作
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            elif parameter == 1:  # 开启
                result = webclient.step_scene_air_open_300000()
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][结束]底层下位机接口应答结果[{result}]")
                if not result.endswith("0"):
                    result_message["message"] = "空调开启失败"
                    result_message["result"] = False
            elif parameter == 2:  # 关闭
                result = webclient.step_scene_air_close_310000()
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][结束]底层下位机接口应答结果[{result}]")
                if not result.endswith("0"):
                    result_message["message"] = "空调关闭失败"
                    result_message["result"] = False
            elif parameter == 3:  # 复位
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            elif parameter == 4:  # 停止
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            else:
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][不存在，无需操作]")
        elif type == 8:  # 8: 照明控制
            if parameter == 0:  # 无操作
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            elif parameter == 1:  # 开启
                result = webclient.step_scene_open_light()
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][结束]底层下位机接口应答结果[{result}]")
                if not result.endswith("0"):
                    result_message["message"] = "照明开启失败"
                    result_message["result"] = False
            elif parameter == 2:  # 关闭
                result = webclient.step_scene_close_light()
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][结束]底层下位机接口应答结果[{result}]")
                if not result.endswith("0"):
                    result_message["message"] = "照明关闭失败"
                    result_message["result"] = False
            elif parameter == 3:  # 重置
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            else:
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][不存在，无需操作]")
                return
        elif type == 100:  # 100: 一键控制
            if parameter == 0:  # 无操作
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            elif parameter == 1:  # 一键打开
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            elif parameter == 2:  # 一键回收
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            elif parameter == 3:  # 一键重置
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            elif parameter == 4:  # 急停复位
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][无需操作]")
            else:
                logger.get_log().info(f"[MQTT]执行[{type}_{parameter}][不存在，无需操作]")
                return
        else:
            result_message["message"] = "不支持的type值"
            result_message["result"] = False
        result_json = json.dumps(result_message, ensure_ascii=False)
        publish(topic_publish, result_json)
    else:
        logger.get_log().info(f"[MQTT]非法结构，不处理")


def do_code_time(msg_topic, message):
    topic_subscribe = f"/api/machine/nest/time_{ini_serialNumber}"
    topic_publish = f"/api/machine/requestResult_{ini_serialNumber}"
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]control的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    result_message = {
        "key": f"{ini_serialNumber}",
        "tid": "",
        "api": f"/api/machine/nest/time_{ini_serialNumber}",
        "message": "ok",
        "result": True
    }
    params = json.loads(message)
    if "key" in params and "tid" in params and "time" in params:
        key = params["key"]
        tid = params["tid"]
        time_str = params["time"]  # 格式为：YYYY-MM-DD hh:mm:ss 东八区时间
        result_message["tid"] = tid  # 初始化应答tid
        if key != ini_serialNumber:
            logger.get_log().info(f"[MQTT]control接入的设备ID[{key}]与本地设备ID[{ini_serialNumber}]不一致，不处理")
            return
        dt = parser.parser(time_str)
        if isinstance(dt, datetime.date):  # 判断合法的时间格式
            logger.get_log().info(f"[MQTT]执行[设置时间][{time_str}][开始]")
            pwd = "wkzn123"
            # os.system(f"date -s '{time_value}'")
            os.system(f"echo {pwd} | sudo -S date -s '{time_str}'")
        else:
            result_message["message"] = "时间非法"
            result_message["result"] = False
        result_json = json.dumps(result_message, ensure_ascii=False)
        publish(topic_publish, result_json)
    else:
        logger.get_log().info(f"[MQTT]非法结构，不处理")


def do_code_log(msg_topic, message):
    topic_subscribe = f"/api/machine/nest/logControl_{ini_serialNumber}"
    topic_publish = f"/api/machine/requestResult_{ini_serialNumber}"
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]control_log的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    result_message = {
        "key": f"{ini_serialNumber}",
        "tid": "",
        "api": f"/api/machine/nest/logControl_{ini_serialNumber}",
        "message": "ok",
        "result": True
    }
    params = json.loads(message)
    required_fields = ["key", "tid", "type", "url", "startDate", "endDate"]
    if check_fields(data=params, fields=required_fields):
        key = params["key"]
        tid = params["tid"]
        type = params["type"]
        url = params["url"]
        startDate = params["startDate"]  # 格式为：YYYY-MM-DD
        endDate = params["endDate"]  # 格式为：YYYY-MM-DD
        result_message["tid"] = tid  # 初始化应答tid
        if key != ini_serialNumber:
            logger.get_log().info(f"[MQTT]control_log接入的设备ID[{key}]与本地设备ID[{ini_serialNumber}]不一致，不处理")
            return
        # TODO url改为配置死的，目前不判断url参数
        # if url is None:
        #     logger.get_log().info(f"[MQTT]control_log参数url为空")
        #     return

        # TODO 检测期间目前不处理正式日志
        # if type == 1:
        #     logger.get_log().info(f"[MQTT]control_log不处理无人机日志")
        #     return
        # elif type == 2:  # 机巢的日志
        #     logger.get_log().info(f"[MQTT]control_log处理机巢日志[开始]")
        #     try:
        #         filelist = logger.getLogFiles(starttime=startDate, endtime=endDate)
        #         # 这块异步处理还是同步处理接口文档没确认
        #         # thread_log_post = Thread(target=do_code_log_post, args=([filelist,tid ,url]), daemon=True)
        #         # thread_log_post.start()
        #         do_code_log_post(filelist, tid, url)
        #     except Exception as e:
        #         logger.get_log().error(f"[MQTT]control_log处理机巢日志发生异常:{e}")
        #         result_message["message"] = "文件获取失败"
        #         result_message["result"] = False
        #
        #     result_json = json.dumps(result_message, ensure_ascii=False)
        #     publish(topic_publish, result_json)
        # else:
        #     logger.get_log().info(f"[MQTT]control_log不处理其他机日志")
        #     return
        do_code_log_post_test(tid, type)
        result_json = json.dumps(result_message, ensure_ascii=False)
        publish(topic_publish, result_json)
    else:
        logger.get_log().info(f"[MQTT]非法结构，不处理")


def do_code_log_post_test(tid, type):
    logger.get_log().info(f"[MQTT]control_log[检测]开始执行http上传日志")
    request_obj = {
        "key": f"{ini_serialNumber}",
        "tid": tid,
        "type": 2
    }
    url = BASEUtile.InitFileTool.get_str_value("hubeidianli_info", "do_log_test_url")
    try:
        if type == 1:  # 无人机
            with open(r"E:\python_jk_mqtt\JIKUPI\testlog\log_1.txt", 'rb') as file:  # 二进制方式打开
                up_files = {'logFile': file}
                request_obj["type"] = 1
                r = requests.post(url, data=request_obj, files=up_files)
                logger.get_log().info(f"[MQTT]control_log[检测]执行http上传日志 应答信息={r.text}")
        elif type == 2:  # 机巢的日志
            with open(r"E:\python_jk_mqtt\JIKUPI\testlog\log_2.txt", 'rb') as file:  # 二进制方式打开
                up_files = {'logFile': file}
                r = requests.post(url, data=request_obj, files=up_files)
                logger.get_log().info(f"[MQTT]control_log[检测]执行http上传日志 应答信息={r.text}")
        else:
            logger.get_log().info(f"[MQTT]control_log[检测]不处理其他机日志")
            return
    except Exception as e:
        logger.get_log().error(f"[MQTT]control_log[检测]处理机巢日志发生异常：{e}")


def do_code_log_post(filelist, tid, url):
    for file_path in filelist:
        try:
            logger.get_log().info(f"[MQTT]control_log处理机巢日志[{file_path}]")
            request_obj = {
                "key": f"{ini_serialNumber}",
                "tid": tid,
                "logFile": "",
                "type": 2
            }
            # with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:  # 文本方式打开
            with open(file_path, 'rb') as file:  # 二进制方式打开
                # 读取文件内容
                content = file.read()
                # print(f"file_path=[{file_path}][{content}]")
                base64_string = base64.b64encode(content).decode('utf-8')
                # print(f"file_path=[{file_path}][{base64_string}]")
                request_obj["logFile"] = base64_string
                json_str = json.dumps(request_obj)
                # logger.get_log().debug(f"[MQTT]control_log url={url} json_str={json_str}")  # 临时放开为info级别日志 改回debug
                r = requests.post(url, data=json_str,
                                  headers={"Content-Type": "application/json"})
                logger.get_log().info(f"postToHzPush 应答信息={r.text}")
        except Exception as e:
            logger.get_log().error(f"[MQTT]control_log处理机巢日志[{file_path}]发生异常：{e}")


def check_fields(data, fields):
    for field in fields:
        if not data.get(field):
            return False
    return True


def do_code_xxxx(msg_topic, msgCode):
    code = "xxxx"  # 处理指令
    msgExplain = "XXXX"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "XXXX"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "设备故障"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/xxxxxxxxx"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/xxxxxxxxx/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = webclient.do_test_step()
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


if __name__ == '__main__':
    # run()
    logger.get_log().info("====1")
    start_mqtt_thread_hubeidianli(None, None)
    logger.get_log().info("====2")
    # time.sleep(5)

    # filelist = logger.getLogFiles(starttime="2024-01-01", endtime="2024-05-01")
    # logger.get_log().info(f"filelist = {filelist}")

    test_message_log = {
        "key": ini_serialNumber,
        "tid": "123456",
        "type": 2,
        "url": "http://127.0.0.1:4523/m1/1148311-0-default/uplog",
        "startDate": "2024-01-01",
        "endDate": "2024-05-01"
    }
    publish(f"/api/machine/nest/logControl_{ini_serialNumber}", json.dumps(test_message_log))
    time.sleep(600)
    # publish(f"uavshelter/devicecontral/{ini_serialNumber}", "ha")

    # test_message1 = {
    #     "key": ini_serialNumber,
    #     "tid": "111111",
    #     "time": "gagagaga"
    # }
    # publish(f"/api/machine/nest/time_{ini_serialNumber}", json.dumps(test_message1))
    # time.sleep(60)
    test_message = {
        "key": ini_serialNumber,
        "tid": "2222222",
        "type": 1,
        "parameter": 0
    }
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 1
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 2
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 3
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 4
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 5
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)

    test_message["type"] = 2
    test_message["parameter"] = 0
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 1
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 2
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 3
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 4
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 5
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)

    test_message["type"] = 3
    test_message["parameter"] = 0
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 1
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 2
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 3
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 4
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 5
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)

    test_message["type"] = 4
    test_message["parameter"] = 0
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 1
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 2
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 3
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 4
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 5
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)

    test_message["type"] = 5
    test_message["parameter"] = 0
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 1
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 2
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 3
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 4
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 5
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)

    test_message["type"] = 6
    test_message["parameter"] = 0
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 1
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 2
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 3
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 4
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 5
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)

    test_message["type"] = 7
    test_message["parameter"] = 0
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 1
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 2
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 3
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 4
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 5
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)

    test_message["type"] = 8
    test_message["parameter"] = 0
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 1
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 2
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 3
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 4
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 5
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)

    test_message["type"] = 100
    test_message["parameter"] = 0
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 1
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 2
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 3
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 4
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
    test_message["parameter"] = 5
    publish(f"/api/machine/nest/control_{ini_serialNumber}", json.dumps(test_message))
    time.sleep(60)
