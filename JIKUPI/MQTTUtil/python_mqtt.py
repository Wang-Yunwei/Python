import json
import time
from threading import Thread

from paho.mqtt import client as mqtt_client

import BASEUtile.InitFileTool
import BASEUtile.HangarState as HangarState
import WFCharge.WFState as WFState
import BASEUtile.OperateUtil as OperateUtil
from ServerManager.websockets import WebSocketUtil

from BASEUtile.logger import Logger

# logger = Logger(__name__)  # 日志记录

# ini_serialNumber = BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "serialNumber")
ini_serialNumber = BASEUtile.InitFileTool.get_str_value("mqtt_info", "client_id")

# 操控系统下发命令主题(通配表达式#会多捕获自己的应答，所以采用元组方式)
topic_subscribe_list = [
    (f"uavshelter/devicecontral/{ini_serialNumber}/shelterdoor", 2),  # 4.1. 方舱舱门控制
    (f"uavshelter/devicecontral/{ini_serialNumber}/centerdevice", 2),  # 4.2. 归中装置控制
    (f"uavshelter/devicecontral/{ini_serialNumber}/airconditioner", 2),  # 4.3. 空调控制
    (f"uavshelter/devicecontral/{ini_serialNumber}/weatherstation", 2),  # 4.4. 气象站控制  # 暂不支持
    (f"uavshelter/devicecontral/{ini_serialNumber}/chargingdevice", 2),  # 4.5. 充电控制  TODO 没无人机没法完整测试
    (f"uavshelter/devicecontral/{ini_serialNumber}/uavcontral", 2),  # 4.6. 无人机控制 TODO 没无人机没法完整测试
    (f"uavshelter/devicecontral/{ini_serialNumber}/edit", 2),
    # 4.7.2. 修改方舱信息（操控系统_发布） # 4.7.1. 查询方舱信息 能做多少做多少 4.7.4. 查询方舱状态 能做多少做多少
    (f"uavshelter/devicecontral/{ini_serialNumber}/readyforflight", 2),
    # 4.8. 起降控制 # 4.8.4. 查询预备起飞状态不实现  4.8.7. 查询预备降落状态不实现 4.8.11.查询降落关舱状态不实现
    (f"uavshelter/devicecontral/{ini_serialNumber}/security", 2),  # 4.9. 安全控制 # 机场复位支持(推杆复位 空调开机)，机场急停不支持
    (f"uavshelter/devicecontral/{ini_serialNumber}/rccontral", 2),  # 4.10.遥控器控制  # 暂不支持该功能
    (f"uavshelter/devicecontral/{ini_serialNumber}/nightlanding", 2),  # 4.11.夜间降落控制 # 暂不支持该功能
    (f"uavshelter/devicecontral/{ini_serialNumber}/floodlight", 2),  # 4.12.照明灯控制 # 暂不支持该功能
    (f"uavshelter/devicecontral/{ini_serialNumber}/switchdrone", 2)  # 4.13.切换适配机型 # 暂不支持该功能

]
# topic_publish = ""  # 终端系统反馈执行结果主题(应答主题改为每个接口不同了)
client_id = 'jiku-001'  # 客户端id

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
            # host_str = BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "mqttHost")
            # port_int = BASEUtile.InitFileTool.get_int_value("mqtt_edit_info", "mqttPort")
            # username = BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "mqttUserName")
            # password = BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "mqttPassWord")
            host_str = BASEUtile.InitFileTool.get_str_value("mqtt_info", "host_str")
            port_int = BASEUtile.InitFileTool.get_int_value("mqtt_info", "port_int")
            username = BASEUtile.InitFileTool.get_str_value("mqtt_info", "username_str")
            password = BASEUtile.InitFileTool.get_str_value("mqtt_info", "password_str")

            global client_id
            # client_id = BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "serialNumber")
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
        message = msg.payload.decode()
        logger.get_log().info(f"[MQTT] 收到来自订阅[{msg.topic}]的消息为:{message}")
        msg_topic = msg.topic
        params = json.loads(message)
        msgType = params["msgType"]
        msgCode = params["msgCode"]
        data = params["data"]
        logger.get_log().info(f"[MQTT]消息核心指令信息 msgType:[{msgType}] msgCode =[{msgCode}]")
        if msgType == "0":
            logger.get_log().info(f"[MQTT] 执行指令:[{msgCode}]")
            if msgCode == "1001":
                do_code_1001(msg_topic, msgCode)
            elif msgCode == "1002":
                do_code_1002(msg_topic, msgCode)
            elif msgCode == "1003":
                do_code_1003(msg_topic, msgCode)
            elif msgCode == "2001":
                do_code_2001(msg_topic, msgCode)
            elif msgCode == "2002":
                do_code_2002(msg_topic, msgCode)
            elif msgCode == "2003":
                do_code_2003(msg_topic, msgCode)
            elif msgCode == "3001":
                do_code_3001(msg_topic, msgCode)
            elif msgCode == "3002":
                do_code_3002(msg_topic, msgCode)
            elif msgCode == "3003":
                do_code_3003(msg_topic, msgCode)
            # 3004主动上报空调数据，没有数据
            # 4001~4003不支持 没天气控制开关
            elif msgCode == "4001":
                do_code_4001(msg_topic, msgCode)  # 不支持，固定返回错误
            elif msgCode == "4002":
                do_code_4002(msg_topic, msgCode)  # 不支持，固定返回错误
            elif msgCode == "4003":
                do_code_4003(msg_topic, msgCode)  # 不支持，固定返回错误
            # 4004主动上报天气数据，没有数据
            elif msgCode == "5001":
                do_code_5001(msg_topic, msgCode)
            elif msgCode == "5002":
                do_code_5002(msg_topic, msgCode)
            elif msgCode == "5003":
                do_code_5003(msg_topic, msgCode)
            elif msgCode == "6001":
                do_code_6001(msg_topic, msgCode)
            elif msgCode == "6002":
                do_code_6002(msg_topic, msgCode)
            # 7001 为定时调用，30秒调用一次
            elif msgCode == "7002":
                do_code_7002(msg_topic, msgCode, data)  # 特殊，设置数据
            # 7003 接口文档中没有
            # 7004 为定时调用，1秒调用一次
            elif msgCode == "8001":
                do_code_8001(msg_topic, msgCode)
            # 8002 不支持 该状态为瞬时状态，中间太多情况导致变动
            elif msgCode == "8002":
                do_code_8002(msg_topic, msgCode)  # 不支持，固定返回错误
            elif msgCode == "8003":
                do_code_8003(msg_topic, msgCode)
            # 8004 不支持 该状态为瞬时状态，中间太多情况导致变动
            elif msgCode == "8004":
                do_code_8004(msg_topic, msgCode)  # 不支持，固定返回错误
            elif msgCode == "8005":
                do_code_8005(msg_topic, msgCode)
            # 8006 不支持 该状态为瞬时状态，中间太多情况导致变动
            elif msgCode == "8006":
                do_code_8006(msg_topic, msgCode)  # 不支持，固定返回错误
            elif msgCode == "9001":
                do_code_9001(msg_topic, msgCode)
            # 9002 不支持 机场急停硬件不支持
            elif msgCode == "9002":
                do_code_9002(msg_topic, msgCode)  # 不支持，固定返回错误
            # 10001~10003不支持 目前版本不支持遥控器控制
            elif msgCode == "10001":
                do_code_10001(msg_topic, msgCode)  # 不支持，固定返回错误
            elif msgCode == "10002":
                do_code_10002(msg_topic, msgCode)  # 不支持，固定返回错误
            elif msgCode == "10003":
                do_code_10003(msg_topic, msgCode)  # 不支持，固定返回错误
            # 11001~11003不支持 目前版本不支持夜间控制开关
            elif msgCode == "11001":
                do_code_11001(msg_topic, msgCode)  # 不支持，固定返回错误
            elif msgCode == "11002":
                do_code_11002(msg_topic, msgCode)  # 不支持，固定返回错误
            elif msgCode == "11003":
                do_code_11003(msg_topic, msgCode)  # 不支持，固定返回错误
            # 12001~12003不支持 目前版本不支持照明灯操作
            elif msgCode == "12001":
                do_code_12001(msg_topic, msgCode)  # 不支持，固定返回错误
            elif msgCode == "12002":
                do_code_12002(msg_topic, msgCode)  # 不支持，固定返回错误
            elif msgCode == "12003":
                do_code_12003(msg_topic, msgCode)  # 不支持，固定返回错误
            # 13001~13003不支持 目前版本不支持切换适配机型
            elif msgCode == "13001":
                do_code_13001(msg_topic, msgCode)  # 不支持，固定返回错误
            elif msgCode == "13003":
                do_code_13003(msg_topic, msgCode)  # 不支持，固定返回错误
            else:
                logger.get_log().info(f"无法识别具体操作的指令:[{msgCode}]，不做任何操作，舍弃该条信息")
        else:
            logger.get_log().info(f"msgType不为0，不是发给终端系统的指令")
        # print(params["msgType"])
        # print(params["msgCode"])

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


def run_7001():
    time.sleep(10)  # 晚10秒启动推送，给MQTT链接创造时间
    while True:
        try:
            do_code_7001()
            time.sleep(30)  # 休眠30秒就推送
        except Exception as e:
            logger.get_log().error(f"[MQTT] do_code_7001发生异常{e}")
            time.sleep(10)  # 异常后晚10秒启动推送，给MQTT链接创造时间


def run_7004():
    time.sleep(10)  # 晚10秒启动推送，给MQTT链接创造时间
    while True:
        try:
            do_code_7004()
            time.sleep(1)  # 休眠1秒就推送
        except Exception as e:
            logger.get_log().error(f"[MQTT] do_code_7004发生异常{e}")
            time.sleep(10)  # 异常后晚10秒启动推送，给MQTT链接创造时间


def start_mqtt_thread_dx(web_client, logger_in):
    global logger
    logger = logger_in
    global webclient
    webclient = web_client
    # global hangstate
    # hangstate = HangarState
    logger.get_log().info("[MQTT] 启动 MQTT 任务线程 [开始]")
    thread = Thread(target=run, args=([]), daemon=True)
    thread.start()
    logger.get_log().info("[MQTT] 启动 MQTT 主接收发送任务线程 [完成]")

    thread_7001 = Thread(target=run_7001, args=([]), daemon=True)
    thread_7001.start()
    logger.get_log().info("[MQTT] 启动 7001定时推送机库配置线程 [完成]")

    thread_7004 = Thread(target=run_7004, args=([]), daemon=True)
    thread_7004.start()
    logger.get_log().info("[MQTT] 启动 7004定时推送机库状态线程 [完成]")

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


def do_code_1001(msg_topic, msgCode):
    code = "1001"  # 处理指令
    msgExplain = "打开舱门"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "正在打开"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "设备故障"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/shelterdoor"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/shelterdoor/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = OperateUtil.operate_hangar("140000")
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_1002(msg_topic, msgCode):
    code = "1002"  # 处理指令
    msgExplain = "关闭舱门"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "正在关闭"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "设备故障"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/shelterdoor"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/shelterdoor/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = OperateUtil.operate_hangar("150000")
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_1003(msg_topic, msgCode):
    code = "1003"  # 处理指令
    msgExplain = "查询舱门状态"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg_open = "已打开"  # 开门描述
    result_msg_close = "已关闭"  # 关门描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "状态异常"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = ""  # 默认返回
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/shelterdoor"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/shelterdoor/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用hangstate获取状态
    flag = HangarState.get_hangar_door_state()
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{flag}]")
    if flag == "open":
        respMsg = result_msg_open
    elif flag == "close":
        respMsg = result_msg_close
    else:
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_2001(msg_topic, msgCode):
    code = "2001"  # 处理指令
    msgExplain = "归中无人机"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "正在归中"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "设备故障"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/centerdevice"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/centerdevice/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = OperateUtil.operate_hangar("2e10002000")
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_2002(msg_topic, msgCode):
    code = "2002"  # 处理指令
    msgExplain = "复位归中装置"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "正在复位"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "设备故障"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/centerdevice"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/centerdevice/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = OperateUtil.operate_hangar("500000")
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_2003(msg_topic, msgCode):
    code = "2003"  # 处理指令
    msgExplain = "查询归中装置状态"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg_open = "已复位"  # 已复位描述
    result_msg_close = "已归中"  # 已归中描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "状态异常"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = ""  # 默认返回
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/centerdevice"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/centerdevice/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用hangstate获取状态
    flag = HangarState.get_hangar_bar_state()
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{flag}]")
    if flag == "open":
        respMsg = result_msg_open
    elif flag == "close":
        respMsg = result_msg_close
    else:
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_3001(msg_topic, msgCode):
    code = "3001"  # 处理指令
    msgExplain = "开启空调"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "开启成功"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "开启失败"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/airconditioner"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/airconditioner/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = OperateUtil.operate_hangar("300000")
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_3002(msg_topic, msgCode):
    code = "3002"  # 处理指令
    msgExplain = "关闭空调"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "关闭成功"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "关闭失败"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/airconditioner"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/airconditioner/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = OperateUtil.operate_hangar("310000")
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_3003(msg_topic, msgCode):
    code = "3003"  # 处理指令
    msgExplain = "查询空调状态"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg_open = "开启状态"  # 开启状态
    result_msg_close = "关闭状态"  # 关闭状态
    result_code_error = "001"  # 故障编码
    result_msg_error = "状态异常"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = ""  # 默认返回
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/airconditioner"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/airconditioner/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用hangstate获取状态
    flag = HangarState.get_air_condition_state()
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{flag}]")
    if flag == "open":
        respMsg = result_msg_open
    elif flag == "close":
        respMsg = result_msg_close
    else:
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_4001(msg_topic, msgCode):
    code = "4001"  # 处理指令
    msgExplain = "开启气象站"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "开启成功"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "不支持该功能"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/weatherstation"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/weatherstation/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = "9xx1"  # 固定错误
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_4002(msg_topic, msgCode):
    code = "4002"  # 处理指令
    msgExplain = "关闭气象站"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "关闭成功"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "不支持该功能"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/weatherstation"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/weatherstation/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = "9xx1"  # 固定错误
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_4003(msg_topic, msgCode):
    code = "4003"  # 处理指令
    msgExplain = "查询气象站状态"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "查询成功"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "不支持该功能"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/weatherstation"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/weatherstation/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = "9xx1"  # 固定错误
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_5001(msg_topic, msgCode):
    code = "5001"  # 处理指令
    msgExplain = "启动充电"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "开启成功"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "充电故障"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/chargingdevice"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/chargingdevice/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = OperateUtil.operate_hangar("cp0000")
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_5002(msg_topic, msgCode):
    code = "5002"  # 处理指令
    msgExplain = "停止充电"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "停止成功"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "设备故障"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/chargingdevice"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/chargingdevice/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = OperateUtil.operate_hangar("sb0000")
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_5003(msg_topic, msgCode):
    code = "5003"  # 处理指令
    msgExplain = "查询充电状态"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg_charging = "正在充电"  # 正在充电(charging)
    result_msg_full = "充电完成"  # 充电完成(full)
    result_msg_other = "未充电"  # 未充电(close/standby/takeoff/outage/cool)
    # result_code_error = "001"  # 故障编码
    # result_msg_error = "设备故障"  # 故障描述 状态异常
    respCode = result_code  # 默认返回(成功)
    respMsg = ""  # 默认返回
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/chargingdevice"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/chargingdevice/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用hangstate获取状态
    flag = WFState.get_battery_state()
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{flag}]")
    # ***注意，这里沟通后认为，只要不是充电中或已充满，就都是未充电，没有异常情况
    if flag == "charging":
        respMsg = result_msg_charging
    elif flag == "full":
        respMsg = result_msg_full
    # elif flag in ["close", "standby", "takeoff", "outage", "cool", "unknown"]:
    else:
        respMsg = result_msg_other
    # else:
    #     # 一般没有异常的
    #     respCode = result_code_error
    #     respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_6001(msg_topic, msgCode):
    code = "6001"  # 处理指令
    msgExplain = "无人机开机"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "开机成功"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "设备故障"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/uavcontral"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/uavcontral/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = OperateUtil.operate_hangar("dt0000")
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_6002(msg_topic, msgCode):
    code = "6002"  # 处理指令
    msgExplain = "无人机关机"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "关机成功"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "设备故障"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/uavcontral"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/uavcontral/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = OperateUtil.operate_hangar("dd0000")
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_7001():
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/info"  # 该接口的应答主题
    result_message = {
        "msgType": "1",
        "msgCode": "7001",
        "msgExplain": "方舱信息",
        "data": {
            # "serialNumber": BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "serialNumber"),
            "serialNumber": BASEUtile.InitFileTool.get_str_value("mqtt_info", "client_id"),
            # "type": BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "type"),
            # "adapter": BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "adapter"),
            # "adress": BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "adress"),
            # "alternatePoint": BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "alternatePoint"),
            # "doorSpeed": BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "doorSpeed"),
            # "centerSpeed": BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "centerSpeed"),
            "type": BASEUtile.InitFileTool.get_str_value("dianxin_info", "type"),
            "adapter": BASEUtile.InitFileTool.get_str_value("dianxin_info", "adapter"),
            "adress": BASEUtile.InitFileTool.get_str_value("dianxin_info", "adress"),
            "alternatePoint": BASEUtile.InitFileTool.get_str_value("dianxin_info", "alternatePoint"),
            "doorSpeed": BASEUtile.InitFileTool.get_str_value("dianxin_info", "doorSpeed"),
            "centerSpeed": BASEUtile.InitFileTool.get_str_value("dianxin_info", "centerSpeed"),
            # "mqttHost": BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "mqttHost"),
            # "mqttPort": BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "mqttPort"),
            # "mqttUserName": BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "mqttUserName"),
            # "mqttPassWord": BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "mqttPassWord")
            "mqttHost": BASEUtile.InitFileTool.get_str_value("mqtt_info", "host_str"),
            "mqttPort": BASEUtile.InitFileTool.get_str_value("mqtt_info", "port_int"),
            "mqttUserName": BASEUtile.InitFileTool.get_str_value("mqtt_info", "username_str"),
            "mqttPassWord": BASEUtile.InitFileTool.get_str_value("mqtt_info", "password_str")
        }
    }
    result_json = json.dumps(result_message, ensure_ascii=False)
    publish(topic_publish, result_json)


def do_code_7002(msg_topic, msgCode, data):
    code = "7002"  # 处理指令
    msgExplain = "修改方舱信息"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "修改成功"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "修改失败"  # 失败描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/edit"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/edit/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")

    try:
        section_name = "mqtt_edit_info"
        # BASEUtile.InitFileTool.set_value(section_name, "serialNumber", data["serialNumber"])
        # BASEUtile.InitFileTool.set_value(section_name, "type", data["type"])
        # BASEUtile.InitFileTool.set_value(section_name, "adapter", data["adapter"])
        # BASEUtile.InitFileTool.set_value(section_name, "adress", data["adress"])
        # BASEUtile.InitFileTool.set_value(section_name, "alternatePoint", data["alternatePoint"])
        # BASEUtile.InitFileTool.set_value(section_name, "doorSpeed", data["doorSpeed"])
        # BASEUtile.InitFileTool.set_value(section_name, "centerSpeed", data["centerSpeed"])
        # BASEUtile.InitFileTool.set_value(section_name, "mqttHost", data["mqttHost"])
        # BASEUtile.InitFileTool.set_value(section_name, "mqttPort", data["mqttPort"])
        # BASEUtile.InitFileTool.set_value(section_name, "mqttUserName", data["mqttUserName"])
        # BASEUtile.InitFileTool.set_value(section_name, "mqttPassWord", data["mqttPassWord"])
        BASEUtile.InitFileTool.set_value("mqtt_info", "client_id", data["serialNumber"])
        BASEUtile.InitFileTool.set_value("dianxin_info", "type", data["type"])
        BASEUtile.InitFileTool.set_value("dianxin_info", "adapter", data["adapter"])
        BASEUtile.InitFileTool.set_value("dianxin_info", "adress", data["adress"])
        BASEUtile.InitFileTool.set_value("dianxin_info", "alternatePoint", data["alternatePoint"])
        BASEUtile.InitFileTool.set_value("dianxin_info", "doorSpeed", data["doorSpeed"])
        BASEUtile.InitFileTool.set_value("dianxin_info", "centerSpeed", data["centerSpeed"])
        BASEUtile.InitFileTool.set_value("mqtt_info", "host_str", data["mqttHost"])
        BASEUtile.InitFileTool.set_value("mqtt_info", "port_int", data["mqttPort"])
        BASEUtile.InitFileTool.set_value("mqtt_info", "username_str", data["mqttUserName"])
        BASEUtile.InitFileTool.set_value("mqtt_info", "password_str", data["mqttPassWord"])
    except Exception as e:
        logger.get_log().error(f"[MQTT]执行指令[{code}]过程中发生异常[{e}]")
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_7004():
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/status"  # 该接口的应答主题
    shelterdoor_result = HangarState.get_hangar_door_state()
    shelterdoor = "已关闭"
    if shelterdoor_result == "open":
        shelterdoor = "已打开"

    centerdevice_result = HangarState.get_hangar_bar_state()
    centerdevice = "已归中"
    if centerdevice_result == "open":
        centerdevice = "已复位"

    chargingdevice_result = WFState.get_battery_state()
    # chargingdevice_value = hangstate.get_wfc_battery_value()
    chargingdevice = "未充电"
    if chargingdevice_result == "charging":
        chargingdevice = "正在充电"
    elif chargingdevice_result == "full":
        chargingdevice = "充电完成"

    # airconditioner = str(hangstate.indoor_tem())
    # weatherstation_temperature = str(hangstate.get_temperature())
    weatherstation_windvelocity = HangarState.get_wind_speed_value()

    weatherstation_winddirection_result = HangarState.get_wind_direction_value()
    if weatherstation_winddirection_result == "北风":
        weatherstation_winddirection = "North"
    elif weatherstation_winddirection_result == "东北风":
        weatherstation_winddirection = "Northeast"
    elif weatherstation_winddirection_result == "东风":
        weatherstation_winddirection = "East"
    elif weatherstation_winddirection_result == "东南风":
        weatherstation_winddirection = "Southeast"
    elif weatherstation_winddirection_result == "南风":
        weatherstation_winddirection = "South"
    elif weatherstation_winddirection_result == "西南风":
        weatherstation_winddirection = "Southwest"
    elif weatherstation_winddirection_result == "西风":
        weatherstation_winddirection = "West"
    elif weatherstation_winddirection_result == "西北风":
        weatherstation_winddirection = "Northwest"
    elif weatherstation_winddirection_result == "北":  # 旧版本一个特性代指[兼容]
        weatherstation_winddirection = "North"
    else:
        weatherstation_winddirection = "North"

    result_message = {
        "msgType": "1",
        "msgCode": "7004",
        "msgExplain": "方舱状态",
        "data": {
            "shelterdoor": shelterdoor,  # 只有已关闭/已打开，没有中间执行中状态 "正在打开/正在关闭/已关闭/已打开",
            "centerdevice": centerdevice,  # 只有已归中/已复位，没有中间执行中状态 "正在归中/正在复位/已归中/已复位",
            "chargingdevice": chargingdevice,  # "未充电/正在充电/充电完成",
            "chargingdevice_voltage": "",  # 无法获取 充电电压,单位 V
            "chargingdevice_current": "",  # 无法获取 充电电流,单位 A
            "airconditioner": "",  # 实际温度值，单位℃
            "weatherstation_temperature": "",  # 温度值，如 28℃
            "weatherstation_humidity": "",  # 湿度，单位%
            "weatherstation_windvelocity": weatherstation_windvelocity,  # 风速，单位 m/s
            "weatherstation_winddirection": weatherstation_winddirection,  # 风向
            "weatherstation_rainfall": "",  # 雨量
            "remote_control": "未知",  # 遥控器状态，我们固定不知道。 开机/关机/未知
            "night_landing": "未知"  # 夜间降落，不清楚。 开启/关闭/未知
        }
    }
    result_json = json.dumps(result_message, ensure_ascii=False)
    publish_debug_log(topic_publish, result_json)  # 因为心跳调用频繁，改为debug日志输出


def do_code_8001(msg_topic, msgCode):
    code = "8001"  # 处理指令
    msgExplain = "预备起飞"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "预备起飞成功"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "预备起飞条件不满足"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/readyforflight"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/readyforflight/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = OperateUtil.operate_hangar("A000")
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_8002(msg_topic, msgCode):
    code = "8002"  # 处理指令
    msgExplain = "查询预备起飞状态"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "未知状态"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "不支持该功能"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/readyforflight"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/readyforflight/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = "9xx1"  # 固定错误
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_8003(msg_topic, msgCode):
    code = "8003"  # 处理指令
    msgExplain = "预备降落"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "预备降落成功"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "预备降落条件不满足"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/readyforflight"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/readyforflight/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = OperateUtil.operate_hangar("B000")
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_8004(msg_topic, msgCode):
    code = "8004"  # 处理指令
    msgExplain = "查询预备降落状态"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "未知状态"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "不支持该功能"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/readyforflight"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/readyforflight/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = "9xx1"  # 固定错误
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_8005(msg_topic, msgCode):
    code = "8005"  # 处理指令
    msgExplain = "降落关舱"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "降落关舱成功"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "设备故障"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/readyforflight"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/readyforflight/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = OperateUtil.operate_hangar("B100")
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_8006(msg_topic, msgCode):
    code = "8006"  # 处理指令
    msgExplain = "查询降落关舱状态"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "未知状态"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "不支持该功能"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/readyforflight"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/readyforflight/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = "9xx1"  # 固定错误
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_9001(msg_topic, msgCode):
    code = "9001"  # 处理指令
    msgExplain = "机场复位"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "执行成功"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "设备故障"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/security"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/security/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库  PS:经过讨论确定，只复位推杆，不动机库门，怕关门夹到无人机
    result = OperateUtil.operate_hangar("500000")
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_9002(msg_topic, msgCode):
    code = "9002"  # 处理指令
    msgExplain = "机场急停"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "执行成功"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "不支持该功能"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/security"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/security/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = "9xx1"  # 固定错误
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_10001(msg_topic, msgCode):
    code = "10001"  # 处理指令
    msgExplain = "开启遥控器"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "开启成功"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "不支持该功能"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/rccontral"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/rccontral/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = "9xx1"  # 固定错误
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_10002(msg_topic, msgCode):
    code = "10002"  # 处理指令
    msgExplain = "关闭遥控器"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "关闭成功"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "不支持该功能"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/rccontral"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/rccontral/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = "9xx1"  # 固定错误
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_10003(msg_topic, msgCode):
    code = "10003"  # 处理指令
    msgExplain = "查询遥控器状态"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "未知"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "不支持该功能"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/rccontral"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/rccontral/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = "9xx1"  # 固定错误
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_11001(msg_topic, msgCode):
    code = "11001"  # 处理指令
    msgExplain = "开启夜间降落"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "开启成功"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "不支持该功能"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/nightlanding"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/nightlanding/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = "9xx1"  # 固定错误
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_11002(msg_topic, msgCode):
    code = "11002"  # 处理指令
    msgExplain = "关闭夜间降落"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "关闭成功"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "不支持该功能"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/nightlanding"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/nightlanding/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = "9xx1"  # 固定错误
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_11003(msg_topic, msgCode):
    code = "11003"  # 处理指令
    msgExplain = "查询夜间降落状态"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "未知"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "不支持该功能"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/nightlanding"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/nightlanding/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = "9xx1"  # 固定错误
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_12001(msg_topic, msgCode):
    code = "12001"  # 处理指令
    msgExplain = "开启照明灯"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "未知"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "不支持该功能"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/floodlight"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/floodlight/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = "9xx1"  # 固定错误
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_12002(msg_topic, msgCode):
    code = "12002"  # 处理指令
    msgExplain = "关闭照明灯"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "未知"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "不支持该功能"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/floodlight"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/floodlight/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = "9xx1"  # 固定错误
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_12003(msg_topic, msgCode):
    code = "12003"  # 处理指令
    msgExplain = "查询照明灯状态"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "未知"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "不支持该功能"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/floodlight"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/floodlight/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = "9xx1"  # 固定错误
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_13001(msg_topic, msgCode):
    code = "13001"  # 处理指令
    msgExplain = "切换适配机型"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "未知"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "不支持该功能"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/switchdrone"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/switchdrone/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = "9xx1"  # 固定错误
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


def do_code_13003(msg_topic, msgCode):
    code = "13003"  # 处理指令
    msgExplain = "查询适配机型"  # 操作指令描述
    result_code = "000"  # 成功编码
    result_msg = "未知"  # 成功描述
    result_code_error = "001"  # 故障编码
    result_msg_error = "不支持该功能"  # 故障描述
    respCode = result_code  # 默认返回(成功)
    respMsg = result_msg  # 默认返回(成功)
    topic_subscribe = f"uavshelter/devicecontral/{ini_serialNumber}/switchdrone"  # 该接口处理的接入主题
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/switchdrone/feedback"  # 该接口的应答主题
    if msg_topic != topic_subscribe:
        logger.get_log().info(f"[MQTT]指令[{code}]的处理订阅[{topic_subscribe}]与接入订阅[{msg_topic}]不一致，不处理")
        return
    if msgCode != code:
        logger.get_log().info(f"[MQTT]接入指令[{msgCode}]与处理指令[{code}]不一致，不处理")
        return
    logger.get_log().info(f"[MQTT]执行指令[{code}][开始]")
    # 调用webclient控制端操控机库
    result = "9xx1"  # 固定错误
    logger.get_log().info(f"[MQTT]执行指令[{code}][结束]底层下位机接口应答结果[{result}]")
    if not result.endswith("0"):
        respCode = result_code_error
        respMsg = result_msg_error
    # 下发应答
    result_json = make_result_message("1", msgCode, msgExplain, respCode, respMsg)
    publish(topic_publish, result_json)


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
    start_mqtt_thread_dx(None, None)
    logger.get_log().info("====2")
    # time.sleep(5)

    # publish(f"uavshelter/devicecontral/{ini_serialNumber}", "ha")

    # test_message = {
    #     "msgType": "0",
    #     "msgCode": "12001",
    #     "msgExplain": "开启照明灯",
    #     "data": {}
    # }
    # test_message = {
    #     "msgType": "0",
    #     "msgCode": "12002",
    #     "msgExplain": "关闭照明灯",
    #     "data": {}
    # }
    # test_message = {
    #     "msgType": "0",
    #     "msgCode": "12003",
    #     "msgExplain": "查询照明灯状态",
    #     "data": {}
    # }
    # publish(f"uavshelter/devicecontral/{ini_serialNumber}/floodlight", json.dumps(test_message))
    # test_message = {
    #     "msgType": "0",
    #     "msgCode": "13001",
    #     "msgExplain": "切换适配机型",
    #     "data": {}
    # }
    # test_message = {
    #     "msgType": "0",
    #     "msgCode": "13003",
    #     "msgExplain": "查询适配机型",
    #     "data": {}
    # }
    # publish(f"uavshelter/devicecontral/{ini_serialNumber}/switchdrone", json.dumps(test_message))

    time.sleep(60)
