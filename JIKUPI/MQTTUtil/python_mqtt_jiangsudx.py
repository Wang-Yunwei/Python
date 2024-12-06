import json
import time
from threading import Thread

from paho.mqtt import client as mqtt_client

import BASEUtile.InitFileTool
from BASEUtile import HangerState
from BASEUtile.logger import Logger

logger = Logger(__name__)  # 日志记录

# 配置中的方舱序列号
ini_serialNumber = BASEUtile.InitFileTool.get_str_value("jsdx_info", "serialNumber")

# 操控系统下发命令主题(通配表达式#会多捕获自己的应答，所以采用元组方式)
topic_subscribe_list = [
    # (f"uavshelter/devicecontral/{ini_serialNumber}/shelterdoor", 2),  # 4.1. 方舱舱门控制
    # (f"uavshelter/devicecontral/{ini_serialNumber}/centerdevice", 2),  # 4.2. 归中装置控制
    # (f"uavshelter/devicecontral/{ini_serialNumber}/airconditioner", 2),  # 4.3. 空调控制
    # (f"uavshelter/devicecontral/{ini_serialNumber}/weatherstation", 2),  # 4.4. 气象站控制  # 暂不支持
    # (f"uavshelter/devicecontral/{ini_serialNumber}/chargingdevice", 2),  # 4.5. 充电控制  TODO 没无人机没法完整测试
    # (f"uavshelter/devicecontral/{ini_serialNumber}/uavcontral", 2),  # 4.6. 无人机控制 TODO 没无人机没法完整测试
    # (f"uavshelter/devicecontral/{ini_serialNumber}/edit", 2),
    # # 4.7.2. 修改方舱信息（操控系统_发布） # 4.7.1. 查询方舱信息 能做多少做多少 4.7.4. 查询方舱状态 能做多少做多少
    # (f"uavshelter/devicecontral/{ini_serialNumber}/readyforflight", 2),
    # # 4.8. 起降控制 # 4.8.4. 查询预备起飞状态不实现  4.8.7. 查询预备降落状态不实现 4.8.11.查询降落关舱状态不实现
    # (f"uavshelter/devicecontral/{ini_serialNumber}/security", 2),  # 4.9. 安全控制 # 机场复位支持(推杆复位 空调开机)，机场急停不支持
    # (f"uavshelter/devicecontral/{ini_serialNumber}/rccontral", 2),  # 4.10.遥控器控制  # 暂不支持该功能
    # (f"uavshelter/devicecontral/{ini_serialNumber}/nightlanding", 2)  # 4.11.夜间降落控制 # 暂不支持该功能，目前只有一款支持
]
# topic_publish = ""  # 终端系统反馈执行结果主题(应答主题改为每个接口不同了)
client_id = BASEUtile.InitFileTool.get_str_value("mqtt_info", "client_id")  # 客户端id

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

int
num_1003 = 0
num_2003 = 0
num_3003 = 0
num_4003 = 0
num_4004 = 0
num_5003 = 0


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
        # TODO 接到消息处理 目前没有MQTT任何操作指令
        message = msg.payload.decode()
        logger.get_log().info(f"[MQTT] 收到来自订阅[{msg.topic}]的消息为:{message}")
        # msg_topic = msg.topic
        # params = json.loads(message)
        # msgType = params["msgType"]
        # msgCode = params["msgCode"]
        # data = params["data"]
        # logger.get_log().info(f"[MQTT]消息核心指令信息 msgType:[{msgType}] msgCode =[{msgCode}]")
        # if msgType == "0":
        #     logger.get_log().info(f"[MQTT] 执行指令:[{msgCode}]")
        #     if msgCode == "1001":
        #         do_code_1001(msg_topic, msgCode)
        #     elif msgCode == "1002":
        #         do_code_1002(msg_topic, msgCode)
        #     elif msgCode == "1003":
        #         do_code_1003(msg_topic, msgCode)
        #     elif msgCode == "2001":
        #         do_code_2001(msg_topic, msgCode)
        #     elif msgCode == "2002":
        #         do_code_2002(msg_topic, msgCode)
        #     elif msgCode == "2003":
        #         do_code_2003(msg_topic, msgCode)
        #     elif msgCode == "3001":
        #         do_code_3001(msg_topic, msgCode)
        #     elif msgCode == "3002":
        #         do_code_3002(msg_topic, msgCode)
        #     elif msgCode == "3003":
        #         do_code_3003(msg_topic, msgCode)
        #     # 3004主动上报空调数据，没有数据
        #     # 4001~4003不支持 没天气控制开关
        #     elif msgCode == "4001":
        #         do_code_4001(msg_topic, msgCode)  # 不支持，固定返回错误
        #     elif msgCode == "4002":
        #         do_code_4002(msg_topic, msgCode)  # 不支持，固定返回错误
        #     elif msgCode == "4003":
        #         do_code_4003(msg_topic, msgCode)  # 不支持，固定返回错误
        #     # 4004主动上报天气数据，没有数据
        #     elif msgCode == "5001":
        #         do_code_5001(msg_topic, msgCode)
        #     elif msgCode == "5002":
        #         do_code_5002(msg_topic, msgCode)
        #     elif msgCode == "5003":
        #         do_code_5003(msg_topic, msgCode)
        #     elif msgCode == "6001":
        #         do_code_6001(msg_topic, msgCode)
        #     elif msgCode == "6002":
        #         do_code_6002(msg_topic, msgCode)
        #     # 7001 为定时调用，30秒调用一次
        #     elif msgCode == "7002":
        #         do_code_7002(msg_topic, msgCode, data)  # 特殊，设置数据
        #     # 7003 接口文档中没有
        #     # 7004 为定时调用，1秒调用一次
        #     elif msgCode == "8001":
        #         do_code_8001(msg_topic, msgCode)
        #     # 8002 不支持 该状态为瞬时状态，中间太多情况导致变动
        #     elif msgCode == "8002":
        #         do_code_8002(msg_topic, msgCode)  # 不支持，固定返回错误
        #     elif msgCode == "8003":
        #         do_code_8003(msg_topic, msgCode)
        #     # 8004 不支持 该状态为瞬时状态，中间太多情况导致变动
        #     elif msgCode == "8004":
        #         do_code_8004(msg_topic, msgCode)  # 不支持，固定返回错误
        #     elif msgCode == "8005":
        #         do_code_8005(msg_topic, msgCode)
        #     # 8006 不支持 该状态为瞬时状态，中间太多情况导致变动
        #     elif msgCode == "8006":
        #         do_code_8006(msg_topic, msgCode)  # 不支持，固定返回错误
        #     elif msgCode == "9001":
        #         do_code_9001(msg_topic, msgCode)
        #     # 9002 不支持 机场急停硬件不支持
        #     elif msgCode == "9002":
        #         do_code_9002(msg_topic, msgCode)  # 不支持，固定返回错误
        #     # 10001~10003不支持 目前版本不支持遥控器控制
        #     elif msgCode == "10001":
        #         do_code_10001(msg_topic, msgCode)  # 不支持，固定返回错误
        #     elif msgCode == "10002":
        #         do_code_10002(msg_topic, msgCode)  # 不支持，固定返回错误
        #     elif msgCode == "10003":
        #         do_code_10003(msg_topic, msgCode)  # 不支持，固定返回错误
        #     # 11001~11003不支持 目前版本不支持夜间控制开关
        #     elif msgCode == "11001":
        #         do_code_11001(msg_topic, msgCode)  # 不支持，固定返回错误
        #     elif msgCode == "11002":
        #         do_code_11002(msg_topic, msgCode)  # 不支持，固定返回错误
        #     elif msgCode == "11003":
        #         do_code_11003(msg_topic, msgCode)  # 不支持，固定返回错误
        #     else:
        #         logger.get_log().info(f"无法识别具体操作的指令:[{msgCode}]，不做任何操作，舍弃该条信息")
        # else:
        #     logger.get_log().info(f"msgType不为0，不是发给终端系统的指令")
        # print(params["msgType"])
        # print(params["msgCode"])

    # client.subscribe(topic_subscribe_list, qos=2)  # 订阅具体topic的消息
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


def publish_no_log(topic_publish, message):
    # logger.get_log().info(f"[MQTT][publish]准备下发消息内容为:{message}")
    global client_publish
    if client_publish is None:
        time.sleep(10)  # 正常走不到这个流程里，正常会有链接对象，等待10秒怎么也链接上了
    # logger.get_log().info(f"[MQTT][publish]执行下发消息:{message}")
    result = client_publish.publish(topic_publish, message, qos=2)
    status = result[0]
    # logger.get_log().info(f"[MQTT][publish]执行下发消息后收到应答码:{status}  含义:{rc_status[status]}")


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
线程启动MQTT[江苏电信定制]
'''


def run_1003():
    time.sleep(10)  # 晚10秒启动推送，给MQTT链接创造时间
    while True:
        try:
            do_code_1003()
            time.sleep(1)  # 休眠1秒就推送
        except Exception as e:
            logger.get_log().error(f"[MQTT] do_code_1003发生异常{e}")
            time.sleep(10)  # 异常后晚10秒启动推送，给MQTT链接创造时间


def run_2003():
    time.sleep(10)  # 晚10秒启动推送，给MQTT链接创造时间
    while True:
        try:
            do_code_2003()
            time.sleep(1)  # 休眠1秒就推送
        except Exception as e:
            logger.get_log().error(f"[MQTT] do_code_2003发生异常{e}")
            time.sleep(10)  # 异常后晚10秒启动推送，给MQTT链接创造时间


def run_3003():
    time.sleep(10)  # 晚10秒启动推送，给MQTT链接创造时间
    while True:
        try:
            do_code_3003()
            time.sleep(1)  # 休眠1秒就推送
        except Exception as e:
            logger.get_log().error(f"[MQTT] do_code_3003发生异常{e}")
            time.sleep(10)  # 异常后晚10秒启动推送，给MQTT链接创造时间


def run_4003():
    time.sleep(10)  # 晚10秒启动推送，给MQTT链接创造时间
    while True:
        try:
            do_code_4003()
            time.sleep(1)  # 休眠1秒就推送
        except Exception as e:
            logger.get_log().error(f"[MQTT] do_code_4003发生异常{e}")
            time.sleep(10)  # 异常后晚10秒启动推送，给MQTT链接创造时间


def run_4004():
    time.sleep(10)  # 晚10秒启动推送，给MQTT链接创造时间
    while True:
        try:
            do_code_4004()
            time.sleep(1)  # 休眠1秒就推送
        except Exception as e:
            logger.get_log().error(f"[MQTT] do_code_4004发生异常{e}")
            time.sleep(10)  # 异常后晚10秒启动推送，给MQTT链接创造时间


def run_5003():
    time.sleep(10)  # 晚10秒启动推送，给MQTT链接创造时间
    while True:
        try:
            do_code_5003()
            time.sleep(1)  # 休眠1秒就推送
        except Exception as e:
            logger.get_log().error(f"[MQTT] do_code_5003发生异常{e}")
            time.sleep(10)  # 异常后晚10秒启动推送，给MQTT链接创造时间


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


def start_mqtt_thread_jiangsudx(web_client, hang_state):
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

    thread_1003 = Thread(target=run_1003, args=([]), daemon=True)
    thread_1003.start()
    logger.get_log().info("[MQTT] 启动 1003定时推送舱门状态 [完成]")

    thread_2003 = Thread(target=run_2003, args=([]), daemon=True)
    thread_2003.start()
    logger.get_log().info("[MQTT] 启动 2003定时推送归中装置状态 [完成]")

    thread_3003 = Thread(target=run_3003, args=([]), daemon=True)
    thread_3003.start()
    logger.get_log().info("[MQTT] 启动 3003定时推送空调状态 [完成]")

    thread_4003 = Thread(target=run_4003, args=([]), daemon=True)
    thread_4003.start()
    logger.get_log().info("[MQTT] 启动 4003定时推送气象站状态 [完成]")

    thread_4004 = Thread(target=run_4004, args=([]), daemon=True)
    thread_4004.start()
    logger.get_log().info("[MQTT] 启动 4004定时推送气象站数据上传 [完成]")

    thread_5003 = Thread(target=run_5003, args=([]), daemon=True)
    thread_5003.start()
    logger.get_log().info("[MQTT] 启动 5003定时推送充电状态 [完成]")

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
    return json.dumps(result_message)


'''
查询舱门状态
'''


def do_code_1003():
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/shelterdoor"  # 该接口的主题
    result_message = {
        "msgType": "1",
        "msgCode": "1003",
        "msgExplain": "查询舱门状态",
        "data": {
            "respCode": "000",
            "respMsg": "已关闭"
        }
    }
    try:
        result = hangstate.get_hanger_door()
        if result == "open":
            result_message['data']['respMsg'] = "已打开"
    except Exception as e:
        result_message['data']['respCode'] = "001"
        result_message['data']['respMsg'] = "设备状态异常"

    result_json = json.dumps(result_message, ensure_ascii=False)
    global num_1003
    num_1003 += 1
    if num_1003 % 30 == 0:
        publish(topic_publish, result_json)
    else:
        publish_debug_log(topic_publish, result_json)


'''
查询归中装置状态
'''


def do_code_2003():
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/centerdevice"  # 该接口的主题
    result_message = {
        "msgType": "1",
        "msgCode": "2003",
        "msgExplain": "查询归中装置状态",
        "data": {
            "respCode": "000",
            "respMsg": "已归中"
        }
    }
    try:
        result = hangstate.get_hanger_bar()
        if result == "open":
            result_message['data']['respMsg'] = "已复位"
    except Exception as e:
        result_message['data']['respCode'] = "001"
        result_message['data']['respMsg'] = "设备状态异常"

    result_json = json.dumps(result_message, ensure_ascii=False)
    global num_2003
    num_2003 += 1
    if num_2003 % 30 == 0:
        publish(topic_publish, result_json)
    else:
        publish_debug_log(topic_publish, result_json)


'''
查询空调状态
'''


def do_code_3003():
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/airconditioner"  # 该接口的主题
    result_message = {
        "msgType": "1",
        "msgCode": "3003",
        "msgExplain": "查询空调状态",
        "data": {
            "respCode": "000",
            "respMsg": "关闭状态"
        }
    }
    try:
        result = hangstate.get_air_condition()
        if result == "open":
            result_message['data']['respMsg'] = "开启状态"
    except Exception as e:
        result_message['data']['respCode'] = "001"
        result_message['data']['respMsg'] = "异常状态"

    result_json = json.dumps(result_message, ensure_ascii=False)
    global num_3003
    num_3003 += 1
    if num_3003 % 30 == 0:
        publish(topic_publish, result_json)
    else:
        publish_debug_log(topic_publish, result_json)


'''
查询气象站状态
'''


def do_code_4003():
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/weatherstation"  # 该接口的主题
    result_message = {
        "msgType": "1",
        "msgCode": "4003",
        "msgExplain": "查询气象站状态",
        "data": {
            "respCode": "000",
            "respMsg": "开启状态"
        }
    }
    # 气象站固定运行开启
    result_json = json.dumps(result_message, ensure_ascii=False)
    global num_4003
    num_4003 += 1
    if num_4003 % 30 == 0:
        publish(topic_publish, result_json)
    else:
        publish_debug_log(topic_publish, result_json)


'''
气象站数据上传
'''


def do_code_4004():
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/airconditioner"  # 该接口的主题
    result_message = {
        "msgType": "1",
        "msgCode": "4004",
        "msgExplain": "气象站数据上传",
        "data": {
            "respCode": "000",
            "respMsg": "数据正常",
            "temperature": "",
            "humidity": "",
            "windvelocity": "",
            "winddirection": "",
            "rainfall": ""
        }
    }
    #  风速
    windvelocity = hangstate.get_windspeed()
    result_message['data']['windvelocity'] = windvelocity
    #  风向
    winddirection = hangstate.get_winddirection()
    if winddirection == "北风":
        winddirection_info = "North"
    elif winddirection == "东北风":
        winddirection_info = "Northeast"
    elif winddirection == "东风":
        winddirection_info = "East"
    elif winddirection == "东南风":
        winddirection_info = "Southeast"
    elif winddirection == "南风":
        winddirection_info = "South"
    elif winddirection == "西南风":
        winddirection_info = "Southwest"
    elif winddirection == "西风":
        winddirection_info = "West"
    elif winddirection == "西北风":
        winddirection_info = "Northwest"
    elif winddirection == "北":  # 旧版本一个特性代指[兼容]
        winddirection_info = "North"
    else:
        winddirection_info = "North"
    result_message['data']['winddirection'] = winddirection_info

    # try:
    #
    #
    #
    # except Exception as e:
    #     result_message['data']['respCode'] = "001"
    #     result_message['data']['respMsg'] = "异常状态"

    result_json = json.dumps(result_message, ensure_ascii=False)
    global num_4004
    num_4004 += 1
    if num_4004 % 30 == 0:
        publish(topic_publish, result_json)
    else:
        publish_debug_log(topic_publish, result_json)

'''
充电状态
'''


def do_code_5003():
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/chargingdevice"  # 该接口的主题
    result_message = {
        "msgType": "1",
        "msgCode": "5003",
        "msgExplain": "充电状态",
        "data": {
            "respCode": "000",
            "respMsg": "未充电"
        }
    }

    try:
        result = hangstate.get_wfcstate()
        if result == "charging":
            result_message['data']['respMsg'] = "正在充电"
    except Exception as e:
        result_message['data']['respCode'] = "001"
        result_message['data']['respMsg'] = "异常状态"
    result_json = json.dumps(result_message, ensure_ascii=False)
    global num_5003
    num_5003 += 1
    if num_5003 % 30 == 0:
        publish(topic_publish, result_json)
    else:
        publish_debug_log(topic_publish, result_json)


def do_code_7001():
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/info"  # 该接口的主题
    result_message = {
        "msgType": "1",
        "msgCode": "7001",
        "msgExplain": "方舱信息",
        "data": {
            "serialNumber": BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "serialNumber"),
            "type": BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "type"),
            "adapter": BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "adapter"),
            "adress": BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "adress"),
            "alternatePoint": BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "alternatePoint"),
            "doorSpeed": BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "doorSpeed"),
            "centerSpeed": BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "centerSpeed"),
            "mqttHost": BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "mqttHost"),
            "mqttPort": BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "mqttPort"),
            "mqttUserName": BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "mqttUserName"),
            "mqttPassWord": BASEUtile.InitFileTool.get_str_value("mqtt_edit_info", "mqttPassWord")
        }
    }
    result_json = json.dumps(result_message)
    publish(topic_publish, result_json)


def do_code_7004():
    topic_publish = f"uavshelter/devicecontral/{ini_serialNumber}/status"  # 该接口的应答主题
    shelterdoor_result = hangstate.get_hanger_door()
    shelterdoor = "已关闭"
    if shelterdoor_result == "open":
        shelterdoor = "已打开"

    centerdevice_result = hangstate.get_hanger_bar()
    centerdevice = "已归中"
    if centerdevice_result == "open":
        centerdevice = "已复位"

    chargingdevice_result = hangstate.get_wfcstate()
    # chargingdevice_value = hangstate.get_wfc_battery_value()
    chargingdevice = "未充电"
    if chargingdevice_result == "charging":
        chargingdevice = "正在充电"
    elif chargingdevice_result == "full":
        chargingdevice = "充电完成"

    # airconditioner = str(hangstate.indoor_tem())
    # weatherstation_temperature = str(hangstate.get_temperature())
    weatherstation_windvelocity = hangstate.get_windspeed()

    weatherstation_winddirection_result = hangstate.get_winddirection()
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
    result_json = json.dumps(result_message)
    publish_debug_log(topic_publish, result_json)  # 因为心跳调用频繁，改为debug日志输出


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
    start_mqtt_thread_jiangsudx(None, None)
    logger.get_log().info("====2")
    # time.sleep(5)
    publish(f"uavshelter/devicecontral/{ini_serialNumber}", "ha")
    time.sleep(60)
